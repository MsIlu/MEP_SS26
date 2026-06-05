
import json
from pathlib import Path
from typing import Any 

"""
Lädt den Red-Flag-Katalog aus red_flags/data/red_flags_de.json.
"""

def load_red_flag_catalog() -> dict:
    
    red_flags_dir = Path(__file__).resolve().parent
    catalog_path = red_flags_dir / "data" / "red_flags_de.json"

    if not catalog_path.exists():
        raise FileNotFoundError(
            f"Kritischer Systemfehler: Der Red-Flag-Katalog wurde unter {catalog_path} nicht gefunden!"
        )

    with catalog_path.open("r", encoding="utf-8") as file:
        return json.load(file)