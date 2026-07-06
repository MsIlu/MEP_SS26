"""HTTP routes for the Careena4 chat; orchestration logic lives in chat.service."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from appointments.schemas import AppointmentSearchRequest, AppointmentSearchResponse
from auth.security import get_optional_current_account, get_session
from careena4.models.input import (
    CancelDraftResponse,
    SymptomDraftResponse,
    SymptomDraftUpdateRequest,
)
from careena4.simulation_runtime import SimulationRequest, normalized_simulation_request
from chat import runtime, service
from chat.schemas import (
    ChatRequest,
    RecommendationRequest,
    SessionRequest,
    SetObservationSeveritiesRequest,
)
from database.models import User
from fhir_mapper.careena4_adapter import build_fhir_bundle_from_careena4_session

router = APIRouter()


@router.post("/session")
def create_session(
    req: SessionRequest | None = None,
    current_user: User | None = Depends(get_optional_current_account),
    session: Session = Depends(get_session),
):
    """
    Create and return a new chat session id.
    """
    profile_id = req.profile_id if req is not None else None
    session_id = service.create_chat_session(
        profile_id=profile_id,
        current_user=current_user,
        db_session=session,
    )
    return {"session_id": session_id}


@router.post("/chatscreen")
def chat(
        req: ChatRequest,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """Process one chat message and return the Flutter chat response."""
    return service.handle_chat_message(
        req=req,
        current_user=current_user,
        db_session=session,
    )


@router.post("/chatscreen/set-severities")
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
    return service.apply_observation_severities(
        req=req,
        current_user=current_user,
        db_session=session,
    )


@router.post("/recommendation/request")
def request_recommendation(
        req: RecommendationRequest,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """Build and return the care recommendation for a session on user request."""
    return service.handle_recommendation_request(
        req=req,
        current_user=current_user,
        db_session=session,
    )


@router.get("/fhir/export/{session_id}")
def export_fhir_bundle(
        session_id: str,
        current_user: User | None = Depends(get_optional_current_account),
        db_session: Session = Depends(get_session),
):
    """Export the session's medical case as a FHIR bundle."""
    careena4_session = service.require_careena4_session_access(
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


@router.post("/appointments/search", response_model=AppointmentSearchResponse)
def search_appointments(
        request: AppointmentSearchRequest,
        current_user: User | None = Depends(get_optional_current_account),
        db_session: Session = Depends(get_session),
):
    """Search FHIR appointments matching the session's recommendation.

    Falls back to the persisted chat history when the in-memory session no
    longer exists (e.g. after a backend restart).
    """
    return service.handle_appointment_search(
        request=request,
        current_user=current_user,
        db_session=db_session,
    )


@router.post("/simulation/run")
def run_simulation(req: SimulationRequest):
    """Run a scripted LLM-vs-LLM simulation (QA/demo tooling, no auth)."""
    result = runtime.careena4_simulation_runner.run(normalized_simulation_request(req))
    return result.model_dump()


@router.post("/warmup")
def warmup():
    """
    Lightweight readiness endpoint for the chat backend.

    Called when a new chat session starts, so it is the explicit refresh path
    for the cached LLM status. Repeated health polling reads the cached value.
    """
    available = runtime.refresh_llm_health_status()
    return {
        "status": "ok" if available else "unavailable",
        "llm": available,
        "model": runtime.careena4_llm_health_status["model"],
        "checked_at": runtime.careena4_llm_health_status["checked_at"],
    }


@router.get("/health/server")
def health_server():
    """Liveness probe for the API process itself."""
    return {"status": "ok", "server": True}


@router.get("/health/llm")
def health_llm():
    """Report the cached LLM availability (refreshed by /warmup, not here)."""
    checked_model = runtime.careena4_llm_health_status["model"]

    if not runtime.careena4_llm_health_status["available"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "LLM service is not reachable.",
                "model": checked_model,
                "checked_at": runtime.careena4_llm_health_status["checked_at"],
            },
        )

    return {
        "status": "ok",
        "llm": True,
        "model": checked_model,
        "checked_at": runtime.careena4_llm_health_status["checked_at"],
    }


@router.get("/input-drafts/{session_id}", response_model=SymptomDraftResponse)
def get_input_draft(
        session_id: str,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """
    Return the current editable symptom draft for a Careena4 session.
    """
    careena4_session = service.require_careena4_session_access(
        session_id=session_id,
        current_user=current_user,
        db_session=session,
    )

    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=careena4_session.symptom_input_draft.symptom_labels(),
        chips=careena4_session.symptom_input_draft.chips,
    )


@router.patch("/input-drafts/{session_id}", response_model=SymptomDraftResponse)
def update_input_draft(
        session_id: str,
        request: SymptomDraftUpdateRequest,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """
    Replace the editable symptom draft after user edits in the frontend.
    """
    careena4_session = service.require_careena4_session_access(
        session_id=session_id,
        current_user=current_user,
        db_session=session,
    )
    previous_labels = careena4_session.symptom_input_draft.symptom_labels()

    if request.chips is not None:
        careena4_session.symptom_input_draft.replace_from_chips(request.chips)
    else:
        careena4_session.symptom_input_draft.replace_from_labels(request.symptoms)

    removed_labels = service._removed_symptom_labels(
        previous_labels,
        careena4_session.symptom_input_draft.symptom_labels(),
    )
    if removed_labels and careena4_session.medical_case is not None:
        careena4_session.medical_case = (
            runtime.careena4_turn_engine.case_manager.negate_observations_by_labels(
                medical_case=careena4_session.medical_case,
                labels=removed_labels,
            )
        )

    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=careena4_session.symptom_input_draft.symptom_labels(),
        chips=careena4_session.symptom_input_draft.chips,
    )


@router.delete("/input-drafts/{session_id}", response_model=CancelDraftResponse)
def cancel_input_draft(
        session_id: str,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """
    Clear the editable symptom draft for a Careena4 session.
    """
    careena4_session = service.require_careena4_session_access(
        session_id=session_id,
        current_user=current_user,
        db_session=session,
    )

    careena4_session.symptom_input_draft.replace_from_labels([])

    return CancelDraftResponse(
        message="Draft cancelled successfully.",
        session_id=session_id,
    )
