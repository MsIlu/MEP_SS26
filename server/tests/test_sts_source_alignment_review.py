# Test case references: documents/Testfaelle_Backend.md#t08-katalog-und-sts-seed-integrity

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


SEED_DIR = Path(__file__).resolve().parents[1] / "database" / "seeds" / "catalog" / "v1"

CONSULTATION_REASONS_PATH = SEED_DIR / "sts_consultation_reasons.seed.json"
CRITERIA_LINKS_PATH = SEED_DIR / "sts_consultation_reason_criteria_links.seed.json"
SOURCE_ALIGNMENT_REVIEW_PATH = SEED_DIR / "sts_source_alignment_review.seed.json"

RISK_SAMPLE_TYPES = {
    "high_risk_sample",
    "safety_sensitive_sample",
    "sensitive_sample",
}


def load_seed(path: Path) -> dict:
    """Load a JSON seed file and tolerate UTF-8 BOM for local editor compatibility."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def active_primary_reason_ids() -> set[str]:
    """Return STS IDs that currently have at least one active primary criterion link."""
    links = load_seed(CRITERIA_LINKS_PATH)["consultation_reason_criteria_links"]

    return {
        item["consultation_reason_source_id"]
        for item in links
        if item.get("is_active", True) is True
        and item["relevance"] == "primary"
    }


def review_samples() -> list[dict]:
    """Return STS source-alignment review samples."""
    return load_seed(SOURCE_ALIGNMENT_REVIEW_PATH)["review_samples"]


def consultation_reasons_by_id() -> dict[str, dict]:
    """Return consultation reason seed items keyed by STS source id."""
    reasons = load_seed(CONSULTATION_REASONS_PATH)["consultation_reasons"]
    return {item["sts_id"]: item for item in reasons}


def test_source_alignment_review_samples_reference_existing_sts_reasons() -> None:
    """Ensure every source-alignment sample references an existing STS consultation reason."""
    reasons_by_id = consultation_reasons_by_id()

    missing_ids = [
        item["sts_id"]
        for item in review_samples()
        if item["sts_id"] not in reasons_by_id
    ]

    assert missing_ids == []


def test_source_alignment_review_samples_match_current_seed_label_and_category() -> None:
    """Ensure review records stay aligned with the current consultation reason seed."""
    reasons_by_id = consultation_reasons_by_id()

    mismatches = []

    for sample in review_samples():
        reason = reasons_by_id[sample["sts_id"]]

        if sample["source_label_de"] != reason["source_label_de"]:
            mismatches.append(
                {
                    "sts_id": sample["sts_id"],
                    "field": "source_label_de",
                    "review_value": sample["source_label_de"],
                    "seed_value": reason["source_label_de"],
                }
            )

        if sample["source_category_de"] != reason["source_category_de"]:
            mismatches.append(
                {
                    "sts_id": sample["sts_id"],
                    "field": "source_category_de",
                    "review_value": sample["source_category_de"],
                    "seed_value": reason["source_category_de"],
                }
            )

    assert mismatches == []


def test_source_alignment_review_samples_have_primary_criterion_links() -> None:
    """Ensure every sampled STS reason currently has at least one active primary criterion link."""
    reason_ids_with_primary_link = active_primary_reason_ids()

    missing_primary_links = [
        sample["sts_id"]
        for sample in review_samples()
        if sample["sts_id"] not in reason_ids_with_primary_link
    ]

    assert missing_primary_links == []


def test_source_alignment_review_has_minimum_category_sample_coverage() -> None:
    """Ensure every category has at least two source-alignment review samples."""
    sample_counts_by_category = Counter(
        sample["source_category_de"]
        for sample in review_samples()
    )

    categories_in_source = {
        item["source_category_de"]
        for item in consultation_reasons_by_id().values()
    }

    missing_or_undercovered_categories = {
        category: sample_counts_by_category.get(category, 0)
        for category in categories_in_source
        if sample_counts_by_category.get(category, 0) < 2
    }

    assert missing_or_undercovered_categories == {}


def test_source_alignment_review_has_risk_based_sample_per_category() -> None:
    """Ensure every category has at least one high-risk, sensitive, or safety-sensitive sample."""
    samples_by_category: dict[str, list[dict]] = defaultdict(list)

    for sample in review_samples():
        samples_by_category[sample["source_category_de"]].append(sample)

    categories_without_risk_sample = sorted(
        category
        for category, samples in samples_by_category.items()
        if not any(sample["review_type"] in RISK_SAMPLE_TYPES for sample in samples)
    )

    assert categories_without_risk_sample == []


def test_miscellaneous_category_has_extra_review_samples() -> None:
    """Ensure the heterogeneous miscellaneous category has more than the minimum sample count."""
    samples = [
        sample
        for sample in review_samples()
        if sample["source_category_de"] == "Verschiedene Konsultationsmotive"
    ]

    assert len(samples) >= 4


def test_reviewed_ok_samples_have_completed_checklist() -> None:
    """Ensure samples marked as reviewed_ok have all checklist items completed."""
    incomplete_reviewed_samples = []

    for sample in review_samples():
        if sample["review_status"] != "reviewed_ok":
            continue

        checklist = sample["review_checklist"]

        if not all(checklist.values()):
            incomplete_reviewed_samples.append(sample["sts_id"])

    assert incomplete_reviewed_samples == []


def test_review_samples_do_not_hide_known_revision_needs() -> None:
    """Prevent committing known source-alignment problems as unresolved review samples."""
    revision_needed_ids = [
        sample["sts_id"]
        for sample in review_samples()
        if sample["review_status"] == "needs_revision"
    ]

    assert revision_needed_ids == []
