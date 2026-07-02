"""
Seed-Skript: Testfamilie "Sarah Nowak" anlegen und Token ausgeben.

Lauf: python seed_family_sarah_nowak.py
      (aus dem server/-Verzeichnis, Backend muss laufen)

Liest die Familiendaten aus seed_family_sarah_nowak.json.
Idempotent — kann mehrfach ausgeführt werden.
Gibt am Ende den JWT-Token aus.
"""
import json
import sys
from pathlib import Path

import requests

BASE = "http://localhost:8000"
SEED_FILE = Path(__file__).parent / "seed_family_sarah_nowak.json"

with open(SEED_FILE, "r", encoding="utf-8") as f:
    SEED = json.load(f)

ACCOUNT = SEED["account"]
EXTRA_PROFILES = SEED["extra_profiles"]


def register_or_login() -> str:
    resp = requests.post(f"{BASE}/auth/login", json={
        "email": ACCOUNT["email"],
        "password": ACCOUNT["password"],
    })
    if resp.status_code == 200:
        print("OK Login erfolgreich")
        return resp.json()["access_token"]

    resp = requests.post(f"{BASE}/auth/register", json=ACCOUNT)
    if resp.status_code not in (200, 201):
        print(f"ERR Registrierung fehlgeschlagen: {resp.status_code} {resp.text}")
        sys.exit(1)
    print("OK Neuer Account registriert")
    return resp.json()["access_token"]


def ensure_profiles(token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    existing = requests.get(f"{BASE}/profiles", headers=headers).json()
    existing_names = {p["display_name"] for p in existing}

    for profile in EXTRA_PROFILES:
        if profile["display_name"] in existing_names:
            print(f"  ~{profile['display_name']} existiert bereits")
            continue
        resp = requests.post(f"{BASE}/profiles", json=profile, headers=headers)
        if resp.status_code in (200, 201):
            print(f"  +{profile['display_name']} angelegt")
        else:
            print(f"  ERR {profile['display_name']}: {resp.status_code} {resp.text}")


if __name__ == "__main__":
    token = register_or_login()
    print("\nProfile:")
    ensure_profiles(token)
    print(f"\n{'='*60}")
    print("JWT-Token (gültig 24h):")
    print(token)
    print(f"{'='*60}")
    print("\nCredentials:")
    print(f"  E-Mail:   {ACCOUNT['email']}")
    print(f"  Passwort: {ACCOUNT['password']}")
