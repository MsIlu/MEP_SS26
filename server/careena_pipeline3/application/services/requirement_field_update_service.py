from __future__ import annotations

from careena_pipeline3.models.domain import MedicalCase
from careena_pipeline3.models.turn import RequirementFieldUpdate


class RequirementFieldUpdateService:
    """Applies one resolved requirement field update directly to canonical truth."""

    def apply(
        self,
        *,
        medical_case: MedicalCase | None,
        update: RequirementFieldUpdate,
    ) -> tuple[MedicalCase, list[str]]:
        case = medical_case or MedicalCase()
        trace_notes = [
            "requirement_field_update:"
            f"{update.requirement_key}:{update.target_kind}"
        ]
        if update.target_kind == "subject":
            self._apply_subject_update(case=case, update=update)
            return case, trace_notes

        target = None
        for observation in case.active_observations(include_negated=True):
            if observation.id == update.target_observation_id:
                target = observation
                break
        if target is None:
            trace_notes.append("requirement_field_update:target_not_found")
            return case, trace_notes

        self._apply_observation_update(target=target, update=update)
        return case, trace_notes

    @staticmethod
    def _apply_subject_update(
        *,
        case: MedicalCase,
        update: RequirementFieldUpdate,
    ) -> None:
        if update.requirement_key == "subject.subject_relation":
            case.subject.relation = str(update.normalized_value)
        elif update.requirement_key == "subject.age":
            value = update.normalized_value
            case.subject.age = int(value) if not isinstance(value, int) else value

    @staticmethod
    def _apply_observation_update(
        *,
        target,
        update: RequirementFieldUpdate,
    ) -> None:
        if update.slot == "duration_or_onset":
            target.set_surface_field("temporality", str(update.normalized_value))
            return
        if update.slot == "severity":
            value = update.normalized_value
            target.set_surface_field("severity", int(value) if isinstance(value, str) and value.isdigit() else value)
            return
        if update.slot == "injury_context":
            target.set_detail_value("injury_context", str(update.normalized_value), overwrite=True)
            return
        if update.slot == "functional_limitation":
            target.set_detail_value(
                "functional_limitation",
                str(update.normalized_value),
                overwrite=True,
            )
