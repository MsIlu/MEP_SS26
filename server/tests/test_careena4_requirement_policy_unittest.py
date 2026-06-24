import unittest

from careena4.application.dialogue.question_resolver import QuestionResolver
from careena4.domain.quality.followup_need_builder import FollowupNeedBuilder
from careena4.models.domain import ActiveQuestion, MedicalCase, Observation


class RequirementPolicyTests(unittest.TestCase):
    def test_followup_needs_follow_required_order(self):
        builder = FollowupNeedBuilder()
        medical_case = MedicalCase(
            observations=[
                Observation(
                    type="symptom",
                    label="Bauchschmerzen",
                )
            ]
        )

        needs = builder.build(case_topic=None, medical_case=medical_case)

        self.assertEqual(
            [need.reason for need in needs],
            [
                "subject_unclear",
                "person_ref_missing",
                "duration_missing",
                "severity_missing",
                "description_missing",
            ],
        )

    def test_observation_person_ref_need_starts_after_case_person_is_known(self):
        builder = FollowupNeedBuilder()
        medical_case = MedicalCase(
            observations=[
                Observation(
                    type="symptom",
                    label="Bauchschmerzen",
                )
            ]
        )
        medical_case.person.relation = "self"

        needs = builder.build(case_topic=None, medical_case=medical_case)

        self.assertEqual(needs[0].reason, "person_ref_missing")

    def test_subject_clarification_can_patch_observation_person_ref(self):
        resolver = QuestionResolver()
        question = ActiveQuestion(
            kind="subject_clarification",
            question_intent="subject_clarification",
            target_followup_id="followup-1",
            target_observation_id="obs-1",
            prompt_text="Betrifft das Sie selbst, Ihr Kind oder eine andere Person?",
            blocking=True,
        )

        result = resolver.resolve(question=question, message="Mein Kind.")

        self.assertEqual(result.status, "resolved")
        self.assertIsNone(result.person_update)
        assert result.observation_patch is not None
        self.assertEqual(result.observation_patch.person_ref, "child")


if __name__ == "__main__":
    unittest.main()
