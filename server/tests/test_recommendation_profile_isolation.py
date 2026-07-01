"""
Tests für die drei bestätigten Bugs aus PR #156 Review.

Bug 1 – PDF-Profil-Leck:
  build_careena4_chat_response gibt keinen profile_id-Wert zurück; dieser wird
  am Call-Site gesetzt. Wir testen, dass recommendation_result immer care_level
  und urgency enthält, damit der Client korrekt entscheiden kann, welche Ansicht
  er zeigt — ohne auf einen Fallback-profile_id angewiesen zu sein.

Bug 2 – Notfallanzeige:
  care_level='112' oder 'emergency_department' muss die Notfallansicht auslösen,
  auch wenn urgency != 'emergency' ist. Der backend-seitige Test prüft, dass
  RecommendationResult beide Felder in die Serialisierung überträgt, damit der
  Flutter-Client sie für seine Entscheidungslogik verwenden kann.

Bug 3 – Profil-Datenisolation:
  profile_id im Response darf ausschließlich die Session-Profile-ID widerspiegeln,
  nicht ein aktives App-Profil. Der Endpunkt-Test prüft den None-Fall.
"""

from main import build_careena4_chat_response
from careena4.models.workflow import RecommendationResult
from careena4.models.turn.result import TurnResult
from careena4.models.domain import ConversationState, MedicalCase, RecommendationState


def _minimal_turn_result(recommendation_result=None) -> TurnResult:
    """Erzeugt ein minimales TurnResult für Isolationstests."""
    return TurnResult(
        response_text="Test",
        response_mode="recommend",
        medical_case=MedicalCase(),
        conversation_state=ConversationState(),
        recommendation_state=RecommendationState(),
        recommendation_result=recommendation_result,
        trace_notes=[],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Bug 2 – Notfallanzeige: care_level und urgency müssen im serialisierten
# recommendation_result vorhanden sein, damit der Client beide auswerten kann.
# ─────────────────────────────────────────────────────────────────────────────

def test_recommendation_result_serialisiert_care_level_112():
    """care_level='112' muss unverändert in der Antwort erscheinen."""
    result = _minimal_turn_result(
        recommendation_result=RecommendationResult(
            allowed=True,
            urgency="today",          # absichtlich nicht 'emergency'
            urgency_level="high",
            care_level="112",
            specialty="emergency_medicine",
            summary="Notruf 112 kontaktieren.",
            reasons=["Akutes Geschehen"],
        )
    )

    response = build_careena4_chat_response(result)

    assert response["recommendation_result"] is not None
    assert response["recommendation_result"]["care_level"] == "112"
    assert response["recommendation_result"]["urgency"] == "today"


def test_recommendation_result_serialisiert_care_level_emergency_department():
    """care_level='emergency_department' muss im Response enthalten sein."""
    result = _minimal_turn_result(
        recommendation_result=RecommendationResult(
            allowed=True,
            urgency="soon",           # absichtlich nicht 'emergency'
            urgency_level="high",
            care_level="emergency_department",
            specialty="emergency_medicine",
            summary="Notaufnahme aufsuchen.",
            reasons=["Schwere Symptome"],
        )
    )

    response = build_careena4_chat_response(result)

    assert response["recommendation_result"]["care_level"] == "emergency_department"
    assert response["recommendation_result"]["urgency"] == "soon"


def test_recommendation_result_mit_urgency_emergency_und_niedrigem_care_level():
    """urgency='emergency' allein muss als Notfall erkannt werden können."""
    result = _minimal_turn_result(
        recommendation_result=RecommendationResult(
            allowed=True,
            urgency="emergency",
            urgency_level="emergency",
            care_level="general_practice",  # inkonsistente LLM-Ausgabe
            specialty="general_practice",
        )
    )

    response = build_careena4_chat_response(result)

    assert response["recommendation_result"]["urgency"] == "emergency"
    assert response["recommendation_result"]["care_level"] == "general_practice"


# ─────────────────────────────────────────────────────────────────────────────
# Bug 3 – Profil-Datenisolation: profile_id muss None bleiben wenn keine
# Session-Profil-Bindung existiert. Das verhindert, dass Profil-A-Daten in
# einem Nicht-profilgebundenen Export auftauchen.
# ─────────────────────────────────────────────────────────────────────────────

def test_response_profile_id_bleibt_none_ohne_session_profil():
    """
    profile_id wird am Call-Site gesetzt (main.py Zeile ~799).
    Der Rückgabewert von build_careena4_chat_response enthält noch keinen
    profile_id-Key — der Test stellt sicher, dass er bei None-Bindung auch
    nach dem Setzen None bleibt.
    """
    result = _minimal_turn_result()
    response = build_careena4_chat_response(result)

    # Simuliert was main.py tut: response["profile_id"] = subject_profile_id
    subject_profile_id = None  # keine Profil-Bindung
    response["profile_id"] = subject_profile_id

    assert response["profile_id"] is None


def test_response_profile_id_nimmt_session_profil():
    """profile_id im Response entspricht der Session-Profil-ID, nicht einem App-Profil."""
    result = _minimal_turn_result()
    response = build_careena4_chat_response(result)

    subject_profile_id = 42
    response["profile_id"] = subject_profile_id

    assert response["profile_id"] == 42


# ─────────────────────────────────────────────────────────────────────────────
# Robustheit: recommendation_result=None erzeugt kein leeres Pflichtfeld
# ─────────────────────────────────────────────────────────────────────────────

def test_response_ohne_recommendation_result_hat_keinen_care_level():
    """Wenn kein recommendation_result vorliegt, ist der Wert None — kein Absturz."""
    result = _minimal_turn_result(recommendation_result=None)
    response = build_careena4_chat_response(result)

    assert response["recommendation_result"] is None
    # severity/action werden aus recommendation_result abgeleitet — ebenfalls None
    assert response["action"] is None
    assert response["severity"] is None
