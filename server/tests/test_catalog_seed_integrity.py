from __future__ import annotations

import json
from pathlib import Path


SEED_DIR = Path(__file__).resolve().parents[1] / "database" / "seeds" / "catalog" / "v1"

CONSULTATION_REASONS_PATH = SEED_DIR / "sts_consultation_reasons.seed.json"
ASSESSMENT_CRITERIA_PATH = SEED_DIR / "assessment_criteria.seed.json"
CRITERIA_LINKS_PATH = SEED_DIR / "sts_consultation_reason_criteria_links.seed.json"


def load_seed(path: Path) -> dict:
    """Load a JSON seed file and tolerate UTF-8 BOM for local editor compatibility."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_assessment_criteria_seed_uses_current_input_model_fields() -> None:
    """Ensure assessment criteria use the current value/input model, not the old answer type field."""
    data = load_seed(ASSESSMENT_CRITERIA_PATH)

    for criterion in data["assessment_criteria"]:
        assert "expected_answer_type" not in criterion
        assert "expected_value_type" in criterion
        assert "suggested_input_mode" in criterion
        assert "free_text_allowed" in criterion

        assert isinstance(criterion["free_text_allowed"], bool)
        assert criterion["expected_value_type"]
        assert criterion["suggested_input_mode"]


def test_assessment_criteria_keys_are_unique() -> None:
    """Ensure reusable assessment criteria can be referenced by a stable unique key."""
    data = load_seed(ASSESSMENT_CRITERIA_PATH)

    keys = [item["criterion_key"] for item in data["assessment_criteria"]]

    assert len(keys) == len(set(keys))


def test_consultation_reason_source_ids_are_unique() -> None:
    """Ensure STS consultation reasons can be referenced by a stable unique source id."""
    data = load_seed(CONSULTATION_REASONS_PATH)

    source_ids = [item["sts_id"] for item in data["consultation_reasons"]]

    assert len(source_ids) == len(set(source_ids))


def test_consultation_reason_criteria_links_reference_existing_seed_items() -> None:
    """Ensure every reason/criterion link references existing seed entries."""
    reasons = load_seed(CONSULTATION_REASONS_PATH)
    criteria = load_seed(ASSESSMENT_CRITERIA_PATH)
    links = load_seed(CRITERIA_LINKS_PATH)

    reason_ids = {item["sts_id"] for item in reasons["consultation_reasons"]}
    criterion_keys = {item["criterion_key"] for item in criteria["assessment_criteria"]}

    missing_reason_ids = []
    missing_criterion_keys = []

    for link in links["consultation_reason_criteria_links"]:
        if link["consultation_reason_source_id"] not in reason_ids:
            missing_reason_ids.append(link["consultation_reason_source_id"])

        if link["criterion_key"] not in criterion_keys:
            missing_criterion_keys.append(link["criterion_key"])

    assert missing_reason_ids == []
    assert missing_criterion_keys == []


def test_consultation_reason_criteria_links_are_unique() -> None:
    """Ensure the same STS reason is not linked to the same criterion more than once."""
    links = load_seed(CRITERIA_LINKS_PATH)

    pairs = [
        (item["consultation_reason_source_id"], item["criterion_key"])
        for item in links["consultation_reason_criteria_links"]
    ]

    assert len(pairs) == len(set(pairs))


def test_user_provided_measurements_use_measurement_value_type() -> None:
    """Ensure user-provided device values are modeled as measurements, not free text."""
    criteria = load_seed(ASSESSMENT_CRITERIA_PATH)

    measurement_keys = {
        "blood_pressure_user_provided",
        "oxygen_saturation_user_provided",
    }

    criteria_by_key = {
        item["criterion_key"]: item
        for item in criteria["assessment_criteria"]
    }

    for key in measurement_keys:
        criterion = criteria_by_key[key]

        assert criterion["expected_value_type"] == "measurement"
        assert criterion["suggested_input_mode"] == "measurement_input"
        assert criterion["free_text_allowed"] is True
