from pydantic import Field

from careena_pipeline.pipeline import CareenaDecisionPipeline
from careena_pipeline.core.exceptions import (
    EmptyLLMResponseError,
    InvalidJSONError,
    SchemaValidationError,
)
from careena_pipeline.core.client import LLMClient
from careena_pipeline.models import CareenaPipelineResult, DialogueState, MedicalCase
from careena_pipeline.models.common.base import PipelineModel
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
    def __init__(self, *, patient_llm: LLMClient, decision_pipeline: CareenaDecisionPipeline):
        self.patient_llm = patient_llm
        self.decision_pipeline = decision_pipeline

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
        messages = [
            {"role": "system", "content": request.patient_prompt},
            {
                "role": "user",
                "content": (
                    "Szenario:\n"
                    f"{request.scenario_prompt}\n\n"
                    "Schreibe die erste Nachricht, mit der dieser Patient Careena kontaktiert.\n"
                    "Wichtig: Starte realistisch unvollstaendig. Nenne das Hauptproblem "
                    "und hoechstens ein bis zwei spontane Zusatzinformationen. Verrate "
                    "nicht direkt alle Details aus dem Szenario."
                ),
            },
        ]
        return self._complete_patient(messages=messages, request=request)

    def _generate_patient_reply(self, *, request: ScenarioRunnerRequest, transcript: list[ScenarioTranscriptEntry]) -> str:
        transcript_text = "\n".join(f"{entry.role}: {entry.content}" for entry in transcript)
        messages = [
            {"role": "system", "content": request.patient_prompt},
            {
                "role": "user",
                "content": (
                    "Szenario:\n"
                    f"{request.scenario_prompt}\n\n"
                    "Bisheriger Chat:\n"
                    f"{transcript_text}\n\n"
                    "Antworte jetzt als Patient auf die letzte Careena-Nachricht.\n"
                    "Antworte knapp und nur auf das, wonach Careena gerade gefragt hat."
                ),
            },
        ]
        return self._complete_patient(messages=messages, request=request)

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
        if _too_similar(patient_message, last_careena) or _looks_like_question(patient_message) or _reply_mismatches_question(patient_message, last_careena):
            repair_prompt = (
                "Deine letzte Antwort war ungeeignet, weil sie die Frage wiederholt "
                "oder nicht zur gestellten Frage passt.\n\n"
                f"Careena fragte:\n{last_careena}\n\n"
                "Antworte jetzt als Patient kurz und direkt mit der passenden Information "
                "aus dem Szenario. Wiederhole die Frage nicht."
            )
            return self._complete_patient(
                messages=[
                    {"role": "system", "content": request.patient_prompt},
                    {"role": "user", "content": f"Szenario:\n{request.scenario_prompt}\n\n{repair_prompt}"},
                ],
                request=request,
            )
        return patient_message

    def _complete_patient(self, *, messages: list[dict], request: ScenarioRunnerRequest) -> str:
        try:
            reply = self.patient_llm.complete(
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
    prefixes = ["patient:", "patientin:", "angehoerige:", "angehÃ¶rige:"]
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
    return normalized.endswith("?") or normalized.startswith(("wie ", "was ", "wann ", "wo ", "wer ", "welche ", "kann ", "koennen ", "kÃ¶nnen "))


def _reply_mismatches_question(reply: str, question: str) -> bool:
    reply_norm = _normalize_text(reply)
    question_norm = _normalize_text(question)
    if "seit wann" in question_norm:
        return not _contains_any(reply_norm, ["seit", "heute", "gestern", "vorhin", "stunde", "stunden", "tag", "tage", "woche", "wochen", "minute", "minuten"])
    if "wie alt" in question_norm:
        return not any(character.isdigit() for character in reply_norm)
    if "skala" in question_norm or "0 bis 10" in question_norm:
        return not any(str(value) in reply_norm.split() for value in range(0, 11))
    if "auftreten" in question_norm or "belasten" in question_norm:
        return not _contains_any(reply_norm, ["auftreten", "stehen", "gehen", "laufen", "belasten", "kaum", "nicht", "normal"])
    return False


def _contains_any(text: str, markers: list[str]) -> bool:
    return any(marker in text for marker in markers)


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().replace("?", "").replace(".", "").replace(",", "").split())
