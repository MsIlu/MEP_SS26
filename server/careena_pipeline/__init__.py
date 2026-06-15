"""
Decision pipeline scaffold for Careena backend experiments.

This package intentionally lives next to the existing extraction package.
It can be wired into a test server without changing the current app flow.
"""

from careena_pipeline.pipeline import CareenaDecisionPipeline

__all__ = ["CareenaDecisionPipeline"]
