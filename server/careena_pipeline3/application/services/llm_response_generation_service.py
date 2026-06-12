from __future__ import annotations

import config

from careena_pipeline3.core.client import LLMClient
from careena_pipeline3.core.exceptions import EmptyLLMResponseError, LLMRequestError
from careena_pipeline3.models.turn import EntryDecision, ResponseStrategy, TurnContext
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
        response_strategy: ResponseStrategy,
        context: TurnContext,
        entry_decision: EntryDecision,
        latest_user_message: str,
        conversation_messages: list[dict[str, str]] | None = None,
        recommendation_result: RecommendationResult | None = None,
    ) -> str:
        del recommendation_result

        if response_strategy.kind != "llm_continue":
            raise ValueError(
                f"unsupported LLM response strategy: {response_strategy.kind}"
            )

        system_prompt = _build_system_prompt()
        user_prompt = _build_user_prompt(
            context=context,
            entry_decision=entry_decision,
            latest_user_message=latest_user_message,
            conversation_messages=conversation_messages,
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
    )


def _build_user_prompt(
    *,
    context: TurnContext,
    entry_decision: EntryDecision,
    latest_user_message: str,
    conversation_messages: list[dict[str, str]] | None,
) -> str:
    primary_focus = (
        context.medical_case.primary_focus_label()
        if context.medical_case is not None
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
    history_text = _format_conversation_history(conversation_messages)

    pending_followup = context.dialogue_state.pending_followup
    pending_followup_text = (
        f"{pending_followup.kind}:{pending_followup.slot}"
        if pending_followup is not None
        else "none"
    )
    return (
        "Antwortstrategie: llm_continue\n"
        f"Response Mode: {context.response_mode or 'continue'}\n"
        f"Response State Medical: {context.response_state.medical_state}\n"
        f"Response State Transition: {context.response_state.transition_state}\n"
        f"Response State Recommendation: {context.response_state.recommendation_state}\n"
        f"Letzte Nutzernachricht: {latest_user_message}\n"
        f"Message-Rolle laut Entry: {entry_decision.message_role}\n"
        f"Additional Medical Information: {entry_decision.additional_medical_information}\n"
        f"Active Modules: {', '.join(entry_decision.active_modules) or 'none'}\n"
        f"Recommendation angefragt: {context.dialogue_state.recommendation_requested}\n"
        f"Recommendation ready: {context.dialogue_state.recommendation_ready}\n"
        f"Pending Follow-up: {pending_followup_text}\n"
        f"Primary Focus: {primary_focus or 'none'}\n"
        "Letzte Konversation:\n"
        f"{history_text}\n"
        "Aktuelle Beobachtungen:\n"
        f"{observation_text}\n"
        "Aufgabe:\n"
        "- Formulieren Sie eine kurze, natuerliche naechste Antwort.\n"
        "- Nutzen Sie ausschliesslich die bekannte medizinische Lage.\n"
        "- Wenn eine Rueckfrage sinnvoll ist, fragen Sie genau einen naechsten "
        "relevanten Punkt.\n"
        "- Antworten Sie nicht bloss mit einer generischen Bestaetigung.\n"
        "- Erfinden Sie keine Symptome, keine Dauerangaben und keine "
        "Subjektinformationen.\n"
    )


def _format_conversation_history(
    conversation_messages: list[dict[str, str]] | None,
) -> str:
    if not conversation_messages:
        return "- none"

    lines: list[str] = []
    for message in conversation_messages[-6:]:
        role = (message.get("role") or "unknown").strip()
        content = (message.get("content") or "").strip()
        if not content:
            continue
        lines.append(f"- {role}: {content}")

    return "\n".join(lines) if lines else "- none"
