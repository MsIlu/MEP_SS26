"""
Medical Rule Engine

Prüft Texte auf medizinische Red-Flags (Notfall-Symptome)
und gibt bei Treffer eine Warnung zurück.
"""

# -------------------------
# 1. REGELN (DATEN)
# -------------------------

medical_rules = [
    {
        "keywords_all": ["brustschmerzen","atemnot"],
        "message": "⚠️ Möglicher Notfall: Bitte sofort 112 anrufen."
    },
    {
        "keywords_all": ["druck", "brust"],
        "message": "⚠️ Kreislaufproblem möglich. Bei starken Symptomen 112 rufen."
    },
    {
        "keywords_all": ["lähmung"],
        "keywords_any": ["einseitig","seite"],
        "message": "⚠️ Möglicher neurologischer Notfall. Sofort 112 anrufen."
    },
    {
        "keywords_all": ["schwellung"],
        "keywords_any": ["gesicht", "hals"],
        "message": "⚠️ Allergische Reaktion möglich. Bei Atemnot 112 rufen.",
    },
    {
        "keywords_all": ["allergie", "atemnot"],
        "message": "⚠️ Schwere allergische Reaktion möglich. Sofort 112 rufen."
    },
]

# -------------------------
# 2. REGEL-ENGINE
# -------------------------

def detect_medical_red_flags(user_input: str) -> str | None:
    """
    Prüft einen Text auf medizinische Red-Flags.

    Args:
        user_input (str): Eingabetext des Nutzers

    Returns:
        str | None (Return Type Hint):
            Warnmeldung bei erkanntem Notfall, sonst None
    """
    text = user_input.lower()

    for rule in medical_rules:

        # AND-Bedingung: alle Keywords müssen enthalten sein
        if "keywords_all" in rule:
            if not all(keyword in text for keyword in rule["keywords_all"]):
                continue

        # OR-Bedingung: mindestens ein Keyword muss enthalten sein
        if "keywords_any" in rule:
            if not any(keyword in text for keyword in rule["keywords_any"]):
                continue

        # Regel erfüllt --> Rückgabe der Warnung
        return rule["message"]
    return None