from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from careena_pipeline3.bootstrap import build_default_services, build_simulation_runner
from careena_pipeline3.server_log import configure_debug_logging, log_json
from careena_pipeline3.models.turn import TurnInput, TurnResult
from careena_pipeline3.simulation_runtime import (
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
dialogue_manager = services.dialogue_manager
session_store = services.session_store
simulation_runner = build_simulation_runner(system_llm_mode="env")


@app.get("/")
def root():
    return {"service": "careena_pipeline3", "status": "ok"}


@app.post("/session")
def create_session():
    session_id = session_store.create_session()
    return {"session_id": session_id}


@app.post("/warmup")
def warmup():
    return {"status": "ok"}


@app.post("/chatscreen")
def chat(req: ChatRequest):
    session = session_store.get(req.session_id)
    if session is None:
        return {"response": "Fehler: Ungueltige Session-ID", "red_flag": False}

    if not req.message.strip():
        return {"response": "Fehler: Leere Eingabe.", "red_flag": False}

    if req.message.strip().startswith("/simrun"):
        selector = req.message.strip()[len("/simrun") :].strip()
        response_text = run_simulation_command(
            selector=selector,
            simulation_runner=simulation_runner,
        )
        response = {
            "response": response_text,
            "red_flag": "Stop-Grund: emergency" in response_text,
        }
        session.messages.append({"role": "user", "content": req.message})
        session.messages.append({"role": "assistant", "content": response["response"]})
        log_json("HTTP /chatscreen SIMRUN RESPONSE", response)
        return response

    turn_result = dialogue_manager.run_turn(
        TurnInput.from_persisted_state(
            message=req.message,
            session_id=req.session_id,
            conversation_messages=session.messages,
            persisted_case=session.case,
            persisted_dialogue_state=session.dialogue_state,
            persisted_concern_state=session.concern_state,
        )
    )

    session.case = turn_result.medical_case
    session.concern_state = turn_result.concern_state
    session.dialogue_state = turn_result.dialogue_state
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
    if session.case is None:
        return {
            "case": None,
            "concern_state": session.concern_state.model_dump(),
            "dialogue_state": session.dialogue_state.model_dump(),
        }
    return {
        "case": session.case.model_dump(),
        "concern_state": session.concern_state.model_dump(),
        "dialogue_state": session.dialogue_state.model_dump(),
    }


@app.post("/simulation/run")
def run_simulation(req: SimulationRequest):
    result = simulation_runner.run(normalized_simulation_request(req))
    log_json("HTTP /simulation/run RESULT", result)
    return result.model_dump()


def _chat_response(result: TurnResult) -> dict:
    pending_followup = result.dialogue_state.pending_followup
    recommendation_ready = result.response_mode in {"guide_next_step", "recommend"}
    return {
        "response": result.response_text,
        "response_mode": result.response_mode,
        "red_flag": result.response_mode == "emergency",
        "trace_notes": list(result.trace_notes),
        "pending_followup": (
            pending_followup.model_dump() if pending_followup is not None else None
        ),
        "recommendation_requested": result.dialogue_state.recommendation_requested,
        "recommendation_ready": recommendation_ready,
        "recommendation_result": (
            result.recommendation_result.model_dump()
            if result.recommendation_result is not None
            else None
        ),
    }
