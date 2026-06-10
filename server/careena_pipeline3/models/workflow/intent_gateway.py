from typing import get_args

from pydantic import Field

from careena_pipeline3.models.common import (
    Call2OperationMode,
    Call2Task,
    IntentCategory,
    MessageRole,
    PipelineModel,
)


_ALLOWED_CALL2_TASKS = set(get_args(Call2Task))
_ALLOWED_CALL2_OPERATION_MODES = set(get_args(Call2OperationMode))


class IntentGateway(PipelineModel):
    """
    Role:
    - Call-1 scout/dispatch contract for the rest of the turn pipeline.

    Input contract:
    - receives only the latest message plus lightweight dialogue/case context
      through the Call-1 extractor.

    Output contract:
    - emits small grouped signal lists for entry, dispatch, case, dialogue,
      and safety boundaries.
    - keeps top-level category and message_role explicit for stable early
      routing and response fallbacks.

    Does not decide:
    - canonical case truth
    - merge/conflict semantics
    - recommendation readiness or final response policy

    Transitional:
    - yes; the grouped signal lists are the new primary contract, while a few
      helper properties keep current downstream consumers stable.
    """

    category: IntentCategory
    message_role: MessageRole
    profile: str = "default"
    entry_signals: list[str] = Field(default_factory=list)
    dispatch_signals: list[str] = Field(default_factory=list)
    case_hints: list[str] = Field(default_factory=list)
    dialogue_hints: list[str] = Field(default_factory=list)
    safety_hints: list[str] = Field(default_factory=list)
    trace_notes: list[str] = Field(default_factory=list)

    @property
    def is_medical(self) -> bool:
        return self.category not in {"smalltalk", "not_medical"}

    @property
    def next_step(self) -> str | None:
        return self._value_from(self.dispatch_signals, "next_step:")

    @property
    def extraction_required(self) -> bool:
        return self.next_step == "extract"

    @property
    def explicit_call2_operation_mode(self) -> Call2OperationMode | None:
        mode = self._value_from(self.dispatch_signals, "operation_mode:")
        if mode not in _ALLOWED_CALL2_OPERATION_MODES:
            return None
        return mode

    @property
    def call2_tasks(self) -> list[Call2Task]:
        tasks: list[Call2Task] = []
        for signal in self.dispatch_signals:
            if not signal.startswith("task:"):
                continue
            task = signal.split(":", 1)[1]
            if task in _ALLOWED_CALL2_TASKS and task not in tasks:
                tasks.append(task)
        return tasks

    @property
    def person_reference_present(self) -> bool:
        return self.has_case_hint("person_context:present")

    @property
    def multi_person_context(self) -> bool:
        return self.has_case_hint("person_context:multi_person")

    @property
    def subject_relation_unclear(self) -> bool:
        return self.has_case_hint("person_context:subject_relation_unclear")

    @property
    def additional_medical_information(self) -> bool:
        return self.has_case_hint("case_hint:followup_answer_contains_additional_info")

    @property
    def recommendation_request(self) -> bool:
        return self.has_dialogue_hint("dialogue_hint:recommendation_requested")

    def has_entry_signal(self, code: str) -> bool:
        return code in self.entry_signals

    def has_case_hint(self, code: str) -> bool:
        return code in self.case_hints

    def has_dialogue_hint(self, code: str) -> bool:
        return code in self.dialogue_hints

    def has_safety_hint(self, code: str) -> bool:
        return code in self.safety_hints

    @staticmethod
    def _value_from(signals: list[str], prefix: str) -> str | None:
        for signal in signals:
            if signal.startswith(prefix):
                return signal.split(":", 1)[1]
        return None
