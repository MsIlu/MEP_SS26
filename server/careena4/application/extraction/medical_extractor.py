from __future__ import annotations

import re

from careena4.core.engine import ExtractionEngine
from careena4.llm.call_control import CallModelConfig, EXTRACTION_CALL
from careena4.llm.prompt_registry import load_prompt
from careena4.models.turn import ExtractionClaims, ObservationClaim
from careena4.server_log import log_event


class MedicalExtractor:
    _OBSERVATION_PATTERNS: tuple[tuple[str, str, str | None], ...] = (
        ("kopfschmerzen", "symptom", "Kopfschmerzen"),
        ("bauchschmerzen", "symptom", "Bauchschmerzen"),
        ("halsschmerzen", "symptom", "Halsschmerzen"),
        ("brustschmerzen", "symptom", "Brustschmerzen"),
        ("husten", "symptom", "Husten"),
        ("fieber", "measurement", "Fieber"),
        ("atemnot", "symptom", "Atemnot"),
        ("luftnot", "symptom", "Atemnot"),
        ("schwindel", "symptom", "Schwindel"),
        ("uebelkeit", "symptom", "Uebelkeit"),
        ("übelkeit", "symptom", "Uebelkeit"),
        ("Ã¼belkeit", "symptom", "Uebelkeit"),
        ("erbrechen", "symptom", "Erbrechen"),
        ("durchfall", "symptom", "Durchfall"),
        ("hueftschmerzen", "injury", "Hueftschmerzen"),
        ("hüftschmerzen", "injury", "Hueftschmerzen"),
        ("hÃ¼ftschmerzen", "injury", "Hueftschmerzen"),
        ("kann kaum auftreten", "injury", "Belastungseinschraenkung"),
        ("kaum auftreten", "injury", "Belastungseinschraenkung"),
    )

    def __init__(
        self,
        *,
        extraction_engine: ExtractionEngine | None = None,
        call_model_config: CallModelConfig | None = None,
    ):
        self.extraction_engine = extraction_engine
        self.call_model_config = call_model_config

    def extract(
        self,
        *,
        message: str,
        case_topic: str | None = None,
        history_messages: list[dict[str, str]] | None = None,
    ) -> ExtractionClaims:
        llm_result = self._extract_with_llm(
            message=message,
            case_topic=case_topic,
            history_messages=history_messages,
        )
        if llm_result is not None:
            return llm_result
        return self._heuristic_extract(message=message)

    def _extract_with_llm(
        self,
        *,
        message: str,
        case_topic: str | None,
        history_messages: list[dict[str, str]] | None,
    ) -> ExtractionClaims | None:
        if self.extraction_engine is None:
            return None
        prompt = load_prompt(EXTRACTION_CALL)
        try:
            result = self.extraction_engine.extract(
                text=self._build_user_prompt(
                    message=message,
                    case_topic=case_topic,
                    history_messages=history_messages,
                ),
                system_prompt=prompt.system_prompt,
                output_schema=ExtractionClaims,
                temperature=0.0,
                max_tokens=900,
                model=self.call_model_config.model_for(EXTRACTION_CALL) if self.call_model_config is not None else None,
                call_name=EXTRACTION_CALL,
                prompt_name=prompt.name,
                prompt_version=prompt.version,
            )
        except Exception as exc:
            log_event(
                "extraction.medical.fallback_used",
                layer="application",
                reason=type(exc).__name__,
            )
            return None

        log_event(
            "extraction.medical.completed",
            layer="application",
            observation_count=len(result.observations),
            has_topic_signal=result.topic_signal is not None,
        )
        return self._canonicalize_claims(result)

    def _build_user_prompt(
        self,
        *,
        message: str,
        case_topic: str | None,
        history_messages: list[dict[str, str]] | None,
    ) -> str:
        history_lines = []
        for item in history_messages or []:
            role = (item.get("role") or "unknown").strip()
            content = (item.get("content") or "").strip()
            if content:
                history_lines.append(f"- {role}: {content}")
        history_text = "\n".join(history_lines[-4:]) if history_lines else "- none"
        return (
            f"Aktiver Fallrahmen: {case_topic or 'none'}\n"
            f"Letzte Konversation:\n{history_text}\n"
            f"Letzte Nutzernachricht:\n{message}"
        )

    def _heuristic_extract(self, *, message: str) -> ExtractionClaims:
        normalized = self._normalize(message)
        subject_claims = self._subject_claims(normalized)
        observations: list[ObservationClaim] = []
        seen: set[tuple[str, str]] = set()
        for pattern, observation_type, label in self._OBSERVATION_PATTERNS:
            if pattern in normalized:
                key = (observation_type, label or pattern)
                if key in seen:
                    continue
                seen.add(key)
                observations.append(
                    ObservationClaim(
                        type=observation_type,  # type: ignore[arg-type]
                        label=label or pattern.title(),
                        normalized_concept=(label or pattern).casefold(),
                        subject_ref=subject_claims.get("relation", "unclear"),  # type: ignore[arg-type]
                        negated=self._is_negated(message, pattern),
                        attributes=self._attributes_for_pattern(normalized, pattern, observation_type),
                        source_span=pattern,
                    )
                )
        generic_pain = self._generic_pain_claim(normalized, subject_claims)
        if generic_pain is not None and (generic_pain.type, generic_pain.label) not in seen:
            observations.append(generic_pain)
        topic_signal = self._topic_signal(normalized, observations)
        return ExtractionClaims(
            topic_signal=topic_signal,
            subject_claims=subject_claims,
            observations=observations,
        )

    def _canonicalize_claims(self, claims: ExtractionClaims) -> ExtractionClaims:
        for observation in claims.observations:
            observation.attributes = self._canonicalize_attributes(observation.attributes)
        return claims

    @staticmethod
    def _canonicalize_attributes(attributes: dict[str, object]) -> dict[str, object]:
        canonical: dict[str, object] = {}
        for key, value in attributes.items():
            target_key = {
                "duration": "duration_or_onset",
                "free_description": "description",
            }.get(key, key)
            canonical[target_key] = value
        return canonical

    def _generic_pain_claim(self, normalized: str, subject_claims: dict[str, object]) -> ObservationClaim | None:
        if "schmerzen" not in normalized:
            return None
        label = "Schmerzen"
        if "huefte" in normalized or "hüfte" in normalized or "hÃ¼fte" in normalized:
            label = "Hueftschmerzen"
        elif "bauch" in normalized:
            label = "Bauchschmerzen"
        elif "brust" in normalized:
            label = "Brustschmerzen"
        elif "kopf" in normalized:
            label = "Kopfschmerzen"
        return ObservationClaim(
            type="symptom" if label != "Hueftschmerzen" else "injury",
            label=label,
            normalized_concept=label.casefold(),
            subject_ref=subject_claims.get("relation", "unclear"),  # type: ignore[arg-type]
            negated=False,
            attributes=self._attributes_for_pattern(normalized, label.casefold(), "symptom"),
            source_span=label,
        )

    def _attributes_for_pattern(self, normalized: str, pattern: str, observation_type: str) -> dict[str, object]:
        attributes: dict[str, object] = {}
        duration = self._extract_duration(normalized)
        if duration:
            attributes["duration_or_onset"] = duration
        severity = self._extract_severity(normalized)
        if severity is not None:
            attributes["severity"] = severity
        body_site = self._extract_body_site(normalized)
        if body_site:
            attributes["body_site"] = body_site
        if observation_type == "injury":
            mechanism = self._extract_mechanism(normalized)
            if mechanism:
                attributes["mechanism"] = mechanism
            if "kaum auftreten" in normalized:
                attributes["functional_limitation"] = "kaum auftreten"
        if pattern in {"fieber"}:
            attributes["kind"] = "temperature"
        return attributes

    @staticmethod
    def _extract_duration(normalized: str) -> str | None:
        match = re.search(r"(seit [^,.!?]+)", normalized)
        if match:
            return match.group(1).strip()
        if "heute" in normalized:
            return "seit heute"
        if "gestern" in normalized:
            return "seit gestern"
        return None

    @staticmethod
    def _extract_severity(normalized: str) -> int | str | None:
        if "sehr stark" in normalized:
            return "sehr stark"
        if "stark" in normalized:
            return "stark"
        if "kaum" in normalized:
            return "deutlich"
        digits = re.search(r"\b([1-9]|10)/10\b", normalized)
        if digits:
            return int(digits.group(1))
        return None

    @staticmethod
    def _extract_body_site(normalized: str) -> str | None:
        for token, label in (
            ("kopf", "Kopf"),
            ("bauch", "Bauch"),
            ("brust", "Brust"),
            ("huefte", "Huefte"),
            ("hüfte", "Huefte"),
            ("hÃ¼fte", "Huefte"),
            ("bein", "Bein"),
            ("arm", "Arm"),
            ("hals", "Hals"),
        ):
            if token in normalized:
                return label
        return None

    @staticmethod
    def _extract_mechanism(normalized: str) -> str | None:
        if "gestuerzt" in normalized or "gestürzt" in normalized or "gestÃ¼rzt" in normalized or "gefallen" in normalized:
            return "Sturz"
        if "umgeknickt" in normalized:
            return "Umknicken"
        return None

    @staticmethod
    def _subject_claims(normalized: str) -> dict[str, object]:
        if "mein kind" in normalized or "meine tochter" in normalized or "mein sohn" in normalized:
            return {"relation": "child"}
        if "meine mutter" in normalized or "mein vater" in normalized or "andere person" in normalized:
            return {"relation": "other"}
        if "ich " in normalized or normalized.startswith("ich") or " mir " in normalized:
            return {"relation": "self"}
        return {}

    def _topic_signal(self, normalized: str, observations: list[ObservationClaim]) -> str | None:
        if "sturz" in normalized or "gefallen" in normalized:
            body_site = self._extract_body_site(normalized)
            if body_site == "Huefte":
                return "Sturz auf die Huefte"
            if body_site == "Bauch":
                return "Sturz auf den Bauch"
            if body_site == "Kopf":
                return "Sturz auf den Kopf"
            return f"Sturz an {body_site}" if body_site else "Sturz"
        if observations:
            return observations[0].label
        return None

    @staticmethod
    def _is_negated(message: str, pattern: str) -> bool:
        normalized = message.casefold()
        return any(f"{prefix} {pattern}" in normalized for prefix in ("kein", "keine", "keinen", "ohne"))

    @staticmethod
    def _normalize(message: str) -> str:
        normalized = (
            message.casefold()
            .replace("\u00e4", "ae")
            .replace("\u00f6", "oe")
            .replace("\u00fc", "ue")
            .replace("\u00df", "ss")
            .replace("\u00c3\u00a4", "ae")
            .replace("\u00c3\u00b6", "oe")
            .replace("\u00c3\u00bc", "ue")
            .replace("\u00c3\u009f", "ss")
        )
        return " ".join(normalized.split())
