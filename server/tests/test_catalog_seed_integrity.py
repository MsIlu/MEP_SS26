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

def test_sts_1001_uses_lay_observable_primary_safety_criterion() -> None:
    """Ensure STS 1001 does not use GCS as the primary lay-observable safety criterion."""
    links = load_seed(CRITERIA_LINKS_PATH)

    sts_1001_links = [
        item
        for item in links["consultation_reason_criteria_links"]
        if item["consultation_reason_source_id"] == "1001"
    ]

    primary_keys = {
        item["criterion_key"]
        for item in sts_1001_links
        if item["relevance"] == "primary"
    }

    assert "breathing_and_responsiveness_observed" in primary_keys
    assert "glasgow_coma_scale_observer_assisted" not in primary_keys

def test_cardiovascular_respiratory_category_has_primary_criterion_links() -> None:
    """Ensure every cardiovascular/respiratory STS reason has at least one primary criterion link."""
    reasons = load_seed(CONSULTATION_REASONS_PATH)
    links = load_seed(CRITERIA_LINKS_PATH)

    category_reason_ids = {
        item["sts_id"]
        for item in reasons["consultation_reasons"]
        if item["source_category_de"] == "Kardiovaskulaer und respiratorisch"
    }

    reason_ids_with_primary_link = {
        item["consultation_reason_source_id"]
        for item in links["consultation_reason_criteria_links"]
        if item.get("is_active", True) is True and item["relevance"] == "primary"
    }

    missing_reason_ids = sorted(category_reason_ids - reason_ids_with_primary_link)

    assert missing_reason_ids == []

def test_neurology_psychiatry_category_has_primary_criterion_links() -> None:
    """Ensure every neurology/psychiatry STS reason has at least one primary criterion link."""
    links = load_seed(CRITERIA_LINKS_PATH)

    neurology_psychiatry_reason_ids = {
        "1101", "1102", "1103", "1104", "1105",
        "1106", "1107", "1108", "1109", "1110",
        "1111", "1112", "1113", "1114", "1115",
    }

    reason_ids_with_primary_link = {
        item["consultation_reason_source_id"]
        for item in links["consultation_reason_criteria_links"]
        if item.get("is_active", True) is True and item["relevance"] == "primary"
    }

    missing_reason_ids = sorted(neurology_psychiatry_reason_ids - reason_ids_with_primary_link)

    assert missing_reason_ids == []

def test_traumatology_category_has_primary_criterion_links() -> None:
    """Ensure every traumatology STS reason has at least one primary criterion link."""
    reasons = load_seed(CONSULTATION_REASONS_PATH)
    links = load_seed(CRITERIA_LINKS_PATH)

    traumatology_reason_ids = {
        item["sts_id"]
        for item in reasons["consultation_reasons"]
        if item["source_category_de"] == "Traumatologie"
    }

    reason_ids_with_primary_link = {
        item["consultation_reason_source_id"]
        for item in links["consultation_reason_criteria_links"]
        if item.get("is_active", True) is True and item["relevance"] == "primary"
    }

    missing_reason_ids = sorted(traumatology_reason_ids - reason_ids_with_primary_link)

    assert missing_reason_ids == []

def test_gastrointestinal_gynecology_category_has_primary_criterion_links() -> None:
    """Ensure every gastrointestinal/gynecology STS reason has at least one primary criterion link."""
    reasons = load_seed(CONSULTATION_REASONS_PATH)
    links = load_seed(CRITERIA_LINKS_PATH)

    category_reason_ids = {
        item["sts_id"]
        for item in reasons["consultation_reasons"]
        if item["source_category_de"] == "Magen - Darm - Gynaekologie"
    }

    reason_ids_with_primary_link = {
        item["consultation_reason_source_id"]
        for item in links["consultation_reason_criteria_links"]
        if item.get("is_active", True) is True and item["relevance"] == "primary"
    }

    missing_reason_ids = sorted(category_reason_ids - reason_ids_with_primary_link)

    assert missing_reason_ids == []

def test_urology_nephrology_category_has_primary_criterion_links() -> None:
    """Ensure every urology/nephrology STS reason has at least one primary criterion link."""
    reasons = load_seed(CONSULTATION_REASONS_PATH)
    links = load_seed(CRITERIA_LINKS_PATH)

    category_reason_ids = {
        item["sts_id"]
        for item in reasons["consultation_reasons"]
        if item["source_category_de"] == "Urologie - Nephrologie"
    }

    reason_ids_with_primary_link = {
        item["consultation_reason_source_id"]
        for item in links["consultation_reason_criteria_links"]
        if item.get("is_active", True) is True and item["relevance"] == "primary"
    }

    missing_reason_ids = sorted(category_reason_ids - reason_ids_with_primary_link)

    assert missing_reason_ids == []

def test_infection_symptoms_category_has_primary_criterion_links() -> None:
    """Ensure every infection-symptoms STS reason has at least one primary criterion link."""
    infection_reason_ids = {"1501", "1502", "1503"}
    links = load_seed(CRITERIA_LINKS_PATH)

    reason_ids_with_primary_link = {
        item["consultation_reason_source_id"]
        for item in links["consultation_reason_criteria_links"]
        if item.get("is_active", True) is True and item["relevance"] == "primary"
    }

    missing_reason_ids = sorted(infection_reason_ids - reason_ids_with_primary_link)

    assert missing_reason_ids == []

def test_hno_category_has_primary_criterion_links() -> None:
    """Ensure every HNO STS reason has at least one primary criterion link."""
    reasons = load_seed(CONSULTATION_REASONS_PATH)
    links = load_seed(CRITERIA_LINKS_PATH)

    category_reason_ids = {
        item["sts_id"]
        for item in reasons["consultation_reasons"]
        if item["source_category_de"] == "HNO"
    }

    reason_ids_with_primary_link = {
        item["consultation_reason_source_id"]
        for item in links["consultation_reason_criteria_links"]
        if item.get("is_active", True) is True and item["relevance"] == "primary"
    }

    missing_reason_ids = sorted(category_reason_ids - reason_ids_with_primary_link)

    assert missing_reason_ids == []


def test_dermatology_category_has_primary_criterion_links() -> None:
    """Ensure every dermatology STS reason has at least one primary criterion link."""
    reasons = load_seed(CONSULTATION_REASONS_PATH)
    links = load_seed(CRITERIA_LINKS_PATH)

    category_reason_ids = {
        item["sts_id"]
        for item in reasons["consultation_reasons"]
        if item["source_category_de"] == "Dermatologie"
    }

    reason_ids_with_primary_link = {
        item["consultation_reason_source_id"]
        for item in links["consultation_reason_criteria_links"]
        if item.get("is_active", True) is True and item["relevance"] == "primary"
    }

    missing_reason_ids = sorted(category_reason_ids - reason_ids_with_primary_link)

    assert missing_reason_ids == []


def test_rheumatology_category_has_primary_criterion_links() -> None:
    """Ensure every rheumatology STS reason has at least one primary criterion link."""
    reasons = load_seed(CONSULTATION_REASONS_PATH)
    links = load_seed(CRITERIA_LINKS_PATH)

    category_reason_ids = {
        item["sts_id"]
        for item in reasons["consultation_reasons"]
        if item["source_category_de"] == "Rheumatologie"
    }

    reason_ids_with_primary_link = {
        item["consultation_reason_source_id"]
        for item in links["consultation_reason_criteria_links"]
        if item.get("is_active", True) is True and item["relevance"] == "primary"
    }

    missing_reason_ids = sorted(category_reason_ids - reason_ids_with_primary_link)

    assert missing_reason_ids == []

def test_miscellaneous_consultation_motives_category_has_primary_criterion_links() -> None:
    """Ensure every miscellaneous STS reason has at least one primary criterion link."""
    reasons = load_seed(CONSULTATION_REASONS_PATH)
    links = load_seed(CRITERIA_LINKS_PATH)

    category_reason_ids = {
        item["sts_id"]
        for item in reasons["consultation_reasons"]
        if item["source_category_de"] == "Verschiedene Konsultationsmotive"
    }

    reason_ids_with_primary_link = {
        item["consultation_reason_source_id"]
        for item in links["consultation_reason_criteria_links"]
        if item.get("is_active", True) is True and item["relevance"] == "primary"
    }

    missing_reason_ids = sorted(category_reason_ids - reason_ids_with_primary_link)

    assert missing_reason_ids == []
