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
    def evaluate(self, *, case_topic: CaseTopic | None, medical_case: MedicalCase) -> list[ObservationQuality]:
        qualities: list[ObservationQuality] = []
        for observation in medical_case.active_observations():
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

    @staticmethod
    def _topic_fit(*, case_topic: CaseTopic | None, observation: Observation) -> ObservationTopicFit:
        if observation.topic_relation in {"central", "related"}:
            return observation.topic_relation  # type: ignore[return-value]
        if case_topic is None:
            return "central"
        topic_tokens = case_topic.search_tokens()
        label_tokens = set(observation.label.casefold().split())
        if topic_tokens.intersection(label_tokens):
            return "central"
        return "weak"

    @staticmethod
    def _specificity(observation: Observation) -> ObservationSpecificity:
        if observation.attributes.get("body_site") or observation.attributes.get("mechanism"):
            return "high"
        if len(observation.label) > 12:
            return "medium"
        return "low"

    @staticmethod
    def _completeness(observation: Observation) -> ObservationCompleteness:
        count = len([value for value in observation.attributes.values() if value not in (None, "", [])])
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
        if observation.type in {"symptom", "injury"} and "duration_or_onset" not in observation.attributes:
            return "necessary"
        if observation.type in {"symptom", "injury"} and "description" not in observation.attributes:
            return "necessary"
        if observation.label.casefold() in {"schmerzen", "verletzung"}:
            return "useful"
        return "none"
