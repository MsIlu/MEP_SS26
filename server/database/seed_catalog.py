from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlmodel import select

from database.catalog.models import (
    AssessmentCriterion,
    ConsultationReason,
    ConsultationReasonAssessmentCriterionLink,
    utc_now,
)
from database.connection import get_db_session


BASE_SEED_DIR = Path(__file__).resolve().parent / "seeds" / "catalog" / "v1"

CONSULTATION_REASONS_SEED_PATH = BASE_SEED_DIR / "sts_consultation_reasons.seed.json"
ASSESSMENT_CRITERIA_SEED_PATH = BASE_SEED_DIR / "assessment_criteria.seed.json"
CRITERIA_LINKS_SEED_PATH = BASE_SEED_DIR / "sts_consultation_reason_criteria_links.seed.json"


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON seed file."""
    if not path.exists():
        raise FileNotFoundError(f"Seed file not found: {path}")

    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump_json(value: Any) -> str:
    """Serialize a Python value to a stable JSON string for database storage."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def dump_json_field(value: Any, default: Any) -> str:
    """Serialize seed values for database text JSON fields."""
    if value is None:
        value = default
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def seed_consultation_reasons() -> dict[str, int]:
    """Import or update STS consultation reasons."""
    data = load_json(CONSULTATION_REASONS_SEED_PATH)
    source = data.get("source", {})

    source_system = source.get("system", "STS")
    source_version = source.get("version")
    source_year = source.get("year")

    inserted = 0
    updated = 0

    with get_db_session() as session:
        for item in data.get("consultation_reasons", []):
            statement = select(ConsultationReason).where(
                ConsultationReason.source_system == source_system,
                ConsultationReason.source_version == source_version,
                ConsultationReason.source_id == item["sts_id"],
            )
            existing = session.exec(statement).first()

            values = {
                "source_system": source_system,
                "source_version": source_version,
                "source_year": source_year,
                "source_id": item["sts_id"],
                "source_category_de": item.get("source_category_de"),
                "source_label_de": item["source_label_de"],
                "source_sts_levels_present_json": dump_json(item.get("source_sts_levels_present", [])),
                "careena_key": item.get("careena_key"),
                "careena_label_de": item.get("careena_label_de"),
                "mapping_status": item.get("mapping_status", "source_indexed"),
                "mapping_notes": item.get("mapping_notes"),
                "is_active": item.get("is_active", True),
                "updated_at": utc_now(),
            }

            if existing is None:
                session.add(ConsultationReason(**values))
                inserted += 1
            else:
                for key, value in values.items():
                    setattr(existing, key, value)
                updated += 1

        session.commit()

    return {"inserted": inserted, "updated": updated}


def seed_assessment_criteria() -> dict[str, int]:
    """Import or update reusable assessment criteria."""
    data = load_json(ASSESSMENT_CRITERIA_SEED_PATH)

    inserted = 0
    updated = 0

    with get_db_session() as session:
        for item in data.get("assessment_criteria", []):
            statement = select(AssessmentCriterion).where(
                AssessmentCriterion.criterion_key == item["criterion_key"],
            )
            existing = session.exec(statement).first()

            values = {
                "criterion_key": item["criterion_key"],
                "label_de": item["label_de"],
                "description_de": item.get("description_de"),
                "criterion_type": item["criterion_type"],
                "suggested_question_texts_json": dump_json(item.get("suggested_question_texts", {})),
                "lay_terms_json": dump_json(item.get("lay_terms", {})),
                "expected_value_type": item.get("expected_value_type", "free_text"),
                "suggested_input_mode": item.get("suggested_input_mode", "free_text"),
                "free_text_allowed": item.get("free_text_allowed", True),
                "observation_context": item.get("observation_context", "self_report_or_observed"),
                "careena_capture_status": item.get("careena_capture_status", "not_assessed"),
                "careena_capture_method": item.get("careena_capture_method", "not_assessed"),
                "careena_use_policy": item.get("careena_use_policy", "not_assessed"),
                "capture_limitation_reason": item.get("capture_limitation_reason"),
                "mapping_status": item.get("mapping_status", "draft"),
                "mapping_notes": item.get("mapping_notes"),
                "is_active": item.get("is_active", True),
                "updated_at": utc_now(),
            }

            if existing is None:
                session.add(AssessmentCriterion(**values))
                inserted += 1
            else:
                for key, value in values.items():
                    setattr(existing, key, value)
                updated += 1

        session.commit()

    return {"inserted": inserted, "updated": updated}


def seed_consultation_reason_criteria_links() -> dict[str, int]:
    """Import or update links between STS consultation reasons and assessment criteria."""
    data = load_json(CRITERIA_LINKS_SEED_PATH)

    inserted = 0
    updated = 0
    skipped = 0

    with get_db_session() as session:
        for item in data.get("consultation_reason_criteria_links", []):
            reason = session.exec(
                select(ConsultationReason).where(
                    ConsultationReason.source_system == "STS",
                    ConsultationReason.source_version == "1.10",
                    ConsultationReason.source_id == item["consultation_reason_source_id"],
                )
            ).first()

            criterion = session.exec(
                select(AssessmentCriterion).where(
                    AssessmentCriterion.criterion_key == item["criterion_key"],
                )
            ).first()

            if reason is None or criterion is None:
                skipped += 1
                continue

            existing = session.exec(
                select(ConsultationReasonAssessmentCriterionLink).where(
                    ConsultationReasonAssessmentCriterionLink.consultation_reason_id == reason.id,
                    ConsultationReasonAssessmentCriterionLink.assessment_criterion_id == criterion.id,
                )
            ).first()

            values = {
                "consultation_reason_id": reason.id,
                "assessment_criterion_id": criterion.id,
                "relevance": item.get("relevance", "supporting"),
                "is_safety_relevant": item.get("is_safety_relevant", False),
                "is_red_flag_candidate": item.get("is_red_flag_candidate", False),
                "careena_decision_role": item.get("careena_decision_role", "supporting_context"),
                "criterion_role": item.get("criterion_role", "supporting_criterion"),
                "target_sts_levels_json": dump_json_field(
                    item.get("target_sts_levels", item.get("target_sts_levels_json")),
                    [],
                ),
                "urgency_effect": item.get("urgency_effect", "supporting_context_only"),
                "interim_care_guidance_key": item.get("interim_care_guidance_key", "none"),
                "source_note": item.get("source_note"),
                "mapping_status": item.get("mapping_status", "draft"),
                "mapping_notes": item.get("mapping_notes"),
                "is_active": item.get("is_active", True),
                "updated_at": utc_now(),
            }

            if existing is None:
                session.add(ConsultationReasonAssessmentCriterionLink(**values))
                inserted += 1
            else:
                for key, value in values.items():
                    setattr(existing, key, value)
                updated += 1

        session.commit()

    return {"inserted": inserted, "updated": updated, "skipped": skipped}


def main() -> None:
    """Run all catalog seed imports in dependency order."""
    result = {
        "consultation_reasons": seed_consultation_reasons(),
        "assessment_criteria": seed_assessment_criteria(),
        "consultation_reason_criteria_links": seed_consultation_reason_criteria_links(),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
