from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StsConsultationReasonCatalog:
    """
    Loads STS consultation reasons for MedGemma STS candidate matching.

    This is catalog metadata, not triage logic. The TurnEngine must not know
    whether the catalog comes from a seed file, database or future repository.
    """

    def __init__(self, *, seed_path: Path | None = None):
        self.seed_path = seed_path or self._default_seed_path()
        self._reasons_cache: str | None = None
        self._index_cache: dict[str, dict[str, Any]] | None = None

    def reasons_for_prompt(self) -> str:
        """
        Return the STS reason catalog as a compact `sts_id: label` list.

        The LLM only needs a stable identifier and a short human-readable label.
        Category and level metadata stay local and are hydrated after the call.
        """

        if self._reasons_cache is not None:
            return self._reasons_cache

        seed = json.loads(self.seed_path.read_text(encoding="utf-8-sig"))
        full_reasons: list[dict[str, Any]] = []
        lines: list[str] = []

        for item in seed.get("consultation_reasons", []):
            sts_id = item.get("sts_id")
            if sts_id is None:
                continue

            full_reasons.append(item)
            lines.append(f"{sts_id}: {item.get('source_label_de', '')}")

        self._reasons_cache = "\n".join(lines)
        self._index_cache = {
            str(item["sts_id"]): {
                "sts_id": str(item["sts_id"]),
                "source_category_de": item.get("source_category_de"),
                "source_label_de": item.get("source_label_de"),
                "source_sts_levels_present": item.get("source_sts_levels_present", []),
            }
            for item in full_reasons
        }
        return self._reasons_cache

    def hydrate_match(self, match: dict[str, Any]) -> dict[str, Any]:
        """
        Fill missing STS metadata from the local STS seed.

        This is not a medical fallback. It only ensures that a partial LLM match
        with a valid STS ID gets the catalog label/category/levels for review.
        """

        self.reasons_for_prompt()
        index = self._index_cache or {}
        seed_reason = index.get(str(match.get("sts_id")))

        if seed_reason is None:
            return match

        hydrated = dict(match)
        hydrated["sts_label_de"] = hydrated.get("sts_label_de") or seed_reason.get("source_label_de")
        hydrated["source_category_de"] = (
            hydrated.get("source_category_de")
            or seed_reason.get("source_category_de")
        )
        hydrated["source_sts_levels_present"] = (
            hydrated.get("source_sts_levels_present")
            or seed_reason.get("source_sts_levels_present", [])
        )
        return hydrated

    @staticmethod
    def _default_seed_path() -> Path:
        """Resolve the STS seed path from the server package location."""

        return (
            Path(__file__).resolve().parents[3]
            / "database"
            / "seeds"
            / "catalog"
            / "v1"
            / "sts_consultation_reasons.seed.json"
        )
