from careena4.domain.case import CaseManager
from careena4.models.common import (
    ObservationAmbiguity,
    ObservationCompleteness,
    ObservationFollowupValue,
    ObservationSpecificity,
    ObservationTopicFit,
    PipelineModel,
)
from careena4.models.domain import CaseTopic, MedicalCase, Observation


class ObservationQuality(PipelineModel):
    observation_id: str
    topic_fit: ObservationTopicFit
    specificity: ObservationSpecificity
    completeness: ObservationCompleteness
    ambiguity: ObservationAmbiguity
    followup_value: ObservationFollowupValue


class ObservationQualityEvaluator:
    def __init__(self, *, case_manager: CaseManager | None = None) -> None:
        self.case_manager = case_manager or CaseManager()

    def evaluate(self, *, case_topic: CaseTopic | None, medical_case: MedicalCase) -> list[ObservationQuality]:
        qualities: list[ObservationQuality] = []
        for observation in self.case_manager.active_observations(medical_case=medical_case):
            qualities.append(
                ObservationQuality(
                    observation_id=observation.observation_id,
                    topic_fit=self._topic_fit(case_topic=case_topic, observation=observation),
                    specificity=self._specificity(observation),
                    completeness=self._completeness(observation),
                    ambiguity=self._ambiguity(observation),
                    followup_value=self._followup_value(observation),
                )
            )
        return qualities

    def _topic_fit(self, *, case_topic: CaseTopic | None, observation: Observation) -> ObservationTopicFit:
        if observation.is_central():
            return "central"
        if case_topic is None:
            return "central"
        topic_tokens = self.case_manager.topic_tokens(case_topic=case_topic)
        label_tokens = set(observation.label.casefold().split())
        if topic_tokens.intersection(label_tokens):
            return "central"
        return "weak"

    @staticmethod
    def _specificity(observation: Observation) -> ObservationSpecificity:
        if observation.body_site or observation.mechanism:
            return "high"
        if len(observation.label) > 12:
            return "medium"
        return "low"

    @staticmethod
    def _completeness(observation: Observation) -> ObservationCompleteness:
        count = len(
            [
                value
                for value in (
                    observation.onset,
                    observation.body_site,
                    observation.description,
                    observation.severity,
                    observation.mechanism,
                    observation.functional_limitation,
                    observation.measurement_kind,
                )
                if value not in (None, "", [])
            ]
        )
        if count >= 3:
            return "rich"
        if count >= 1:
            return "usable"
        return "sparse"

    @staticmethod
    def _ambiguity(observation: Observation) -> ObservationAmbiguity:
        generic_labels = {"schmerzen", "beschwerden", "verletzung"}
        return "high" if observation.label.casefold() in generic_labels else "low"

    @staticmethod
    def _followup_value(observation: Observation) -> ObservationFollowupValue:
        if observation.type in {"symptom", "injury"} and observation.onset in (None, ""):
            return "necessary"
        if observation.type in {"symptom", "injury"} and observation.description in (None, ""):
            return "necessary"
        if observation.label.casefold() in {"schmerzen", "verletzung"}:
            return "useful"
        return "none"
