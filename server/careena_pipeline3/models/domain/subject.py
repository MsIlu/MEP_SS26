from pydantic import Field

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.common.types import SubjectRelation


class Subject(PipelineModel):
    relation: SubjectRelation = "unknown"
    description: str | None = None
    age: int | None = Field(default=None, ge=0, le=130)
    sex: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    confirmed: bool = False
