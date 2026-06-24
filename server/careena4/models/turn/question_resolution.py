from pydantic import Field

from careena4.models.common import PipelineModel, SubjectScope
from careena4.models.domain import Source
from careena4.models.turn.extraction_claims import ExtractedCaseInput


class PersonUpdate(PipelineModel):
    relation: SubjectScope
    relation_source: Source | None = None


class ObservationPatch(PipelineModel):
    onset: str | None = None
    onset_source: Source | None = None
    body_site: str | None = None
    body_site_source: Source | None = None
    description: str | None = None
    description_source: Source | None = None
    severity: int | str | None = None
    severity_source: Source | None = None
    mechanism: str | None = None
    mechanism_source: Source | None = None
    functional_limitation: str | None = None
    functional_limitation_source: Source | None = None
    measurement_kind: str | None = None
    measurement_kind_source: Source | None = None

    def has_values(self) -> bool:
        return any(
            value not in (None, "", [])
            for value in (
                self.onset,
                self.body_site,
                self.description,
                self.severity,
                self.mechanism,
                self.functional_limitation,
                self.measurement_kind,
            )
        )

    def field_keys(self) -> list[str]:
        return [
            field_name
            for field_name, value in (
                ("onset", self.onset),
                ("body_site", self.body_site),
                ("description", self.description),
                ("severity", self.severity),
                ("mechanism", self.mechanism),
                ("functional_limitation", self.functional_limitation),
                ("measurement_kind", self.measurement_kind),
            )
            if value not in (None, "", [])
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
    recommendation_choice: str | None = None
    next_question_text: str | None = None
    trace_notes: list[str] = Field(default_factory=list)
