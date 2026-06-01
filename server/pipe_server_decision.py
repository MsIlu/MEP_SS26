from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from careena_pipeline.bootstrap import build_default_services
from careena_pipeline.observability.logging import (
    configure_debug_logging,
    log_json,
    log_testrun_response,
)
from careena_pipeline.models import ConfirmationUpdate
from careena_pipeline.response import case_to_payload, pipeline_result_to_chat_response
from careena_pipeline.tooling.scenario import DEFAULT_TESTRUN_SCENARIO, SCENARIO_PROMPTS
from careena_pipeline.tooling.scenario.runner import ScenarioRunnerRequest


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
synthetic_patient_runner = services.synthetic_patient_runner


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
        return {"response": "Fehler: Ungültige Session-ID", "red_flag": False}

    if not req.message.strip():
        return {"response": "Fehler: Leere Eingabe.", "red_flag": False}

    if req.message.strip().startswith("/testrun"):
        scenario_prompt = req.message.strip()[len("/testrun"):].strip()
        scenario_prompt = _resolve_scenario_prompt(scenario_prompt)

        result = synthetic_patient_runner.run(
            ScenarioRunnerRequest(
                scenario_prompt=scenario_prompt,
                max_turns=8,
            )
        )
        response = {
            "response": _format_scenario_transcript(result),
            "red_flag": False,
        }
        session.messages.append({"role": "user", "content": req.message})
        session.messages.append({"role": "assistant", "content": response["response"]})
        log_testrun_response("HTTP /chatscreen TESTRUN RESPONSE", response)
        return response

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
    session = session_store.get(session_id)
    if session is None:
        return {"error": "invalid_session"}
    if session.case is None:
        return {"case": None}
    return {
        "case": case_to_payload(
            session.case,
            dialogue_state=session.dialogue_state,
        )
    }


@app.post("/case/confirm")
def confirm_case(req: ConfirmationRequest):
    session = session_store.get(req.session_id)
    if session is None:
        return {"error": "invalid_session"}
    if session.case is None:
        return {"error": "missing_case"}

    session.case = confirmation_service.apply(session.case, req.update)
    log_json("HTTP /case/confirm CASE", session.case)
    return {
        "case": case_to_payload(
            session.case,
            dialogue_state=session.dialogue_state,
        )
    }


@app.post("/scenario/run")
def run_scenario(req: ScenarioRunnerRequest):
    result = synthetic_patient_runner.run(req)
    log_json("HTTP /scenario/run RESULT", result)
    return result.model_dump()


def _resolve_scenario_prompt(value: str) -> str:
    if not value:
        return DEFAULT_TESTRUN_SCENARIO

    key = value.strip().lower()
    return SCENARIO_PROMPTS.get(key, value)


def _format_scenario_transcript(result) -> str:
    lines = [
        "Testlauf abgeschlossen.",
        f"Stop-Grund: {result.stopped_reason}",
        "",
        "Transcript:",
    ]

    for entry in result.transcript:
        speaker = "Patient" if entry.role == "patient" else "Careena"
        lines.append(f"{speaker}: {entry.content}")
        lines.append("")

    final_case = result.final_case
    final_dialogue_state = result.final_result.dialogue_state if result.final_result is not None else None
    if final_case is not None:
        final_case.ensure_primary_problem()
        lines.extend(
            [
                "Finaler Case:",
                f"- Hauptfokus: {final_case.primary_focus_label() or 'unklar'}",
                f"- Pending Slot: {(final_dialogue_state.pending_followup if final_dialogue_state else None) or 'keiner'}",
            ]
        )
        for observation in final_case.observations[:5]:
            details = []
            if observation.temporality:
                details.append(f"Zeit: {observation.temporality}")
            if observation.severity is not None:
                details.append(f"Stärke: {observation.severity}/10")
            if observation.measurement:
                details.append(f"Messwert: {observation.measurement}")
            if observation.details:
                details.append(f"Details: {observation.details}")
            suffix = f" ({'; '.join(details)})" if details else ""
            lines.append(f"- {observation.type}: {observation.patient_label}{suffix}")

    return "\n".join(lines).strip()
