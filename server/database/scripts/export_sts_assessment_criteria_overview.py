from __future__ import annotations

import json
from pathlib import Path

from sqlmodel import select

from database.catalog.models import (
    AssessmentCriterion,
    ConsultationReason,
    ConsultationReasonAssessmentCriterionLink,
)
from database.connection import get_db_session


EXPORT_PATH = (
    Path(__file__).resolve().parents[1]
    / "exports"
    / "catalog"
    / "v1"
    / "sts_assessment_criteria_overview.md"
)


def load_json_field(value: str) -> object:
    """Parse a JSON string field for readable export output."""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def format_list(value: object) -> str:
    """Format JSON values into compact markdown-friendly text."""
    if isinstance(value, dict):
        de_value = value.get("de")
        if isinstance(de_value, list):
            return ", ".join(de_value)
        if isinstance(de_value, str):
            return de_value
        return json.dumps(value, ensure_ascii=False)

    if isinstance(value, list):
        return ", ".join(str(item) for item in value)

    return str(value) if value is not None else ""


def main() -> None:
    """Export active STS assessment criteria links for human review."""
    rows = []

    with get_db_session() as session:
        links = session.exec(
            select(ConsultationReasonAssessmentCriterionLink)
            .where(ConsultationReasonAssessmentCriterionLink.is_active == True)
        ).all()

        for link in links:
            reason = session.get(ConsultationReason, link.consultation_reason_id)
            criterion = session.get(AssessmentCriterion, link.assessment_criterion_id)

            if reason is None or criterion is None:
                continue

            rows.append(
                {
                    "sts_id": reason.source_id,
                    "sts_category": reason.source_category_de,
                    "sts_reason": reason.source_label_de,
                    "criterion_key": criterion.criterion_key,
                    "criterion_label": criterion.label_de,
                    "expected_value_type": criterion.expected_value_type,
                    "suggested_input_mode": criterion.suggested_input_mode,
                    "free_text_allowed": criterion.free_text_allowed,
                    "capture_status": criterion.careena_capture_status,
                    "capture_method": criterion.careena_capture_method,
                    "use_policy": criterion.careena_use_policy,
                    "limitation": criterion.capture_limitation_reason or "",
                    "relevance": link.relevance,
                    "safety_relevant": link.is_safety_relevant,
                    "red_flag_candidate": link.is_red_flag_candidate,
                    "decision_role": link.careena_decision_role,
                    "lay_terms": format_list(load_json_field(criterion.lay_terms_json)),
                    "source_note": link.source_note or "",
                }
            )

    rows.sort(key=lambda item: (item["sts_id"], item["relevance"], item["criterion_key"]))

    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# STS Assessment Criteria Overview",
        "",
        "Generated review export for Careena Pipeline3 catalog work.",
        "",
        "This export shows how STS consultation reasons are linked to reusable assessment criteria.",
        "It is intended for medical/product review, not as runtime case state.",
        "",
        "## Columns",
        "",
        "- `expected_value_type`: structured value Pipeline3 should extract",
        "- `suggested_input_mode`: optional UI/input helper",
        "- `free_text_allowed`: whether users may still answer freely",
        "- `capture_status`: whether Careena can responsibly capture the criterion",
        "- `use_policy`: whether Careena may ask actively or only accept user-provided information",
        "- `decision_role`: possible later Pipeline3 role; not a direct emergency decision",
        "",
        "## Review Table",
        "",
        "| STS ID | STS reason | Criterion | Value type | Input mode | Free text | Capture | Use policy | Relevance | Safety | Red flag candidate | Decision role |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            "| "
            f"{row['sts_id']} | "
            f"{row['sts_reason']} | "
            f"{row['criterion_key']} | "
            f"{row['expected_value_type']} | "
            f"{row['suggested_input_mode']} | "
            f"{row['free_text_allowed']} | "
            f"{row['capture_status']} / {row['capture_method']} | "
            f"{row['use_policy']} | "
            f"{row['relevance']} | "
            f"{row['safety_relevant']} | "
            f"{row['red_flag_candidate']} | "
            f"{row['decision_role']} |"
        )

    lines.extend(
        [
            "",
            "## Review Notes",
            "",
            "- `1001 Herzstillstand, Atemstillstand` now uses `breathing_and_responsiveness_observed` as primary lay-observable safety criterion.",
            "- `glasgow_coma_scale_observer_assisted` remains conditional/supporting and must not be used as the primary criterion for STS 1001.",
            "- GCS is more suitable for neurologic, trauma, intoxication, or reduced-consciousness contexts.",
            "- Further criteria links should be reviewed iteratively before being treated as stable.",
            "",
        ]
    )

    EXPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Export written to: {EXPORT_PATH}")


if __name__ == "__main__":
    main()
