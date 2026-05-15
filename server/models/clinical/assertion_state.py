from .base import BaseSchema


class AssertionState(BaseSchema):
    negated: bool = False

    uncertain: bool = False

    hypothetical: bool = False

    reported_by_patient: bool = True