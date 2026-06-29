from careena4.models.common import PipelineModel, SubjectScope
from careena4.models.domain.source import Source


class Person(PipelineModel):
    relation: SubjectScope = "unclear"
    relation_source: Source | None = None
    age: int | None = None
    age_source: Source | None = None
    sex: str | None = None
    sex_source: Source | None = None
