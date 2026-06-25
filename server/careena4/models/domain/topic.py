from pydantic import Field

from careena4.models.common import PipelineModel
from careena4.models.domain.provenance import Source


class TopicEntry(PipelineModel):
    topic_part: str
    source: Source


class Topic(PipelineModel):
    label: str
    entries: list[TopicEntry] = Field(default_factory=list)
