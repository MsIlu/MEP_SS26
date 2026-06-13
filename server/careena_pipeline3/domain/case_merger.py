from careena_pipeline3.domain.case_merge_policy import CaseMergePolicy
from careena_pipeline3.domain.case_update_applier import CaseUpdateApplier
from careena_pipeline3.domain.case_update import CaseUpdateOutcome
from careena_pipeline3.models.domain import MedicalCase
from careena_pipeline3.models.turn.case_update_bridge import CaseUpdateBridge


"""
Date: 2026-06-08
Last changed: 2026-06-08
Author: workbench@freddy

Short description:
Coordinates turn-wise case updates from one truth-edge bridge into the canonical medical case.
It orchestrates policy decisions, mutation application, and primary-focus updates.
"""
class CaseMerger:
    """Merges a truth-edge bridge into an existing medical case."""

    def __init__(
        self,
        *,
        merge_policy: CaseMergePolicy | None = None,
        update_applier: CaseUpdateApplier | None = None,
    ):
        self.merge_policy = merge_policy or CaseMergePolicy()
        self.update_applier = update_applier or CaseUpdateApplier()

    def merge_delta(
        self,
        existing_case: MedicalCase | None,
        delta: CaseUpdateBridge,
    ) -> CaseUpdateOutcome:
        if existing_case is None:
            existing_case = MedicalCase()

        merge_hints = delta.merge_hints
        case_payload = delta.claims
        merged_any = False
        trace_notes: list[str] = []
        dialogue_consequences: list[str] = []
        decision_log = []

        self.update_applier.apply_subject_update(
            case=existing_case,
            subject=case_payload.subject,
        )

        trace_notes.append(
            "case_update:case_extension_status:"
            f"{merge_hints.case_extension_status}"
        )

        if merge_hints.case_extension_status == "no_relevant_change":
            self.update_applier.finalize_case(
                case=existing_case,
                message_role=merge_hints.message_role,
                merged_any=merged_any,
            )
            if existing_case.primary_problem_id is None:
                existing_case.ensure_primary_problem()
            trace_notes.append("case_update:skip_observation_write:no_relevant_change")
            return CaseUpdateOutcome(
                medical_case=existing_case,
                trace_notes=trace_notes,
                dialogue_consequences=dialogue_consequences,
                decision_log=decision_log,
            )

        for observation in case_payload.all_observations:
            decision = self.merge_policy.decide_observation_update(
                case=existing_case,
                delta=delta,
                observation=observation,
            )
            decision_log.append(decision)
            trace_notes.extend(decision.notes)
            if decision.dialogue_consequence != "none":
                dialogue_consequences.append(decision.dialogue_consequence)
                trace_notes.append(
                    f"case_update:dialogue_consequence:{decision.dialogue_consequence}"
                )
            already_present = self.merge_policy.already_present(
                case=existing_case,
                observation=observation,
            )
            applied = self.update_applier.apply_observation_decision(
                case=existing_case,
                observation=observation,
                decision=decision,
                message_role=merge_hints.message_role,
                already_present=already_present,
            )
            if not applied:
                self.update_applier.apply_non_mutating_decision(
                    case=existing_case,
                    observation=observation,
                    decision=decision,
                )
            if decision.action == "create_observation" and already_present:
                trace_notes.append("case_update:skip_already_present")
            merged_any = merged_any or applied

        self.update_applier.finalize_case(
            case=existing_case,
            message_role=merge_hints.message_role,
            merged_any=merged_any,
        )

        if merge_hints.possible_new_topic:
            primary = self.merge_policy.latest_focus_candidate(case=existing_case, delta=delta)
            if primary is not None:
                existing_case.set_primary_observation(primary)
        elif existing_case.primary_problem_id is None:
            existing_case.ensure_primary_problem()

        topic_written = self.update_applier.apply_case_frame_label(
            case=existing_case,
            case_frame_label=case_payload.case_frame_label,
        )
        if topic_written:
            trace_notes.append("case_update:set_case_frame_label")
        elif case_payload.case_frame_label is not None and existing_case.case_frame_label is not None:
            trace_notes.append("case_update:skip_case_frame_label:already_set")

        return CaseUpdateOutcome(
            medical_case=existing_case,
            trace_notes=trace_notes,
            dialogue_consequences=dialogue_consequences,
            decision_log=decision_log,
        )
