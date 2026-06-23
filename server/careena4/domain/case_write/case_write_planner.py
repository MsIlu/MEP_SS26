from careena4.domain.case._case_write_planner import _CaseWritePlanner
from careena4.models.domain import MedicalCase
from careena4.models.turn import CaseWritePlan, ExtractionClaims


class CaseWritePlanner:
    """
    Public adapter for building write plans from extracted claims.

    The newer case package owns the implementation; this class keeps the
    existing TurnEngine import stable.
    """

    def __init__(self, planner: _CaseWritePlanner | None = None):
        self._planner = planner or _CaseWritePlanner()

    def build(
        self,
        *,
        medical_case: MedicalCase,
        claims: ExtractionClaims,
        topic_id: str | None,
    ) -> CaseWritePlan:
        return self._planner.build_write_plan(
            existing_observations=medical_case.observations,
            claims=claims,
            topic_id=topic_id,
        )
