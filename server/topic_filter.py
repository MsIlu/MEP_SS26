"""
Topic Filter für die Demo-Anwendung.
Es garantiert, dass nur gesundheitsbezogene Anliegen verarbeitet werden.
Nutzt Keyword-Matching und eine Kontext-Historie als Guard-Rails.
"""
import logging

logger = logging.getLogger(__name__)

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

# Standardisierte Antworttexte als Konstanten
OUT_OF_SCOPE_RESPONSE = ("Diese Anwendung ist nur für gesundheitsbezogene Anliegen gedacht.\n\n"
    "Bitte beschreiben Sie eine körperliche oder psychische Beschwerde, ein Symptom oder eine gesundheitliche Sorge.\n\n"
    "Hinweis:\n"
    "Diese Einschätzung ersetzt keine ärztliche Untersuchung und stellt keine Diagnose dar."
)


SMALLTALK_GOODBYE_RESPONSE = (
    "Ich verstehe. Diese Anwendung ist nur für gesundheitsbezogene Anliegen gedacht und nicht für allgemeinen Smalltalk.\n\n"
    "Wenn Sie eine körperliche oder psychische Beschwerde, ein Symptom oder eine gesundheitliche Sorge haben, "
    "können Sie diese gerne beschreiben.\n\n"
    "Alles Gute."
)


def _contains_any(text: str, keywords: list[str]) -> bool:
    """Hilfsfunktion: Prüft, ob mindestens ein Keyword im Text enthalten ist."""
    return any(keyword in text for keyword in keywords)


def _history_has_health_context(messages: list[dict]) -> bool:
    """Prüft die letzten 8 Nachrichten im Verlauf auf medizinischen Kontext"""
    recent_messages = messages[-8:]
    for message in recent_messages:
        content = message.get("content", "").lower()
        if _contains_any(content, HEALTH_KEYWORDS):
            return True
    return False


def is_smalltalk_or_boredom(user_input: str) -> bool:
    """"Prüft, ob die Eingabe reiner Smalltalk aus Langweile ist. """
    text = user_input.lower().strip()
    return _contains_any(text, SMALLTALK_OR_BOREDOM_KEYWORDS)


def is_health_related(user_input: str, messages: list[dict] | None = None) -> bool:
    """
    Zentrale Guard-Rail-Funktion, welche entscheidet, ob eine Nachricht an die KI weitergeleitet werden darf.
    """
    text = user_input.lower().strip()

    if not text:
        return False

    # Begrüßung zum Chatstart erlaubt
    if text in GREETINGS:
        return True

    # Aktuelle Nachricht ist klar gesundheitsbezogen.
    if _contains_any(text, HEALTH_KEYWORDS):
        return True

    # Kontextprüfung aus dem bisherigen Verlauf
    if messages and _history_has_health_context(messages):
        logger.info("Thema außerhalb der Keywords, aber medizinischer Kontext in Historie erkannt.")
        return True

    # Expliziter Ausschluss bei technischen/alltäglichen Themen
    if _contains_any(text, CLEAR_NON_HEALTH_KEYWORDS):
        logger.info(f"Nachricht blockiert (Technik/Alltag erkannt): '{text}'")
        return False

    # Alles andere im Zweifel blockieren
    return False