from careena4.models.domain import MedicalCase, Observation


class CaseManager:
    """
    Public read boundary for case state used by readiness checks.

    The full write path currently lives in case_write. This lightweight
    manager keeps read access centralized without importing missing internals.
    """

    def has_active_observations(self, *, medical_case: MedicalCase) -> bool:
        return any(not observation.negated for observation in medical_case.observations)

    def central_observations(self, *, medical_case: MedicalCase) -> list[Observation]:
        return [
            observation
            for observation in medical_case.observations
            if not observation.negated and observation.topic_relation == "central"
        ]


__all__ = ["CaseManager"]
