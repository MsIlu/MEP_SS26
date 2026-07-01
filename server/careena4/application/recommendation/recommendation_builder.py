import json
import logging

from careena4.domain.case import CaseManager
from careena4.models.domain import MedicalCase
from careena4.models.turn.input import DiaryEntry, MedicationEntry
from careena4.models.workflow import RecommendationResult

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Du bist ein medizinisches Assistenzsystem für Laien. "
    "Analysiere den geschilderten Fall und gib eine strukturierte, differenzierte "
    "Handlungsempfehlung auf Deutsch aus. "
    "Berücksichtige Alter, Geschlecht, alle genannten Symptome, deren Schweregrad, "
    "den Verlauf aus dem Symptomtagebuch und die aktuell eingenommenen Medikamente. "
    "Wähle die Versorgungsebene (care_level) so niedrig wie medizinisch vertretbar — "
    "schicke nicht pauschal zum Hausarzt, wenn Selbstbehandlung oder die Apotheke ausreichen. "
    "Antworte ausschließlich mit einem gültigen JSON-Objekt, ohne Markdown-Blöcke oder Erklärungen."
)

# Concrete decision guidance so the model differentiates instead of always
# defaulting to general_practice. Ordered from least to most urgent.
_CARE_LEVEL_GUIDANCE = """
Wähle care_level nach folgender Eskalationslogik (niedrigste vertretbare Stufe):
- self_care: leichte, klar harmlose Beschwerden, kurze Dauer, kein Schweregrad-Hinweis
  (z.B. leichter Schnupfen, leichte Kopfschmerzen). next_step: konkrete Selbsthilfe.
- pharmacy: Beschwerden, bei denen rezeptfreie Mittel oder eine Apothekenberatung helfen
  (z.B. Erkältung, leichte Schmerzen, Sodbrennen). next_step: Apotheke aufsuchen.
- general_practice: anhaltende, unklare oder mittelschwere Beschwerden, die ärztlich
  abgeklärt werden sollten, aber nicht dringend sind.
- specialist: Beschwerden mit klarem Fachbezug (z.B. Hautbefund -> dermatology).
- 116117: ärztlich abklärungsbedürftig außerhalb der Praxiszeiten, aber kein Notfall.
- emergency_department / 112: Warnzeichen, akute schwere Symptome, Hinweise auf Notfall.
Begründe in "reasons" konkret anhand der genannten Symptome, des Schweregrads und —
falls vorhanden — des Verlaufs und der Medikamente, warum diese Stufe gewählt wurde.
"""

_JSON_SCHEMA = """
{
  "urgency": "<unknown|self_observation|routine|soon|today|emergency>",
  "urgency_level": "<low|medium|high|emergency|unclear>",
  "care_level": "<self_care|pharmacy|general_practice|specialist|116117|emergency_department|112|unknown>",
  "specialty": "<unknown|general_practice|orthopedics|dermatology|neurology|ent|emergency_medicine>",
  "summary": "<1-2 Sätze Zusammenfassung der klinischen Situation>",
  "next_step": "<konkrete Handlungsempfehlung für den Patienten, 1-2 Sätze>",
  "reasons": ["<konkreter Grund 1>", "<konkreter Grund 2>"]
}
"""

_FALLBACK_RESULT = RecommendationResult(
    allowed=True,
    summary="Es liegen ausreichend Angaben für eine vorsichtige Orientierung vor.",
    urgency="routine",
    urgency_level="low",
    care_level="general_practice",
    specialty="general_practice",
    reasons=["Konservative Einschätzung aufgrund fehlender KI-Antwort."],
    next_step=(
        "Wenn die Beschwerden anhalten, zunehmen oder du dich unsicher fühlst, "
        "vereinbare einen Termin in einer Hausarztpraxis."
    ),
    limitations=[
        "Die Empfehlung konnte nicht durch KI-Analyse erstellt werden.",
        "Sie ersetzt keine ärztliche Untersuchung oder Diagnose.",
    ],
)

_VALID_URGENCY = {"unknown", "self_observation", "routine", "soon", "today", "emergency"}
_VALID_LEVEL = {"low", "medium", "high", "emergency", "unclear"}
_VALID_CARE = {"self_care", "pharmacy", "general_practice", "specialist", "116117", "emergency_department", "112", "unknown"}
_VALID_SPECIALTY = {"unknown", "general_practice", "orthopedics", "dermatology", "neurology", "ent", "emergency_medicine"}


def _serialize_case(medical_case: MedicalCase, case_manager: CaseManager) -> str:
    parts: list[str] = []

    person = medical_case.person
    if person:
        age_str = f"{person.age} Jahre" if person.age else "unbekanntes Alter"
        sex_str = person.sex if person.sex else "unbekanntes Geschlecht"
        parts.append(f"Patient: {age_str}, {sex_str}")

    topic_label = case_manager.topic_label(medical_case=medical_case)
    if topic_label:
        parts.append(f"Hauptproblem: {topic_label}")

    observations = case_manager.central_non_negated_observations(medical_case=medical_case)
    if observations:
        symptom_lines = []
        for obs in observations:
            line = obs.normalized_label_de
            if obs.onset:
                line += f" (seit {obs.onset})"
            if obs.severity:
                line += f", Schwere: {obs.severity}/10"
            if obs.description:
                line += f", Charakter: {obs.description}"
            symptom_lines.append(line)
        parts.append("Symptome: " + "; ".join(symptom_lines))

    return "\n".join(parts) if parts else "Keine Fallinformationen verfügbar."


def _serialize_diary(diary_history: list[DiaryEntry]) -> str:
    if not diary_history:
        return ""
    lines = ["Symptomtagebuch (chronologisch, neueste zuerst):"]
    for entry in diary_history:
        line = f"- {entry.date}: {entry.symptom}, Intensität {entry.intensity}/10"
        if entry.body_area:
            line += f", Körperbereich: {entry.body_area}"
        if entry.note:
            line += f", Notiz: {entry.note}"
        lines.append(line)
    return "\n".join(lines)


def _serialize_medications(medication_history: list[MedicationEntry]) -> str:
    if not medication_history:
        return ""
    lines = ["Aktueller Medikamentenplan:"]
    for entry in medication_history:
        line = f"- {entry.name}"
        if entry.dose:
            line += f", Dosis: {entry.dose}"
        if entry.active_substance:
            line += f", Wirkstoff: {entry.active_substance}"
        if entry.frequency:
            line += f", Einnahme: {entry.frequency}"
        if entry.schedule:
            line += f" ({entry.schedule})"
        lines.append(line)
    return "\n".join(lines)


def _build_data_sources(
    *,
    medical_case: MedicalCase,
    case_manager: CaseManager,
    diary_history: list[DiaryEntry],
    medication_history: list[MedicationEntry],
) -> list[str]:
    """Deterministically describe which inputs fed into the recommendation.

    Never derived from the LLM, so the provenance shown to the user is reliable.
    """
    sources: list[str] = []

    if case_manager.central_non_negated_observations(medical_case=medical_case):
        sources.append("Angaben aus dem Chat")

    person = medical_case.person
    if person and (person.age or person.sex):
        sources.append("Profilangaben (Alter/Geschlecht)")

    if diary_history:
        count = len(diary_history)
        label = "Eintrag" if count == 1 else "Einträge"
        sources.append(f"Symptom-Tagebuch ({count} {label})")

    if medication_history:
        count = len(medication_history)
        label = "Medikament" if count == 1 else "Medikamente"
        sources.append(f"Medikamentenplan ({count} {label})")

    return sources


class RecommendationBuilder:
    def __init__(self, *, case_manager: CaseManager | None = None, llm_client=None) -> None:
        self.case_manager = case_manager or CaseManager()
        self._llm_client = llm_client

    def build(
        self,
        *,
        medical_case: MedicalCase,
        diary_history: list[DiaryEntry] | None = None,
        medication_history: list[MedicationEntry] | None = None,
    ) -> RecommendationResult:
        diary_history = diary_history or []
        medication_history = medication_history or []

        data_sources = _build_data_sources(
            medical_case=medical_case,
            case_manager=self.case_manager,
            diary_history=diary_history,
            medication_history=medication_history,
        )

        if self._llm_client is None:
            return _FALLBACK_RESULT.model_copy(update={"data_sources": data_sources})

        case_text = _serialize_case(medical_case, self.case_manager)
        diary_text = _serialize_diary(diary_history)
        medication_text = _serialize_medications(medication_history)

        user_prompt_parts = [case_text]
        if diary_text:
            user_prompt_parts.append(diary_text)
        if medication_text:
            user_prompt_parts.append(medication_text)
        user_prompt_parts.append(_CARE_LEVEL_GUIDANCE)
        user_prompt_parts.append(
            f"Gib eine Handlungsempfehlung als JSON in diesem Format aus:\n{_JSON_SCHEMA}"
        )
        user_prompt = "\n\n".join(user_prompt_parts)

        try:
            raw = self._llm_client.complete(
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=700,
                temperature=0.2,
                call_name="recommendation_build",
            )
            return self._parse(raw or "", data_sources=data_sources)
        except Exception:
            logger.exception("Recommendation generation failed; using fallback.")
            return _FALLBACK_RESULT.model_copy(update={"data_sources": data_sources})

    def _parse(self, raw: str, *, data_sources: list[str] | None = None) -> RecommendationResult:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.warning("RecommendationBuilder: JSON parse failed, using fallback. raw=%r", raw[:200])
            return _FALLBACK_RESULT.model_copy(update={"data_sources": data_sources or []})

        urgency = data.get("urgency", "unknown")
        urgency_level = data.get("urgency_level", "unclear")
        care_level = data.get("care_level", "unknown")
        specialty = data.get("specialty", "unknown")

        return RecommendationResult(
            allowed=True,
            summary=data.get("summary") or "",
            urgency=urgency if urgency in _VALID_URGENCY else "unknown",
            urgency_level=urgency_level if urgency_level in _VALID_LEVEL else "unclear",
            care_level=care_level if care_level in _VALID_CARE else "unknown",
            specialty=specialty if specialty in _VALID_SPECIALTY else "unknown",
            reasons=data.get("reasons") or [],
            next_step=data.get("next_step") or "",
            limitations=["Diese Empfehlung ersetzt keine aerztliche Untersuchung oder Diagnose."],
            data_sources=data_sources or [],
        )
