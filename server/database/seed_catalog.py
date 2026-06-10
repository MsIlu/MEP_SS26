# Author: Cesca
# Created as part of the central Careena medical catalog implementation.
# This script imports versioned catalog seed JSON files into the local database.
#
# Important:
# This script imports reference/demo data only.
# It must not be used for real user medical data.

from __future__ import annotations

import json
from pathlib import Path

from sqlmodel import select

from database.catalog.models import ConsultationReason, utc_now
from database.connection import get_db_session


SEED_FILE = (
    Path(__file__).resolve().parent
    / "seeds"
    / "catalog"
    / "v1"
    / "sts_consultation_reasons.seed.json"
)


def load_seed_file() -> dict:
    """
    Load the STS consultation reason seed file.
    """
    if not SEED_FILE.exists():
        raise FileNotFoundError(f"Seed file not found: {SEED_FILE}")

    with SEED_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def levels_to_json(entry: dict) -> str:
    """
    Convert source STS urgency levels into a stable JSON string.

    STS levels are source metadata only.
    They are not direct Careena runtime decisions.
    """
    levels = entry.get("source_sts_levels_present", [])
    return json.dumps(levels, ensure_ascii=False)


def upsert_consultation_reason(session, *, entry: dict, source: dict) -> str:
    """
    Insert or update one consultation reason by source system, version, and source id.
    """
    source_system = source.get("system", "STS")
    source_version = str(source.get("version", ""))
    source_year = source.get("year")

    source_id = str(entry.get("sts_id") or entry.get("source_id"))

    existing = session.exec(
        select(ConsultationReason)
        .where(ConsultationReason.source_system == source_system)
        .where(ConsultationReason.source_version == source_version)
        .where(ConsultationReason.source_id == source_id)
    ).first()

    if existing is None:
        consultation_reason = ConsultationReason(
            source_system=source_system,
            source_version=source_version,
            source_year=source_year,
            source_id=source_id,
            source_category_de=entry.get("source_category_de"),
            source_label_de=entry["source_label_de"],
            source_sts_levels_present_json=levels_to_json(entry),
            careena_key=entry.get("careena_key"),
            careena_label_de=entry.get("careena_label_de"),
            mapping_status=entry.get("mapping_status", "source_indexed"),
            mapping_notes=entry.get("mapping_notes"),
            is_active=entry.get("is_active", True),
        )
        session.add(consultation_reason)
        return "inserted"

    existing.source_category_de = entry.get("source_category_de")
    existing.source_label_de = entry["source_label_de"]
    existing.source_sts_levels_present_json = levels_to_json(entry)
    existing.careena_key = entry.get("careena_key")
    existing.careena_label_de = entry.get("careena_label_de")
    existing.mapping_status = entry.get("mapping_status", "source_indexed")
    existing.mapping_notes = entry.get("mapping_notes")
    existing.is_active = entry.get("is_active", True)
    existing.updated_at = utc_now()

    session.add(existing)
    return "updated"


def seed_sts_consultation_reasons() -> dict:
    """
    Import all STS consultation reasons from the versioned seed JSON.
    """
    payload = load_seed_file()
    source = payload.get("source", {})
    entries = payload.get("consultation_reasons", [])

    if not entries:
        raise ValueError("Seed file contains no consultation reasons.")

    inserted = 0
    updated = 0

    with get_db_session() as session:
        for entry in entries:
            action = upsert_consultation_reason(
                session,
                entry=entry,
                source=source,
            )
            if action == "inserted":
                inserted += 1
            elif action == "updated":
                updated += 1

        session.commit()

    return {
        "seed_file": str(SEED_FILE),
        "total": len(entries),
        "inserted": inserted,
        "updated": updated,
    }


if __name__ == "__main__":
    result = seed_sts_consultation_reasons()
    print(json.dumps(result, indent=2, ensure_ascii=False))
