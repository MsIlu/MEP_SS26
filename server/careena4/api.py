from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

from careena4.bootstrap import build_default_services, build_simulation_runner
from careena4.models.input import CancelDraftResponse, SymptomDraftResponse, SymptomDraftUpdateRequest
from careena4.models.turn import TurnInput, TurnResult
from careena4.server_log import configure_debug_logging, log_event, log_json
from careena4.simulation_runtime import (
    SimulationRequest,
    normalized_simulation_request,
    run_simulation_command,
)


configure_debug_logging()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str


services = build_default_services(llm_mode="env")
turn_engine = services.turn_engine
session_store = services.session_store
simulation_runner = build_simulation_runner(system_llm_mode="env")


@app.get("/")
def root():
    return {"service": "careena4", "status": "ok"}


@app.post("/session")
def create_session():
    session_id = session_store.create_session()
    log_event("http.session.created", layer="http", route="/session", session_id=session_id)
    return {"session_id": session_id}


@app.post("/warmup")
def warmup():
    return {"status": "ok"}




def _require_session(session_id: str):
    session = session_store.get(session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found.",
        )
    return session


@app.get("/input-drafts/{session_id}", response_model=SymptomDraftResponse)
def get_input_draft(session_id: str):
    """
    Return the current editable symptom draft for a Careena4 session.
    """

    session = _require_session(session_id)
    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=session.symptom_input_draft.symptom_labels(),
        chips=session.symptom_input_draft.chips,
    )


@app.patch("/input-drafts/{session_id}", response_model=SymptomDraftResponse)
def update_input_draft(
    session_id: str,
    request: SymptomDraftUpdateRequest,
):
    """
    Replace the editable symptom draft after user edits in the frontend.
    """

    session = _require_session(session_id)
    if request.chips is not None:
        session.symptom_input_draft.replace_from_chips(request.chips)
    else:
        session.symptom_input_draft.replace_from_labels(request.symptoms)

    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=session.symptom_input_draft.symptom_labels(),
        chips=session.symptom_input_draft.chips,
    )


@app.delete("/input-drafts/{session_id}", response_model=CancelDraftResponse)
def cancel_input_draft(session_id: str):
    """
    Clear the editable symptom draft for a Careena4 session.
    """

    session = _require_session(session_id)
    session.symptom_input_draft.replace_from_labels([])

    return CancelDraftResponse(
        message="Draft cancelled successfully.",
        session_id=session_id,
    )


@app.post("/chatscreen")
def chat(req: ChatRequest):
    session = session_store.get(req.session_id)
    turn_id = str(uuid4())
    log_event(
        "http.chat.request",
        layer="http",
        route="/chatscreen",
        session_id=req.session_id,
        turn_id=turn_id,
        message_chars=len(req.message),
        history_message_count=len(session.messages) if session is not None else None,
    )
    if session is None:
        return {"response": "Fehler: Ungueltige Session-ID", "red_flag": False}
    if not req.message.strip():
        return {"response": "Fehler: Leere Eingabe.", "red_flag": False}
    if req.message.strip().startswith("/simrun"):
        selector = req.message.strip()[len("/simrun"):].strip()
        response_text = run_simulation_command(selector=selector, simulation_runner=simulation_runner)
        response = {"response": response_text, "red_flag": "Stop-Grund: emergency" in response_text}
        session.messages.append({"role": "user", "content": req.message})
        session.messages.append({"role": "assistant", "content": response["response"]})
        log_json("HTTP /chatscreen SIMRUN RESPONSE", response)
        return response
    turn_result = turn_engine.run_turn(
        TurnInput.from_persisted_state(
            message=req.message,
            session_id=req.session_id,
            turn_id=turn_id,
            conversation_messages=session.messages,
            persisted_case_topic=session.case_topic,
            persisted_medical_case=session.medical_case,
            persisted_conversation_state=session.conversation_state,
            persisted_recommendation_state=session.recommendation_state,
            persisted_symptom_input_draft=session.symptom_input_draft,
        )
    )
    session.case_topic = turn_result.case_topic
    session.medical_case = turn_result.medical_case
    session.conversation_state = turn_result.conversation_state
    session.recommendation_state = turn_result.recommendation_state
    session.last_turn_understanding = turn_result.current_turn_understanding
    if turn_result.symptom_input_draft is not None:
        session.symptom_input_draft = turn_result.symptom_input_draft
    session.messages.append({"role": "user", "content": req.message})
    response = _chat_response(turn_result)
    session.messages.append({"role": "assistant", "content": response["response"]})
    log_json("HTTP /chatscreen RESPONSE", response)
    return response


@app.get("/case/{session_id}")
def get_case(session_id: str):
    session = session_store.get(session_id)
    if session is None:
        return {"error": "invalid_session"}
    return {
        "case": session.medical_case.model_dump() if session.medical_case is not None else None,
        "case_topic": session.case_topic.model_dump() if session.case_topic is not None else None,
        "conversation_state": session.conversation_state.model_dump(),
        "recommendation_state": session.recommendation_state.model_dump(),
        "symptom_input_draft": session.symptom_input_draft.model_dump(),
        "last_turn_understanding": (
            session.last_turn_understanding.model_dump()
            if session.last_turn_understanding is not None
            else None
        ),
    }


@app.post("/simulation/run")
def run_simulation(req: SimulationRequest):
    result = simulation_runner.run(normalized_simulation_request(req))
    log_json("HTTP /simulation/run RESULT", result)
    return result.model_dump()


def _chat_response(result: TurnResult) -> dict:
    active_question = result.conversation_state.active_question
    pending_followup = None
    if active_question is not None and active_question.kind in {"followup", "subject_clarification"}:
        pending_followup = {
            "question_id": active_question.question_id,
            "kind": active_question.kind,
            "question_intent": active_question.question_intent,
            "target_observation_id": active_question.target_observation_id,
            "target_followup_id": active_question.target_followup_id,
            "prompt_text": active_question.prompt_text,
            "blocking": active_question.blocking,
        }
    recommendation_ready = result.response_mode in {"guide_next_step", "recommend"}
    return {
        "response": result.response_text,
        "response_mode": result.response_mode,
        "red_flag": result.response_mode == "emergency",
        "trace_notes": list(result.trace_notes),
        "pending_followup": pending_followup,
        "recommendation_requested": result.conversation_state.recommendation_requested,
        "recommendation_ready": recommendation_ready,
        "recommendation_result": (
            result.recommendation_result.model_dump() if result.recommendation_result is not None else None
        ),
    }
