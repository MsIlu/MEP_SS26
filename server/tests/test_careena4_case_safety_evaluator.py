from unittest.mock import MagicMock

from careena4.application.safety import CaseSafetyEvaluator
from careena4.models.domain import MedicalCase, Observation
from careena4.models.domain.safety_catalog import SafetyCatalogMatch
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus


def _make_case(*labels: str) -> MedicalCase:
    case = MedicalCase()
    for label in labels:
        obs = Observation(normalized_label_de=label, type="symptom", status="active")
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
        result = CaseSafetyEvaluator(catalog_cache=None).evaluate(medical_case=_make_case())
        assert not result.red_flag_detected
        assert result.red_flag_status == SafetyRedFlagStatus.NONE

    def test_empty_case_and_no_understanding_returns_no_flag(self):
        result = CaseSafetyEvaluator().evaluate(medical_case=MedicalCase())
        assert not result.red_flag_detected


class TestCaseSafetyEvaluatorCheck2LayTerms:
    def _mock_cache(self, lay_matches=None, clinical_matches=None):
        cache = MagicMock()
        cache.is_loaded = True
        cache.scan_lay_terms.return_value = lay_matches or []
        cache.scan_clinical_terms.return_value = clinical_matches or []
        return cache

    def test_lay_term_match_triggers_suspected(self):
        cache = self._mock_cache(lay_matches=[_make_match("dyspnea_01")])
        result = CaseSafetyEvaluator(catalog_cache=cache).evaluate(
            medical_case=_make_case("Atemnot")
        )
        assert result.red_flag_detected is True
        assert result.red_flag_status == SafetyRedFlagStatus.SUSPECTED
        assert result.action == SafetyAction.ASK_SAFETY_CLARIFICATION
        assert "check2_lay_terms" in " ".join(result.trace_notes)

    def test_no_lay_match_falls_through_to_check3(self):
        cache = self._mock_cache(lay_matches=[], clinical_matches=[_make_match("dyspnea_01")])
        medical_case = _make_case("Atemnot")
        medical_case.observations[0].clinical_term_de = "Dyspnoe"
        result = CaseSafetyEvaluator(catalog_cache=cache).evaluate(medical_case=medical_case)
        assert result.red_flag_detected is True
        assert "check3_clinical_terms" in " ".join(result.trace_notes)

    def test_no_match_in_either_db_check_returns_no_flag_without_llm(self):
        cache = self._mock_cache(lay_matches=[], clinical_matches=[])
        result = CaseSafetyEvaluator(catalog_cache=cache).evaluate(
            medical_case=_make_case("Kopfschmerzen")
        )
        assert not result.red_flag_detected

    def test_non_safety_urgency_match_ignored(self):
        cache = self._mock_cache(
            lay_matches=[_make_match("some_crit", urgency="supporting_context_only")]
        )
        result = CaseSafetyEvaluator(catalog_cache=cache).evaluate(
            medical_case=_make_case("Atemnot")
        )
        assert not result.red_flag_detected

    def test_empty_case_does_not_scan_lay_terms(self):
        cache = self._mock_cache(lay_matches=[_make_match("dyspnea_01")])
        result = CaseSafetyEvaluator(catalog_cache=cache).evaluate(medical_case=_make_case())
        cache.scan_lay_terms.assert_not_called()
        assert not result.red_flag_detected


class TestCaseSafetyEvaluatorCheck4MedGemma:
    def _mock_cache_no_match(self):
        cache = MagicMock()
        cache.is_loaded = True
        cache.scan_lay_terms.return_value = []
        cache.scan_clinical_terms.return_value = []
        return cache

    def test_medgemma_called_when_db_has_no_match(self):
        llm_client = MagicMock()
        llm_client.complete.return_value = "JA"
        cache = self._mock_cache_no_match()
        result = CaseSafetyEvaluator(catalog_cache=cache, llm_client=llm_client).evaluate(
            medical_case=_make_case("Atemnot"),
        )
        llm_client.complete.assert_called_once()
        assert result.red_flag_detected is True
        assert "check4_medgemma" in " ".join(result.trace_notes)

    def test_medgemma_not_called_without_active_observations(self):
        llm_client = MagicMock()
        cache = self._mock_cache_no_match()
        result = CaseSafetyEvaluator(catalog_cache=cache, llm_client=llm_client).evaluate(
            medical_case=MedicalCase(),
        )
        llm_client.complete.assert_not_called()
        assert not result.red_flag_detected

    def test_medgemma_nein_returns_no_flag(self):
        llm_client = MagicMock()
        llm_client.complete.return_value = "NEIN"
        cache = self._mock_cache_no_match()
        result = CaseSafetyEvaluator(catalog_cache=cache, llm_client=llm_client).evaluate(
            medical_case=_make_case("Kopfschmerzen"),
        )
        assert not result.red_flag_detected
