"""Process-wide Careena4 runtime state for the chat endpoints.

Sessions and their profile bindings are kept in memory for the current backend
process. This is acceptable for the demo deployment, but everything here is
reset on backend restart.
"""

from datetime import datetime, timezone

from careena4.application.dialogue.person_initialiser import PersonInitialiser
from careena4.bootstrap import build_default_services, build_simulation_runner

careena4_services = build_default_services(llm_mode="env")
careena4_turn_engine = careena4_services.turn_engine
careena4_session_store = careena4_services.session_store

# session_id -> owning (authenticated active) profile, bound on /session or on
# the first /chatscreen request that carries a profile_id.
careena4_session_profiles: dict[str, int | None] = {}
# session_id -> profile the case is *about* (the "Für wen?" answer), which can
# differ from the session's owning profile above. Kept separate so the session
# still belongs to the authenticated active profile (cross-profile guard),
# while diary, medications and the reported profile follow the chosen person.
careena4_session_case_profiles: dict[str, int] = {}
# session_ids whose "Für wen?" answer resolved to a person with no diary profile
# ("Jemand anderes" or a free-form relation like "meine Oma"). For these the case
# is deliberately *not* bound to any profile, so diary, medications and the
# reported profile must NOT fall back to the active session profile.
careena4_session_unbound_cases: set[str] = set()

careena4_person_initialiser = PersonInitialiser()
careena4_simulation_runner = build_simulation_runner(system_llm_mode="env")

# Cached LLM availability, refreshed by /warmup and by successful turns.
careena4_llm_health_status: dict[str, object] = {
    "available": False,
    "model": careena4_services.call_model_config.default_model,
    "checked_at": None,
}


def refresh_llm_health_status() -> bool:
    """Query the LLM endpoint once and cache the result for /health/llm."""
    checked_model = careena4_services.call_model_config.default_model
    available = careena4_services.llm_client.is_model_available(checked_model)
    careena4_llm_health_status.update(
        {
            "available": available,
            "model": checked_model,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return available


def mark_llm_available() -> None:
    """Record a successful LLM-backed turn in the health cache."""
    careena4_llm_health_status.update(
        {
            "available": True,
            "model": careena4_services.call_model_config.default_model,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
    )
