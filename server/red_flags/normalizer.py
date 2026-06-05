
def normalize_text(text: str) -> str:
    """
    Normalisiert den übergebenen Text für eine Vergleichbarkeit.
    Wandelt den Text in Kleinbuchstaben um, löst Sonderzeichen auf und bereinigt Whitespaces.
    
    Args: text (str): Der Freitext des Benutzers aus dem Chat.

    Returns: str: Der normalisierte String.
    """
    if not text:
        return ""

    # Kleinschreibung erzwingen
    normalized = text.lower()

    # Zeichenersetzung für das deutsche Umlaute und Whitespaces 
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "-": " ",
        "\n": " ",
        "\t": " "
    }

    for old_value, new_value in replacements.items():
        normalized = normalized.replace(old_value, new_value)

    # Mehrfache Whitespaces trimmen
    return " ".join(normalized.split())