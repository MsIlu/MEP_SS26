from typing import Protocol

from careena_pipeline3.models.domain import SafetyCatalogMatch


class SafetyCatalogRepository(Protocol):
    """Repository contract for safety-relevant catalog lookups."""

    def find_matches_for_evidence_terms(
        self,
        evidence_terms: list[str],
    ) -> list[SafetyCatalogMatch]:
        """Find safety-relevant catalog matches for raw safety evidence."""
        ...