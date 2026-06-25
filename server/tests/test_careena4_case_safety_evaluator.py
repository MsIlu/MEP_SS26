from unittest.mock import MagicMock

import pytest

from careena4.application.safety import CaseSafetyEvaluator
from careena4.models.domain import MedicalCase, Observation
from careena4.models.domain.safety_catalog import SafetyCatalogMatch
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus


def _make_case(*labels: str) -> MedicalCase:
    case = MedicalCase()
    for label in labels:
        obs = Observation(label=label, type="symptom", status="active")
        case.observations.append(obs)
    return case


def _make_match(criterion_key: str, urgency: str = "requires_safety_clarification") -> SafetyCatalogMatch:
    return SafetyCatalogMatch(
        evidence_term="atemnot",
        matched_lay_term="Atemnot",
        consultation_reason_source_id="1008",
        consultation_reason_key="dyspnea",
        criterion_key=criterion_key,
        criterion_role="primary_criterion",
        urgency_effect=urgency,
        careena_decision_role="safety_relevant",
        is_safety_relevant=True,
        is_red_flag_candidate=True,
    )


class TestCaseSafetyEvaluatorNoCache:
    def test_no_cache_returns_no_flag(self):
        case = _make_case("Atemnot", "Brustschmerzen")
        result = CaseSafetyEvaluator(catalog_cache=None).evaluate(case)
        assert not result.red_flag_detected
        assert result.red_flag_status == SafetyRedFlagStatus.NONE

    def test_empty_case_returns_no_flag(self):
        result = CaseSafetyEvaluator().evaluate(MedicalCase())
        assert not result.red_flag_detected

    def test_all_negated_returns_no_flag(self):
        case = MedicalCase()
        obs = Observation(label="Atemnot", type="symptom", status="negated")
        case.observations.append(obs)
        result = CaseSafetyEvaluator().evaluate(case)
        assert not result.red_flag_detected


class TestCaseSafetyEvaluatorWithCache:
    def _mock_cache(self, matches: list[SafetyCatalogMatch]):
        cache = MagicMock()
        cache.is_loaded = True
        cache.scan_labels.return_value = matches
        return cache

    def test_catalog_match_triggers_suspected(self):
        cache = self._mock_cache([_make_match("dyspnea_01")])
        case = _make_case("Atemnot")
        result = CaseSafetyEvaluator(catalog_cache=cache).evaluate(case)

        assert result.red_flag_detected is True
        assert result.red_flag_status == SafetyRedFlagStatus.SUSPECTED
        assert result.action == SafetyAction.ASK_SAFETY_CLARIFICATION
        assert result.requires_safety_clarification is True

    def test_no_catalog_match_returns_no_flag(self):
        cache = self._mock_cache([])
        case = _make_case("Kopfschmerzen")
        result = CaseSafetyEvaluator(catalog_cache=cache).evaluate(case)

        assert not result.red_flag_detected
        assert result.red_flag_status == SafetyRedFlagStatus.NONE

    def test_negated_observation_excluded(self):
        cache = self._mock_cache([_make_match("dyspnea_01")])
        case = MedicalCase()
        obs = Observation(label="Atemnot", type="symptom", status="negated")
        case.observations.append(obs)
        result = CaseSafetyEvaluator(catalog_cache=cache).evaluate(case)

        # negated → no active labels → evaluator returns early, cache never consulted
        cache.scan_labels.assert_not_called()
        assert not result.red_flag_detected

    def test_evidence_terms_populated(self):
        match = _make_match("dyspnea_01")
        cache = self._mock_cache([match])
        case = _make_case("Atemnot")
        result = CaseSafetyEvaluator(catalog_cache=cache).evaluate(case)

        assert len(result.evidence_terms) > 0

    def test_high_urgency_match_triggers_suspected(self):
        match = _make_match("dyspnea_01", urgency="confirms_emergency")
        cache = self._mock_cache([match])
        case = _make_case("Atemnot")
        result = CaseSafetyEvaluator(catalog_cache=cache).evaluate(case)

        assert result.red_flag_detected is True
        assert result.red_flag_status == SafetyRedFlagStatus.SUSPECTED


class TestCaseSafetyEvaluatorMedGemma:
    def _mock_cache_no_match(self):
        cache = MagicMock()
        cache.is_loaded = True
        cache.scan_labels.return_value = []
        return cache

    def test_medgemma_not_called_without_catalog_signal(self):
        llm_client = MagicMock()
        cache = self._mock_cache_no_match()
        case = _make_case("Atemnot")

        CaseSafetyEvaluator(catalog_cache=cache, llm_client=llm_client).evaluate(case)

        llm_client.complete.assert_not_called()
