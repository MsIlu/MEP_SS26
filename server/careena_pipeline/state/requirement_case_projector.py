from careena_pipeline.models import CaseObservation, MedicalCase, MessageUpdate


class RequirementCaseProjector:
    """
    Transitional bridge that projects resolved requirement signals into the case.

    This is intentionally separated from `CaseMerger` so requirement-driven
    enrichment is visible as a compatibility path instead of hidden merge
    behavior.
    """

    def apply(
        self,
        case: MedicalCase,
        update: MessageUpdate,
    ) -> None:
        if not update.resolved_fields:
            return

        resolved_keys = {item.key for item in update.resolved_fields}
        sources = update.observations_added + update.negated_observations_added
        overwrite = update.message_role == "correction"
        for module in ("injury", "symptom"):
            if not any(key.startswith(f"{module}.") for key in resolved_keys):
                continue
            for target in self._requirement_targets(case, module=module):
                self._project_fields(
                    target=target,
                    sources=sources,
                    resolved_keys=resolved_keys,
                    module=module,
                    overwrite=overwrite,
                    fallback_text=update.raw_text,
                )
                # For now only enrich one intended target per module to avoid
                # spraying a follow-up answer across multiple observations.
                break

    @classmethod
    def _project_fields(
        cls,
        *,
        target: CaseObservation,
        sources: list[CaseObservation],
        resolved_keys: set[str],
        module: str,
        overwrite: bool,
        fallback_text: str | None,
    ) -> None:
        if f"{module}.duration_or_onset" in resolved_keys:
            value = cls._first_value(sources, "temporality")
            if value and (overwrite or not target.temporality):
                target.temporality = value
        if f"{module}.severity" in resolved_keys:
            value = cls._first_value(sources, "severity")
            if value is not None and (overwrite or target.severity is None):
                target.severity = value
        if f"{module}.body_site" in resolved_keys:
            value = cls._first_value(sources, "body_site")
            if value and (overwrite or not target.body_site):
                target.body_site = value
        if f"{module}.course" in resolved_keys:
            value = cls._first_value(sources, "course")
            if value and (overwrite or target.course is None):
                target.course = value
        if module == "injury" and "injury.injury_context" in resolved_keys:
            value = cls._first_detail(sources, "context") or fallback_text
            if value and (overwrite or "context" not in target.details):
                target.details["context"] = value
        if module == "injury" and "injury.functional_limitation" in resolved_keys:
            value = cls._first_detail(sources, "functional_limitation")
            if value and (
                overwrite or "functional_limitation" not in target.details
            ):
                target.details["functional_limitation"] = value
        target.synchronize_structure()

    @staticmethod
    def _requirement_targets(
        case: MedicalCase,
        *,
        module: str,
    ) -> list[CaseObservation]:
        primary = case.primary_observation()
        if primary is not None and primary.type == module:
            return [primary]

        targets = case.observations_of_type(module, include_negated=True)
        if not targets:
            return []

        primary_focus = case.primary_focus_label()
        if primary_focus:
            focused = [
                observation
                for observation in targets
                if observation.patient_label == primary_focus
            ]
            if focused:
                return focused

        return targets

    @staticmethod
    def _first_value(sources: list[CaseObservation], field: str):
        for source in sources:
            value = getattr(source, field)
            if value is not None:
                return value
        return None

    @staticmethod
    def _first_detail(sources: list[CaseObservation], key: str) -> str | None:
        for source in sources:
            value = source.details.get(key)
            if value:
                return value
        return None
