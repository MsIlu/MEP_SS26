from __future__ import annotations

from careena4.application.topic.topic_label_builder import TopicLabelBuilder
from careena4.domain.case import CaseManager
from careena4.models.domain import MedicalCase
from careena4.models.turn import ExtractedTopicEntryInput


class TopicUpdater:
    def __init__(
        self,
        *,
        case_manager: CaseManager | None = None,
        topic_label_builder: TopicLabelBuilder | None = None,
    ) -> None:
        self.case_manager = case_manager or CaseManager()
        self.topic_label_builder = topic_label_builder or TopicLabelBuilder()

    def apply(
        self,
        *,
        medical_case: MedicalCase,
        topic_entries_to_add: list[ExtractedTopicEntryInput],
    ) -> MedicalCase:
        if not topic_entries_to_add:
            return medical_case
        medical_case = self.case_manager.append_topic_entries(
            medical_case=medical_case,
            entries=topic_entries_to_add,
        )
        label = self.topic_label_builder.build(medical_case=medical_case)
        if label not in (None, ""):
            medical_case = self.case_manager.set_topic_label(
                medical_case=medical_case,
                label=label,
            )
        return medical_case
