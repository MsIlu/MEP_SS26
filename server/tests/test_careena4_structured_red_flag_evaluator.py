from careena4.application.safety import StructuredRedFlagEvaluator
from careena4.models.safety import CurrentTurnSafetyEvidence, SymptomSafetyEvidence
from careena4.models.turn import SafetyAction, SafetyRedFlagStatus
from careena4.models.understanding import CurrentTurnUnderstanding, ExtractedSymptomCandidate


def test_structured_dyspnea_text_needs_safety_clarification():
    evidence = CurrentTurnSafetyEvidence(
        symptom_evidence=[
            SymptomSafetyEvidence(
                source_label="Atemnot",
                clinical_term_de="Dyspnoe",
                snomed_code="267036007",
                mapping_confidence=0.94,
                validation_status="candidate",
            )
        ]
    )

    result = StructuredRedFlagEvaluator().evaluate(evidence)

    assert result.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert result.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert result.requires_safety_clarification is True
    assert result.requires_emergency_response is False
    assert "1008" in result.consultation_reason_source_ids
    assert result.matched_snomed_codes == []
    assert "structured_suspected_dyspnea" in result.matched_rule_ids


def test_structured_critical_dyspnea_text_confirms_emergency():
    evidence = CurrentTurnSafetyEvidence(
        raw_message="Ich bekomme keine Luft.",
        symptom_evidence=[
            SymptomSafetyEvidence(
                source_label="Atemnot",
                clinical_term_de="Dyspnoe",
                snomed_code="267036007",
                mapping_confidence=0.94,
                validation_status="candidate",
            )
        ],
    )

    result = StructuredRedFlagEvaluator().evaluate(evidence)

    assert result.red_flag_status == SafetyRedFlagStatus.CONFIRMED
    assert result.action == SafetyAction.EMERGENCY
    assert result.requires_emergency_response is True
    assert result.requires_safety_clarification is False
    assert "1008" in result.consultation_reason_source_ids
    assert result.matched_snomed_codes == []
    assert "structured_critical_dyspnea" in result.matched_rule_ids


def test_structured_chest_pain_text_needs_safety_clarification():
    evidence = CurrentTurnSafetyEvidence(
        symptom_evidence=[
            SymptomSafetyEvidence(
                source_label="Brustschmerzen",
                clinical_term_de="Thoraxschmerzen",
                snomed_code="29857009",
                mapping_confidence=0.93,
                validation_status="candidate",
            )
        ]
    )

    result = StructuredRedFlagEvaluator().evaluate(evidence)

    assert result.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert result.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert result.requires_safety_clarification is True
    assert "1002" in result.consultation_reason_source_ids
    assert result.matched_snomed_codes == []
    assert "structured_suspected_chest_pain" in result.matched_rule_ids


def test_structured_ignores_snomed_code_without_matching_text_signal():
    evidence = CurrentTurnSafetyEvidence(
        symptom_evidence=[
            SymptomSafetyEvidence(
                source_label="Schwindel",
                clinical_term_de="Schwindel",
                snomed_code="267036007",
                mapping_confidence=0.92,
                validation_status="candidate",
            )
        ]
    )

    result = StructuredRedFlagEvaluator().evaluate(evidence)

    assert result.red_flag_status == SafetyRedFlagStatus.NONE
    assert result.action == SafetyAction.NONE
    assert result.red_flag_detected is False
    assert result.requires_emergency_response is False
    assert result.requires_safety_clarification is False
    assert result.matched_snomed_codes == []
    assert result.trace_notes == ["structured_red_flag:none"]


def test_structured_non_safety_symptom_returns_none():
    evidence = CurrentTurnSafetyEvidence(
        symptom_evidence=[
            SymptomSafetyEvidence(
                source_label="Schwindel",
                clinical_term_de="Schwindel",
                snomed_code="404640003",
                mapping_confidence=0.92,
                validation_status="candidate",
            )
        ]
    )

    result = StructuredRedFlagEvaluator().evaluate(evidence)

    assert result.red_flag_status == SafetyRedFlagStatus.NONE
    assert result.action == SafetyAction.NONE
    assert result.red_flag_detected is False
    assert result.requires_emergency_response is False
    assert result.requires_safety_clarification is False
    assert result.trace_notes == ["structured_red_flag:none"]


def test_structured_result_converts_to_existing_safety_state_contract():
    evidence = CurrentTurnSafetyEvidence(
        symptom_evidence=[
            SymptomSafetyEvidence(
                source_label="Atemnot",
                clinical_term_de="Dyspnoe",
                snomed_code="267036007",
            )
        ]
    )

    result = StructuredRedFlagEvaluator().evaluate(evidence)
    safety_state = result.to_safety_state()

    assert safety_state.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert safety_state.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert safety_state.requires_safety_clarification is True
    assert "structured_red_flag:suspected_needs_clarification" in safety_state.trace_notes


def test_safety_evidence_from_turn_understanding_maps_dyspnea():
    understanding = CurrentTurnUnderstanding(
        raw_message="Ich kann nicht atme",
        symptoms=[
            ExtractedSymptomCandidate(
                source_label="Ich kann nicht atme",
                normalized_label_de="Atemnot",
                clinical_term_de="Dyspnoe",
                confidence=0.95,
            )
        ],
    )

    evidence = CurrentTurnSafetyEvidence.from_turn_understanding(
        raw_message=understanding.raw_message,
        understanding=understanding,
    )

    assert len(evidence.symptom_evidence) == 1
    assert "atemnot" in evidence.searchable_text()
    assert "dyspnoe" in evidence.searchable_text()

    result = StructuredRedFlagEvaluator().evaluate(evidence=evidence)

    assert result.red_flag_status == SafetyRedFlagStatus.SUSPECTED
    assert result.action == SafetyAction.ASK_SAFETY_CLARIFICATION
    assert result.matched_snomed_codes == []
    assert "structured_suspected_dyspnea" in result.matched_rule_ids