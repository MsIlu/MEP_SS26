from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from careena4.models.understanding import StsConsultationReasonCandidate

# Generic tokens that appear in STS labels but are too broad to use for matching.
_MATCH_STOPWORDS = {
    "schmerzen", "symptome", "beschwerden", "stoerung", "stoerungen",
    "zustand", "bereich", "region", "trauma", "defizit", "zustand",
}


def _normalize_token(text: str) -> str:
    text = text.casefold()
    text = (
        text.replace("ä", "ae").replace("ö", "oe")
        .replace("ü", "ue").replace("ß", "ss")
    )
    return re.sub(r"[^a-z0-9]", "", text)


def _sts_tokens(label: str) -> list[str]:
    """Extract matchable keyword tokens from an STS label."""
    raw_tokens = re.split(r"[^a-zA-Z0-9äöüÄÖÜß]+", label)
    tokens = []
    for raw in raw_tokens:
        t = _normalize_token(raw)
        if len(t) >= 6 and t not in _MATCH_STOPWORDS:
            tokens.append(t)
    return tokens


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
        self._match_entries_cache: list[dict[str, Any]] | None = None

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
        self._match_entries_cache = full_reasons
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

    def match_by_labels(
        self,
        labels: list[str],
        *,
        max_results: int = 3,
    ) -> list[StsConsultationReasonCandidate]:
        """Match normalized symptom labels against STS entries by keyword overlap.

        Runs after normalization so that STS catalog content cannot bias
        the normalization step.
        """
        if not labels:
            return []

        symptom_text = " ".join(_normalize_token(label) for label in labels)
        self.reasons_for_prompt()

        matches: list[StsConsultationReasonCandidate] = []
        for entry in self._match_entries_cache or []:
            tokens = _sts_tokens(entry.get("source_label_de", ""))
            if not tokens:
                continue
            if any(token in symptom_text for token in tokens):
                matches.append(
                    StsConsultationReasonCandidate(
                        sts_id=str(entry["sts_id"]),
                        sts_label_de=entry.get("source_label_de"),
                        source_category_de=entry.get("source_category_de"),
                        source_sts_levels_present=entry.get("source_sts_levels_present", []),
                        match_confidence=1.0,
                        match_reason="keyword_match",
                    )
                )
            if len(matches) >= max_results:
                break

        return matches

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
