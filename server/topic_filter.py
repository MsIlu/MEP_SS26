"""
Topic Filter für die Demo-Anwendung.

Ziel:
Die Anwendung soll nur gesundheitsbezogene Anliegen bearbeiten.
Allgemeiner Smalltalk, technische Fragen oder andere Themen werden freundlich abgelehnt.

Wichtig:
Einzelne Wörter wie "Alter", "Falten" oder "Stress" können im Kontext gesundheitsbezogen sein.
Deshalb wird auch der bisherige Gesprächsverlauf berücksichtigt.
"""

HEALTH_KEYWORDS = [
    # Allgemeine Gesundheitsbegriffe
    "gesundheit", "beschwerde", "beschwerden", "symptom", "symptome",
    "krank", "krankheit", "arzt", "ärztin", "hausarzt", "facharzt",
    "notaufnahme", "notruf", "112", "116117", "medizinisch",

    # Körperbereiche
    "kopf", "bauch", "brust", "rücken", "hals", "bein", "arm", "hand",
    "fuß", "fuss", "auge", "ohr", "nase", "mund", "zahn", "haut",
    "haare", "haar", "herz", "lunge", "magen",

    # Beschwerden / Symptome
    "schmerz", "schmerzen", "atemnot", "fieber", "übelkeit", "uebelkeit",
    "erbrechen", "durchfall", "blutung", "schwindel", "ohnmacht",
    "bewusstlos", "husten", "ausschlag", "juckreiz", "schwellung",
    "lähmung", "laehmung", "taub", "kribbeln", "müde", "muede",
    "müdigkeit", "muedigkeit", "schwach", "schwäche", "schwaeche",

    # Psychische Belastung
    "angst", "panik", "stress", "depressiv", "traurig", "überfordert",
    "ueberfordert", "schlaf", "schlaflos", "sorge", "sorgen",

    # Körperliche Veränderungen / gesundheitsnahe Anliegen
    "haarausfall", "haarverlust", "graue haare", "weiße haare",
    "weisse haare", "falten", "hautveränderung", "veraenderung",
    "körper", "koerper", "alter", "älter", "aelter",
]

CLEAR_NON_HEALTH_KEYWORDS = [
    # Technik
    "computer", "laptop", "drucker", "internet", "wlan", "wifi",
    "passwort", "login", "github", "flutter", "python", "code",
    "programmieren", "android studio", "vscode", "pycharm",

    # Schule / Arbeit / Alltag
    "hausaufgabe", "mathe", "übersetze", "uebersetze", "email schreiben",
    "urlaub", "reise", "kochen", "rezept", "wetter", "film", "musik",
    "spiel", "gaming",
]

SMALLTALK_OR_BOREDOM_KEYWORDS = [
    "mir ist langweilig",
    "ich bin gelangweilt",
    "ich will chatten",
    "lass uns chatten",
    "erzähl mir was",
    "erzaehl mir was",
    "unterhalte mich",
    "smalltalk",
]

GREETINGS = [
    "hallo",
    "hi",
    "hey",
    "guten morgen",
    "guten tag",
    "guten abend",
]


OUT_OF_SCOPE_RESPONSE = """Diese Anwendung ist nur für gesundheitsbezogene Anliegen gedacht.

Bitte beschreibe eine körperliche oder psychische Beschwerde, ein Symptom oder eine gesundheitliche Sorge.

Hinweis:
Diese Anwendung ersetzt keine ärztliche Untersuchung und stellt keine Diagnose dar."""


SMALLTALK_GOODBYE_RESPONSE = """Ich verstehe. Diese Anwendung ist nur für gesundheitsbezogene Anliegen gedacht und nicht für allgemeinen Smalltalk.

Wenn du eine körperliche oder psychische Beschwerde, ein Symptom oder eine gesundheitliche Sorge hast, kannst du diese gerne beschreiben.

Alles Gute."""


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _history_has_health_context(messages: list[dict]) -> bool:
    """
    Prüft, ob es im bisherigen Chat bereits um ein gesundheitsbezogenes Thema ging.
    So werden Folgeantworten wie "ich glaube, es kommt vom Alter" nicht fälschlich blockiert.
    """
    recent_messages = messages[-8:]

    for message in recent_messages:
        content = message.get("content", "").lower()
        if _contains_any(content, HEALTH_KEYWORDS):
            return True

    return False


def is_smalltalk_or_boredom(user_input: str) -> bool:
    text = user_input.lower().strip()
    return _contains_any(text, SMALLTALK_OR_BOREDOM_KEYWORDS)


def is_health_related(user_input: str, messages: list[dict] | None = None) -> bool:
    text = user_input.lower().strip()

    if not text:
        return False

    # Begrüßung erlauben, damit der Chat normal starten kann.
    if text in GREETINGS:
        return True

    # Aktuelle Nachricht ist klar gesundheitsbezogen.
    if _contains_any(text, HEALTH_KEYWORDS):
        return True

    # Falls der bisherige Verlauf gesundheitsbezogen war,
    # dürfen kurze Folgeantworten weiterhin durch.
    if messages and _history_has_health_context(messages):
        return True

    # Klare technische/alltägliche Themen blockieren.
    if _contains_any(text, CLEAR_NON_HEALTH_KEYWORDS):
        return False

    # Unklare Nachrichten lieber nicht an das Modell geben.
    return False