from __future__ import annotations

import config

from careena_pipeline3.core.exceptions import EmptyLLMResponseError, LLMRequestError
from careena_pipeline3.core.client import LLMClient
from careena_pipeline3.models.turn import (
    EntryDecision,
    RecommendationGateDecision,
    ResponseState,
    ResponseStrategy,
    TurnContext,
)
from careena_pipeline3.models.workflow import RecommendationResult


class LLMResponseGenerationService:
    """
    Generates a narrow free-form conversational response for selected response
    strategies. It is intentionally not a policy layer.
    """

    def __init__(self, *, llm_client: LLMClient):
        self.llm_client = llm_client

    def build(
        self,
        *,
        response_mode: str,
        response_state: ResponseState,
        response_strategy: ResponseStrategy,
        context: TurnContext,
        entry_decision: EntryDecision,
        latest_user_message: str,
        response_history_messages: list[dict[str, str]] | None = None,
        recommendation_result: RecommendationResult | None = None,
    ) -> str:
        del recommendation_result

        if response_strategy.kind not in {"llm_continue", "llm_bounded_response"}:
            raise ValueError(
                f"unsupported LLM response strategy: {response_strategy.kind}"
            )

        system_prompt = _build_system_prompt()
        user_prompt = _build_user_prompt(
            response_mode=response_mode,
            response_state=response_state,
            response_strategy=response_strategy,
            context=context,
            entry_decision=entry_decision,
            latest_user_message=latest_user_message,
            response_history_messages=response_history_messages,
        )
        try:
            content = self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=220,
            )
        except EmptyLLMResponseError:
            raise
        except Exception as exc:
            raise LLMRequestError(
                "LLM response generation request failed"
            ) from exc
        normalized = content.strip()
        if not normalized:
            raise EmptyLLMResponseError("LLM response generation returned empty text")
        return normalized


def _build_system_prompt() -> str:
    return (
        f"{config.MASTER_PROMPT}\n\n"
        "Zusatz fuer careena_pipeline3:\n"
        "- Sie erzeugen genau eine kurze Antwort fuer einen laufenden Turn.\n"
        "- Sie arbeiten auf bereits verarbeiteten Signalen und duerfen keine "
        "neue medizinische Wahrheit erfinden.\n"
        "- Nutzen Sie nur die gelieferten Fakten und keine Vermutungen.\n"
        "- Bleiben Sie kurz, ruhig und natuerlich.\n"
        "- Stellen Sie hoechstens eine Frage.\n"
        "- Geben Sie keine finale Versorgungsempfehlung, wenn dies nicht "
        "explizit angefordert und freigegeben wurde.\n"
        "- Schreiben Sie keine Ueberschriften und keine Listen.\n"
        "- Erwaehnen Sie nur Informationen, die in den bekannten Fakten unten "
        "explizit enthalten sind.\n"
        "- Wenn bekannte Fakten fuer eine freie Antwort nicht reichen, "
        "formulieren Sie nur eine knappe, gezielte Rueckfrage.\n"
        "- Wenn eine gezielte naechste medizinische Rueckfrage sinnvoll ist, "
        "stellen Sie genau diese eine Rueckfrage.\n"
        "- Bleiben Sie strikt innerhalb der unten beschriebenen erlaubten "
        "Antwortfamilie.\n"
        "- Wenn dort eine Rueckfrage gefragt ist, stellen Sie genau eine "
        "gezielte Rueckfrage und fuehren Sie kein langes Schema aus.\n"
        "- Wenn dort nur eine bestaetigende medizinische Weiterfuehrung "
        "erlaubt ist, antworten Sie kurz und stellen Sie keine zusaetzliche "
        "zweite Frage.\n"
    )


def _build_user_prompt(
    *,
    response_mode: str,
    response_state: ResponseState,
    response_strategy: ResponseStrategy,
    context: TurnContext,
    entry_decision: EntryDecision,
    latest_user_message: str,
    response_history_messages: list[dict[str, str]] | None,
) -> str:
    case_frame = (
        context.medical_case.current_case_frame_label()
        if context.medical_case is not None
        else None
    )
    followup_focus_label = (
        pending_followup.focus_label
        if (pending_followup := context.dialogue_state.pending_followup) is not None
        else None
    )
    observations = []
    if context.medical_case is not None:
        for observation in context.medical_case.active_observations(include_negated=True)[:3]:
            details = []
            if observation.runtime_value("body_site"):
                details.append(f"Ort={observation.runtime_value('body_site')}")
            if observation.runtime_value("temporality"):
                details.append(f"Beginn={observation.runtime_value('temporality')}")
            if observation.runtime_value("severity") is not None:
                details.append(f"Staerke={observation.runtime_value('severity')}")
            detail_suffix = f" ({', '.join(details)})" if details else ""
            observations.append(f"- {observation.patient_label}{detail_suffix}")
    observation_text = "\n".join(observations) if observations else "- keine"
    history_text = _format_conversation_history(response_history_messages)
    allowed_next_step = _allowed_next_step(context.gate_decision)

    pending_followup_text = (
        f"{pending_followup.kind}:{pending_followup.slot}"
        if pending_followup is not None
        else "none"
    )
    return (
        f"Antwortstrategie: {response_strategy.kind}\n"
        f"Response Mode: {response_mode}\n"
        f"Response State Medical: {response_state.medical_state}\n"
        f"Response State Transition: {response_state.transition_state}\n"
        f"Response State Recommendation: {response_state.recommendation_state}\n"
        f"Concern Relation: {context.concern_relation}\n"
        f"Latest Turn Role: {context.latest_turn_role}\n"
        f"Concern Phase: {context.concern_state.phase}\n"
        f"Concern Information Sufficiency: {context.concern_state.information_sufficiency}\n"
        f"Allowed Next Step: {allowed_next_step or 'none'}\n"
        f"Gate Status: {context.gate_decision.gate_status if context.gate_decision is not None else 'none'}\n"
        f"Letzte Nutzernachricht: {latest_user_message}\n"
        f"Message-Rolle laut Entry: {entry_decision.message_role}\n"
        f"Additional Medical Information: {entry_decision.additional_medical_information}\n"
        f"Active Modules: {', '.join(entry_decision.active_modules) or 'none'}\n"
        f"Recommendation angefragt: {context.dialogue_state.recommendation_requested}\n"
        f"Pending Follow-up: {pending_followup_text}\n"
        f"Pending Follow-up Focus: {followup_focus_label or 'none'}\n"
        f"Case Frame: {case_frame or 'none'}\n"
        f"Erlaubte Antwortfamilie: {_allowed_response_family(response_mode=response_mode, gate_decision=context.gate_decision)}\n"
        "Letzte Konversation:\n"
        f"{history_text}\n"
        "Aktuelle Beobachtungen:\n"
        f"{observation_text}\n"
        "Aufgabe:\n"
        "- Formulieren Sie eine kurze, natuerliche naechste Antwort.\n"
        "- Nutzen Sie ausschliesslich die bekannte medizinische Lage.\n"
        "- Bleiben Sie innerhalb des erlaubten naechsten Zugs.\n"
        "- Wenn eine Rueckfrage sinnvoll ist, fragen Sie genau einen naechsten "
        "relevanten Punkt.\n"
        "- Antworten Sie nicht bloss mit einer generischen Bestaetigung.\n"
        "- Erfinden Sie keine Symptome, keine Dauerangaben und keine "
        "Subjektinformationen.\n"
    )


def _format_conversation_history(
    response_history_messages: list[dict[str, str]] | None,
) -> str:
    if not response_history_messages:
        return "- none"

    lines: list[str] = []
    for message in response_history_messages[-6:]:
        role = (message.get("role") or "unknown").strip()
        content = (message.get("content") or "").strip()
        if not content:
            continue
        lines.append(f"- {role}: {content}")

    return "\n".join(lines) if lines else "- none"


def _allowed_response_family(
    *,
    response_mode: str,
    gate_decision: RecommendationGateDecision | None,
) -> str:
    if response_mode == "ask_followup":
        return "gezielte einzelne medizinische Rueckfrage"
    if response_mode == "continue":
        if _allowed_next_step(gate_decision) == "continue_medical":
            return "kurze natuerliche medizinische Weiterfuehrung oder genau eine passende Rueckfrage"
        return "kurze medizinische Weiterfuehrung ohne Themenwechsel"
    return "keine freie Antwortfamilie"


def _allowed_next_step(
    gate_decision: RecommendationGateDecision | None,
) -> str | None:
    if gate_decision is None:
        return None
    return gate_decision.allowed_next_step
