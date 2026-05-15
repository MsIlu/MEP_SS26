#server/red_flags/normalizer.py
# normalizes german user input tu ensure comparability

def normalize_text(text: str) -> str:


    normalized = text.lower()

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

    return " ".join(normalized.split())