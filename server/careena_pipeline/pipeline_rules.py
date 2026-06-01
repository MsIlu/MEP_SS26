import unicodedata

FOLLOWUP_QUESTIONS = {
    "subject_age": "Wie alt ist die betroffene Person?",
    "duration_or_onset": "Seit wann bestehen die Beschwerden?",
    "injury_context": "Wie ist es dazu gekommen, zum Beispiel durch Sturz, Stoß, Unfall oder Sport?",
    "severity": "Wie stark sind die Beschwerden auf einer Skala von 0 bis 10?",
    "functional_limitation": "Können Sie auftreten, stehen oder das betroffene Bein belasten?",
    "main_complaint": "Welche gesundheitliche Beschwerde steht gerade im Vordergrund?",
    "subject": "Geht es um Sie selbst oder um eine andere Person?",
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


def question_for_slot(missing_information: str) -> str:
    return FOLLOWUP_QUESTIONS.get(
        missing_information,
        "Welche wichtige Information fehlt noch zu den Beschwerden?",
    )


def user_requests_recommendation(text: str) -> bool:
    return contains_any(text, _RECOMMENDATION_REQUEST_MARKERS)
