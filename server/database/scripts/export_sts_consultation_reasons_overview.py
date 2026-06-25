from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

DATABASE_DIR = Path(__file__).resolve().parents[1]

SEED_PATH = DATABASE_DIR / "seeds/catalog/v1/sts_consultation_reasons.seed.json"
OUTPUT_PATH = DATABASE_DIR / "exports/catalog/v1/sts_consultation_reasons_overview.md"



def load_seed(path: Path) -> dict[str, Any]:
    """Load the STS consultation reason seed file."""
    if not path.exists():
        raise FileNotFoundError(f"Seed file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def group_reasons_by_category(seed_data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Group STS consultation reasons by their original STS source category."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for reason in seed_data.get("consultation_reasons", []):
        category = reason.get("source_category_de", "Unbekannte STS-Kategorie")
        grouped[category].append(reason)

    return dict(sorted(grouped.items(), key=lambda item: item[0].lower()))


def render_markdown(seed_data: dict[str, Any], grouped_reasons: dict[str, list[dict[str, Any]]]) -> str:
    """Render a human-readable STS catalog overview for review."""
    source = seed_data.get("source", {})

    lines: list[str] = [
        "# STS Consultation Reasons Overview",
        "",
        f"- Source system: {source.get('system', 'unknown')}",
        f"- Source version: {source.get('version', 'unknown')}",
        f"- Source year: {source.get('year', 'unknown')}",
        f"- Language: {source.get('language', 'unknown')}",
        "",
        "This file is generated from the STS consultation reason seed.",
        "It is intended for review and team alignment, not as runtime triage logic.",
        "",
    ]

    for category, reasons in grouped_reasons.items():
        lines.append(f"## {category}")
        lines.append("")

        for reason in sorted(reasons, key=lambda item: item.get("sts_id", "")):
            sts_id = reason.get("sts_id", "unknown")
            label = reason.get("source_label_de", "unknown")
            levels = reason.get("source_sts_levels_present", [])

            lines.append(f"- **{sts_id}** {label}")
            lines.append(f"  - STS levels present in source: {levels}")

        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Generate a grouped STS consultation reason overview."""
    seed_data = load_seed(SEED_PATH)
    grouped_reasons = group_reasons_by_category(seed_data)
    markdown = render_markdown(seed_data, grouped_reasons)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(markdown, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "source": str(SEED_PATH),
                "output": str(OUTPUT_PATH),
                "category_count": len(grouped_reasons),
                "consultation_reason_count": sum(len(items) for items in grouped_reasons.values()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
