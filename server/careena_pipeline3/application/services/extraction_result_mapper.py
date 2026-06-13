from careena_pipeline3.models.domain import CaseObservation, Provenance, Subject
from careena_pipeline3.models.extraction import (
    Call2ExtractionResult,
    ExtractedObservation,
    ExtractedSubject,
    ExtractionResult,
)
from careena_pipeline3.models.turn import (
    CaseUpdateBridge,
    CaseUpdateClaims,
    CaseUpdateMergeHints,
)


class ExtractionResultMapper:
    """
    Builds the truth-edge bridge from the active Call-2 contract.

    `ExtractionResult` support remains only as a compatibility helper for
    observability-oriented tests and transitional tooling.
    """

    def to_case_update_bridge(
        self,
        result: Call2ExtractionResult,
        *,
        message_role: str = "new_information",
        possible_new_topic: bool = False,
    ) -> CaseUpdateBridge:
        return CaseUpdateBridge(
            claims=CaseUpdateClaims(
                subject=self._map_subject(result.subject_update),
                case_frame_label=_normalized_case_frame_label(result.case_frame_label),
                observations_added=[
                    self._map_observation(item)
                    for item in result.all_observations()
                    if not item.negated
                ],
                negated_observations_added=[
                    self._map_observation(item)
                    for item in result.all_observations()
                    if item.negated
                ],
            ),
            merge_hints=CaseUpdateMergeHints(
                message_role=message_role,
                possible_new_topic=possible_new_topic,
                case_extension_status=result.case_extension_status,
            ),
        )

    def extraction_result_to_case_update_bridge(
        self,
        result: ExtractionResult,
        *,
        message_role: str = "new_information",
        possible_new_topic: bool = False,
    ) -> CaseUpdateBridge:
        return CaseUpdateBridge(
            claims=CaseUpdateClaims(
                subject=self._map_subject(result.case_payload.subject),
                case_frame_label=_normalized_case_frame_label(
                    result.case_payload.case_frame_label
                ),
                observations_added=[
                    self._map_observation(item)
                    for item in result.case_payload.observations
                    if not item.negated
                ],
                negated_observations_added=[
                    self._map_observation(item)
                    for item in result.case_payload.observations
                    if item.negated
                ],
            ),
            merge_hints=CaseUpdateMergeHints(
                message_role=message_role,
                possible_new_topic=possible_new_topic,
                case_extension_status=result.case_extension_status,
            ),
        )

    @staticmethod
    def active_modules(result: Call2ExtractionResult) -> list[str]:
        if result.open_questions:
            return ["requirement_resolution"]
        return []

    @staticmethod
    def _map_subject(subject: ExtractedSubject | None) -> Subject | None:
        if subject is None:
            return None

        return Subject(
            relation=subject.relation or "unknown",
            age=subject.age,
            sex=subject.sex,
            confidence=subject.confidence or 0.0,
        )

    @staticmethod
    def _map_observation(observation: ExtractedObservation) -> CaseObservation:
        attributes = dict(observation.attributes)
        observation_type = _observation_type_value(observation.observation_type)
        mapped = _map_observation_attributes(
            observation_type=observation_type,
            attributes=attributes,
        )
        observation_kwargs = {}
        if observation.observation_id:
            observation_kwargs["id"] = observation.observation_id

        return CaseObservation(
            **observation_kwargs,
            type=observation_type,
            label=observation.raw_label,
            display_label=observation.raw_label,
            concept=observation.normalized_concept,
            source_span=observation.source_span or observation.raw_label,
            negated=observation.negated,
            certainty=_map_certainty(observation.certainty),
            temporality=mapped["temporality"],
            severity=mapped["severity"],
            body_site=mapped["body_site"],
            laterality=mapped["laterality"],
            course=mapped["course"],
            measurement=mapped["measurement"],
            subject_ref=observation.subject_ref,
            details=mapped["details"],
            confidence=observation.confidence,
            provenance=[
                Provenance(
                    source="user_message",
                    source_span=observation.source_span,
                    confidence=observation.confidence,
                )
            ],
        )


SURFACE_ATTRIBUTE_KEYS_BY_TYPE: dict[str, set[str]] = {
    "symptom": {
        "temporality",
        "severity",
        "body_site",
        "laterality",
        "course",
    },
    "injury": {
        "temporality",
        "severity",
        "body_site",
        "laterality",
    },
    "measurement": {
        "temporality",
        "body_site",
        "laterality",
    },
}

MEASUREMENT_ATTRIBUTE_KEYS = {
    "kind",
    "value",
    "numeric_value",
    "unit",
    "measured_at",
    "is_current",
}

DETAIL_ATTRIBUTE_KEYS_BY_TYPE: dict[str, set[str]] = {
    "symptom": {"quality"},
    "injury": {"injury_context", "functional_limitation"},
    "medication": {"dose", "frequency", "route", "use_context"},
    "diagnosis": {"status", "chronicity"},
}

DETAIL_ATTRIBUTE_ALIASES_BY_TYPE: dict[str, dict[str, str]] = {
    "injury": {
        "mechanism": "injury_context",
    }
}


def _map_observation_attributes(
    *,
    observation_type: str,
    attributes: dict[str, object],
) -> dict[str, object]:
    normalized_attributes = _normalize_attribute_aliases(
        observation_type=observation_type,
        attributes=attributes,
    )
    surface_keys = SURFACE_ATTRIBUTE_KEYS_BY_TYPE.get(observation_type, set())
    return {
        "temporality": _surface_string_value(
            normalized_attributes,
            surface_keys=surface_keys,
            key="temporality",
        ),
        "severity": _surface_severity_value(
            normalized_attributes,
            surface_keys=surface_keys,
        ),
        "body_site": _surface_string_value(
            normalized_attributes,
            surface_keys=surface_keys,
            key="body_site",
        ),
        "laterality": _surface_laterality_value(
            normalized_attributes,
            surface_keys=surface_keys,
        ),
        "course": _surface_course_value(
            normalized_attributes,
            surface_keys=surface_keys,
        ),
        "measurement": _extract_measurement(
            observation_type=observation_type,
            attributes=normalized_attributes,
        ),
        "details": _extract_details(
            observation_type=observation_type,
            attributes=normalized_attributes,
            surface_keys=surface_keys,
        ),
    }


def _normalize_attribute_aliases(
    *,
    observation_type: str,
    attributes: dict[str, object],
) -> dict[str, object]:
    normalized = dict(attributes)
    aliases = DETAIL_ATTRIBUTE_ALIASES_BY_TYPE.get(observation_type, {})
    for source_key, target_key in aliases.items():
        if target_key in normalized:
            continue
        if source_key in normalized and normalized[source_key] is not None:
            normalized[target_key] = normalized[source_key]
    return normalized


def _extract_measurement(
    *,
    observation_type: str,
    attributes: dict[str, object],
) -> dict[str, str | bool]:
    if observation_type != "measurement":
        return {}
    result: dict[str, str | bool] = {}
    for key in MEASUREMENT_ATTRIBUTE_KEYS:
        value = attributes.get(key)
        if isinstance(value, bool):
            result[key] = value
        elif value is not None:
            result[key] = str(value)
    return result


def _extract_details(
    *,
    observation_type: str,
    attributes: dict[str, object],
    surface_keys: set[str],
) -> dict[str, str]:
    allowed_detail_keys = DETAIL_ATTRIBUTE_KEYS_BY_TYPE.get(observation_type, set())
    excluded = surface_keys.union(MEASUREMENT_ATTRIBUTE_KEYS)
    return {
        key: str(value)
        for key, value in attributes.items()
        if key not in excluded
        and value is not None
        and key in allowed_detail_keys
    }


def _map_certainty(value: str | None) -> str:
    if value in {"confirmed", "suspected", "uncertain"}:
        return value
    return "confirmed"


def _string_value(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _surface_string_value(
    attributes: dict[str, object],
    *,
    surface_keys: set[str],
    key: str,
) -> str | None:
    if key not in surface_keys:
        return None
    return _string_value(attributes.get(key))


def _severity_value(value: object) -> int | str | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None
        if normalized.isdigit():
            return int(normalized)
        return normalized
    return None


def _surface_severity_value(
    attributes: dict[str, object],
    *,
    surface_keys: set[str],
) -> int | str | None:
    if "severity" not in surface_keys:
        return None
    return _severity_value(attributes.get("severity"))


def _laterality_value(value: object) -> str | None:
    if value in {"left", "right", "bilateral", "unknown"}:
        return str(value)
    return None


def _surface_laterality_value(
    attributes: dict[str, object],
    *,
    surface_keys: set[str],
) -> str | None:
    if "laterality" not in surface_keys:
        return None
    return _laterality_value(attributes.get("laterality"))


def _course_value(value: object) -> str | None:
    if value in {"worsening", "improving", "stable", "sudden", "recurrent", "unknown"}:
        return str(value)
    return None


def _surface_course_value(
    attributes: dict[str, object],
    *,
    surface_keys: set[str],
) -> str | None:
    if "course" not in surface_keys:
        return None
    return _course_value(attributes.get("course"))


def _observation_type_value(value: object) -> str:
    if value in {
        "symptom",
        "medication",
        "diagnosis",
        "injury",
        "measurement",
        "risk_factor",
        "concern",
        "administrative",
        "observation",
    }:
        return str(value)
    return "observation"


def _normalized_case_frame_label(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None
