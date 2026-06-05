from typing import Any
from models.safety.red_flag import RedFlag

from red_flags.catalog_loader import load_red_flag_catalog
from red_flags.normalizer import normalize_text


def find_matching_keywords(keywords: list[str], normalized_user_input: str) -> list[str]:
    """
    Gibt alle Keywords zurück, die in der Nutzereingabe gefunden wurden.
    """

    matched_keywords = []
    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)

        if normalized_keyword in normalized_user_input:
            matched_keywords.append(keyword)
    return matched_keywords


def match_keyword_groups(keyword_groups: list[list[str]], normalized_user_input: str) -> tuple[bool, list[str]]:
    """
    Prüft Gruppenlogik:
    Jede Gruppe muss mindestens ein passendes Keyword enthalten.

    Beispiel:
    Gruppe 1: ["bauchschmerzen", "bauchweh"]
    Gruppe 2: ["kollaps", "blut", "atemnot"]

    Regel trifft nur, wenn aus JEDER Gruppe mindestens ein Begriff matcht.
    """

    if not keyword_groups:
        return False, []

    all_matched_keywords = []

    for group in keyword_groups:
        matched_keywords_in_group = find_matching_keywords(group, normalized_user_input)

        if not matched_keywords_in_group:
            return False, []

        all_matched_keywords.extend(matched_keywords_in_group)

    return True, all_matched_keywords


def rule_matches(rule: dict, normalized_user_input: str) -> tuple[bool, list[str]]:
    """
    Prüft, ob eine einzelne Red-Flag-Regel zur Nutzereingabe passt.
    """

    match_config = rule.get("match", {})

    keywords_any = match_config.get("keywords_any", [])
    keyword_groups_all = match_config.get("keyword_groups_all", [])

    # 1. Option: ODER-Logik (Irgendein Keyword matcht direkt)
    direct_matches = find_matching_keywords(keywords_any, normalized_user_input)
    if direct_matches:
        return True, direct_matches

    # 2. Option: UND-Logik über die Gruppen hinweg
    groups_match, group_matches = match_keyword_groups(keyword_groups_all, normalized_user_input)
    if groups_match:
        return True, group_matches

    return False, []


def detect_medical_red_flags(user_input: str) -> dict:
    """
    Erkennt Red Flags anhand des Katalogs.
    Die Funktion stellt keine Diagnose.
    Sie prüft nur, ob eine sicherheitsrelevante Regel aus dem Katalog greift.
    Wenn kein Match vorliegt, wird None zurückgegeben.
    
    Pydantic-Sicherheitsmodell (Architektur-Entscheidung):
    -----------------------------------------------------
    Statt eines unüberprüften, nativen Python-Dictionaries wird hier ein voll
    validiertes 'RedFlag'-Pydantic-Objekt zurückgegeben. 
    
    Vorteile für das Gesamtprojekt:
    1. Typensicherheit & Integrität: Verhindert 'Garbage-In, Garbage-Out'. Tippfehler
       in den Attributnamen (z. B. im Server-Rework oder Frontend) werden sofort an 
       der Schnittstelle abgefangen, bevor sie die Datenbank korrumpieren.
    2. Fail-Safe-Prinzip: Durch 'extra="forbid"' im globalen BaseSchema blockiert das
       System unbefugte oder manipulierte Zusatzfelder (Schutz vor Injections).
    3. Entwickler-Komfort: Ermöglicht Autovervollständigung im restlichen
       Backend (z. B. beim PDF-Export) und generiert die interaktive Swagger-API-
       Dokumentation (/docs) vollautomatisch.
    """

    catalog = load_red_flag_catalog()
    defaults = catalog.get("defaults", {})
    normalized_user_input = normalize_text(user_input)

    for rule in catalog.get("rules", []):
        matches, matched_keywords = rule_matches(rule, normalized_user_input)

        if matches:
            return {
                "red_flag": True,
                "rule_id": rule.get("id"),
                "rule_name": rule.get("name"),
                "category": rule.get("category"),
                "severity": rule.get("severity", defaults.get("severity")),
                "action": rule.get("action", defaults.get("action")),
                "block_ai_response": rule.get(
                    "block_ai_response",
                    defaults.get("block_ai_response", True)
                ),
                "message_key": rule.get(
                    "message_key",
                    defaults.get("message_key")
                ),
                "matched_keywords": matched_keywords
            }

    return {
        "red_flag": False,
        "block_ai_response": False
    }