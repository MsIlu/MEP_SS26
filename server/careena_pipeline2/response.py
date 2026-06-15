from careena_pipeline2.models import DialogueState, MedicalCase, PipelineResult
from careena_pipeline2.text import question_for_requirement


EMERGENCY_TEXT = (
    "Wichtiger Hinweis:\n"
    "Ihre Angaben koennen auf eine akute Notfallsituation hinweisen.\n\n"
    "Naechster Schritt:\n"
    "Bitte waehlen Sie sofort den Notruf 112 oder holen Sie umgehend medizinische Hilfe.\n\n"
    "Hinweis:\n"
    "Diese Einschaetzung ersetzt keine aerztliche Untersuchung und stellt keine Diagnose dar."
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
    "116117": "Aerztlicher Bereitschaftsdienst 116117",
    "emergency_department": "Notaufnahme",
    "112": "Notruf 112",
    "unknown": "Hausarztpraxis",
}

SPECIALTY_LABELS = {
    "general_practice": "Hausarztpraxis",
    "orthopedics": "Orthopaedie",
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
    "self_care": "Beobachten Sie die Entwicklung zunaechst weiter und holen Sie aerztlichen Rat ein, wenn es zunimmt oder Sie stark besorgt sind.",
    "pharmacy": "Lassen Sie sich in einer Apotheke beraten, sofern keine deutliche Verschlechterung oder Warnzeichen dazukommen.",
    "specialist": "Vereinbaren Sie einen Termin in der passenden Facharztpraxis; bei rascher Verschlechterung holen Sie frueher aerztlichen Rat ein.",
    "116117": "Kontaktieren Sie den aerztlichen Bereitschaftsdienst unter 116117.",
    "emergency_department": "Lassen Sie die Beschwerden heute in einer Notaufnahme oder Notfallpraxis abklaeren.",
    "112": "Waehlen Sie sofort den Notruf 112 oder holen Sie umgehend medizinische Hilfe.",
}


def pipeline_result_to_chat_response(result: PipelineResult) -> dict:
    if result.response_mode == "emergency":
        return _emergency_response(result)
    if result.response_mode == "confirm_case":
        return _text_response(_confirmation_text(result))
    if result.response_mode == "ask_followup":
        return _text_response(_followup_text(result))
    if result.response_mode == "recommend" and result.recommendation is not None:
        return _text_response(_recommendation_text(result))
    if result.response_mode == "out_of_scope":
        return _text_response(OUT_OF_SCOPE_TEXT)
    return _text_response(DEFAULT_CANNOT_ASSESS_TEXT)


def case_to_payload(
    case: MedicalCase,
    *,
    dialogue_state: DialogueState | None = None,
) -> dict:
    primary = case.primary_observation()
    return {
        "case_id": case.case_id,
        "subject": case.subject.model_dump(),
        "primary_problem_id": case.primary_problem_id,
        "primary_focus": case.primary_focus_label(),
        "active_problem_ids": case.active_problem_ids(),
        "observations": [observation.model_dump() for observation in case.observations],
        "dialogue": {
            "pending_followup": (
                dialogue_state.pending_requirement if dialogue_state is not None else None
            ),
            "open_requirements": (
                [dialogue_state.pending_requirement]
                if dialogue_state is not None and dialogue_state.pending_requirement
                else []
            ),
            "awaiting_confirmation": (
                dialogue_state.awaiting_confirmation if dialogue_state is not None else False
            ),
            "pending_confirmation_observation_ids": (
                list(dialogue_state.pending_confirmation_observation_ids)
                if dialogue_state is not None
                else []
            ),
            "pending_confirmation_subject": (
                dialogue_state.pending_confirmation_subject
                if dialogue_state is not None
                else False
            ),
            "focus_observation_id": (
                dialogue_state.focus_observation_id
                if dialogue_state is not None
                else (primary.id if primary is not None else case.primary_problem_id)
            ),
            "focus_label": (
                case.primary_focus_label()
                if dialogue_state is None or dialogue_state.focus_observation_id is None
                else case.primary_focus_label()
            ),
        },
    }


def _text_response(text: str) -> dict:
    return {"response": text, "red_flag": False}


def _emergency_response(result: PipelineResult) -> dict:
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


def _followup_text(result: PipelineResult) -> str:
    if result.followup_question:
        return result.followup_question
    requirement = (
        result.dialogue_state.pending_requirement
        if result.dialogue_state is not None
        else None
    )
    return question_for_requirement(requirement) or DEFAULT_FOLLOWUP_TEXT


def _confirmation_text(result: PipelineResult) -> str:
    case = result.case
    state = result.dialogue_state
    if case is None or state is None:
        return "Ich habe noch keine Angaben erkannt, die Sie bestaetigen koennen."

    lines = ["Ich habe bisher verstanden:"]
    if state.pending_confirmation_subject and case.subject.has_value():
        subject_line = "Es geht "
        if case.subject.relation == "self":
            subject_line += "um Sie selbst."
        elif case.subject.relation == "child":
            subject_line += "um Ihr Kind."
        elif case.subject.relation == "relative":
            subject_line += "um eine andere angehoerige Person."
        elif case.subject.relation == "other_person":
            subject_line += "um eine andere Person."
        else:
            subject_line += "um die betroffene Person."
        lines.append(f"- {subject_line}")

    observation_ids = set(state.pending_confirmation_observation_ids)
    items = [
        _observation_summary(observation)
        for observation in case.observations
        if observation.id in observation_ids and observation.verification_status != "rejected"
    ]
    if not items and case.unconfirmed_observations():
        items = [_observation_summary(observation) for observation in case.unconfirmed_observations()[:5]]
    if not items and not state.pending_confirmation_subject:
        return "Ich habe noch keine Angaben erkannt, die Sie bestaetigen koennen."

    for item in items[:5]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("Stimmt das so?")
    return "\n".join(lines).strip()


def _recommendation_text(result: PipelineResult) -> str:
    recommendation = result.recommendation
    case = result.case.clone_confirmed_case() if result.case is not None else None
    if case is not None:
        case.ensure_primary_problem(source="confirmed")
    reasons = "\n".join(f"- {reason}" for reason in recommendation.reasons[:6])
    if not reasons:
        reasons = "- auf Basis Ihrer geschilderten Angaben"
    return (
        "Kurze Zusammenfassung:\n"
        f"Im Vordergrund steht aktuell: {_case_focus_label(case)}.\n\n"
        "Dringlichkeit:\n"
        f"{_urgency_label(recommendation.urgency, recommendation.urgency_level)}\n\n"
        "Empfohlene Versorgungsebene:\n"
        f"{_care_level_label(recommendation.care_level, recommendation.specialty)}\n\n"
        "Naechster Schritt:\n"
        f"{_next_step_label(recommendation.care_level, recommendation.urgency)}\n\n"
        "Begruendung:\n"
        f"{reasons}\n\n"
        "Hinweis:\n"
        "Diese Einschaetzung ersetzt keine aerztliche Untersuchung und stellt keine Diagnose dar."
    )


def _care_level_label(care_level: str, specialty: str) -> str:
    if care_level == "specialist":
        return SPECIALTY_LABELS.get(specialty, specialty)
    return CARE_LEVEL_LABELS.get(care_level, care_level)


def _case_focus_label(case: MedicalCase | None) -> str:
    if case is None:
        return "Ihre Angaben"
    focus = case.primary_focus_label(source="confirmed")
    if focus:
        return focus
    for observation in case.active_observations(source="confirmed"):
        return observation.patient_label
    return "Ihre Angaben"


def _next_step_label(care_level: str, urgency: str) -> str:
    if care_level == "general_practice":
        if urgency in {"soon", "today"}:
            return "Kontaktieren Sie zeitnah eine Hausarztpraxis oder den aerztlichen Bereitschaftsdienst 116117, wenn die Praxis nicht erreichbar ist."
        return "Vereinbaren Sie regulaer einen Termin in einer Hausarztpraxis."
    return NEXT_STEP_LABELS.get(
        care_level,
        "Holen Sie aerztlichen Rat ein, wenn die Beschwerden anhalten, zunehmen oder Sie unsicher sind.",
    )


def _urgency_label(value: str, urgency_level: str | None = None) -> str:
    if value == "unknown" and urgency_level:
        return URGENCY_LEVEL_LABELS.get(urgency_level, urgency_level)
    return URGENCY_LABELS.get(value, value)


def _observation_summary(observation) -> str:
    details: list[str] = []
    temporality = observation.runtime_value("temporality")
    if temporality:
        details.append(f"seit/zeitlich: {temporality}")
    severity = observation.runtime_value("severity")
    if severity is not None:
        details.append(f"Staerke: {severity}/10")
    context = observation.runtime_detail_value("context")
    if context:
        details.append(f"Hergang: {context}")
    limitation = observation.runtime_detail_value("functional_limitation")
    if limitation:
        details.append(f"Belastbarkeit: {limitation}")
    suffix = f" ({'; '.join(details)})" if details else ""
    return f"{observation.patient_label}{suffix}"
