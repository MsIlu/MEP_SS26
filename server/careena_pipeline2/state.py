from __future__ import annotations

from dataclasses import dataclass

from careena_pipeline2.models import (
    CaseObservation,
    ConfirmationUpdate,
    DialogueState,
    MedicalCase,
    MessageRole,
    MessageUpdate,
    Provenance,
    Subject,
)
from careena_pipeline2.text import normalize_text


@dataclass
class MergeResult:
    case: MedicalCase
    dialogue_state: DialogueState
    changed_observation_ids: list[str]
    subject_changed: bool = False


class CaseUpdater:
    def apply(
        self,
        case: MedicalCase,
        dialogue_state: DialogueState,
        update: MessageUpdate,
    ) -> MergeResult:
        changed_observation_ids: list[str] = []
        subject_changed = self._merge_subject(case, update.subject, update.message_role)

        for observation in update.observations:
            target = self._find_target(case, update, observation)
            if target is None:
                case.observations.append(observation)
                changed_observation_ids.append(observation.id)
                continue
            if self._merge_observation(target, observation, update.message_role):
                changed_observation_ids.append(target.id)

        if update.possible_new_topic and changed_observation_ids:
            latest_id = changed_observation_ids[-1]
            for observation in case.observations:
                if observation.id == latest_id:
                    case.set_primary_observation(observation)
                    break
        else:
            case.ensure_primary_problem()

        if case.primary_problem_id is not None:
            dialogue_state.focus_observation_id = case.primary_problem_id

        return MergeResult(
            case=case,
            dialogue_state=dialogue_state,
            changed_observation_ids=changed_observation_ids,
            subject_changed=subject_changed,
        )

    @staticmethod
    def _merge_subject(
        case: MedicalCase,
        incoming: Subject | None,
        message_role: MessageRole,
    ) -> bool:
        if incoming is None or not incoming.has_value():
            return False
        changed = False
        target = case.subject
        if incoming.relation != "unknown" and incoming.relation != target.relation:
            target.relation = incoming.relation
            changed = True
        if incoming.description and incoming.description != target.description:
            target.description = incoming.description
            changed = True
        if incoming.age is not None and incoming.age != target.age:
            target.age = incoming.age
            changed = True
        if incoming.sex and incoming.sex != target.sex:
            target.sex = incoming.sex
            changed = True
        if incoming.confidence > target.confidence:
            target.confidence = incoming.confidence
        if changed or message_role in {"confirmation", "correction"}:
            target.verification_status = incoming.verification_status
        return changed

    @classmethod
    def _find_target(
        cls,
        case: MedicalCase,
        update: MessageUpdate,
        observation: CaseObservation,
    ) -> CaseObservation | None:
        if observation.id:
            for existing in case.observations:
                if existing.id == observation.id:
                    return existing

        exact = cls._exact_match(case, observation)
        if exact is not None:
            return exact

        if update.message_role in {"answer_to_followup", "correction"}:
            primary = case.primary_observation()
            if primary is not None and cls._compatible_with_primary(primary, observation):
                return primary

        if not update.possible_new_topic:
            for existing in case.observations:
                if cls._same_focus(existing, observation):
                    return existing
        return None

    @staticmethod
    def _exact_match(case: MedicalCase, observation: CaseObservation) -> CaseObservation | None:
        for existing in case.observations:
            if (
                existing.type == observation.type
                and (existing.concept or existing.label) == (observation.concept or observation.label)
                and normalize_text(existing.source_span) == normalize_text(observation.source_span)
            ):
                return existing
        return None

    @staticmethod
    def _compatible_with_primary(primary: CaseObservation, incoming: CaseObservation) -> bool:
        if primary.type == incoming.type:
            return True
        return primary.type in {"symptom", "injury"} and incoming.type in {"symptom", "injury"}

    @staticmethod
    def _same_focus(left: CaseObservation, right: CaseObservation) -> bool:
        left_key = (
            left.type,
            normalize_text(left.concept or left.label or ""),
            normalize_text(left.runtime_value("body_site") or ""),
        )
        right_key = (
            right.type,
            normalize_text(right.concept or right.label or ""),
            normalize_text(right.runtime_value("body_site") or ""),
        )
        return left_key == right_key

    @staticmethod
    def _merge_observation(
        target: CaseObservation,
        source: CaseObservation,
        message_role: MessageRole,
    ) -> bool:
        changed = False
        overwrite = message_role == "correction"

        for field_name in ("label", "display_label", "concept", "source_span", "body_site", "temporality"):
            incoming = getattr(source, field_name)
            current = getattr(target, field_name)
            if incoming and (overwrite or not current or current != incoming):
                setattr(target, field_name, incoming)
                changed = True

        for field_name in ("severity", "laterality", "course", "subject_ref", "certainty"):
            incoming = getattr(source, field_name)
            current = getattr(target, field_name)
            if incoming is not None and (overwrite or current != incoming):
                setattr(target, field_name, incoming)
                changed = True

        if source.negated != target.negated:
            target.negated = source.negated
            changed = True

        if source.measurement:
            for key, value in source.measurement.items():
                if overwrite or target.measurement.get(key) != value:
                    target.measurement[key] = value
                    changed = True

        if source.details:
            for key, value in source.details.items():
                if overwrite or target.details.get(key) != value:
                    target.details[key] = value
                    changed = True

        for field_name in (
            "symptom_data",
            "injury_data",
            "measurement_data",
            "medication_data",
            "diagnosis_data",
        ):
            incoming = getattr(source, field_name)
            if incoming is not None and (overwrite or getattr(target, field_name) != incoming):
                setattr(target, field_name, incoming)
                changed = True

        if source.confidence is not None and (
            target.confidence is None or source.confidence > target.confidence
        ):
            target.confidence = source.confidence

        if source.provenance:
            target.provenance.extend(source.provenance)

        if changed or message_role in {"confirmation", "correction"}:
            target.verification_status = source.verification_status
        return changed


class ConfirmationService:
    def apply(self, case: MedicalCase, update: ConfirmationUpdate) -> MedicalCase:
        for observation in case.observations:
            if observation.id in update.confirmed_observation_ids:
                observation.verification_status = "confirmed"
                observation.provenance.append(
                    Provenance(source="user_confirmation", note="confirmed via API")
                )
            if observation.id in update.rejected_observation_ids:
                observation.verification_status = "rejected"
                observation.provenance.append(
                    Provenance(source="user_correction", note="rejected via API")
                )

        for corrected in update.corrected_observations:
            corrected.verification_status = "corrected"
            corrected.provenance.append(
                Provenance(source="user_correction", note="corrected via API")
            )
            self._replace_or_add(case, corrected)

        for added in update.added_observations:
            added.verification_status = "confirmed"
            added.provenance.append(
                Provenance(source="user_confirmation", note="added via API")
            )
            case.observations.append(added)

        if update.confirm_subject and case.subject.has_value():
            case.subject.verification_status = "confirmed"
        if update.corrected_subject is not None:
            corrected_subject = update.corrected_subject.model_copy(deep=True)
            corrected_subject.verification_status = "corrected"
            case.subject = corrected_subject

        case.ensure_primary_problem()
        return case

    @staticmethod
    def confirm_pending(case: MedicalCase, state: DialogueState) -> None:
        if state.pending_confirmation_subject and case.subject.has_value():
            case.subject.verification_status = "confirmed"
        for observation in case.observations:
            if observation.id in state.pending_confirmation_observation_ids:
                observation.verification_status = "confirmed"
                observation.provenance.append(
                    Provenance(source="user_confirmation", note="confirmed in chat")
                )
        ConfirmationService.clear_pending(state)

    @staticmethod
    def clear_pending(state: DialogueState) -> None:
        state.awaiting_confirmation = False
        state.pending_confirmation_observation_ids = []
        state.pending_confirmation_subject = False

    @staticmethod
    def _replace_or_add(case: MedicalCase, observation: CaseObservation) -> None:
        for index, existing in enumerate(case.observations):
            if existing.id == observation.id:
                case.observations[index] = observation
                case.ensure_primary_problem()
                return
        case.observations.append(observation)
        case.ensure_primary_problem()
