#server/red_flags/catalog_loader
# loads red flag catalor from server/data/red_flags_de.json
import json
from pathlib import Path


def load_red_flag_catalog() -> dict:
    """
    Lädt den Red-Flag-Katalog aus red_flags/data/red_flags_de.json.
    """

    red_flags_dir = Path(__file__).resolve().parent
    catalog_path = red_flags_dir / "data" / "red_flags_de.json"

    with catalog_path.open("r", encoding="utf-8") as file:
        return json.load(file)