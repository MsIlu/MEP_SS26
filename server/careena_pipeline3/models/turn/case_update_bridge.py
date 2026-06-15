from pydantic import Field

from careena_pipeline3.models.common import MessageRole, PipelineModel
from careena_pipeline3.models.domain import CaseObservation, Subject
from careena_pipeline3.models.extraction import Call2CaseExtensionStatus


class CaseUpdateClaims(PipelineModel):
    subject: Subject | None = None
    case_frame_label: str | None = None
    observations_added: list[CaseObservation] = Field(default_factory=list)
    negated_observations_added: list[CaseObservation] = Field(default_factory=list)

    @property
    def all_observations(self) -> list[CaseObservation]:
        return self.observations_added + self.negated_observations_added

    @property
    def has_updates(self) -> bool:
        return (
            self.subject is not None
            or self.case_frame_label is not None
            or bool(self.all_observations)
        )


class CaseUpdateMergeHints(PipelineModel):
    message_role: MessageRole = "new_information"
    possible_new_topic: bool = False
    case_extension_status: Call2CaseExtensionStatus = "mixed_update_and_new"


class CaseUpdateBridge(PipelineModel):
    """
    Transitional truth-edge contract between extraction and case mutation.

    The bridge is intentionally limited to canonicalizable case claims plus
    the small merge hints that current identity and update policy still need.
    It is not meant to carry broader planner, requirement, trace, or process
    signals.
    """

    claims: CaseUpdateClaims = Field(default_factory=CaseUpdateClaims)
    merge_hints: CaseUpdateMergeHints = Field(default_factory=CaseUpdateMergeHints)
