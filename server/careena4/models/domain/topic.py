import re
from uuid import uuid4

from pydantic import Field

from careena4.models.common import (
    CaseTopicType,
    PipelineModel,
    SubjectScope,
    TopicStatus,
)
from careena4.models.domain.case_extension import CaseExtension
from careena4.models.domain.provenance import Source


class TopicEntry(PipelineModel):
    concern: str
    source: Source


class Topic(PipelineModel):
    label: str
    sources: list[Source] = Field(default_factory=list)
    entries: list[TopicEntry] = Field(default_factory=list)


class CaseTopic(PipelineModel):
    topic_id: str = ""
    initial_label: str
    current_label: str
    topic_type: CaseTopicType = "unclear_medical_case"
    subject_scope: SubjectScope = "unclear"
    status: TopicStatus = "tentative"
    confidence: float | None = None
    opened_at_turn: str | None = None
    extensions: list[CaseExtension] = Field(default_factory=list)

    def __init__(self, **data):
        if not data.get("topic_id"):
            data["topic_id"] = str(uuid4())
        if data.get("current_label") in (None, "") and data.get("initial_label"):
            data["current_label"] = data["initial_label"]
        super().__init__(**data)

    def search_tokens(self) -> set[str]:
        values = [self.initial_label, self.current_label, *(extension.value for extension in self.extensions)]
        tokens: set[str] = set()
        for value in values:
            tokens.update(
                token
                for token in re.findall(r"[a-zA-ZaeoeuessÃ¤Ã¶Ã¼Ã„Ã–Ãœ]+", value.casefold())
                if len(token) > 2
            )
        return tokens
