from pydantic import Field

from careena_pipeline3.models.common import PipelineModel


class SafetyCatalogMatch(PipelineModel):
    """Pipeline-facing view of one safety-relevant catalog criterion match."""

    evidence_term: str
    matched_lay_term: str | None = None

    source_system: str = "STS"
    source_version: str | None = None

    consultation_reason_source_id: str
    consultation_reason_key: str | None = None
    consultation_reason_label_de: str | None = None

    criterion_key: str
    criterion_label_de: str | None = None
    criterion_role: str
    urgency_effect: str
    careena_decision_role: str

    suggested_question_text: str | None = None
    suggested_input_mode: str = "free_text"
    free_text_allowed: bool = True

    is_safety_relevant: bool = False
    is_red_flag_candidate: bool = False
    mapping_status: str = "catalog_matched"

    trace_notes: list[str] = Field(default_factory=list)