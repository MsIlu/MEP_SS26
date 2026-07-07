"""Orchestration logic for the Careena4 chat endpoints.

Everything here is HTTP-agnostic apart from raising HTTPException for access
errors; the thin route handlers live in chat.router. Session state comes from
chat.runtime and is persisted back onto the in-memory session objects.

Collaborators that tests replace (turn engine, profile/appointment services)
are deliberately accessed as module attributes (runtime.X, profiles_service.X)
so monkeypatching the owning module takes effect here as well.
"""

import logging
import re
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from sqlmodel import Session, select

from appointments import service as appointments_service
from appointments.schemas import AppointmentSearchRequest, AppointmentSearchResponse
from appointments.service import AppointmentProviderUnavailable
from careena4.domain.case import CaseManager
from careena4.models.turn import RecommendationRequestInput, TurnInput, TurnResult
from careena4.models.turn.input import DiaryEntry, MedicationEntry, ProfileSnapshot
from careena4.models.workflow.recommendation_result import RecommendationResult
from careena4.simulation_runtime import run_simulation_command
from chat import runtime
from chat.schemas import ChatRequest, RecommendationRequest, SetObservationSeveritiesRequest
from database.models import ChatHistory, User
from fhir_mapper.careena4_adapter import build_fhir_bundle_from_careena4_session
from medications.service import list_medications
from profiles import service as profiles_service
from symptoms.service import list_symptom_entries

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Session access
# --------------------------------------------------------------------------

def require_careena4_session(session_id: str):
    """Return the in-memory Careena4 session or raise 404."""
    careena4_session = runtime.careena4_session_store.get(session_id)

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
    """Return the session after an access check.

    Anonymous sessions (no bound profile) are returned as-is; profile-bound
    sessions additionally require an authenticated account with access to that
    profile.
    """
    careena4_session = require_careena4_session(session_id)
    profile_id = runtime.careena4_session_profiles.get(session_id)

    if profile_id is None:
        return careena4_session

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required for profile draft requests.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    profiles_service.get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=db_session,
    )

    return careena4_session


def create_chat_session(
        *,
        profile_id: int | None,
        current_user: User | None,
        db_session: Session,
) -> str:
    """Create a new chat session, optionally bound to a profile."""
    if profile_id is not None:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required for profile chat sessions.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        profiles_service.get_profile_access_role(
            account_id=current_user.id,
            profile_id=profile_id,
            session=db_session,
        )

    session_id = runtime.careena4_session_store.create_session()
    runtime.careena4_session_profiles[session_id] = profile_id

    print("Created Careena4 session:", session_id)
    return session_id


# --------------------------------------------------------------------------
# Profile / history mapping helpers
# --------------------------------------------------------------------------

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
    if session_id in runtime.careena4_session_unbound_cases:
        return None
    return runtime.careena4_session_case_profiles.get(session_id) or session_profile_id


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


# --------------------------------------------------------------------------
# Response building
# --------------------------------------------------------------------------

def _pending_followup_payload(question) -> dict:
    """Serialize an active question for the pending_followup response field."""
    return {
        "question_id": question.question_id,
        "kind": question.kind,
        "question_intent": question.question_intent,
        "target_observation_id": question.target_observation_id,
        "target_followup_id": question.target_followup_id,
        "prompt_text": question.prompt_text,
        "blocking": question.blocking,
    }


def _question_reply_options(question) -> list[str]:
    """Return the guided-input option labels of a question (or an empty list)."""
    if question.guided_input is not None and question.guided_input.options:
        return [opt.label for opt in question.guided_input.options]
    return []


def build_careena4_chat_response(result: TurnResult) -> dict:
    """Convert a Careena4 TurnResult into the Flutter chat response JSON."""
    active_question = result.conversation_state.active_question
    pending_followup = None

    if active_question is not None and active_question.kind in {
        "followup",
        "person_clarification",
    }:
        pending_followup = _pending_followup_payload(active_question)

    recommendation_state = result.recommendation_state
    recommendation_ready = bool(
        recommendation_state is not None
        and recommendation_state.recommendation_allowed
    )

    reply_options: list[str] = []
    reply_suggestions: list[str] = []
    if active_question is not None:
        reply_options = _question_reply_options(active_question)
        if not reply_options and active_question.reply_suggestions:
            reply_suggestions = active_question.reply_suggestions

    case_observations = []
    if result.medical_case is not None:
        case_observations = [
            {
                "label": obs.normalized_label_de,
                "severity": obs.severity,
                "onset_date": _resolve_onset_date(obs.onset),
            }
            for obs in result.medical_case.observations
            if obs.is_active() and obs.normalized_label_de
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


def build_careena4_simrun_response(*, message: str) -> dict:
    """Handle the /simrun chat command (runs a scripted LLM simulation)."""
    selector = message.strip()[len("/simrun"):].strip()
    response_text = run_simulation_command(
        selector=selector,
        simulation_runner=runtime.careena4_simulation_runner,
    )
    return {
        "response": response_text,
        "red_flag": "Stop-Grund: emergency" in response_text,
    }


def persist_careena4_turn_result(*, careena4_session, turn_result: TurnResult) -> None:
    """Write the TurnResult state back onto the in-memory session."""
    careena4_session.medical_case = turn_result.medical_case
    careena4_session.conversation_state = turn_result.conversation_state
    careena4_session.recommendation_state = turn_result.recommendation_state
    careena4_session.last_turn_interpretation = getattr(turn_result, "turn_interpretation", None)
    careena4_session.last_turn_understanding = turn_result.current_turn_understanding

    if turn_result.symptom_input_draft is not None:
        careena4_session.symptom_input_draft = turn_result.symptom_input_draft


# --------------------------------------------------------------------------
# /chatscreen orchestration
# --------------------------------------------------------------------------

def handle_chat_message(
        *,
        req: ChatRequest,
        current_user: User | None,
        db_session: Session,
) -> dict:
    """Process one chat message and return the Flutter chat response.

    Flow:
      1. Validate the session and bind/verify its owning profile.
      2. Person pre-turn: on the first medical message ask "Für wen?" first —
         unless the message matches the safety catalog, in which case the
         safety question takes priority and the profile question is deferred.
      3. Run the TurnEngine and persist the resulting state on the session.
      4. Person post-turn: record the chosen case subject; if a medical message
         was deferred during profile selection, replay it as a second turn.
      5. If a safety clarification was just resolved, inject the deferred
         profile question before returning.
    """
    careena4_session = require_careena4_session(req.session_id)

    if not req.message.strip():
        return {"response": "Fehler: Leere Eingabe.", "red_flag": False}

    session_profile_id = _bind_session_profile(
        req=req,
        current_user=current_user,
        db_session=db_session,
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
    if needs_profile_pre_turn and _safety_bypass_profile_pre_turn(
        req=req,
        careena4_session=careena4_session,
        current_user=current_user,
        db_session=db_session,
    ):
        needs_profile_pre_turn = False
    if needs_profile_pre_turn:
        skip_response = _profile_pre_turn_response(
            req=req,
            careena4_session=careena4_session,
            current_user=current_user,
            db_session=db_session,
        )
        if skip_response is not None:
            return skip_response

    subject_profile_id = _resolve_subject_profile_id(req.session_id, session_profile_id)
    diary_history = _load_diary_history(subject_profile_id, current_user, db_session)

    prev_active_question_kind = (
        careena4_session.conversation_state.active_question.kind
        if careena4_session.conversation_state and careena4_session.conversation_state.active_question
        else None
    )

    turn_result = runtime.careena4_turn_engine.run_turn(
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

    runtime.mark_llm_available()

    persist_careena4_turn_result(
        careena4_session=careena4_session,
        turn_result=turn_result,
    )

    careena4_session.messages.append({"role": "user", "content": req.message})

    response = build_careena4_chat_response(turn_result)

    response, profile_warning, pending_message = _apply_person_post_turn(
        req=req,
        careena4_session=careena4_session,
        current_user=current_user,
        db_session=db_session,
        session_profile_id=session_profile_id,
        subject_profile_id=subject_profile_id,
        diary_history=diary_history,
        response=response,
    )

    response = _maybe_inject_deferred_profile_question(
        req=req,
        careena4_session=careena4_session,
        current_user=current_user,
        db_session=db_session,
        prev_active_question_kind=prev_active_question_kind,
        profile_warning=profile_warning,
        pending_message=pending_message,
        response=response,
    )

    careena4_session.messages.append(
        {"role": "assistant", "content": response["response"]}
    )

    return response


def _bind_session_profile(
        *,
        req: ChatRequest,
        current_user: User | None,
        db_session: Session,
):
    """Bind the session to the requested profile or verify the existing binding.

    Profile-bound requests always require an authenticated account with access
    to that profile; a mismatch between request and session profile is a 409.
    """
    session_profile_id = runtime.careena4_session_profiles.get(req.session_id)

    if session_profile_id is None and req.profile_id is not None:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required for profile chat requests.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        profiles_service.get_profile_access_role(
            account_id=current_user.id,
            profile_id=req.profile_id,
            session=db_session,
        )

        runtime.careena4_session_profiles[req.session_id] = req.profile_id
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

        profiles_service.get_profile_access_role(
            account_id=current_user.id,
            profile_id=session_profile_id,
            session=db_session,
        )

    return session_profile_id


def _safety_bypass_profile_pre_turn(
        *,
        req: ChatRequest,
        careena4_session,
        current_user: User | None,
        db_session: Session,
) -> bool:
    """Return True when profile selection must be skipped for this message.

    Safety-critical messages (catalog match) bypass profile selection so the
    safety question fires immediately without making the user pick a person
    first. The profile question is remembered and injected later.
    """
    raw_safety_precheck = runtime.careena4_turn_engine.raw_red_flag_detector.detect(req.message)
    if not (
        raw_safety_precheck.requires_safety_clarification
        or raw_safety_precheck.requires_emergency_response
    ):
        return False

    # For a single profile, still fill in person data so the safety question
    # runs with demographics and pre_turn is not needed on subsequent turns.
    # This is best-effort: a failure here must never block the safety question,
    # so errors are logged and the bypass proceeds without person data.
    try:
        bypass_snapshots = [
            _snapshot_from_profile(p)
            for p in profiles_service.list_profiles(current_user=current_user, session=db_session)
        ]
        if len(bypass_snapshots) == 1:
            runtime.careena4_person_initialiser.pre_turn(
                session_id=req.session_id,
                careena4_session=careena4_session,
                profiles=bypass_snapshots,
                pending_message=None,
            )
        elif raw_safety_precheck.requires_safety_clarification:
            runtime.careena4_person_initialiser.remember_pending_message(
                session_id=req.session_id,
                pending_message=req.message,
            )
    except Exception:
        logger.exception(
            "Safety bypass: profile pre-initialisation failed for session %s; "
            "continuing without person data",
            req.session_id,
        )
    return True


def _profile_pre_turn_response(
        *,
        req: ChatRequest,
        careena4_session,
        current_user: User | None,
        db_session: Session,
) -> dict | None:
    """Run the person pre-turn ("Für wen?"); return the profile question
    response when the turn must be skipped, else None."""
    try:
        snapshots = [
            _snapshot_from_profile(p)
            for p in profiles_service.list_profiles(current_user=current_user, session=db_session)
        ]
        skip_turn = runtime.careena4_person_initialiser.pre_turn(
            session_id=req.session_id,
            careena4_session=careena4_session,
            profiles=snapshots,
            pending_message=req.message,
        )
    except Exception:
        logger.exception(
            "Person pre-turn failed for session %s; falling back to a normal turn",
            req.session_id,
        )
        skip_turn = False

    if not skip_turn:
        return None

    question = careena4_session.conversation_state.active_question
    careena4_session.messages.append({"role": "user", "content": req.message})
    careena4_session.messages.append({"role": "assistant", "content": question.prompt_text})
    return {
        "response": question.prompt_text,
        "response_mode": "ask_followup",
        "red_flag": False,
        "trace_notes": [],
        "pending_followup": _pending_followup_payload(question),
        "recommendation_ready": False,
        "reply_options": _question_reply_options(question),
        "reply_suggestions": [],
        "recommendation_result": None,
        "action": None,
        "severity": None,
        "case_observations": [],
    }


def _apply_person_post_turn(
        *,
        req: ChatRequest,
        careena4_session,
        current_user: User | None,
        db_session: Session,
        session_profile_id,
        subject_profile_id,
        diary_history: list[DiaryEntry],
        response: dict,
):
    """Evaluate the person post-turn and update case-subject bindings.

    Returns (response, profile_warning, pending_message). When a medical
    message was deferred during profile selection, it is replayed here as a
    second turn and its response replaces the first one.
    """
    (
        profile_warning,
        profile_reply_options,
        pending_message,
        matched_profile_id,
        resolved_non_profile,
    ) = runtime.careena4_person_initialiser.post_turn(
        session_id=req.session_id,
        careena4_session=careena4_session,
        message=req.message,
    )
    # The user picked a profile in the "Für wen?" step. Record it as the case
    # subject so diary, medications and the reported profile_id follow that
    # person, without changing the session's owning profile (which stays the
    # authenticated active profile and keeps the cross-profile guard intact).
    if matched_profile_id is not None:
        runtime.careena4_session_case_profiles[req.session_id] = matched_profile_id
        runtime.careena4_session_unbound_cases.discard(req.session_id)
        if matched_profile_id != subject_profile_id:
            subject_profile_id = matched_profile_id
            diary_history = _load_diary_history(subject_profile_id, current_user, db_session)
    elif resolved_non_profile:
        # Case is explicitly about a person without a profile. Unbind it so the
        # deferred medical message (and later the recommendation/PDF) does not
        # pull the active profile's diary, medications or reported profile_id.
        runtime.careena4_session_unbound_cases.add(req.session_id)
        runtime.careena4_session_case_profiles.pop(req.session_id, None)
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
        second_turn_result = runtime.careena4_turn_engine.run_turn(
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

    return response, profile_warning, pending_message


def _maybe_inject_deferred_profile_question(
        *,
        req: ChatRequest,
        careena4_session,
        current_user: User | None,
        db_session: Session,
        prev_active_question_kind,
        profile_warning,
        pending_message,
        response: dict,
) -> dict:
    """Safety-just-resolved: if the previous turn held a safety_clarification and
    the user answered it (non-emergency), inject the deferred profile question
    that was skipped by the safety bypass. Must run after post_turn() so "Nein"
    is not misread as a profile name."""
    if not (
        prev_active_question_kind == "safety_clarification"
        and response.get("response_mode") != "emergency"
        and current_user is not None
        and not profile_warning
        and not pending_message
        and req.session_id not in runtime.careena4_session_case_profiles
        and req.session_id not in runtime.careena4_session_unbound_cases
    ):
        return response

    new_active_kind = (
        careena4_session.conversation_state.active_question.kind
        if careena4_session.conversation_state and careena4_session.conversation_state.active_question
        else None
    )
    if new_active_kind == "safety_clarification":
        return response

    # Best-effort: a failure here must not break the already-built response,
    # so errors are logged and the original response is returned unchanged.
    try:
        deferred_snapshots = [
            _snapshot_from_profile(p)
            for p in profiles_service.list_profiles(current_user=current_user, session=db_session)
        ]
        deferred_question = runtime.careena4_person_initialiser.inject_deferred_clarification(
            session_id=req.session_id,
            careena4_session=careena4_session,
            profiles=deferred_snapshots,
        )
        if deferred_question is not None:
            response = {
                **response,
                "response": deferred_question.prompt_text,
                "response_mode": "ask_followup",
                "reply_options": _question_reply_options(deferred_question),
                "pending_followup": _pending_followup_payload(deferred_question),
            }
    except Exception:
        logger.exception(
            "Deferred profile question injection failed for session %s; "
            "returning the turn response unchanged",
            req.session_id,
        )
    return response


# --------------------------------------------------------------------------
# Recommendation / severities
# --------------------------------------------------------------------------

def handle_recommendation_request(
        *,
        req: RecommendationRequest,
        current_user: User | None,
        db_session: Session,
) -> dict:
    """Build and return the care recommendation for a session on user request."""
    careena4_session = require_careena4_session_access(
        session_id=req.session_id,
        current_user=current_user,
        db_session=db_session,
    )

    turn_id = str(uuid4())

    session_profile_id = runtime.careena4_session_profiles.get(req.session_id)
    # Diary, medications and the reported profile follow the case subject (the
    # "Für wen?" answer) when it differs from the session's owning profile, and
    # are dropped entirely when the case is about a person without a profile.
    subject_profile_id = _resolve_subject_profile_id(req.session_id, session_profile_id)
    diary_history = _load_diary_history(subject_profile_id, current_user, db_session)
    medication_history = _load_medication_history(subject_profile_id, current_user, db_session)

    turn_result = runtime.careena4_turn_engine.request_recommendation(
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


def apply_observation_severities(
        *,
        req: SetObservationSeveritiesRequest,
        current_user: User | None,
        db_session: Session,
) -> dict:
    """Update observation severities directly in the session.

    Called when the user sets intensity via the in-chat symptom editor.
    Also resolves any pending severity question for affected observations so
    the backend will not ask again.
    """
    careena4_session = require_careena4_session_access(
        session_id=req.session_id,
        current_user=current_user,
        db_session=db_session,
    )

    if careena4_session.medical_case is None:
        return {"ok": True}

    label_map = {label.casefold(): severity for label, severity in req.severities.items()}

    for obs in careena4_session.medical_case.observations:
        if obs.is_active() and obs.normalized_label_de.casefold() in label_map:
            obs.severity = str(label_map[obs.normalized_label_de.casefold()])

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


# --------------------------------------------------------------------------
# Appointment search
# --------------------------------------------------------------------------

def handle_appointment_search(
        *,
        request: AppointmentSearchRequest,
        current_user: User | None,
        db_session: Session,
) -> AppointmentSearchResponse:
    """Search FHIR appointments matching the session's recommendation.

    Falls back to the persisted chat history when the in-memory session no
    longer exists (e.g. after a backend restart).
    """
    try:
        careena4_session = require_careena4_session_access(
            session_id=request.session_id,
            current_user=current_user,
            db_session=db_session,
        )
    except HTTPException as exc:
        if exc.status_code != status.HTTP_404_NOT_FOUND:
            raise
        return _search_appointments_from_persisted_history(
            request=request,
            current_user=current_user,
            db_session=db_session,
        )

    session_profile_id = runtime.careena4_session_profiles.get(request.session_id)

    if session_profile_id is not None and session_profile_id != request.profile_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Requested profile does not match chat session profile.",
        )

    # Anonymous searches are isolated by their chat session and use zero only
    # as an internal simulator key. They can never be persisted as bookings.
    search_profile_id = session_profile_id or 0

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
        profile_id=search_profile_id,
    )

    try:
        return appointments_service.search_fhir_appointments(
            session_id=request.session_id,
            profile_id=search_profile_id,
            postal_code=request.postal_code,
            recommendation_result=recommendation_result,
            fhir_bundle=fhir_bundle,
        )
    except AppointmentProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


def _search_appointments_from_persisted_history(
        *,
        request: AppointmentSearchRequest,
        current_user: User | None,
        db_session: Session,
) -> AppointmentSearchResponse:
    """Appointment search based on a persisted chat history entry (requires
    authentication because history rows are always profile-bound)."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required for appointment searches.",
        )

    history = db_session.exec(
        select(ChatHistory)
        .where(ChatHistory.session_id == request.session_id)
        .where(ChatHistory.profile_id == request.profile_id)
    ).first()
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Der gespeicherte Chatverlauf wurde nicht gefunden.",
        )

    profiles_service.get_profile_access_role(
        account_id=current_user.id,
        profile_id=request.profile_id,
        session=db_session,
    )
    recommendation = (history.recommendation or "").strip()
    next_steps = (history.next_steps or "").strip()
    if not recommendation and not next_steps:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Im gespeicherten Verlauf ist keine Handlungsempfehlung vorhanden.",
        )

    recommendation_result = _recommendation_from_history(
        recommendation=recommendation,
        next_steps=next_steps,
    )
    history_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "identifier": {
            "system": "https://careena.local/fhir/chat-history",
            "value": str(history.id),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entry": [],
    }
    try:
        return appointments_service.search_fhir_appointments(
            session_id=request.session_id,
            profile_id=request.profile_id,
            postal_code=request.postal_code,
            recommendation_result=recommendation_result,
            fhir_bundle=history_bundle,
        )
    except AppointmentProviderUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


def _recommendation_from_history(
        *,
        recommendation: str,
        next_steps: str,
) -> RecommendationResult:
    """Reconstruct a RecommendationResult from persisted free-text history.

    Keyword-based fallback for old history rows that carry no structured
    specialty/urgency metadata.
    """
    text = f"{recommendation} {next_steps}".casefold()
    specialty = "general_practice"
    care_level = "general_practice"
    for marker, mapped_specialty in (
        (("orthop", "bewegungsapparat"), "orthopedics"),
        (("kardiolog", "herzarzt", "herzpraxis"), "cardiology"),
        (("haut", "dermat"), "dermatology"),
        (("gastro", "magen-darm", "verdauung"), "gastroenterology"),
        (("neurolog",), "neurology"),
        (("hno", "hals-nasen-ohren"), "ent"),
        (("psychiatr", "psychische", "psychisch"), "psychiatry"),
        (("zahn", "kiefer"), "dentistry"),
        (("auge", "augenarzt", "ophthalm"), "ophthalmology"),
        (("gyn", "frauenarzt"), "gynecology"),
        (("kinderarzt", "pädiatr"), "pediatrics"),
        (("urolog",), "urology"),
    ):
        if any(value in text for value in marker):
            specialty = mapped_specialty
            care_level = "specialist"
            break
    if "116117" in text or "bereitschaftsdienst" in text:
        care_level = "116117"

    urgency_level = "low"
    if any(value in text for value in ("sofort", "heute", "dringend", "hoch")):
        urgency_level = "high"
    elif any(value in text for value in ("zeitnah", "mittel", "bald")):
        urgency_level = "medium"

    return RecommendationResult(
        summary=recommendation or next_steps,
        urgency_level=urgency_level,
        care_level=care_level,
        specialty=specialty,
        next_step=next_steps or recommendation,
    )


# --------------------------------------------------------------------------
# Symptom draft helpers
# --------------------------------------------------------------------------

def _removed_symptom_labels(
    previous_labels: list[str],
    updated_labels: list[str],
) -> list[str]:
    """Return labels the user removed from the draft (normalized comparison),
    so the matching case observations can be negated."""
    updated_identities = {
        normalized
        for label in updated_labels
        if (normalized := _normalized_symptom_label(label)) is not None
    }
    removed_labels: list[str] = []

    for label in previous_labels:
        normalized = _normalized_symptom_label(label)
        if normalized is None or normalized in updated_identities:
            continue
        removed_labels.append(label)

    return removed_labels


def _normalized_symptom_label(label: str | None) -> str | None:
    return CaseManager._normalized_label(label)
