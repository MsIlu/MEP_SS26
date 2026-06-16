from typing import Protocol

from careena4.models.domain import SafetyCatalogMatch


class SafetyCatalogRepository(Protocol):
    def find_matches_for_evidence_terms(
        self,
        evidence_terms: list[str],
    ) -> list[SafetyCatalogMatch]:
        ...
