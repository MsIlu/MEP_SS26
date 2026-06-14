from __future__ import annotations

from typing import Any

from pydantic import ValidationError

try:
    from fhir.resources.bundle import Bundle
except ImportError as exc:  # pragma: no cover
    Bundle = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class FhirValidationError(ValueError):
    """Raised when generated FHIR data is structurally invalid."""


def validate_fhir_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """
    Validates a generated FHIR Bundle with fhir.resources.

    This is a structural validation step for the MVP.
    It does not replace validation against a specific German implementation guide
    or a real external FHIR server.
    """

    if Bundle is None:
        raise RuntimeError(
            "fhir.resources is not installed. "
            "Install dependencies with: python -m pip install -r requirements.txt"
        ) from _IMPORT_ERROR

    try:
        validated_bundle = Bundle.model_validate(bundle)
    except ValidationError as exc:
        raise FhirValidationError(str(exc)) from exc

    return validated_bundle.model_dump(mode="json", exclude_none=True)