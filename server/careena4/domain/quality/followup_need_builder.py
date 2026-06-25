from __future__ import annotations

from careena4.domain.case import CaseManager
from careena4.domain.quality.observation_quality_evaluator import ObservationQuality
from careena4.models.domain import CaseTopic, FollowupNeed, MedicalCase, Observation


class FollowupNeedBuilder:
    def __init__(self, *, case_manager: CaseManager | None = None) -> None:
        self.case_manager = case_manager or CaseManager()

    def build(
        self,
        *,
        case_topic: CaseTopic | None,
        medical_case: MedicalCase,
        qualities: list[ObservationQuality],
    ) -> list[FollowupNeed]:
        needs: list[FollowupNeed] = []
        active_observations = self.case_manager.active_observations(medical_case=medical_case)
        topic_label = self.case_manager.topic_label(case_topic=case_topic)
        topic_extension_kinds = self.case_manager.topic_extension_kinds(case_topic=case_topic)

        if (
            self.case_manager.has_observations(medical_case=medical_case)
            and self.case_manager.person_relation(medical_case=medical_case) == "unclear"
        ):
            needs.append(
                FollowupNeed(
                    reason="subject_unclear",
                    priority="high",
                    blocking=True,
                )
            )
        quality_by_id = {quality.observation_id: quality for quality in qualities}

        duration_candidates = self._candidate_observations(
            observations=active_observations,
            quality_by_id=quality_by_id,
            require_attribute="duration_or_onset",
        )
        if duration_candidates and "duration_or_onset" not in topic_extension_kinds:
            chosen = duration_candidates[0]
            needs.append(
                FollowupNeed(
                    observation_id=chosen.observation_id,
                    reason="duration_missing",
                    target_extension_kind="duration_or_onset",
                    case_focus_label=topic_label or chosen.label,
                    related_observation_ids=[observation.observation_id for observation in duration_candidates],
                    priority="high",
                    blocking=True,
                )
            )

        description_candidates = self._description_candidates(
            observations=active_observations,
            quality_by_id=quality_by_id,
        )
        if description_candidates and "description" not in topic_extension_kinds:
            chosen = description_candidates[0]
            chosen_quality = quality_by_id.get(chosen.observation_id)
            needs.append(
                FollowupNeed(
                    observation_id=chosen.observation_id,
                    reason="description_missing",
                    target_extension_kind="description",
                    case_focus_label=topic_label or chosen.label,
                    related_observation_ids=[observation.observation_id for observation in description_candidates],
                    priority="medium",
                    blocking=chosen_quality.topic_fit == "central" if chosen_quality is not None else False,
                )
            )
        return needs

    def _candidate_observations(
        self,
        *,
        observations: list[Observation],
        quality_by_id: dict[str, ObservationQuality],
        require_attribute: str,
    ) -> list[Observation]:
        candidates: list[tuple[int, Observation]] = []
        for observation in observations:
            quality = quality_by_id.get(observation.observation_id)
            if quality is None:
                continue
            if observation.type not in {"symptom", "injury"}:
                continue
            if observation.attributes.get(require_attribute) not in (None, "", []):
                continue
            if quality.topic_fit not in {"central", "related"}:
                continue
            candidates.append((self._topic_rank(quality.topic_fit), observation))
        candidates.sort(key=lambda item: item[0], reverse=True)
        return [observation for _, observation in candidates]

    def _description_candidates(
        self,
        *,
        observations: list[Observation],
        quality_by_id: dict[str, ObservationQuality],
    ) -> list[Observation]:
        candidates: list[tuple[int, Observation]] = []
        for observation in observations:
            quality = quality_by_id.get(observation.observation_id)
            if quality is None:
                continue
            if observation.type not in {"symptom", "injury"}:
                continue
            if observation.attributes.get("description") not in (None, "", []):
                continue
            if quality.topic_fit not in {"central", "related"}:
                continue
            if not self._needs_description(observation=observation, quality=quality):
                continue
            candidates.append((self._topic_rank(quality.topic_fit), observation))
        candidates.sort(key=lambda item: item[0], reverse=True)
        return [observation for _, observation in candidates]

    @staticmethod
    def _topic_rank(topic_fit: str) -> int:
        return {"central": 2, "related": 1}.get(topic_fit, 0)

    @staticmethod
    def _needs_description(*, observation: Observation, quality: ObservationQuality) -> bool:
        if observation.type == "injury":
            return True
        if quality.ambiguity == "high":
            return True
        informative_keys = {
            key
            for key, value in observation.attributes.items()
            if value not in (None, "", [])
            and key in {"duration_or_onset", "body_site", "severity", "mechanism", "functional_limitation"}
        }
        if len(informative_keys) <= 1:
            return True
        return len(informative_keys) <= 2 and observation.label.casefold().endswith("schmerzen")
