# Backend server using FastAPI and Uvicorn.
#
# Notes:
# - Chat handling is currently session-based.
# - Authentication and account data are persisted in PostgreSQL.
# - Medical profiles are stored separately from login accounts.
# - Chat history is still managed through the session manager unless explicitly persisted elsewhere.
#
# Requirements:
# <bash> pip install -r requirements.txt
#
# Run:
# <bash> uvicorn main:app --reload
# or
# <bash> python -m uvicorn main:app --reload

import re
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session
from auth.security import get_optional_current_account, get_session
from database.models import User
from profiles.service import get_profile_access_role
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database.connection import create_db_and_tables
from auth.router import router as auth_router
from chat_history.router import router as chat_history_router
from profiles.router import router as profiles_router
from medications.router import router as medications_router
from medications.service import list_medications
from symptoms.router import router as symptoms_router
from symptoms.service import list_symptom_entries
from appointments.router import router as appointments_router
from logging_config import configure_logging
from fhir_mapper.careena4_adapter import build_fhir_bundle_from_careena4_session
from appointments.schemas import AppointmentSearchRequest, AppointmentSearchResponse
from appointments.service import AppointmentProviderUnavailable, search_fhir_appointments

from uuid import uuid4 #for turn_id

from careena4.bootstrap import build_default_services, build_simulation_runner #for Careena4 runtime: LLM, TurnEngine, SessionStore
from careena4.models.turn import RecommendationRequestInput, TurnInput, TurnResult #for User message in Careena4 and Response-Helpfunction
from careena4.models.turn.input import DiaryEntry, MedicationEntry, ProfileSnapshot
from careena4.application.dialogue.person_initialiser import PersonInitialiser
from careena4.models.input import (
    CancelDraftResponse,
    SymptomDraftResponse,
    SymptomDraftUpdateRequest,
)
from careena4.simulation_runtime import (
    SimulationRequest,
    normalized_simulation_request,
    run_simulation_command,
)

app = FastAPI()

# Careena4 is the chat runtime used by /session, /chatscreen and /input-drafts.
# Sessions are kept in memory for the current backend process.
# This is acceptable for the demo deployment, but sessions are reset on backend restart.
careena4_services = build_default_services(llm_mode="env")
careena4_turn_engine = careena4_services.turn_engine
careena4_session_store = careena4_services.session_store
careena4_session_profiles: dict[str, int | None] = {}
# session_id -> profile the case is *about* (the "Für wen?" answer), which can
# differ from the session's owning profile above. Kept separate so the session
# still belongs to the authenticated active profile (cross-profile guard),
# while diary, medications and the reported profile follow the chosen person.
careena4_session_case_profiles: dict[str, int] = {}
# session_ids whose "Für wen?" answer resolved to a person with no diary profile
# ("Jemand anderes" or a free-form relation like "meine Oma"). For these the case
# is deliberately *not* bound to any profile, so diary, medications and the
# reported profile must NOT fall back to the active session profile.
careena4_session_unbound_cases: set[str] = set()
careena4_person_initialiser = PersonInitialiser()
careena4_simulation_runner = build_simulation_runner(system_llm_mode="env")


def _snapshot_from_profile(p) -> ProfileSnapshot:
    """Maps a server-layer Profile ORM object to a careena4 ProfileSnapshot."""
    from datetime import date as _date

    def _age(dob) -> int | None:
        if dob is None:
            return None
        today = _date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def _sex(bio: str | None) -> str | None:
        if not bio:
            return None
        s = bio.strip().lower()
        if s in ("female", "weiblich", "f", "w"):
            return "female"
        if s in ("male", "männlich", "maennlich", "m"):
            return "male"
        if s in ("diverse", "divers", "d"):
            return "diverse"
        return None

    return ProfileSnapshot(
        display_name=p.display_name,
        profile_type=p.profile_type,
        id=p.id,
        age=_age(p.date_of_birth),
        sex=_sex(p.biological_sex),
    )
careena4_llm_health_status: dict[str, object] = {
    "available": False,
    "model": careena4_services.call_model_config.default_model,
    "checked_at": None,
}

app.state.careena4_session_store = careena4_session_store
app.state.careena4_session_profiles = careena4_session_profiles

app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(medications_router)
app.include_router(appointments_router)
app.include_router(chat_history_router)
app.include_router(symptoms_router)

# CORS is permissive for local Flutter development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure_logging()

class ChatRequest(BaseModel):
    message: str
    session_id: str
    profile_id: int | None = None


class SessionRequest(BaseModel):
    profile_id: int | None = None


def _refresh_llm_health_status() -> bool:
    checked_model = careena4_services.call_model_config.default_model
    available = careena4_services.llm_client.is_model_available(checked_model)
    careena4_llm_health_status.update(
        {
            "available": available,
            "model": checked_model,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return available


class RecommendationRequest(BaseModel):
    session_id: str


class SetObservationSeveritiesRequest(BaseModel):
    session_id: str
    severities: dict[str, int]  # symptom label -> severity (1-10)


def require_careena4_session(session_id: str):
    careena4_session = careena4_session_store.get(session_id)

    if careena4_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found.",
        )

    return careena4_session


def require_careena4_session_access(
        session_id: str,
        current_user: User | None,
        db_session: Session,
):
    careena4_session = require_careena4_session(session_id)
    profile_id = careena4_session_profiles.get(session_id)

    if profile_id is None:
        return careena4_session

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required for profile draft requests.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=db_session,
    )

    return careena4_session

def _resolve_onset_date(onset: str | None) -> str | None:
    """Resolve a German temporal onset string to an ISO date string (YYYY-MM-DD)."""
    if not onset:
        return None
    today = datetime.now().date()
    s = onset.lower().strip()

    if s in ("heute", "today"):
        return today.isoformat()
    if s in ("gestern", "yesterday"):
        return (today - timedelta(days=1)).isoformat()
    if s == "vorgestern":
        return (today - timedelta(days=2)).isoformat()
    if re.search(r"seit\s+heute", s):
        return today.isoformat()
    if re.search(r"seit\s+gestern", s):
        return (today - timedelta(days=1)).isoformat()
    if re.search(r"seit\s+vorgestern", s):
        return (today - timedelta(days=2)).isoformat()
    m = re.search(r"seit\s+(\d+)\s+tag", s)
    if m:
        return (today - timedelta(days=int(m.group(1)))).isoformat()
    m = re.search(r"seit\s+einer\s+woche?", s)
    if m:
        return (today - timedelta(weeks=1)).isoformat()
    m = re.search(r"seit\s+(\d+)\s+woche?n?", s)
    if m:
        return (today - timedelta(weeks=int(m.group(1)))).isoformat()
    # Future references — ignore
    if any(w in s for w in ("übermorgen", "nächste woche", "morgen früh")):
        return None
    return None


_MEDICATION_FREQUENCY_LABELS = {
    "daily": "täglich",
    "twice_daily": "zweimal täglich",
    "weekdays": "werktags",
    "weekly": "wöchentlich",
    "monthly": "monatlich",
}


def _resolve_subject_profile_id(session_id: str, session_profile_id):
    """Profile the case is *about*, used to load diary/medications and report to
    the client (PDF export).

    Order of precedence:
      1. Non-profile subject ("Jemand anderes"/free-form) -> None, so no data of
         the active profile leaks into a case that is not about that person.
      2. A profile explicitly chosen in the "Für wen?" step.
      3. Fallback to the session's owning (active) profile.
    """
    if session_id in careena4_session_unbound_cases:
        return None
    return careena4_session_case_profiles.get(session_id) or session_profile_id


def _load_diary_history(profile_id, current_user, session) -> list[DiaryEntry]:
    """Load the symptom diary for a profile as pipeline DiaryEntry objects."""
    if profile_id is None:
        return []
    raw_entries = list_symptom_entries(
        profile_id=profile_id,
        current_user=current_user,
        session=session,
    )
    return [
        DiaryEntry(
            date=e.date.isoformat() if hasattr(e.date, "isoformat") else str(e.date),
            symptom=e.symptom,
            body_area=e.body_area or "",
            intensity=e.intensity,
            note=e.note or "",
        )
        for e in raw_entries
    ]


def _load_medication_history(profile_id, current_user, session) -> list[MedicationEntry]:
    """Load the medication plan for a profile as pipeline MedicationEntry objects."""
    if profile_id is None:
        return []
    raw_entries = list_medications(
        profile_id=profile_id,
        current_user=current_user,
        session=session,
    )
    history: list[MedicationEntry] = []
    for e in raw_entries:
        times = [f"{e.intake_hour:02d}:{e.intake_minute:02d}"]
        if e.second_intake_hour is not None and e.second_intake_minute is not None:
            times.append(f"{e.second_intake_hour:02d}:{e.second_intake_minute:02d}")
        history.append(
            MedicationEntry(
                name=e.name,
                dose=e.dose or "",
                frequency=_MEDICATION_FREQUENCY_LABELS.get(e.frequency, e.frequency),
                schedule=", ".join(times),
                active_substance=(
                    e.catalog_item.active_substance if e.catalog_item else ""
                ),
            )
        )
    return history


#Helper: convert Careena4 TurnResult into the Flutter chat response JSON.
def build_careena4_chat_response(result: TurnResult) -> dict:
    active_question = result.conversation_state.active_question
    pending_followup = None

    if active_question is not None and active_question.kind in {
        "followup",
        "person_clarification",
    }:
        pending_followup = {
            "question_id": active_question.question_id,
            "kind": active_question.kind,
            "question_intent": active_question.question_intent,
            "target_observation_id": active_question.target_observation_id,
            "target_followup_id": active_question.target_followup_id,
            "prompt_text": active_question.prompt_text,
            "blocking": active_question.blocking,
        }

    recommendation_state = result.recommendation_state
    recommendation_ready = bool(
        recommendation_state is not None
        and recommendation_state.recommendation_allowed
    )

    reply_options: list[str] = []
    reply_suggestions: list[str] = []
    if active_question is not None:
        if active_question.guided_input is not None and active_question.guided_input.options:
            reply_options = [opt.label for opt in active_question.guided_input.options]
        elif active_question.reply_suggestions:
            reply_suggestions = active_question.reply_suggestions

    case_observations = []
    if result.medical_case is not None:
        case_observations = [
            {
                "label": obs.label,
                "severity": obs.severity,
                "onset_date": _resolve_onset_date(obs.onset),
            }
            for obs in result.medical_case.observations
            if obs.is_active() and obs.label
        ]

    return {
        "response": result.response_text,
        "response_mode": result.response_mode,
        "red_flag": result.response_mode == "emergency",
        "trace_notes": list(result.trace_notes),
        "pending_followup": pending_followup,
        "recommendation_ready": recommendation_ready,
        "reply_options": reply_options,
        "reply_suggestions": reply_suggestions,
        "recommendation_result": (
            result.recommendation_result.model_dump()
            if result.recommendation_result is not None
            else None
        ),
        "action": (
            result.recommendation_result.next_step
            if result.recommendation_result is not None
            else None
        ),
        "severity": (
            result.recommendation_result.urgency_level
            if result.recommendation_result is not None
            else None
        ),
        "case_observations": case_observations,
    }

@app.get("/fhir/export/{session_id}")
def export_fhir_bundle(
        session_id: str,
        current_user: User | None = Depends(get_optional_current_account),
        db_session: Session = Depends(get_session),
):
    careena4_session = require_careena4_session_access(
        session_id=session_id,
        current_user=current_user,
        db_session=db_session,
    )

    if careena4_session.medical_case is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No extracted medical case data available for this session.",
        )

    return build_fhir_bundle_from_careena4_session(careena4_session)


def build_careena4_simrun_response(*, message: str) -> dict:
    selector = message.strip()[len("/simrun"):].strip()
    response_text = run_simulation_command(
        selector=selector,
        simulation_runner=careena4_simulation_runner,
    )
    return {
        "response": response_text,
        "red_flag": "Stop-Grund: emergency" in response_text,
    }

@app.post("/appointments/search", response_model=AppointmentSearchResponse)
def search_appointments(
        request: AppointmentSearchRequest,
        current_user: User | None = Depends(get_optional_current_account),
        db_session: Session = Depends(get_session),
):
    careena4_session = require_careena4_session_access(
        session_id=request.session_id,
        current_user=current_user,
        db_session=db_session,
    )

    session_profile_id = careena4_session_profiles.get(request.session_id)

    if session_profile_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Chat session is not linked to a profile.",
        )

    if session_profile_id != request.profile_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Requested profile does not match chat session profile.",
        )

    recommendation_state = getattr(careena4_session, "recommendation_state", None)
    recommendation_result = getattr(
        recommendation_state,
        "recommendation_result",
        None,
    )

    if recommendation_result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No Careena recommendation available for this session.",
        )

    fhir_bundle = build_fhir_bundle_from_careena4_session(
        careena4_session,
        profile_id=request.profile_id,
    )

    try:
        return search_fhir_appointments(
            session_id=request.session_id,
            profile_id=request.profile_id,
            postal_code=request.postal_code,
            recommendation_result=recommendation_result,
            fhir_bundle=fhir_bundle,
        )
    except AppointmentProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

app.state.careena4_turn_engine = careena4_turn_engine
app.state.careena4_response_builder = build_careena4_chat_response

def persist_careena4_turn_result(*, careena4_session, turn_result: TurnResult) -> None:
    careena4_session.medical_case = turn_result.medical_case
    careena4_session.conversation_state = turn_result.conversation_state
    careena4_session.recommendation_state = turn_result.recommendation_state
    careena4_session.last_turn_interpretation = getattr(turn_result, "turn_interpretation", None)
    careena4_session.last_turn_understanding = turn_result.current_turn_understanding

    if turn_result.symptom_input_draft is not None:
        careena4_session.symptom_input_draft = turn_result.symptom_input_draft


#1. checks if Careena4-Session exist
#2. validate empty input
#3. save profile_id
#4. build TurnInput
#5. Careena4 processes TurnInput
#6. write new state in session
#7. build API-Response for Flutter

@app.post("/chatscreen")
def chat(
        req: ChatRequest,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    careena4_session = require_careena4_session(req.session_id)

    if not req.message.strip():
        return {"response": "Fehler: Leere Eingabe.", "red_flag": False}

    session_profile_id = careena4_session_profiles.get(req.session_id)

    if session_profile_id is None and req.profile_id is not None:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required for profile chat requests.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        get_profile_access_role(
            account_id=current_user.id,
            profile_id=req.profile_id,
            session=session,
        )

        careena4_session_profiles[req.session_id] = req.profile_id
        session_profile_id = req.profile_id

    elif session_profile_id is not None:
        if req.profile_id is not None and req.profile_id != session_profile_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chat session belongs to a different profile.",
            )

        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required for profile chat requests.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        get_profile_access_role(
            account_id=current_user.id,
            profile_id=session_profile_id,
            session=session,
        )

    if req.message.strip().startswith("/simrun"):
        careena4_session.messages.append({"role": "user", "content": req.message})
        response = build_careena4_simrun_response(message=req.message)
        careena4_session.messages.append(
            {"role": "assistant", "content": response["response"]}
        )
        return response

    turn_id = str(uuid4())

    needs_profile_pre_turn = (
        careena4_session.medical_case is None
        and current_user is not None
        and (
            careena4_session.conversation_state is None
            or careena4_session.conversation_state.active_question is None
        )
    )
    if needs_profile_pre_turn:
        # Safety-critical messages (catalog match) bypass profile selection so the
        # safety question fires immediately without making the user pick a person first.
        raw_safety_precheck = careena4_turn_engine.raw_red_flag_detector.detect(req.message)
        if raw_safety_precheck.requires_safety_clarification or raw_safety_precheck.requires_emergency_response:
            needs_profile_pre_turn = False
    if needs_profile_pre_turn:
        try:
            from profiles.service import list_profiles
            snapshots = [_snapshot_from_profile(p) for p in list_profiles(current_user=current_user, session=session)]
            skip_turn = careena4_person_initialiser.pre_turn(
                session_id=req.session_id,
                careena4_session=careena4_session,
                profiles=snapshots,
                pending_message=req.message,
            )
        except Exception:
            skip_turn = False

        if skip_turn:
            question = careena4_session.conversation_state.active_question
            reply_options = (
                [opt.label for opt in question.guided_input.options]
                if question.guided_input is not None and question.guided_input.options
                else []
            )
            careena4_session.messages.append({"role": "user", "content": req.message})
            careena4_session.messages.append({"role": "assistant", "content": question.prompt_text})
            return {
                "response": question.prompt_text,
                "response_mode": "ask_followup",
                "red_flag": False,
                "trace_notes": [],
                "pending_followup": {
                    "question_id": question.question_id,
                    "kind": question.kind,
                    "question_intent": question.question_intent,
                    "target_observation_id": question.target_observation_id,
                    "target_followup_id": question.target_followup_id,
                    "prompt_text": question.prompt_text,
                    "blocking": question.blocking,
                },
                "recommendation_ready": False,
                "reply_options": reply_options,
                "reply_suggestions": [],
                "recommendation_result": None,
                "action": None,
                "severity": None,
                "case_observations": [],
            }

    subject_profile_id = _resolve_subject_profile_id(req.session_id, session_profile_id)
    diary_history = _load_diary_history(subject_profile_id, current_user, session)

    turn_result = careena4_turn_engine.run_turn(
        TurnInput.from_persisted_state(
            message=req.message,
            session_id=req.session_id,
            turn_id=turn_id,
            profile_id=session_profile_id,
            diary_history=diary_history,
            conversation_messages=careena4_session.messages,
            persisted_medical_case=careena4_session.medical_case,
            persisted_conversation_state=careena4_session.conversation_state,
            persisted_recommendation_state=careena4_session.recommendation_state,
            persisted_symptom_input_draft=careena4_session.symptom_input_draft,
        )
    )

    careena4_llm_health_status.update(
        {
            "available": True,
            "model": careena4_services.call_model_config.default_model,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    persist_careena4_turn_result(
        careena4_session=careena4_session,
        turn_result=turn_result,
    )

    careena4_session.messages.append({"role": "user", "content": req.message})

    response = build_careena4_chat_response(turn_result)

    (
        profile_warning,
        profile_reply_options,
        pending_message,
        matched_profile_id,
        resolved_non_profile,
    ) = careena4_person_initialiser.post_turn(
        session_id=req.session_id,
        careena4_session=careena4_session,
        message=req.message,
    )
    # The user picked a profile in the "Für wen?" step. Record it as the case
    # subject so diary, medications and the reported profile_id follow that
    # person, without changing the session's owning profile (which stays the
    # authenticated active profile and keeps the cross-profile guard intact).
    if matched_profile_id is not None:
        careena4_session_case_profiles[req.session_id] = matched_profile_id
        careena4_session_unbound_cases.discard(req.session_id)
        if matched_profile_id != subject_profile_id:
            subject_profile_id = matched_profile_id
            diary_history = _load_diary_history(subject_profile_id, current_user, session)
    elif resolved_non_profile:
        # Case is explicitly about a person without a profile. Unbind it so the
        # deferred medical message (and later the recommendation/PDF) does not
        # pull the active profile's diary, medications or reported profile_id.
        careena4_session_unbound_cases.add(req.session_id)
        careena4_session_case_profiles.pop(req.session_id, None)
        subject_profile_id = None
        diary_history = []
    if profile_warning:
        response["response"] = profile_warning
        response["reply_options"] = profile_reply_options
    elif pending_message:
        # Profile just got resolved — process the medical message that was
        # deferred while we waited for the user to pick a profile. Drop any
        # follow-up question the first turn queued while the person was
        # still unresolved (e.g. person_missing); it's stale now that
        # post_turn() has filled in relation/age/sex from the profile.
        if careena4_session.conversation_state is not None:
            careena4_session.conversation_state.active_question = None
        second_turn_result = careena4_turn_engine.run_turn(
            TurnInput.from_persisted_state(
                message=pending_message,
                session_id=req.session_id,
                turn_id=str(uuid4()),
                profile_id=session_profile_id,
                diary_history=diary_history,
                conversation_messages=careena4_session.messages,
                persisted_medical_case=careena4_session.medical_case,
                persisted_conversation_state=careena4_session.conversation_state,
                persisted_recommendation_state=careena4_session.recommendation_state,
                persisted_symptom_input_draft=careena4_session.symptom_input_draft,
            )
        )
        persist_careena4_turn_result(
            careena4_session=careena4_session,
            turn_result=second_turn_result,
        )
        careena4_session.messages.append({"role": "user", "content": pending_message})
        response = build_careena4_chat_response(second_turn_result)

    careena4_session.messages.append(
        {"role": "assistant", "content": response["response"]}
    )

    return response


@app.post("/chatscreen/set-severities")
def set_observation_severities(
        req: SetObservationSeveritiesRequest,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """Update observation severities directly in the session.

    Called when the user sets intensity via the in-chat symptom editor.
    Also resolves any pending severity question for affected observations so
    the backend will not ask again.
    """
    careena4_session = require_careena4_session_access(
        session_id=req.session_id,
        current_user=current_user,
        db_session=session,
    )

    if careena4_session.medical_case is None:
        return {"ok": True}

    label_map = {label.casefold(): severity for label, severity in req.severities.items()}

    for obs in careena4_session.medical_case.observations:
        if obs.is_active() and obs.label.casefold() in label_map:
            obs.severity = str(label_map[obs.label.casefold()])

    # Resolve the active severity question if it now has an answer.
    active_q = careena4_session.conversation_state.active_question
    if active_q is not None and active_q.question_intent == "severity":
        target_id = active_q.target_observation_id
        if target_id:
            for obs in careena4_session.medical_case.observations:
                if obs.observation_id == target_id and obs.severity is not None:
                    careena4_session.conversation_state.active_question = None
                    break

    return {"ok": True}


@app.post("/recommendation/request")
def request_recommendation(
        req: RecommendationRequest,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    careena4_session = require_careena4_session_access(
        session_id=req.session_id,
        current_user=current_user,
        db_session=session,
    )

    turn_id = str(uuid4())

    session_profile_id = careena4_session_profiles.get(req.session_id)
    # Diary, medications and the reported profile follow the case subject (the
    # "Für wen?" answer) when it differs from the session's owning profile, and
    # are dropped entirely when the case is about a person without a profile.
    subject_profile_id = _resolve_subject_profile_id(req.session_id, session_profile_id)
    diary_history = _load_diary_history(subject_profile_id, current_user, session)
    medication_history = _load_medication_history(subject_profile_id, current_user, session)

    turn_result = careena4_turn_engine.request_recommendation(
        RecommendationRequestInput.from_persisted_state(
            session_id=req.session_id,
            turn_id=turn_id,
            conversation_messages=careena4_session.messages,
            diary_history=diary_history,
            medication_history=medication_history,
            persisted_medical_case=careena4_session.medical_case,
            persisted_conversation_state=careena4_session.conversation_state,
            persisted_recommendation_state=careena4_session.recommendation_state,
            persisted_symptom_input_draft=careena4_session.symptom_input_draft,
        )
    )

    persist_careena4_turn_result(
        careena4_session=careena4_session,
        turn_result=turn_result,
    )

    response = build_careena4_chat_response(turn_result)
    # Expose the case subject profile so the client (e.g. the PDF export) uses
    # the profile the recommendation is actually about — not the app's currently
    # selected profile, which can differ after in-chat person resolution.
    response["profile_id"] = subject_profile_id
    careena4_session.messages.append(
        {"role": "assistant", "content": response["response"]}
    )
    return response


@app.post("/simulation/run")
def run_simulation(req: SimulationRequest):
    result = careena4_simulation_runner.run(normalized_simulation_request(req))
    return result.model_dump()

@app.post("/warmup")
def warmup():
    """
    Lightweight readiness endpoint for the chat backend.

    Called when a new chat session starts, so it is the explicit refresh path
    for the cached LLM status. Repeated health polling reads the cached value.
    """
    available = _refresh_llm_health_status()
    return {
        "status": "ok" if available else "unavailable",
        "llm": available,
        "model": careena4_llm_health_status["model"],
        "checked_at": careena4_llm_health_status["checked_at"],
    }


@app.get("/health/server")
def health_server():
    return {"status": "ok", "server": True}


@app.get("/health/llm")
def health_llm():
    checked_model = careena4_llm_health_status["model"]

    if not careena4_llm_health_status["available"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "LLM service is not reachable.",
                "model": checked_model,
                "checked_at": careena4_llm_health_status["checked_at"],
            },
        )

    return {
        "status": "ok",
        "llm": True,
        "model": checked_model,
        "checked_at": careena4_llm_health_status["checked_at"],
    }


@app.get("/input-drafts/{session_id}", response_model=SymptomDraftResponse)
def get_input_draft(
        session_id: str,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """
    Return the current editable symptom draft for a Careena4 session.
    """
    careena4_session = require_careena4_session_access(
        session_id=session_id,
        current_user=current_user,
        db_session=session,
    )

    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=careena4_session.symptom_input_draft.symptom_labels(),
        chips=careena4_session.symptom_input_draft.chips,
    )


@app.patch("/input-drafts/{session_id}", response_model=SymptomDraftResponse)
def update_input_draft(
        session_id: str,
        request: SymptomDraftUpdateRequest,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """
    Replace the editable symptom draft after user edits in the frontend.
    """
    careena4_session = require_careena4_session_access(
        session_id=session_id,
        current_user=current_user,
        db_session=session,
    )

    if request.chips is not None:
        careena4_session.symptom_input_draft.replace_from_chips(request.chips)
    else:
        careena4_session.symptom_input_draft.replace_from_labels(request.symptoms)

    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=careena4_session.symptom_input_draft.symptom_labels(),
        chips=careena4_session.symptom_input_draft.chips,
    )

@app.delete("/input-drafts/{session_id}", response_model=CancelDraftResponse)
def cancel_input_draft(
        session_id: str,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """
    Clear the editable symptom draft for a Careena4 session.
    """
    careena4_session = require_careena4_session_access(
        session_id=session_id,
        current_user=current_user,
        db_session=session,
    )

    careena4_session.symptom_input_draft.replace_from_labels([])

    return CancelDraftResponse(
        message="Draft cancelled successfully.",
        session_id=session_id,
    )


@app.post("/session")
def create_session(
    req: SessionRequest | None = None,
    current_user: User | None = Depends(get_optional_current_account),
    session: Session = Depends(get_session),
):
    """
    Create and return a new chat session id.
    """
    profile_id = req.profile_id if req is not None else None

    if profile_id is not None:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required for profile chat sessions.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        get_profile_access_role(
            account_id=current_user.id,
            profile_id=profile_id,
            session=session,
        )

    session_id = careena4_session_store.create_session()
    careena4_session_profiles[session_id] = profile_id

    print("Created Careena4 session:", session_id)
    return {"session_id": session_id}

# Editor: Ilu
# Modified as part of the authentication and profile management implementation.
# Runs automatically when the FastAPI server starts.
# Creates all database tables if they do not already exist.
def _seed_catalog() -> None:
    """Run catalog seed imports on startup. Logs a warning on failure instead of crashing."""
    try:
        from database.seed_catalog import (
            seed_assessment_criteria,
            seed_consultation_reason_criteria_links,
            seed_consultation_reasons,
        )
        r1 = seed_consultation_reasons()
        r2 = seed_assessment_criteria()
        r3 = seed_consultation_reason_criteria_links()
        print(f"Catalog seeded: reasons={r1}, criteria={r2}, links={r3}")
    except Exception as exc:
        print(f"Warning: Catalog seeding skipped ({exc})")


@app.on_event("startup")
def on_startup():
    """
    Initialize database tables on application startup.
    """
    create_db_and_tables()
    _seed_catalog()
    n = careena4_services.safety_catalog_cache.load()
    print(f"SafetyCatalogCache loaded: {n} entries")
    _refresh_llm_health_status()
