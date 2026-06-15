from careena_pipeline.models import ConfirmationUpdate, MedicalCase


class ConfirmationService:
    def apply(self, case: MedicalCase, update: ConfirmationUpdate) -> MedicalCase:
        for observation in case.observations:
            if observation.id in update.confirmed_observation_ids:
                observation.status = "user_confirmed"

            if observation.id in update.rejected_observation_ids:
                observation.status = "user_rejected"

        for corrected in update.corrected_observations:
            corrected.status = "user_corrected"
            self._replace_or_add(case, corrected)

        for added in update.added_observations:
            added.status = "user_confirmed"
            self._append(case, added)

        case.ensure_primary_problem()
        return case

    def _replace_or_add(self, case: MedicalCase, observation) -> None:
        for index, existing in enumerate(case.observations):
            if existing.id == observation.id:
                case.observations[index] = observation
                self._rebuild_groups(case)
                return
        self._append(case, observation)

    def _append(self, case: MedicalCase, observation) -> None:
        case.observations.append(observation)
        case.ensure_primary_problem()

    @staticmethod
    def _rebuild_groups(case: MedicalCase) -> None:
        case.ensure_primary_problem()
