from careena_pipeline.models import Subject


class SubjectDetector:
    """
    Lightweight subject detection for the current prototype.

    This catches common phrasing before richer LLM-based subject extraction is
    added to the CaseUpdate schema.
    """

    def detect(self, text: str) -> Subject:
        lowered = text.lower()
        padded = f" {lowered} "

        if self._contains(lowered, ["mein kind", "meine tochter", "mein sohn"]):
            return Subject(relation="child", description="child", confidence=0.8)

        if self._contains(
            lowered,
            ["meine mutter", "mein vater", "meine oma", "mein opa", "meine frau", "mein mann"],
        ):
            return Subject(relation="relative", description="relative", confidence=0.75)

        if self._contains(lowered, ["jemand", "eine person", "ein mann", "eine frau"]):
            return Subject(relation="other_person", description="other person", confidence=0.65)

        if self._contains(padded, [" ich ", " mir ", " mich ", " meine ", " mein "]):
            return Subject(relation="self", description="user", confidence=0.8)

        return Subject(relation="unknown", confidence=0.0)

    @staticmethod
    def _contains(text: str, markers: list[str]) -> bool:
        return any(marker in text for marker in markers)
