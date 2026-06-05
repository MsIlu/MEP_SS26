from careena_pipeline.models import CaseObservation, MedicalCase, MessageUpdate


class RequirementCaseProjector:
    """
    Transitional bridge that projects requirement-style process signals into the
    case.

    This component is intentionally *not* part of the canonical merge truth.
    It exists as a compatibility layer for follow-up answers whose requirement
    state is already known, but whose content is not yet stably represented as a
    proper case delta.
    """

    TRANSITIONAL_COMPONENT = True
    TRUST_LEVEL = "distrust"

    def apply(
        self,
        case: MedicalCase,
        update: MessageUpdate,
    ) -> bool:
        # Compatibility entry point kept for older call sites.
        return self.project_transitional_signals(case, update)

    def project_transitional_signals(
        self,
        case: MedicalCase,
        update: MessageUpdate,
    ) -> None:
        requirement_hints = update.requirement_hints
        case_payload = update.case_payload
        intent_signals = update.intent_signals

        if not self._should_project(
            case_payload=case_payload,
            requirement_hints=requirement_hints,
            intent_signals=intent_signals,
        ):
            return False

        resolved_keys = {item.key for item in requirement_hints.resolved_fields}
        sources = case_payload.all_observations
        overwrite = intent_signals.message_role == "correction"
        projected_any = False
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
                projected_any = True
                # For now only enrich one intended target per module to avoid
                # spraying a follow-up answer across multiple observations.
                break
        return projected_any

    @staticmethod
    def _should_project(
        *,
        case_payload,
        requirement_hints,
        intent_signals,
    ) -> bool:
        if not requirement_hints.resolved_fields:
            return False

        # Once a message already produced an explicit case delta, the canonical
        # merge path should stay authoritative and this compatibility bridge
        # should not mutate the case a second time.
        if case_payload.has_updates:
            return False

        # Restrict projection to the narrow transition paths it was introduced
        # for instead of treating every resolved requirement as a reason to
        # write back into case truth.
        return intent_signals.message_role in {"answer_to_followup", "correction"}

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
                target.set_surface_field("temporality", value)
        if f"{module}.severity" in resolved_keys:
            value = cls._first_value(sources, "severity")
            if value is not None and (overwrite or target.severity is None):
                target.set_surface_field("severity", value)
        if f"{module}.body_site" in resolved_keys:
            value = cls._first_value(sources, "body_site")
            if value and (overwrite or not target.body_site):
                target.set_surface_field("body_site", value)
        if f"{module}.course" in resolved_keys:
            value = cls._first_value(sources, "course")
            if value and (overwrite or target.course is None):
                target.set_surface_field("course", value)
        if module == "injury" and "injury.injury_context" in resolved_keys:
            value = cls._first_detail(sources, "context") or fallback_text
            if value and (overwrite or "context" not in target.details):
                target.set_detail_value("context", value, overwrite=overwrite)
        if module == "injury" and "injury.functional_limitation" in resolved_keys:
            value = cls._first_detail(sources, "functional_limitation")
            if value and (
                overwrite or "functional_limitation" not in target.details
            ):
                target.set_detail_value(
                    "functional_limitation",
                    value,
                    overwrite=overwrite,
                )

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
