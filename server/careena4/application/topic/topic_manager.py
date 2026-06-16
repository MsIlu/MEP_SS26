import re

from careena4.models.domain import CaseTopic, MedicalCase
from careena4.models.turn import ExtractionClaims


class TopicManager:
    def ensure_topic(
        self,
        *,
        existing_topic: CaseTopic | None,
        medical_case: MedicalCase | None,
        claims: ExtractionClaims | None,
        latest_message: str,
        turn_id: str | None,
    ) -> CaseTopic | None:
        if existing_topic is not None:
            return existing_topic
        label = None
        if claims is not None and claims.topic_signal:
            label = claims.topic_signal
        elif claims is not None and claims.observations:
            label = claims.observations[0].label
        elif medical_case is not None and medical_case.observations:
            label = medical_case.observations[0].label
        else:
            label = self._message_topic_label(latest_message)
        if label is None:
            return None
        return CaseTopic(
            initial_label=label,
            current_label=label,
            topic_type=self._topic_type(label),
            subject_scope=self._subject_scope(claims),
            status="active",
            confidence=0.7,
            opened_at_turn=turn_id,
        )

    def evaluate_topic_fit(self, *, case_topic: CaseTopic | None, message: str, claims: ExtractionClaims | None) -> str:
        if case_topic is None:
            return "fits"
        topic_tokens = case_topic.search_tokens()
        if claims is not None:
            claim_tokens = self._claim_tokens(claims)
            if claim_tokens and topic_tokens.intersection(claim_tokens):
                return "fits"
            if claim_tokens:
                return "mismatch"
        message_tokens = self._text_tokens(message)
        if topic_tokens.intersection(message_tokens):
            return "fits"
        if message_tokens:
            return "mismatch"
        return "unclear"

    @staticmethod
    def _claim_tokens(claims: ExtractionClaims) -> set[str]:
        tokens: set[str] = set()
        for claim in claims.observations:
            tokens.update(TopicManager._text_tokens(claim.label))
            for value in claim.attributes.values():
                if value in (None, "", []):
                    continue
                tokens.update(TopicManager._text_tokens(str(value)))
        return tokens

    @staticmethod
    def _text_tokens(text: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-zA-ZaeoeuessäöüÄÖÜ]+", text.casefold())
            if len(token) > 2
        }

    @staticmethod
    def _message_topic_label(message: str) -> str | None:
        stripped = message.strip()
        if not stripped:
            return None
        return stripped[:80]

    @staticmethod
    def _topic_type(label: str) -> str:
        normalized = label.casefold()
        if any(token in normalized for token in ("sturz", "verletz", "huefte", "hüfte", "umgeknickt", "gefallen")):
            return "injury_case"
        if any(token in normalized for token in ("medikament", "tablette", "ibuprofen")):
            return "medication_case"
        if any(token in normalized for token in ("schmerz", "fieber", "husten", "atem", "bruch", "druck")):
            return "symptom_case"
        return "unclear_medical_case"

    @staticmethod
    def _subject_scope(claims: ExtractionClaims | None) -> str:
        if claims is None:
            return "unclear"
        relation = claims.subject_claims.get("relation")
        if relation in {"self", "child", "other", "unclear"}:
            return relation
        return "unclear"
