from typing import Literal

from pydantic import Field

from careena_pipeline.core.client import LLMClient
from careena_pipeline.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
from careena_pipeline.models import CareenaPipelineResult, DialogueState, MedicalCase
from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.pipeline import CareenaDecisionPipeline
from careena_pipeline.response import pipeline_result_to_chat_response
from careena_pipeline.tooling.scenario.prompts import DEFAULT_PATIENT_PROMPT


class ScenarioRunnerRequest(PipelineModel):
    scenario_prompt: str = Field(..., description="Freitext-Szenario fuer den Fake-Patienten.")
    patient_prompt: str = Field(
        default=DEFAULT_PATIENT_PROMPT,
        description="Systemprompt, der das Verhalten des Fake-Patienten steuert.",
    )
    opening_message: str | None = Field(
        default=None,
        description="Optionale erste Patientennachricht. Wenn leer, erzeugt das LLM sie.",
    )
    max_turns: int = Field(default=6, ge=1, le=20)
    patient_llm_mode: Literal["env", "local"] | None = Field(
        default=None,
        description="Optionaler LLM-Modus fuer den Fake-Patienten.",
    )
    patient_model: str | None = None
    patient_temperature: float = Field(default=0.25, ge=0.0, le=1.5)


class ScenarioTranscriptEntry(PipelineModel):
    role: str
    content: str
    response_mode: str | None = None


class ScenarioRunnerResult(PipelineModel):
    transcript: list[ScenarioTranscriptEntry] = Field(default_factory=list)
    final_case: MedicalCase | None = None
    final_result: CareenaPipelineResult | None = None
    stopped_reason: str


class SyntheticPatientRunner:
    def __init__(
        self,
        *,
        patient_llm: LLMClient | None = None,
        patient_llms: dict[str, LLMClient] | None = None,
        default_patient_llm_mode: Literal["env", "local"] = "local",
        decision_pipeline: CareenaDecisionPipeline,
    ):
        llm_map = dict(patient_llms or {})
        if patient_llm is not None:
            llm_map.setdefault(default_patient_llm_mode, patient_llm)
            llm_map.setdefault("default", patient_llm)
        if not llm_map:
            raise ValueError("SyntheticPatientRunner requires at least one patient LLM client.")

        self.patient_llms = llm_map
        self.default_patient_llm_mode = default_patient_llm_mode
        self.decision_pipeline = decision_pipeline
        self.default_patient_llm = (
            self.patient_llms.get(self.default_patient_llm_mode)
            or self.patient_llms.get("default")
            or next(iter(self.patient_llms.values()))
        )

    def run(self, request: ScenarioRunnerRequest) -> ScenarioRunnerResult:
        transcript: list[ScenarioTranscriptEntry] = []
        case: MedicalCase | None = None
        dialogue_state: DialogueState | None = None
        final_result: CareenaPipelineResult | None = None

        patient_message = request.opening_message or self._generate_opening(request)

        for _ in range(request.max_turns):
            transcript.append(ScenarioTranscriptEntry(role="patient", content=patient_message))
            try:
                result = self.decision_pipeline.run(
                    patient_message,
                    existing_case=case,
                    existing_dialogue_state=dialogue_state,
                    conversation_messages=_transcript_to_messages(transcript),
                )
            except (EmptyLLMResponseError, InvalidJSONError, SchemaValidationError) as exc:
                transcript.append(
                    ScenarioTranscriptEntry(
                        role="system",
                        content=f"Careena pipeline failed: {exc}",
                        response_mode="error",
                    )
                )
                return ScenarioRunnerResult(
                    transcript=transcript,
                    final_case=case,
                    final_result=final_result,
                    stopped_reason="pipeline_error",
                )
            final_result = result
            if result.case is not None:
                case = result.case
            if result.dialogue_state is not None:
                dialogue_state = result.dialogue_state

            careena_response = pipeline_result_to_chat_response(result)
            transcript.append(
                ScenarioTranscriptEntry(
                    role="careena",
                    content=careena_response["response"],
                    response_mode=result.response_mode,
                )
            )
            if result.response_mode in {"recommend", "emergency", "out_of_scope"}:
                return ScenarioRunnerResult(
                    transcript=transcript,
                    final_case=case,
                    final_result=final_result,
                    stopped_reason=result.response_mode,
                )

            patient_message = self._generate_patient_reply(request=request, transcript=transcript)
            patient_message = self._repair_bad_patient_reply(
                request=request,
                transcript=transcript,
                patient_message=patient_message,
            )

        return ScenarioRunnerResult(
            transcript=transcript,
            final_case=case,
            final_result=final_result,
            stopped_reason="max_turns_reached",
        )

    def _generate_opening(self, request: ScenarioRunnerRequest) -> str:
        return self._complete_patient(
            request=request,
            instruction=(
                "Formuliere die erste Chat-Nachricht dieser Person an Careena.\n"
                "Schreibe natuerlich, alltagssprachlich und nicht wie ein Testfall.\n"
                "Starte realistisch unvollstaendig: nenne das Hauptproblem und "
                "hoechstens ein bis zwei spontane Zusatzinformationen.\n"
                "Keine Aufzaehlung, keine Analyse, kein vollstaendiger Fact-Dump."
            ),
        )

    def _generate_patient_reply(
        self,
        *,
        request: ScenarioRunnerRequest,
        transcript: list[ScenarioTranscriptEntry],
    ) -> str:
        transcript_text = "\n".join(f"{entry.role}: {entry.content}" for entry in transcript)
        return self._complete_patient(
            request=request,
            instruction=(
                "Bisheriger Chat:\n"
                f"{transcript_text}\n\n"
                "Antworte jetzt als dieselbe Person auf die letzte Careena-Nachricht.\n"
                "Antworte kurz, natuerlich und nur mit den Informationen, die gerade "
                "wirklich zur letzten Frage passen.\n"
                "Keine Listen, keine Meta-Erklaerung, keine komplette Wiederholung des Szenarios."
            ),
        )

    def _repair_bad_patient_reply(
        self,
        *,
        request: ScenarioRunnerRequest,
        transcript: list[ScenarioTranscriptEntry],
        patient_message: str,
    ) -> str:
        last_careena = _last_content(transcript, role="careena")
        if not last_careena:
            return patient_message
        if self._needs_retry(patient_message=patient_message, last_careena=last_careena):
            return self._complete_patient(
                request=request,
                instruction=(
                    "Deine letzte Antwort war noch keine gute Patientenantwort.\n\n"
                    f"Careena fragte:\n{last_careena}\n\n"
                    f"Deine letzte Antwort war:\n{patient_message}\n\n"
                    "Antworte jetzt kurz, direkt und menschlich mit der passenden Information "
                    "aus dem Szenario. Wiederhole die Frage nicht und stelle keine Gegenfrage."
                ),
            )
        return patient_message

    def _needs_retry(self, *, patient_message: str, last_careena: str) -> bool:
        return _too_similar(patient_message, last_careena) or _looks_like_question(patient_message)

    def _complete_patient(
        self,
        *,
        request: ScenarioRunnerRequest,
        instruction: str,
    ) -> str:
        patient_llm = self.patient_llms.get(request.patient_llm_mode) or self.default_patient_llm
        messages = [
            {"role": "system", "content": request.patient_prompt},
            {
                "role": "user",
                "content": (
                    "Szenario:\n"
                    f"{request.scenario_prompt}\n\n"
                    f"{instruction}"
                ),
            },
        ]
        try:
            reply = patient_llm.complete(
                messages=messages,
                temperature=request.patient_temperature,
                max_tokens=300,
                model=request.patient_model,
                json_mode=False,
            )
        except EmptyLLMResponseError:
            return "Ich weiss nicht genau."
        return _clean_patient_reply(reply)


def _clean_patient_reply(reply: str) -> str:
    cleaned = reply.strip().strip('"')
    prefixes = ["patient:", "patientin:", "angehoerige:", "angehoeriger:"]
    lowered = cleaned.lower()
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return cleaned[len(prefix) :].strip()
    return cleaned


def _transcript_to_messages(transcript: list[ScenarioTranscriptEntry]) -> list[dict[str, str]]:
    role_map = {"patient": "user", "careena": "assistant", "system": "system"}
    messages: list[dict[str, str]] = []
    for entry in transcript:
        role = role_map.get(entry.role)
        if role is not None:
            messages.append({"role": role, "content": entry.content})
    return messages


def _last_content(transcript: list[ScenarioTranscriptEntry], *, role: str) -> str | None:
    for entry in reversed(transcript):
        if entry.role == role:
            return entry.content
    return None


def _too_similar(left: str, right: str) -> bool:
    left_norm = _normalize_text(left)
    right_norm = _normalize_text(right)
    if not left_norm or not right_norm:
        return False
    return left_norm == right_norm or left_norm in right_norm or right_norm in left_norm


def _looks_like_question(text: str) -> bool:
    normalized = text.strip().lower()
    return normalized.endswith("?") or normalized.startswith(
        ("wie ", "was ", "wann ", "wo ", "wer ", "welche ", "kann ", "koennen ")
    )


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().replace("?", "").replace(".", "").replace(",", "").split())
