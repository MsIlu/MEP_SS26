from __future__ import annotations

import re

from careena4.domain.case import CaseManager
from careena4.models.domain import CaseExtension, CaseTopic, MedicalCase, Observation


class CaseFrameRefiner:
    _BODY_SITE_BY_LABEL = (
        ("hueft", "Huefte"),
        ("hÃ¼ft", "Huefte"),
        ("bauch", "Bauch"),
        ("brust", "Brust"),
        ("kopf", "Kopf"),
        ("hals", "Hals"),
        ("bein", "Bein"),
        ("arm", "Arm"),
    )

    def __init__(self, *, case_manager: CaseManager | None = None) -> None:
        self.case_manager = case_manager or CaseManager()

    def refine(self, *, case_topic: CaseTopic | None, medical_case: MedicalCase | None) -> CaseTopic | None:
        if case_topic is None:
            return None
        return self.case_manager.update_topic_projection(
            case_topic=case_topic,
            extensions=self._build_extensions(case_topic=case_topic, medical_case=medical_case),
            current_label=self._build_current_label(case_topic=case_topic),
        )

    def _build_extensions(self, *, case_topic: CaseTopic, medical_case: MedicalCase | None) -> list[CaseExtension]:
        extensions: list[CaseExtension] = []
        seen: set[tuple[str, str]] = set()
        if medical_case is not None:
            for observation in self.case_manager.active_observations(medical_case=medical_case):
                self._append_observation_extensions(
                    extensions=extensions,
                    seen=seen,
                    observation=observation,
                )
            relation = self.case_manager.person_relation(medical_case=medical_case)
            if relation != "unclear":
                self._append_extension(
                    extensions=extensions,
                    seen=seen,
                    kind="subject_scope",
                    value=relation,
                    source="subject_state",
                    confidence=1.0,
                    related_observation_id=None,
                )
        return extensions

    def _append_observation_extensions(
        self,
        *,
        extensions: list[CaseExtension],
        seen: set[tuple[str, str]],
        observation: Observation,
    ) -> None:
        for key, value in (
            ("body_site", observation.body_site),
            ("duration_or_onset", observation.onset),
            ("description", observation.description),
        ):
            if value in (None, "", []):
                continue
            self._append_extension(
                extensions=extensions,
                seen=seen,
                kind=key,
                value=str(value),
                source="observation_attribute",
                confidence=0.9 if observation.is_central() else 0.7,
                related_observation_id=observation.observation_id,
            )
        if observation.body_site in (None, ""):
            body_site = self._body_site_from_label(observation.label)
            if body_site is not None:
                self._append_extension(
                    extensions=extensions,
                    seen=seen,
                    kind="body_site",
                    value=body_site,
                    source="observation_label",
                    confidence=0.6,
                    related_observation_id=observation.observation_id,
                )

    @staticmethod
    def _append_extension(
        *,
        extensions: list[CaseExtension],
        seen: set[tuple[str, str]],
        kind: str,
        value: str,
        source: str,
        confidence: float | None,
        related_observation_id: str | None,
    ) -> None:
        key = (kind, value.casefold())
        if key in seen:
            return
        seen.add(key)
        extensions.append(
            CaseExtension(
                kind=kind,  # type: ignore[arg-type]
                value=value,
                source=source,  # type: ignore[arg-type]
                confidence=confidence,
                related_observation_id=related_observation_id,
            )
        )

    def _build_current_label(self, *, case_topic: CaseTopic) -> str:
        extension_map = self._extension_map(self.case_manager.topic_extensions(case_topic=case_topic))
        label = self._build_symptom_label(case_topic=case_topic, extension_map=extension_map)
        normalized = " ".join(label.split())
        return normalized[:80].rstrip(", ")

    @staticmethod
    def _extension_map(extensions: list[CaseExtension]) -> dict[str, str]:
        result: dict[str, str] = {}
        for extension in extensions:
            result.setdefault(extension.kind, extension.value)
        return result

    def _build_symptom_label(self, *, case_topic: CaseTopic, extension_map: dict[str, str]) -> str:
        body_site = extension_map.get("body_site")
        duration = self._duration_fragment(extension_map.get("duration_or_onset"))
        label = self.case_manager.topic_initial_label(case_topic=case_topic) or ""
        if body_site and body_site.casefold() not in label.casefold():
            label = f"{label} {self._symptom_body_phrase(body_site)}"
        if duration and duration.casefold() not in label.casefold():
            label = f"{label} {duration}"
        return label

    @staticmethod
    def _symptom_body_phrase(body_site: str) -> str:
        return {
            "Huefte": "an der Huefte",
            "Brust": "in der Brust",
            "Bauch": "im Bauch",
            "Kopf": "am Kopf",
            "Hals": "im Hals",
            "Bein": "im Bein",
            "Arm": "im Arm",
        }.get(body_site, f"an der {body_site}")

    def _body_site_from_label(self, label: str) -> str | None:
        normalized = label.casefold()
        for token, body_site in self._BODY_SITE_BY_LABEL:
            if token in normalized:
                return body_site
        return None

    @staticmethod
    def _clean_fragment(value: str | None) -> str | None:
        if value in (None, ""):
            return None
        return str(value).strip().rstrip(".!?")

    def _duration_fragment(self, value: str | None) -> str | None:
        cleaned = self._clean_fragment(value)
        if cleaned is None:
            return None
        if cleaned and cleaned[0].isupper():
            return cleaned[0].lower() + cleaned[1:]
        return cleaned

    def tokens_for_topic(self, case_topic: CaseTopic | None) -> set[str]:
        return self.case_manager.topic_tokens(case_topic=case_topic)
