from pydantic import Field

from careena4.models.common import PipelineModel, SubjectScope
from careena4.models.domain import Source
from careena4.models.turn.extraction_claims import ExtractedCaseInput


class PersonUpdate(PipelineModel):
    relation: SubjectScope | None = None
    relation_source: Source | None = None
    age: int | None = None
    age_source: Source | None = None
    sex: str | None = None
    sex_source: Source | None = None


class ObservationPatch(PipelineModel):
    person_ref: SubjectScope | None = None
    person_ref_source: Source | None = None
    onset: str | None = None
    onset_source: Source | None = None
    body_site: str | None = None
    body_site_source: Source | None = None
    description: str | None = None
    description_source: Source | None = None
    severity: int | str | None = None
    severity_source: Source | None = None

    def has_values(self) -> bool:
        return any(
            value not in (None, "", [], "unclear")
            for value in (
                self.person_ref,
                self.onset,
                self.body_site,
                self.description,
                self.severity,
            )
        )

    def field_keys(self) -> list[str]:
        return [
            field_name
            for field_name, value in (
                ("person_ref", self.person_ref),
                ("onset", self.onset),
                ("body_site", self.body_site),
                ("description", self.description),
                ("severity", self.severity),
            )
            if value not in (None, "", [], "unclear")
        ]


class QuestionResolution(PipelineModel):
    status: str
    answer_kind: str | None = None
    clear_active_question: bool = False
    resolved_followup_id: str | None = None
    person_update: PersonUpdate | None = None
    observation_patch: ObservationPatch | None = None
    additional_medical_information: bool = False
    extra_case_input: ExtractedCaseInput | None = None
    next_question_text: str | None = None
    trace_notes: list[str] = Field(default_factory=list)
