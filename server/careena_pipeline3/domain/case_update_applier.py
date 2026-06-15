from __future__ import annotations

from careena_pipeline3.models.domain import CaseIssue, CaseObservation, MedicalCase, Subject
from careena_pipeline3.domain.case_update import ObservationUpdateDecision


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


"""
Date: 2026-06-08
Last changed: 2026-06-08
Author: workbench@freddy

Short description:
Applies explicit observation update decisions to the canonical medical case.
It owns the actual mutation step after policy and identity decisions are already made.
"""
class CaseUpdateApplier:
    """Applies explicit update decisions to canonical case truth."""

    def apply_subject_update(
        self,
        *,
        case: MedicalCase,
        subject: Subject | None,
    ) -> None:
        if subject is None or subject.relation == "unknown":
            return
        if case.subject.relation == "unknown" or subject.confidence >= case.subject.confidence:
            case.subject = subject

    @staticmethod
    def apply_case_frame_label(
        *,
        case: MedicalCase,
        case_frame_label: str | None,
    ) -> bool:
        if case.case_frame_label is not None or case_frame_label is None:
            return False
        normalized = case_frame_label.strip()
        if not normalized or not case.problem_observations():
            return False
        case.case_frame_label = normalized
        return True

    def apply_observation_decision(
        self,
        *,
        case: MedicalCase,
        observation: CaseObservation,
        decision: ObservationUpdateDecision,
        message_role: str,
        already_present: bool,
    ) -> bool:
        if (
            decision.action in {
                "enrich_observation",
                "correct_observation",
                "confirm_observation",
            }
            and decision.target is not None
        ):
            self._merge_observation(
                decision.target,
                observation,
                message_role=message_role,
                action=decision.action,
            )
            return True

        if decision.action == "create_observation":
            if already_present:
                return False
            observation.status = self._status_for_new_observation(
                message_role,
                default=observation.status,
            )
            case.observations.append(observation)
            return True

        return False

    def finalize_case(
        self,
        *,
        case: MedicalCase,
        message_role: str,
        merged_any: bool,
    ) -> None:
        primary = case.primary_observation()
        if primary is None:
            return
        if message_role == "confirmation" and not merged_any:
            primary.status = "user_confirmed"

    def apply_non_mutating_decision(
        self,
        *,
        case: MedicalCase,
        observation: CaseObservation,
        decision: ObservationUpdateDecision,
    ) -> None:
        if decision.action == "flag_conflict":
            self._append_case_issue(
                case=case,
                issue=CaseIssue(
                    kind="conflict",
                    focus_observation_id=(
                        decision.target.id if decision.target is not None else None
                    ),
                    incoming_observation_label=observation.patient_label,
                    incoming_observation_type=observation.type,
                    note="case_update_conflict",
                ),
            )
            return

        if decision.action == "defer_update":
            self._append_case_issue(
                case=case,
                issue=CaseIssue(
                    kind="ambiguity",
                    focus_observation_id=(
                        decision.target.id if decision.target is not None else None
                    ),
                    incoming_observation_label=observation.patient_label,
                    incoming_observation_type=observation.type,
                    note="case_update_deferred_ambiguity",
                ),
            )

    @staticmethod
    def _merge_observation(
        target: CaseObservation,
        source: CaseObservation,
        *,
        message_role: str,
        action: str,
    ) -> None:
        overwrite = message_role == "correction" or action == "correct_observation"
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
        elif message_role == "correction" or action == "correct_observation":
            target.status = "user_corrected"

    @staticmethod
    def _status_for_new_observation(message_role: str, *, default: str) -> str:
        if message_role == "confirmation":
            return "user_confirmed"
        if message_role == "correction":
            return "user_corrected"
        return default

    @staticmethod
    def _append_case_issue(
        *,
        case: MedicalCase,
        issue: CaseIssue,
    ) -> None:
        for existing in case.issues:
            if existing.status != "active":
                continue
            if (
                existing.kind == issue.kind
                and existing.focus_observation_id == issue.focus_observation_id
                and existing.incoming_observation_label == issue.incoming_observation_label
                and existing.incoming_observation_type == issue.incoming_observation_type
            ):
                return
        case.issues.append(issue)
