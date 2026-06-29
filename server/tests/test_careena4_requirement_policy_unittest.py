import unittest

from careena4.application.dialogue.question_builder import QuestionBuilder
from careena4.application.dialogue.question_resolver import QuestionResolver
from careena4.domain.quality.followup_need_builder import FollowupNeedBuilder
from careena4.models.domain import ActiveQuestion, FollowupNeed, MedicalCase, Observation


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

        needs = builder.build(medical_case=medical_case)

        self.assertEqual(
            [need.reason for need in needs],
            [
                "person_missing",
                "person_ref_missing",
                "duration_missing",
                "severity_missing",
                "description_missing",
            ],
        )

    def test_age_and_sex_needs_start_after_case_person_is_known(self):
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

        needs = builder.build(medical_case=medical_case)

        self.assertEqual([need.reason for need in needs[:3]], ["age_missing", "sex_missing", "person_ref_missing"])

    def test_person_clarification_can_patch_observation_person_ref(self):
        resolver = QuestionResolver()
        question = ActiveQuestion(
            kind="person_clarification",
            question_intent="person_clarification",
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

    def test_person_age_clarification_updates_case_person_age(self):
        resolver = QuestionResolver()
        question = ActiveQuestion(
            kind="person_clarification",
            question_intent="person_age",
            target_followup_id="followup-1",
            prompt_text="Wie alt sind Sie?",
            blocking=True,
        )

        result = resolver.resolve(question=question, message="24")

        self.assertEqual(result.status, "resolved")
        assert result.person_update is not None
        self.assertEqual(result.person_update.age, 24)

    def test_person_sex_clarification_updates_case_person_sex(self):
        resolver = QuestionResolver()
        question = ActiveQuestion(
            kind="person_clarification",
            question_intent="person_sex",
            target_followup_id="followup-1",
            prompt_text="Welches Geschlecht haben Sie?",
            blocking=True,
        )

        result = resolver.resolve(question=question, message="weiblich")

        self.assertEqual(result.status, "resolved")
        assert result.person_update is not None
        self.assertEqual(result.person_update.sex, "female")

    def test_description_question_does_not_infer_body_site_from_observation_label(self):
        builder = QuestionBuilder()

        question = builder.build_for_need(
            need=FollowupNeed(
                observation_id="obs-1",
                reason="description_missing",
                blocking=True,
            ),
            focus_label="Bauchschmerzen",
        )

        self.assertEqual(
            question.prompt_text,
            "Koennen Sie die Bauchschmerzen bitte etwas genauer beschreiben?",
        )
        self.assertNotIn("im Bauch", question.prompt_text)


if __name__ == "__main__":
    unittest.main()
