import re
import unicodedata


FOLLOWUP_QUESTIONS = {
    "main_complaint": "Welche gesundheitliche Beschwerde steht gerade im Vordergrund?",
    "subject.subject_relation": "Geht es um Sie selbst oder um eine andere Person?",
    "subject.age": "Wie alt ist die betroffene Person?",
    "symptom.duration_or_onset": "Seit wann bestehen die Beschwerden?",
    "injury.duration_or_onset": "Seit wann besteht die Verletzung oder seit wann sind die Beschwerden da?",
    "injury.injury_context": "Wie ist es dazu gekommen, zum Beispiel durch Sturz, Stoss, Unfall oder Sport?",
    "injury.functional_limitation": "Koennen Sie auftreten, stehen oder das betroffene Bein belasten?",
    "symptom.severity": "Wie stark sind die Beschwerden auf einer Skala von 0 bis 10?",
    "injury.severity": "Wie stark sind die Beschwerden auf einer Skala von 0 bis 10?",
    "measurement.kind": "Welcher Messwert wurde gemessen?",
    "measurement.value": "Wie hoch war der gemessene Wert genau?",
}

_QUESTION_PREFIXES = (
    "wie ",
    "was ",
    "wann ",
    "wo ",
    "wer ",
    "welche ",
    "welcher ",
    "welches ",
    "koennen ",
    "konnen ",
    "seit wann",
)

_RECOMMENDATION_REQUEST_MARKERS = (
    "was soll ich tun",
    "was kann ich tun",
    "wo soll ich hin",
    "wohin soll ich",
    "muss ich zum arzt",
    "muss ich ins krankenhaus",
    "muss ich in die notaufnahme",
    "brauche ich einen arzt",
    "soll ich zum arzt",
    "soll ich in die notaufnahme",
    "soll ich den notruf",
    "arzt rufen",
    "notarzt rufen",
    "notruf",
    "112",
    "116117",
    "hausarzt",
    "krankenhaus",
    "notaufnahme",
    "welcher arzt",
    "wo kann ich hingehen",
)

_AFFIRMATIVE_CONFIRMATIONS = {
    "ja",
    "ja klar",
    "ja stimmt",
    "stimmt",
    "genau",
    "korrekt",
    "richtig",
    "so ist es",
}

_NEGATIVE_CONFIRMATIONS = {
    "nein",
    "nicht ganz",
    "stimmt nicht",
    "falsch",
}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()


def contains_any(text: str, markers: tuple[str, ...] | list[str] | set[str]) -> bool:
    normalized_text = normalize_text(text)
    return any(marker in normalized_text for marker in markers)


def starts_with_any(text: str, prefixes: tuple[str, ...] | list[str]) -> bool:
    normalized_text = normalize_text(text).strip()
    return any(normalized_text.startswith(prefix) for prefix in prefixes)


def looks_like_question(text: str) -> bool:
    stripped = text.strip()
    return stripped.endswith("?") or starts_with_any(stripped, _QUESTION_PREFIXES)


def question_for_requirement(requirement: str | None) -> str:
    if not requirement:
        return "Welche wichtige Information fehlt noch zu den Beschwerden?"
    return FOLLOWUP_QUESTIONS.get(
        requirement,
        "Welche wichtige Information fehlt noch zu den Beschwerden?",
    )


def user_requests_recommendation(text: str) -> bool:
    return contains_any(text, _RECOMMENDATION_REQUEST_MARKERS)


def is_affirmative_confirmation(text: str) -> bool:
    normalized = _normalized_reply_token(text)
    return normalized in _AFFIRMATIVE_CONFIRMATIONS


def is_negative_confirmation(text: str) -> bool:
    normalized = _normalized_reply_token(text)
    return normalized in _NEGATIVE_CONFIRMATIONS


def _normalized_reply_token(text: str) -> str:
    normalized = normalize_text(text).strip()
    normalized = re.sub(r"[.!?]+$", "", normalized)
    normalized = " ".join(normalized.split())
    return normalized
