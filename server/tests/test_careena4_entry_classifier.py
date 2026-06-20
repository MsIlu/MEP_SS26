from careena4.application.entry.entry_classifier import EntryClassifier
from careena4.models.domain import ActiveQuestion
from careena4.models.turn import EntryAssessment


def _duration_question() -> ActiveQuestion:
    return ActiveQuestion(
        kind="followup",
        question_intent="duration",
        prompt_text="Seit wann bestehen die Beschwerden?",
    )


def test_active_followup_answer_stays_in_scope_without_medical_hint():
    assessment = EntryClassifier().classify(
        message="seit gestern",
        active_question=_duration_question(),
    )

    assert assessment.in_scope is True
    assert assessment.answers_active_question is True
    assert assessment.message_kind == "question_answer"
    assert assessment.medical_relevance == "medical"


def test_active_followup_answer_stays_in_scope_even_with_out_of_scope_hint():
    assessment = EntryClassifier().classify(
        message="seit gestern im Urlaub",
        active_question=_duration_question(),
    )

    assert assessment.in_scope is True
    assert assessment.answers_active_question is True
    assert assessment.message_kind == "question_answer"


def test_out_of_scope_without_active_question_stays_out_of_scope():
    assessment = EntryClassifier().classify(
        message="Wie wird das Wetter morgen?",
        active_question=None,
    )

    assert assessment.in_scope is False
    assert assessment.answers_active_question is False
    assert assessment.message_kind == "out_of_scope"
    assert assessment.medical_relevance == "non_medical"


class _OutOfScopeEntryEngine:
    def extract(self, **kwargs):
        return EntryAssessment(
            in_scope=False,
            medical_relevance="non_medical",
            answers_active_question=False,
            contains_new_medical_information=False,
            possible_topic_shift=True,
            message_kind="out_of_scope",
        )


def test_llm_entry_result_cannot_outscope_open_followup_question():
    assessment = EntryClassifier(
        extraction_engine=_OutOfScopeEntryEngine(),
    ).classify(
        message="seit gestern",
        active_question=_duration_question(),
    )

    assert assessment.in_scope is True
    assert assessment.answers_active_question is True
    assert assessment.message_kind == "question_answer"
    assert assessment.medical_relevance == "medical"
    assert assessment.possible_topic_shift is False
