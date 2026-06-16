from careena4.models.common import PipelineModel, SubjectScope


class Subject(PipelineModel):
    relation: SubjectScope = "unclear"
    age: int | None = None
    sex: str = "unknown"
