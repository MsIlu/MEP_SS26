import pytest

from careena4.application.extraction.medical_extractor import MedicalExtractor


@pytest.mark.parametrize(
    ("message", "expected_label"),
    [
        ("Mir ist schlecht.", "Uebelkeit"),
        ("Mir ist \u00fcbel.", "Uebelkeit"),
        ("Mir ist komisch.", "Unwohlsein"),
        ("Ich f\u00fchle mich komisch.", "Unwohlsein"),
        ("Ich f\u00fchle mich schwach.", "Schwaeche"),
    ],
)
def test_lay_symptom_phrases_create_observation_claims(message, expected_label):
    claims = MedicalExtractor().extract(message=message)

    labels = {observation.label for observation in claims.observations}

    assert expected_label in labels
    assert claims.topic_signal == expected_label


def test_lay_symptom_subject_is_self_when_message_uses_first_person():
    claims = MedicalExtractor().extract(message="Mir ist schlecht.")

    observation = claims.observations[0]

    assert observation.subject_ref == "self"
