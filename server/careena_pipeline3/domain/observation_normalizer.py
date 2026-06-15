from __future__ import annotations

from careena_pipeline3.models.domain import CaseObservation


"""
Date: 2026-06-08
Last changed: 2026-06-08
Author: workbench@freddy

Short description:
Normalizes incoming observations before case-truth decisions are made.
It keeps canonical surface fields and structural bridges in sync.
"""
class ObservationNormalizer:
    """Applies canonical surface normalization before case-truth decisions."""

    def normalize(self, observation: CaseObservation) -> CaseObservation:
        if not observation.display_label:
            observation.display_label = observation.label
        if not observation.source_span:
            observation.source_span = observation.display_label or observation.label
        if observation.subject_ref == "":
            observation.subject_ref = None
        return observation
