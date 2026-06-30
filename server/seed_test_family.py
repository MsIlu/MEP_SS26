"""
Seed-Skript: Test-Familie anlegen und Token ausgeben.

Lauf: python seed_test_family.py
      (aus dem server/-Verzeichnis, Backend muss laufen)

Idempotent — kann mehrfach ausgeführt werden.
Gibt am Ende den JWT-Token aus.
"""
import sys
import requests

BASE = "http://localhost:8000"

ACCOUNT = {
    "email": "test@careena.dev",
    "password": "Test1234!",
    "display_name": "Tester Testi",
    "date_of_birth": "1990-05-15",
    "biological_sex": "female",
}

EXTRA_PROFILES = [
    {
        "display_name": "Paula",
        "date_of_birth": "1992-03-20",
        "biological_sex": "female",
        "profile_type": "other",
    },
    {
        "display_name": "Paul",
        "date_of_birth": "1988-11-10",
        "biological_sex": "male",
        "profile_type": "other",
    },
    {
        "display_name": "Herbert",
        "date_of_birth": "1955-07-01",
        "biological_sex": "male",
        "profile_type": "other",
    },
]


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
