from careena_pipeline.models import CaseObservation, MedicalCase, MessageUpdate
from careena_pipeline.state.case_merge_policy import CaseMergePolicy


def _pick_text(
    *,
    current: str | None,
    incoming: str | None,
    overwrite: bool,
    ignore_values: set[str] | None = None,
) -> str | None:
    if not incoming:
        return current
    if ignore_values is not None and incoming in ignore_values:
        return current
    if overwrite or not current:
        return incoming
    return current


def _pick_value(
    *,
    current,
    incoming,
    overwrite: bool,
    ignore_values: set | None = None,
):
    if incoming is None:
        return current
    if ignore_values is not None and incoming in ignore_values:
        return current
    if overwrite or current is None:
        return incoming
    return current


class CaseMerger:
    """
    Merges a structured CaseUpdate into an existing MedicalCase.

    This is intentionally conservative: it appends new observations and keeps
    the existing focus unless the case did not have one yet.
    """

    def __init__(
        self,
        *,
        merge_policy: CaseMergePolicy | None = None,
    ):
        self.merge_policy = merge_policy or CaseMergePolicy()

    def merge_update(
        self,
        existing_case: MedicalCase | None,
        update: MessageUpdate,
    ) -> MedicalCase:
        if existing_case is None:
            existing_case = MedicalCase()

        intent_signals = update.intent_signals
        case_payload = update.case_payload
        merged_any = False
        if case_payload.subject is not None and case_payload.subject.relation != "unknown":
            if (
                existing_case.subject.relation == "unknown"
                or case_payload.subject.confidence >= existing_case.subject.confidence
            ):
                existing_case.subject = case_payload.subject

        for observation in case_payload.observations_added:
            target = self.merge_policy.merge_target(
                case=existing_case,
                update=update,
                observation=observation,
            )
            if target is not None:
                self._merge_observation(
                    target,
                    observation,
                    message_role=intent_signals.message_role,
                )
                merged_any = True
                continue
            if self.merge_policy.already_present(
                case=existing_case,
                observation=observation,
            ):
                continue
            observation.status = self._status_for_new_observation(
                intent_signals.message_role,
                default=observation.status,
            )
            self._append(existing_case, observation)
            merged_any = True

        for observation in case_payload.negated_observations_added:
            target = self.merge_policy.merge_target(
                case=existing_case,
                update=update,
                observation=observation,
            )
            if target is not None:
                self._merge_observation(
                    target,
                    observation,
                    message_role=intent_signals.message_role,
                )
                merged_any = True
                continue
            if self.merge_policy.already_present(
                case=existing_case,
                observation=observation,
            ):
                continue
            observation.status = self._status_for_new_observation(
                intent_signals.message_role,
                default=observation.status,
            )
            existing_case.observations.append(observation)
            merged_any = True

        self._apply_message_role(existing_case, intent_signals.message_role, merged_any=merged_any)

        if intent_signals.possible_new_topic:
            primary = self.merge_policy.latest_focus_candidate(
                case=existing_case,
                update=update,
            )
            if primary is not None:
                existing_case.set_primary_observation(primary)
        elif existing_case.primary_problem_id is None:
            existing_case.ensure_primary_problem()

        return existing_case

    @staticmethod
    def _append(case: MedicalCase, observation: CaseObservation) -> None:
        case.observations.append(observation)

    @staticmethod
    def _merge_observation(
        target: CaseObservation,
        source: CaseObservation,
        *,
        message_role: str,
    ) -> None:
        overwrite = message_role == "correction"
        target.display_label = _pick_text(
            current=target.display_label,
            incoming=source.display_label,
            overwrite=overwrite,
        )
        target.concept = _pick_text(
            current=target.concept,
            incoming=source.concept,
            overwrite=overwrite,
        )
        temporality = _pick_text(
            current=target.runtime_value("temporality"),
            incoming=source.runtime_value("temporality"),
            overwrite=overwrite,
        )
        if temporality != target.temporality:
            target.set_surface_field("temporality", temporality)

        severity = _pick_value(
            current=target.runtime_value("severity"),
            incoming=source.runtime_value("severity"),
            overwrite=overwrite,
        )
        if severity != target.severity:
            target.set_surface_field("severity", severity)

        body_site = _pick_text(
            current=target.runtime_value("body_site"),
            incoming=source.runtime_value("body_site"),
            overwrite=overwrite,
        )
        if body_site != target.body_site:
            target.set_surface_field("body_site", body_site)

        target.laterality = _pick_value(
            current=target.laterality,
            incoming=source.laterality,
            overwrite=overwrite,
            ignore_values={"unknown"},
        )
        course = _pick_value(
            current=target.runtime_value("course"),
            incoming=source.runtime_value("course"),
            overwrite=overwrite,
            ignore_values={"unknown"},
        )
        if course != target.course:
            target.set_surface_field("course", course)

        if source.measurement:
            target.merge_measurement_values(source.measurement, overwrite=overwrite)
        if source.details:
            target.merge_detail_values(source.details, overwrite=overwrite)
        target.subject_ref = _pick_text(
            current=target.subject_ref,
            incoming=source.subject_ref,
            overwrite=overwrite,
            ignore_values={"unknown"},
        )
        if overwrite and source.source_span:
            target.source_span = source.source_span
        if overwrite:
            if source.negated:
                target.negated = True
            if source.certainty != "confirmed":
                target.certainty = source.certainty
        if source.provenance:
            target.provenance.extend(source.provenance)
        if source.confidence is not None and (
            target.confidence is None or source.confidence > target.confidence
        ):
            target.confidence = source.confidence
        if message_role == "confirmation":
            target.status = "user_confirmed"
        elif message_role == "correction":
            target.status = "user_corrected"

    @staticmethod
    def _status_for_new_observation(message_role: str, *, default: str) -> str:
        if message_role == "confirmation":
            return "user_confirmed"
        if message_role == "correction":
            return "user_corrected"
        return default

    @staticmethod
    def _apply_message_role(
        case: MedicalCase,
        message_role: str,
        *,
        merged_any: bool,
    ) -> None:
        primary = case.primary_observation()
        if primary is None:
            return
        if message_role == "confirmation" and not merged_any:
            primary.status = "user_confirmed"
