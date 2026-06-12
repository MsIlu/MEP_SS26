from __future__ import annotations

from careena_pipeline3.models.domain import ConcernState, MedicalCase


class ConcernStateService:
    """
    Role:
    - owns the small concern-layer continuity contract for a turn.

    Input contract:
    - existing concern state plus optional canonical medical case truth

    Output contract:
    - returns a concern state that is at least initialized and whose
      observation links still point at currently active case observations

    Does not decide:
    - recommendation readiness
    - response policy
    - medical case truth
    - concern summary inference

    Transitional:
    - yes; this service currently normalizes and preserves state without
      pretending the full concern semantics are already modeled
    """

    def ensure_state(
        self,
        concern_state: ConcernState | None,
    ) -> ConcernState:
        return concern_state if concern_state is not None else ConcernState()

    def sync_after_case_update(
        self,
        *,
        concern_state: ConcernState,
        medical_case: MedicalCase | None,
    ) -> tuple[ConcernState, list[str]]:
        if medical_case is None or not concern_state.linked_observation_ids:
            return concern_state, []

        valid_ids = {
            observation.id for observation in medical_case.active_observations()
        }
        filtered_ids = [
            observation_id
            for observation_id in concern_state.linked_observation_ids
            if observation_id in valid_ids
        ]
        if filtered_ids == concern_state.linked_observation_ids:
            return concern_state, []

        concern_state.linked_observation_ids = filtered_ids
        return concern_state, ["concern_state:pruned_missing_observation_links"]
