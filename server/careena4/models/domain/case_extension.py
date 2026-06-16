from careena4.models.common import CaseExtensionKind, CaseExtensionSource, PipelineModel


class CaseExtension(PipelineModel):
    kind: CaseExtensionKind
    value: str
    source: CaseExtensionSource
    confidence: float | None = None
    related_observation_id: str | None = None
