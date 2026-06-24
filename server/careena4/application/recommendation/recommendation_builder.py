from careena4.domain.case import CaseManager
from careena4.models.domain import CaseTopic, MedicalCase
from careena4.models.workflow import RecommendationResult


class RecommendationBuilder:
    def __init__(self, *, case_manager: CaseManager | None = None) -> None:
        self.case_manager = case_manager or CaseManager()

    def build(self, *, case_topic: CaseTopic | None, medical_case: MedicalCase) -> RecommendationResult:
        central_observations = self.case_manager.central_non_negated_observations(
            medical_case=medical_case
        )
        focus_label = self.case_manager.topic_label(case_topic=case_topic) if case_topic is not None else (
            central_observations[0].label if central_observations else "den aktuellen Fall"
        )
        reasons = [f"Es liegen ausreichend Angaben zu {focus_label} vor."]
        limitations = [
            "Die Empfehlung basiert auf einer konservativen V1-Regellogik.",
            "Sie ersetzt keine aerztliche Untersuchung oder Diagnose.",
        ]
        if any(
            obs.type == "injury" and obs.functional_limitation == "kaum auftreten"
            for obs in central_observations
        ):
            return RecommendationResult(
                allowed=True,
                summary=f"Die Angaben zu {focus_label} sprechen fuer eine zeitnahe aerztliche Abklaerung.",
                urgency="today",
                urgency_level="high",
                care_level="emergency_department",
                specialty="orthopedics",
                reasons=reasons + ["Belastung ist deutlich eingeschraenkt."],
                next_step="Bitte lassen Sie die Verletzung heute aerztlich untersuchen.",
                limitations=limitations,
            )
        if any(obs.type == "measurement" and obs.label.casefold() == "fieber" for obs in central_observations):
            return RecommendationResult(
                allowed=True,
                summary=f"Die Angaben zu {focus_label} passen zu einer medizinischen Abklaerung, wenn die Beschwerden anhalten oder zunehmen.",
                urgency="soon",
                urgency_level="medium",
                care_level="general_practice",
                specialty="general_practice",
                reasons=reasons,
                next_step="Beobachten Sie den Verlauf. Bei Verschlechterung oder anhaltenden Beschwerden wenden Sie sich an eine Hausarztpraxis.",
                limitations=limitations,
            )
        return RecommendationResult(
            allowed=True,
            summary=f"Es liegen ausreichend Angaben zu {focus_label} fuer eine vorsichtige Orientierung vor.",
            urgency="routine",
            urgency_level="low",
            care_level="general_practice",
            specialty="general_practice",
            reasons=reasons,
            next_step="Wenn die Beschwerden anhalten, zunehmen oder Sie sich unsicher fuehlen, vereinbaren Sie einen Termin in einer Hausarztpraxis.",
            limitations=limitations,
        )
