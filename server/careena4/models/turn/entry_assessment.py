from careena4.models.common import EntryMessageKind, MedicalRelevance, PipelineModel


class EntryAssessment(PipelineModel):
    in_scope: bool
    medical_relevance: MedicalRelevance
    answers_active_question: bool = False
    contains_new_medical_information: bool = False
    message_kind: EntryMessageKind
