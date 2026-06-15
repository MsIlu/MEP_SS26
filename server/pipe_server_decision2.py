from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from careena_pipeline2.bootstrap import build_default_services
from careena_pipeline2.logs import configure_debug_logging, log_json
from careena_pipeline2.models import ConfirmationUpdate
from careena_pipeline2.response import case_to_payload, pipeline_result_to_chat_response


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


class ConfirmationRequest(BaseModel):
    session_id: str
    update: ConfirmationUpdate


services = build_default_services(llm_mode="env")
decision_pipeline = services.decision_pipeline
session_store = services.session_store
confirmation_service = services.confirmation_service


@app.post("/session")
def create_session():
    session_id = session_store.create_session()
    log_json("HTTP /session RESPONSE", {"session_id": session_id})
    return {"session_id": session_id}


@app.post("/warmup")
def warmup():
    log_json("HTTP /warmup RESPONSE", {"status": "ok"})
    return {"status": "ok"}


@app.post("/chatscreen")
def chat(req: ChatRequest):
    log_json(
        "HTTP /chatscreen REQUEST",
        {"session_id": req.session_id, "message": req.message},
    )
    session = session_store.get(req.session_id)
    if session is None:
        return {"response": "Fehler: Ungueltige Session-ID", "red_flag": False}
    if not req.message.strip():
        return {"response": "Fehler: Leere Eingabe.", "red_flag": False}

    result = decision_pipeline.run(
        req.message,
        existing_case=session.case,
        existing_dialogue_state=session.dialogue_state,
        conversation_messages=session.messages,
    )
    if result.case is not None:
        session.case = result.case
    if result.dialogue_state is not None:
        session.dialogue_state = result.dialogue_state

    session.messages.append({"role": "user", "content": req.message})
    response = pipeline_result_to_chat_response(result)
    session.messages.append({"role": "assistant", "content": response["response"]})
    log_json("HTTP /chatscreen RESPONSE", response)
    return response


@app.get("/case/{session_id}")
def get_case(session_id: str):
    log_json("HTTP /case REQUEST", {"session_id": session_id})
    session = session_store.get(session_id)
    if session is None:
        return {"error": "invalid_session"}
    if session.case is None:
        return {"case": None}
    response = {
        "case": case_to_payload(
            session.case,
            dialogue_state=session.dialogue_state,
        )
    }
    log_json("HTTP /case RESPONSE", response)
    return response


@app.post("/case/confirm")
def confirm_case(req: ConfirmationRequest):
    log_json(
        "HTTP /case/confirm REQUEST",
        {"session_id": req.session_id, "update": req.update},
    )
    session = session_store.get(req.session_id)
    if session is None:
        return {"error": "invalid_session"}
    if session.case is None:
        return {"error": "missing_case"}

    session.case = confirmation_service.apply(session.case, req.update)
    response = {
        "case": case_to_payload(
            session.case,
            dialogue_state=session.dialogue_state,
        )
    }
    log_json("HTTP /case/confirm RESPONSE", response)
    return response
