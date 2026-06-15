from typing import Literal
from uuid import uuid4

from pydantic import Field, field_validator

from careena_pipeline3.models.common import PipelineModel
from careena_pipeline3.models.common.types import ObservationStatus, ObservationType
from careena_pipeline3.models.domain.provenance import Provenance


class CaseObservation(PipelineModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: ObservationType
    label: str
    source_span: str
    display_label: str | None = None
    concept: str | None = None
    negated: bool = False
    certainty: Literal["confirmed", "suspected", "uncertain"] = "confirmed"
    temporality: str | None = None
    severity: int | None = Field(default=None, ge=0, le=10)
    body_site: str | None = None
    laterality: Literal["left", "right", "bilateral", "unknown"] | None = None
    course: Literal[
        "worsening",
        "improving",
        "stable",
        "sudden",
        "recurrent",
        "unknown",
    ] | None = None
    measurement: dict[str, str | bool] = Field(default_factory=dict)
    subject_ref: str | None = None
    details: dict[str, str] = Field(default_factory=dict)
    status: ObservationStatus = "extracted"
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    provenance: list[Provenance] = Field(default_factory=list)

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, value):
        if value is None or isinstance(value, int):
            return value
        if isinstance(value, float):
            return round(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if not normalized:
                return None
            if normalized.isdigit():
                return int(normalized)
            words = {
                "none": 0,
                "no": 0,
                "keine": 0,
                "mild": 2,
                "leicht": 2,
                "moderate": 5,
                "mittel": 5,
                "maessig": 5,
                "strong": 8,
                "severe": 8,
                "stark": 8,
                "schwer": 8,
                "very strong": 9,
                "sehr stark": 9,
                "unbearable": 10,
                "unertraeglich": 10,
            }
            if normalized in words:
                return words[normalized]
        return value

    def set_surface_field(self, name: str, value) -> None:
        self._set_field(name, value)

    def set_detail_value(self, key: str, value: str, *, overwrite: bool = False) -> None:
        if not overwrite and key in self.details:
            return
        self.details[key] = value

    def merge_detail_values(
        self,
        values: dict[str, str],
        *,
        overwrite: bool = False,
    ) -> None:
        changed = False
        for key, value in values.items():
            if _is_placeholder_merge_value(value):
                continue
            if overwrite or key not in self.details:
                self.details[key] = value
                changed = True

    def merge_measurement_values(
        self,
        values: dict[str, str | bool],
        *,
        overwrite: bool = False,
    ) -> None:
        changed = False
        for key, value in values.items():
            if _is_placeholder_merge_value(value):
                continue
            if overwrite or key not in self.measurement:
                self.measurement[key] = value
                changed = True

    def runtime_value(self, name: str):
        if name == "temporality":
            return self._runtime_temporality()
        if name == "body_site":
            return self._runtime_body_site()
        if name == "severity":
            return self._runtime_severity()
        if name == "course":
            return self._runtime_course()
        return getattr(self, name, None)

    def runtime_measurement_value(self, key: str):
        if key == "kind":
            return self.measurement.get("kind")
        if key == "value":
            return (
                self.measurement.get("value")
                or self.measurement.get("numeric_value")
            )
        if key == "unit":
            return self.measurement.get("unit")
        return self.measurement.get(key)

    def requirement_value(self, field: str):
        if self.type == "symptom":
            return self._symptom_requirement_value(field)
        if self.type == "injury":
            return self._injury_requirement_value(field)
        if self.type == "measurement":
            return self._measurement_requirement_value(field)
        if self.type == "medication":
            return self._medication_requirement_value(field)
        if self.type == "risk_factor" and field == "kind":
            return self.label or self.concept
        if self.type == "concern" and field == "main_concern":
            return self.display_label or self.label
        if self.type == "diagnosis" and field == "name":
            return self.label or self.concept
        return None

    @property
    def patient_label(self) -> str:
        return self.display_label or self.label or "Angabe"

    @property
    def searchable_text(self) -> str:
        parts = [
            self.type,
            self.label,
            self.display_label or "",
            self.concept or "",
            self.runtime_value("body_site") or "",
            self.source_span,
        ]
        parts.extend(str(value) for value in self.details.values())
        parts.extend(str(value) for value in self.measurement.values())
        return " ".join(part for part in parts if part)

    def _symptom_requirement_value(self, field: str):
        if field == "duration_or_onset":
            return self.temporality
        if field == "body_site":
            return self.body_site
        if field == "severity":
            return self.severity
        if field == "course":
            return self.course
        return None

    def _injury_requirement_value(self, field: str):
        if field == "duration_or_onset":
            return self.temporality
        if field == "body_site":
            return self.body_site
        if field == "severity":
            return self.severity
        if field == "injury_context":
            return self.details.get("injury_context")
        if field == "functional_limitation":
            return self.details.get("functional_limitation")
        return None

    def _measurement_requirement_value(self, field: str):
        if field == "kind":
            return self.measurement.get("kind")
        if field == "value":
            return (
                self.measurement.get("value")
                or self.measurement.get("numeric_value")
            )
        return None

    def _medication_requirement_value(self, field: str):
        if field == "name":
            return self.label or self.concept
        if field == "use_context":
            return self.details.get("use_context")
        return None

    def _runtime_temporality(self):
        if self.type == "symptom":
            return self._symptom_requirement_value("duration_or_onset")
        if self.type == "injury":
            return self._injury_requirement_value("duration_or_onset")
        if self.type == "measurement":
            return self.temporality
        return self.temporality

    def _runtime_body_site(self):
        if self.type == "symptom":
            return self._symptom_requirement_value("body_site")
        if self.type == "injury":
            return self._injury_requirement_value("body_site")
        return self.body_site

    def _runtime_severity(self):
        if self.type == "symptom":
            return self._symptom_requirement_value("severity")
        if self.type == "injury":
            return self._injury_requirement_value("severity")
        return self.severity

    def _runtime_course(self):
        if self.type == "symptom":
            return self._symptom_requirement_value("course")
        return self.course

    def _runtime_injury_context(self) -> str | None:
        if self.type == "injury":
            return self._injury_requirement_value("injury_context")
        return self.details.get("injury_context")

    def _runtime_functional_limitation(self) -> str | None:
        if self.type == "injury":
            return self._injury_requirement_value("functional_limitation")
        return self.details.get("functional_limitation")

    def _set_field(self, name: str, value) -> None:
        object.__setattr__(self, name, value)


def _is_placeholder_merge_value(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"", "unknown", "unklar"}
    return False
