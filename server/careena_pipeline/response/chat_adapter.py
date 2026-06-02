from careena_pipeline.models import CareenaPipelineResult
from careena_pipeline.planning.requirement_state import normalized_followup_slot


EMERGENCY_TEXT = (
    "Wichtiger Hinweis:\n"
    "Ihre Angaben können auf eine akute Notfallsituation hinweisen.\n\n"
    "Nächster Schritt:\n"
    "Bitte wählen Sie sofort den Notruf 112 oder holen Sie umgehend medizinische Hilfe.\n\n"
    "Hinweis:\n"
    "Diese Einschätzung ersetzt keine ärztliche Untersuchung und stellt keine Diagnose dar."
)

OUT_OF_SCOPE_TEXT = (
    "Ich kann hier nur bei gesundheitsbezogenen Anliegen helfen. "
    "Bitte beschreiben Sie eine gesundheitliche Beschwerde oder Frage."
)

DEFAULT_FOLLOWUP_TEXT = "Welche wichtige Information fehlt noch zu den Beschwerden?"
DEFAULT_CANNOT_ASSESS_TEXT = (
    "Ich habe noch nicht genug konkrete medizinische Informationen. "
    "Welche gesundheitliche Beschwerde steht gerade im Vordergrund?"
)

CARE_LEVEL_LABELS = {
    "self_care": "Selbstbeobachtung",
    "pharmacy": "Apotheke",
    "general_practice": "Hausarztpraxis",
    "116117": "Ärztlicher Bereitschaftsdienst 116117",
    "emergency_department": "Notaufnahme",
    "112": "Notruf 112",
    "unknown": "Hausarztpraxis",
}

SPECIALTY_LABELS = {
    "general_practice": "Hausarztpraxis",
    "orthopedics": "Orthopädie",
    "dermatology": "Dermatologie",
    "neurology": "Neurologie",
    "ent": "HNO-Praxis",
    "emergency_medicine": "Notfallmedizin",
    "unknown": "Hausarztpraxis",
}

URGENCY_LABELS = {
    "self_observation": "Selbstbeobachtung",
    "routine": "Routine",
    "soon": "zeitnah",
    "today": "heute",
    "emergency": "sofort",
    "unknown": "unklar",
}

URGENCY_LEVEL_LABELS = {
    "low": "niedrig",
    "medium": "mittel",
    "high": "hoch",
    "emergency": "Notfall",
    "unclear": "nicht eindeutig",
}

NEXT_STEP_LABELS = {
    "self_care": "Beobachten Sie die Entwicklung zunächst weiter und holen Sie ärztlichen Rat ein, wenn es zunimmt oder Sie stark besorgt sind.",
    "pharmacy": "Lassen Sie sich in einer Apotheke beraten, sofern keine deutliche Verschlechterung oder Warnzeichen dazukommen.",
    "specialist": "Vereinbaren Sie einen Termin in der passenden Facharztpraxis; bei rascher Verschlechterung holen Sie früher ärztlichen Rat ein.",
    "116117": "Kontaktieren Sie den ärztlichen Bereitschaftsdienst unter 116117.",
    "emergency_department": "Lassen Sie die Beschwerden heute in einer Notaufnahme oder Notfallpraxis abklären.",
    "112": "Wählen Sie sofort den Notruf 112 oder holen Sie umgehend medizinische Hilfe.",
}


def pipeline_result_to_chat_response(result: CareenaPipelineResult) -> dict:
    if result.response_mode == "emergency":
        return _emergency_response(result)
    if result.response_mode == "confirm_information":
        return _text_response(_confirmation_text(result))
    if result.response_mode == "ask_followup":
        return _text_response(_followup_text(result))
    if result.response_mode == "recommend" and result.recommendation:
        return _text_response(_recommendation_text(result))
    if result.response_mode == "out_of_scope":
        return _text_response(OUT_OF_SCOPE_TEXT)
    return _text_response(DEFAULT_CANNOT_ASSESS_TEXT)


def _text_response(text: str) -> dict:
    return {"response": text, "red_flag": False}


def _emergency_response(result: CareenaPipelineResult) -> dict:
    return {
        "response": EMERGENCY_TEXT,
        "red_flag": True,
        "severity": result.safety.severity,
        "action": result.safety.action,
        "rule_id": result.safety.rule_id,
        "rule_name": result.safety.rule_name,
        "category": result.safety.category,
        "message_key": result.safety.message_key,
        "matched_keywords": result.safety.matched_keywords,
    }


def _followup_text(result: CareenaPipelineResult) -> str:
    pending_followup = normalized_followup_slot(_pending_followup(result))
    if pending_followup == "subject":
        return "Geht es um Sie selbst oder um eine andere Person?"
    if result.recommendation_gate and result.recommendation_gate.question:
        return result.recommendation_gate.question
    return DEFAULT_FOLLOWUP_TEXT


def _recommendation_text(result: CareenaPipelineResult) -> str:
    recommendation = result.recommendation
    case = result.case
    if case is not None:
        case.ensure_primary_problem()

    reasons = "\n".join(f"- {reason}" for reason in recommendation.reasons[:6]) or "- auf Basis Ihrer geschilderten Angaben"
    return (
        "Kurze Zusammenfassung:\n"
        f"Im Vordergrund steht aktuell: {_case_focus_label(case)}.\n\n"
        "Dringlichkeit:\n"
        f"{_urgency_label(recommendation.urgency, recommendation.urgency_level)}\n\n"
        "Empfohlene Versorgungsebene:\n"
        f"{_care_level_label(recommendation.care_level, recommendation.specialty)}\n\n"
        "Nächster Schritt:\n"
        f"{_next_step_label(recommendation.care_level, recommendation.urgency)}\n\n"
        "Begründung:\n"
        f"{reasons}\n\n"
        "Hinweis:\n"
        "Diese Einschätzung ersetzt keine ärztliche Untersuchung und stellt keine Diagnose dar."
    )


def _confirmation_text(result: CareenaPipelineResult) -> str:
    if not result.case or not result.case.observations:
        return "Ich habe noch keine Angaben erkannt, die Sie bestätigen können."

    items = [
        f"- {observation.patient_label}"
        for observation in result.case.observations
        if observation.status != "user_rejected"
    ]
    if not items:
        return "Ich habe noch keine aktiven Angaben erkannt, die Sie bestätigen können."
    return "Ich habe folgende Angaben erkannt:\n" + "\n".join(items[:6]) + "\n\nStimmt das so?"


def _care_level_label(care_level: str, specialty: str) -> str:
    if care_level == "specialist":
        return SPECIALTY_LABELS.get(specialty, specialty)
    return CARE_LEVEL_LABELS.get(care_level, care_level)


def _case_focus_label(case) -> str:
    if not case:
        return "Ihre Angaben"
    case.ensure_primary_problem()
    focus = case.primary_focus_label()
    if focus:
        return focus
    for observation in case.observations:
        if observation.status != "user_rejected":
            return observation.patient_label
    return "Ihre Angaben"


def _pending_followup(result: CareenaPipelineResult) -> str | None:
    if result.dialogue_state and result.dialogue_state.pending_followup:
        return result.dialogue_state.pending_followup
    if result.recommendation_gate and result.recommendation_gate.missing_information:
        return result.recommendation_gate.missing_information[0]
    if result.readiness and result.readiness.blocking_requirements:
        return result.readiness.blocking_requirements[0]
    if result.readiness and result.readiness.missing_information:
        return result.readiness.missing_information[0]
    return None


def _next_step_label(care_level: str, urgency: str) -> str:
    if care_level == "general_practice":
        if urgency in {"soon", "today"}:
            return "Kontaktieren Sie zeitnah eine Hausarztpraxis oder den ärztlichen Bereitschaftsdienst 116117, wenn die Praxis nicht erreichbar ist."
        return "Vereinbaren Sie regulär einen Termin in einer Hausarztpraxis."
    return NEXT_STEP_LABELS.get(
        care_level,
        "Holen Sie ärztlichen Rat ein, wenn die Beschwerden anhalten, zunehmen oder Sie unsicher sind.",
    )


def _urgency_label(value: str, urgency_level: str | None = None) -> str:
    if value == "unknown" and urgency_level:
        return URGENCY_LEVEL_LABELS.get(urgency_level, urgency_level)
    return URGENCY_LABELS.get(value, value)
