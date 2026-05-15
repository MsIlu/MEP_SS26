from .base import BaseSchema


class TemporalState(BaseSchema):
    onset: str | None = None

    duration: str | None = None

    progression: str | None = None

    episodic: bool = True

    resolved: bool = False