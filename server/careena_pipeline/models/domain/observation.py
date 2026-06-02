from typing import Literal
from uuid import uuid4

from pydantic import Field, field_validator, model_validator

from careena_pipeline.models.common.base import PipelineModel
from careena_pipeline.models.common.types import ObservationStatus, ObservationType
from careena_pipeline.models.domain.observation_data import (
    DiagnosisObservationData,
    InjuryObservationData,
    MeasurementObservationData,
    MedicationObservationData,
    SymptomObservationData,
)
from careena_pipeline.models.domain.provenance import Provenance


class CaseObservation(PipelineModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: ObservationType
    label: str
    display_label: str | None = None
    concept: str | None = None
    source_span: str
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
    measurement: dict[str, str | int | float | bool] = Field(default_factory=dict)
    subject_ref: str | None = None
    details: dict[str, str] = Field(default_factory=dict)
    symptom_data: SymptomObservationData | None = None
    injury_data: InjuryObservationData | None = None
    measurement_data: MeasurementObservationData | None = None
    medication_data: MedicationObservationData | None = None
    diagnosis_data: DiagnosisObservationData | None = None
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

    @model_validator(mode="after")
    def harmonize_structure(self):
        self._seed_structured_data_from_legacy()
        self._seed_legacy_fields_from_structured()
        return self

    def synchronize_structure(self) -> None:
        self._seed_structured_data_from_legacy()
        self._seed_legacy_fields_from_structured()

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
            return (
                (self.diagnosis_data.name if self.diagnosis_data is not None else None)
                or self.label
                or self.concept
            )
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
            self.body_site or "",
            self.source_span,
        ]
        parts.extend(str(value) for value in self.details.values())
        parts.extend(str(value) for value in self.measurement.values())
        return " ".join(part for part in parts if part)

    def _seed_structured_data_from_legacy(self) -> None:
        if self.type == "symptom":
            self._ensure_symptom_data()
        elif self.type == "injury":
            self._ensure_injury_data()
        elif self.type == "measurement":
            self._ensure_measurement_data()
        elif self.type == "medication":
            self._ensure_medication_data()
        elif self.type == "diagnosis":
            self._ensure_diagnosis_data()

    def _seed_legacy_fields_from_structured(self) -> None:
        if self.symptom_data is not None:
            self._set_field(
                "temporality",
                self.temporality or self.symptom_data.duration_or_onset,
            )
            self._set_field(
                "body_site",
                self.body_site or self.symptom_data.body_site,
            )
            self._set_field(
                "severity",
                self.severity if self.severity is not None else self.symptom_data.severity,
            )
            self._set_field(
                "course",
                self.course or self.symptom_data.course,
            )
            if self.symptom_data.quality and "quality" not in self.details:
                self.details["quality"] = self.symptom_data.quality

        if self.injury_data is not None:
            self._set_field(
                "temporality",
                self.temporality or self.injury_data.duration_or_onset,
            )
            self._set_field(
                "body_site",
                self.body_site or self.injury_data.body_site,
            )
            self._set_field(
                "severity",
                self.severity if self.severity is not None else self.injury_data.severity,
            )
            if self.injury_data.injury_context and "context" not in self.details:
                self.details["context"] = self.injury_data.injury_context
            if (
                self.injury_data.functional_limitation
                and "functional_limitation" not in self.details
            ):
                self.details["functional_limitation"] = self.injury_data.functional_limitation

        if self.measurement_data is not None:
            if self.measurement_data.kind and "kind" not in self.measurement:
                self.measurement["kind"] = self.measurement_data.kind
            if self.measurement_data.value and "value" not in self.measurement:
                self.measurement["value"] = self.measurement_data.value
            if (
                self.measurement_data.numeric_value is not None
                and "numeric_value" not in self.measurement
            ):
                self.measurement["numeric_value"] = self.measurement_data.numeric_value
            if self.measurement_data.unit and "unit" not in self.measurement:
                self.measurement["unit"] = self.measurement_data.unit
            if self.measurement_data.measured_at and not self.temporality:
                self._set_field("temporality", self.measurement_data.measured_at)

        if self.medication_data is not None:
            if self.medication_data.name:
                self._set_field("label", self.label or self.medication_data.name)
            if self.medication_data.use_context and "use_context" not in self.details:
                self.details["use_context"] = self.medication_data.use_context
            if self.medication_data.dose and "dose" not in self.details:
                self.details["dose"] = self.medication_data.dose
            if self.medication_data.frequency and "frequency" not in self.details:
                self.details["frequency"] = self.medication_data.frequency
            if self.medication_data.route and "route" not in self.details:
                self.details["route"] = self.medication_data.route
            if (
                self.medication_data.is_current is not None
                and "is_current" not in self.measurement
            ):
                self.measurement["is_current"] = self.medication_data.is_current

        if self.diagnosis_data is not None:
            self._set_field(
                "label",
                self.label or self.diagnosis_data.name or self.label,
            )
            if self.diagnosis_data.status and "status" not in self.details:
                self.details["status"] = self.diagnosis_data.status
            if self.diagnosis_data.chronicity and "chronicity" not in self.details:
                self.details["chronicity"] = self.diagnosis_data.chronicity

    def _ensure_symptom_data(self) -> None:
        if self.symptom_data is None:
            quality = self.details.get("quality")
            if not any(
                (
                    self.temporality,
                    self.body_site,
                    self.severity is not None,
                    self.course,
                    quality,
                )
            ):
                return
            self._set_field(
                "symptom_data",
                SymptomObservationData(
                    duration_or_onset=self.temporality,
                    body_site=self.body_site,
                    severity=self.severity,
                    course=self.course,
                    quality=quality,
                ),
            )

    def _ensure_injury_data(self) -> None:
        if self.injury_data is None:
            injury_context = self.details.get("context")
            functional_limitation = self.details.get("functional_limitation")
            if not any(
                (
                    self.temporality,
                    self.body_site,
                    self.severity is not None,
                    injury_context,
                    functional_limitation,
                )
            ):
                return
            self._set_field(
                "injury_data",
                InjuryObservationData(
                    duration_or_onset=self.temporality,
                    body_site=self.body_site,
                    severity=self.severity,
                    injury_context=injury_context,
                    functional_limitation=functional_limitation,
                ),
            )

    def _ensure_measurement_data(self) -> None:
        if self.measurement_data is None:
            if not self.measurement and not self.temporality:
                return
            numeric_value = None
            raw_numeric = self.measurement.get("numeric_value")
            if isinstance(raw_numeric, int | float):
                numeric_value = float(raw_numeric)
            raw_value = self.measurement.get("value")
            value = str(raw_value) if raw_value is not None else None
            self._set_field(
                "measurement_data",
                MeasurementObservationData(
                    kind=_string_or_none(self.measurement.get("kind")),
                    value=value,
                    numeric_value=numeric_value,
                    unit=_string_or_none(self.measurement.get("unit")),
                    measured_at=self.temporality,
                ),
            )

    def _ensure_medication_data(self) -> None:
        if self.medication_data is None:
            if not any(
                (
                    self.label,
                    self.concept,
                    self.details.get("use_context"),
                    self.details.get("dose"),
                    self.details.get("frequency"),
                    self.details.get("route"),
                )
            ):
                return
            self._set_field(
                "medication_data",
                MedicationObservationData(
                    name=self.label or self.concept,
                    dose=self.details.get("dose"),
                    frequency=self.details.get("frequency"),
                    route=self.details.get("route"),
                    use_context=self.details.get("use_context"),
                    is_current=_bool_or_none(self.measurement.get("is_current")),
                ),
            )

    def _ensure_diagnosis_data(self) -> None:
        if self.diagnosis_data is None:
            if not any((self.label, self.concept, self.details)):
                return
            self._set_field(
                "diagnosis_data",
                DiagnosisObservationData(
                    name=self.label or self.concept,
                    status=self.details.get("status"),
                    chronicity=self.details.get("chronicity"),
                ),
            )

    def _symptom_requirement_value(self, field: str):
        data = self.symptom_data
        if field == "duration_or_onset":
            return (data.duration_or_onset if data is not None else None) or self.temporality
        if field == "body_site":
            return (data.body_site if data is not None else None) or self.body_site
        if field == "severity":
            return (data.severity if data is not None else None)
        if field == "course":
            return (data.course if data is not None else None) or self.course
        return None

    def _injury_requirement_value(self, field: str):
        data = self.injury_data
        if field == "duration_or_onset":
            return (data.duration_or_onset if data is not None else None) or self.temporality
        if field == "body_site":
            return (data.body_site if data is not None else None) or self.body_site
        if field == "severity":
            return (data.severity if data is not None else None)
        if field == "injury_context":
            return (data.injury_context if data is not None else None) or self.details.get("context")
        if field == "functional_limitation":
            return (
                (data.functional_limitation if data is not None else None)
                or self.details.get("functional_limitation")
            )
        return None

    def _measurement_requirement_value(self, field: str):
        data = self.measurement_data
        if field == "kind":
            return (data.kind if data is not None else None) or self.measurement.get("kind")
        if field == "value":
            return (
                (data.value if data is not None else None)
                or (data.numeric_value if data is not None else None)
                or self.measurement.get("value")
                or self.measurement.get("numeric_value")
            )
        return None

    def _medication_requirement_value(self, field: str):
        data = self.medication_data
        if field == "name":
            return (data.name if data is not None else None) or self.label or self.concept
        if field == "use_context":
            return (data.use_context if data is not None else None) or self.details.get("use_context")
        return None

    def _set_field(self, name: str, value) -> None:
        object.__setattr__(self, name, value)


def _string_or_none(value) -> str | None:
    if value is None:
        return None
    return str(value)


def _bool_or_none(value) -> bool | None:
    if isinstance(value, bool):
        return value
    return None
