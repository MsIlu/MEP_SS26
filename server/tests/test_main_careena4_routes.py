from datetime import date
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from appointments.schemas import AppointmentSearchResponse, FhirAppointment
from careena4.models.domain.case import MedicalCase
from careena4.models.domain.dialogue import ActiveQuestion, ConversationState
from careena4.models.domain.recommendation import RecommendationState
from careena4.models.turn.input import DiaryEntry
import main
from main import (
    app,
    careena4_session_profiles,
    careena4_session_store,
    careena4_turn_engine,
    careena4_simulation_runner,
)


@pytest.fixture(autouse=True)
def clear_careena4_state():
    careena4_session_profiles.clear()
    careena4_session_store._sessions.clear()
    main.careena4_session_case_profiles.clear()
    main.careena4_session_unbound_cases.clear()
    main.careena4_llm_health_status.update(
        {
            "available": False,
            "model": main.careena4_services.call_model_config.default_model,
            "checked_at": None,
        }
    )

    yield

    careena4_session_profiles.clear()
    careena4_session_store._sessions.clear()
    main.careena4_session_case_profiles.clear()
    main.careena4_session_unbound_cases.clear()


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(main, "create_db_and_tables", lambda: None)
    monkeypatch.setattr(
        main.careena4_services.llm_client,
        "is_model_available",
        lambda model: True,
    )

    def override_get_session():
        yield SimpleNamespace()

    app.dependency_overrides[main.get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def _fake_turn_result(response_text: str = "Okay."):
    return SimpleNamespace(
        response_text=response_text,
        response_mode="ask_followup",
        trace_notes=[],
        recommendation_result=None,
        current_turn_understanding=None,
        symptom_input_draft=None,
        medical_case=None,
        conversation_state=SimpleNamespace(
            active_question=None,
        ),
        recommendation_state=RecommendationState(
            recommendation_allowed=False,
        ),
    )


def test_guest_session_can_be_created(client: TestClient):
    response = client.post("/session", json={})

    assert response.status_code == 200
    session_id = response.json()["session_id"]

    assert session_id
    assert careena4_session_profiles[session_id] is None


def test_server_health_endpoint_reports_ok(client):
    response = client.get("/health/server")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "server": True}


def test_llm_health_endpoint_reports_cached_ok(client):
    response = client.get("/health/llm")

    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "ok"
    assert payload["llm"] is True
    assert payload["model"] == main.careena4_services.call_model_config.default_model
    assert payload["checked_at"] is not None


def test_llm_health_endpoint_reports_unavailable(client, monkeypatch):
    monkeypatch.setattr(
        main.careena4_services.llm_client,
        "is_model_available",
        lambda model: False,
    )
    client.post("/warmup")

    response = client.get("/health/llm")

    payload = response.json()
    assert response.status_code == 503
    assert payload["detail"]["message"] == "LLM service is not reachable."
    assert payload["detail"]["model"] == main.careena4_services.call_model_config.default_model
    assert payload["detail"]["checked_at"] is not None


def test_llm_health_endpoint_does_not_call_llm(client, monkeypatch):
    def fail_if_called(model):
        raise AssertionError("health endpoint must only read the cached status")

    monkeypatch.setattr(
        main.careena4_services.llm_client,
        "is_model_available",
        fail_if_called,
    )

    response = client.get("/health/llm")

    assert response.status_code == 200


def test_warmup_refreshes_cached_llm_status(client, monkeypatch):
    monkeypatch.setattr(
        main.careena4_services.llm_client,
        "is_model_available",
        lambda model: False,
    )

    response = client.post("/warmup")

    payload = response.json()
    assert response.status_code == 200
    assert payload["status"] == "unavailable"
    assert payload["llm"] is False

    response = client.get("/health/llm")

    assert response.status_code == 503


def test_guest_input_draft_can_be_read(client: TestClient):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    response = client.get(f"/input-drafts/{session_id}")

    assert response.status_code == 200
    assert response.json()["session_id"] == session_id
    assert response.json()["symptoms"] == []
    assert response.json()["chips"] == []


def test_profile_session_requires_auth(client: TestClient):
    response = client.post("/session", json={"profile_id": 1})

    assert response.status_code == 401


def test_chat_unknown_session_returns_404(client: TestClient):
    response = client.post(
        "/chatscreen",
        json={
            "session_id": "unknown-session",
            "message": "Ich habe Kopfschmerzen.",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Chat session not found."


def test_guest_chat_uses_careena4_turn_engine(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    calls = []

    def fake_run_turn(turn_input):
        calls.append(turn_input)
        return _fake_turn_result("Careena4 Antwort.")

    monkeypatch.setattr(careena4_turn_engine, "run_turn", fake_run_turn)

    response = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "Ich habe Kopfschmerzen.",
        },
    )

    assert response.status_code == 200
    assert response.json()["response"] == "Careena4 Antwort."
    assert response.json()["red_flag"] is False
    assert len(calls) == 1


def test_self_message_replays_with_active_profile_without_profile_question(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]
    careena4_session_profiles[session_id] = 1

    app.dependency_overrides[main.get_optional_current_account] = (
        lambda: SimpleNamespace(id=7)
    )


def _fake_diary_entry() -> DiaryEntry:
    return DiaryEntry(
        date="2026-07-01",
        symptom="Kopfschmerzen",
        body_area="Kopf",
        intensity=4,
        note="seit gestern",
    )
    monkeypatch.setattr(main, "get_profile_access_role", lambda **kwargs: "owner")

    def fake_list_profiles(*, current_user, session):
        assert current_user.id == 7
        return [
            SimpleNamespace(
                id=1,
                display_name="Anna",
                profile_type="self",
                date_of_birth=date(2000, 4, 12),
                biological_sex="female",
            ),
            SimpleNamespace(
                id=2,
                display_name="Ben",
                profile_type="child",
                date_of_birth=date(2015, 8, 20),
                biological_sex="male",
            ),
        ]

    monkeypatch.setattr("profiles.service.list_profiles", fake_list_profiles)
    monkeypatch.setattr(
        main,
        "_load_diary_history",
        lambda profile_id, current_user, session: [_fake_diary_entry()] if profile_id == 1 else [],
    )

    def _turn_result(
        *,
        response_text: str,
        medical_case: MedicalCase,
        active_question: ActiveQuestion | None = None,
    ):
        return SimpleNamespace(
            response_text=response_text,
            response_mode="ask_followup",
            trace_notes=[],
            recommendation_result=None,
            current_turn_understanding=None,
            symptom_input_draft=None,
            medical_case=medical_case,
            conversation_state=ConversationState(active_question=active_question),
            recommendation_state=RecommendationState(recommendation_allowed=False),
            turn_interpretation=None,
        )

    replay_inputs: list[tuple[str, int, str, int | None, str | None]] = []

    def fake_run_turn(turn_input):
        medical_case = turn_input.persisted_medical_case or MedicalCase()
        replay_inputs.append(
            (
                turn_input.message,
                len(turn_input.diary_history),
                medical_case.person.relation,
                medical_case.person.age,
                medical_case.person.sex,
            )
        )
        if len(replay_inputs) == 1:
            medical_case.person.relation = "self"
            return _turn_result(
                response_text="Wie alt bist du?",
                medical_case=medical_case,
                active_question=ActiveQuestion(
                    kind="followup",
                    question_intent="person_age",
                    prompt_text="Wie alt bist du?",
                    blocking=True,
                ),
            )
        assert len(replay_inputs) == 2
        assert medical_case.person.relation == "self"
        assert medical_case.person.age == 26
        assert medical_case.person.sex == "female"
        return _turn_result(
            response_text="Weiter mit Symptomen.",
            medical_case=medical_case,
        )

    monkeypatch.setattr(careena4_turn_engine, "run_turn", fake_run_turn)

    response = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "Ich habe seit gestern Kopfschmerzen.",
        },
    )

    assert response.status_code == 200
    assert response.json()["response"] == "Weiter mit Symptomen."
    assert response.json()["pending_followup"] is None
    assert replay_inputs == [
        ("Ich habe seit gestern Kopfschmerzen.", 0, "unclear", None, None),
        ("Ich habe seit gestern Kopfschmerzen.", 1, "self", 26, "female"),
    ]


def test_safety_bypass_profile_selection_replays_deferred_medical_message(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    app.dependency_overrides[main.get_optional_current_account] = (
        lambda: SimpleNamespace(id=7)
    )

    def fake_list_profiles(*, current_user, session):
        assert current_user.id == 7
        return [
            SimpleNamespace(
                id=1,
                display_name="Anna",
                profile_type="self",
                date_of_birth=date(2000, 4, 12),
                biological_sex="female",
            ),
            SimpleNamespace(
                id=2,
                display_name="Ben",
                profile_type="child",
                date_of_birth=date(2015, 8, 20),
                biological_sex="male",
            ),
        ]

    monkeypatch.setattr("profiles.service.list_profiles", fake_list_profiles)
    monkeypatch.setattr(main, "_load_diary_history", lambda profile_id, current_user, session: [])

    def fake_detect(message):
        return SimpleNamespace(
            requires_safety_clarification=message == "Ich habe Brustschmerzen.",
            requires_emergency_response=False,
            trace_notes=[],
        )

    monkeypatch.setattr(careena4_turn_engine.raw_red_flag_detector, "detect", fake_detect)

    replay_inputs: list[tuple[str, int | None, str | None]] = []

    def _turn_result(
        *,
        response_text: str,
        response_mode: str,
        medical_case: MedicalCase,
        active_question: ActiveQuestion | None = None,
    ):
        return SimpleNamespace(
            response_text=response_text,
            response_mode=response_mode,
            trace_notes=[],
            recommendation_result=None,
            current_turn_understanding=None,
            symptom_input_draft=None,
            medical_case=medical_case,
            conversation_state=ConversationState(active_question=active_question),
            recommendation_state=RecommendationState(recommendation_allowed=False),
            turn_interpretation=None,
        )

    def fake_run_turn(turn_input):
        medical_case = turn_input.persisted_medical_case or MedicalCase()
        replay_inputs.append(
            (
                turn_input.message,
                medical_case.person.age,
                medical_case.person.sex,
            )
        )
        if turn_input.message == "Ich habe Brustschmerzen." and len(replay_inputs) == 1:
            return _turn_result(
                response_text="Notfall?",
                response_mode="ask_safety_question",
                medical_case=medical_case,
                active_question=ActiveQuestion(
                    kind="safety_clarification",
                    question_intent="free_description",
                    prompt_text="Ist das ein Notfall?",
                    blocking=True,
                ),
            )
        if turn_input.message == "Nein":
            return _turn_result(
                response_text="Okay.",
                response_mode="ask_followup",
                medical_case=medical_case,
            )
        if turn_input.message == "Anna":
            return _turn_result(
                response_text="Profil ausgewaehlt.",
                response_mode="ask_followup",
                medical_case=medical_case,
            )
        if turn_input.message == "Ich habe Brustschmerzen." and len(replay_inputs) == 4:
            assert medical_case.person.relation == "self"
            assert medical_case.person.age == 26
            assert medical_case.person.sex == "female"
            return _turn_result(
                response_text="Weiter mit Symptomen.",
                response_mode="ask_followup",
                medical_case=medical_case,
            )
        raise AssertionError(f"unexpected turn input: {turn_input.message}")

    monkeypatch.setattr(careena4_turn_engine, "run_turn", fake_run_turn)

    first = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "Ich habe Brustschmerzen.",
        },
    )
    assert first.status_code == 200
    assert first.json()["response"] == "Notfall?"

    second = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "Nein",
        },
    )
    assert second.status_code == 200
    assert second.json()["pending_followup"]["question_intent"] == "person_profile_selection"
    assert "Anfrage" in second.json()["response"]

    third = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "Anna",
        },
    )
    assert third.status_code == 200
    assert third.json()["response"] == "Weiter mit Symptomen."
    assert third.json()["pending_followup"] is None
    assert replay_inputs == [
        ("Ich habe Brustschmerzen.", None, None),
        ("Nein", None, None),
        ("Anna", None, None),
        ("Ich habe Brustschmerzen.", 26, "female"),
    ]


def test_safety_bypass_self_message_replays_without_profile_question(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]
    careena4_session_profiles[session_id] = 1

    app.dependency_overrides[main.get_optional_current_account] = (
        lambda: SimpleNamespace(id=7)
    )
    monkeypatch.setattr(main, "get_profile_access_role", lambda **kwargs: "owner")

    def fake_list_profiles(*, current_user, session):
        assert current_user.id == 7
        return [
            SimpleNamespace(
                id=1,
                display_name="Anna",
                profile_type="self",
                date_of_birth=date(2000, 4, 12),
                biological_sex="female",
            ),
            SimpleNamespace(
                id=2,
                display_name="Ben",
                profile_type="child",
                date_of_birth=date(2015, 8, 20),
                biological_sex="male",
            ),
        ]

    monkeypatch.setattr("profiles.service.list_profiles", fake_list_profiles)
    monkeypatch.setattr(
        main,
        "_load_diary_history",
        lambda profile_id, current_user, session: [_fake_diary_entry()] if profile_id == 1 else [],
    )

    replay_inputs: list[tuple[str, int, str, int | None, str | None]] = []

    def _turn_result(
        *,
        response_text: str,
        response_mode: str,
        medical_case: MedicalCase,
        active_question: ActiveQuestion | None = None,
    ):
        return SimpleNamespace(
            response_text=response_text,
            response_mode=response_mode,
            trace_notes=[],
            recommendation_result=None,
            current_turn_understanding=None,
            symptom_input_draft=None,
            medical_case=medical_case,
            conversation_state=ConversationState(active_question=active_question),
            recommendation_state=RecommendationState(recommendation_allowed=False),
            turn_interpretation=None,
        )

    def fake_run_turn(turn_input):
        medical_case = turn_input.persisted_medical_case or MedicalCase()
        replay_inputs.append(
            (
                turn_input.message,
                len(turn_input.diary_history),
                medical_case.person.relation,
                medical_case.person.age,
                medical_case.person.sex,
            )
        )
        if len(replay_inputs) == 1:
            medical_case.person.relation = "self"
            return _turn_result(
                response_text="Ist das ein Notfall?",
                response_mode="ask_safety_question",
                medical_case=medical_case,
                active_question=ActiveQuestion(
                    kind="safety_clarification",
                    question_intent="free_description",
                    prompt_text="Ist das ein Notfall?",
                    blocking=True,
                ),
            )
        if len(replay_inputs) == 2:
            assert turn_input.message == "Nein"
            assert medical_case.person.relation == "self"
            return _turn_result(
                response_text="Okay.",
                response_mode="ask_followup",
                medical_case=medical_case,
            )
        assert len(replay_inputs) == 3
        assert turn_input.message == "Ich habe Brustschmerzen."
        assert medical_case.person.relation == "self"
        assert medical_case.person.age == 26
        assert medical_case.person.sex == "female"
        return _turn_result(
            response_text="Weiter mit Symptomen.",
            response_mode="ask_followup",
            medical_case=medical_case,
        )

    monkeypatch.setattr(careena4_turn_engine, "run_turn", fake_run_turn)

    first = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "Ich habe Brustschmerzen.",
        },
    )
    assert first.status_code == 200
    assert first.json()["response"] == "Ist das ein Notfall?"

    second = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "Nein",
        },
    )
    assert second.status_code == 200
    assert second.json()["response"] == "Weiter mit Symptomen."
    assert second.json()["pending_followup"] is None
    assert replay_inputs == [
        ("Ich habe Brustschmerzen.", 0, "unclear", None, None),
        ("Nein", 0, "self", None, None),
        ("Ich habe Brustschmerzen.", 1, "self", 26, "female"),
    ]


def test_chat_simrun_uses_simulation_runner_shortcut(client, monkeypatch):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    def fake_run(request):
        raise AssertionError("simulation runner should be invoked through run_simulation_command")

    def fake_run_simulation_command(*, selector, simulation_runner):
        assert selector == ""
        assert simulation_runner is careena4_simulation_runner
        return "Simulation abgeschlossen.\nStop-Grund: recommend"

    def fake_run_turn(_turn_input):
        raise AssertionError("turn engine must not receive /simrun commands")

    monkeypatch.setattr(careena4_simulation_runner, "run", fake_run)
    monkeypatch.setattr(main, "run_simulation_command", fake_run_simulation_command)
    monkeypatch.setattr(careena4_turn_engine, "run_turn", fake_run_turn)

    response = client.post(
        "/chatscreen",
        json={
            "session_id": session_id,
            "message": "/simrun",
        },
    )

    assert response.status_code == 200
    assert response.json()["response"].startswith("Simulation abgeschlossen.")
    assert response.json()["red_flag"] is False


def test_recommendation_request_unknown_session_returns_404(client: TestClient):
    response = client.post(
        "/recommendation/request",
        json={"session_id": "unknown-session"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Chat session not found."


def test_recommendation_request_uses_careena4_turn_engine(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    calls = []

    def fake_request_recommendation(request_input):
        calls.append(request_input)
        return _fake_turn_result("Empfehlung angefragt.")

    monkeypatch.setattr(
        careena4_turn_engine,
        "request_recommendation",
        fake_request_recommendation,
    )

    response = client.post(
        "/recommendation/request",
        json={"session_id": session_id},
    )

    assert response.status_code == 200
    assert response.json()["response"] == "Empfehlung angefragt."
    assert len(calls) == 1


def test_profile_draft_requires_auth(client):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    careena4_session_profiles[session_id] = 1

    response = client.get(f"/input-drafts/{session_id}")

    assert response.status_code == 401


class FakeMedicalCase(SimpleNamespace):
    def active_observations(self):
        return [
            observation
            for observation in self.observations
            if not getattr(observation, "negated", False)
            and getattr(observation, "status", "reported") != "rejected"
        ]


def _attach_exportable_medical_case(session_id: str):
    careena4_session = careena4_session_store.get(session_id)

    careena4_session.messages.append(
        {
            "role": "user",
            "content": "Ich habe seit gestern Kopfschmerzen.",
        }
    )

    careena4_session.medical_case = FakeMedicalCase(
        case_id="test-case",
        observations=[
            SimpleNamespace(
                observation_id="observation-1",
                type="symptom",
                label="Kopfschmerzen",
                normalized_concept="kopfschmerzen",
                subject_ref="patient",
                negated=False,
                status="reported",
                topic_relation="central",
                attributes={
                    "duration": "seit gestern",
                },
                provenance=[],
            )
        ],
    )

    careena4_session.recommendation_state = SimpleNamespace(
        recommendation_result=SimpleNamespace(
            next_step="Bei anhaltenden Beschwerden hausärztlich abklären lassen.",
            summary="Es liegen ausreichend Angaben vor.",
            urgency_level="low",
            care_level="general_practice",
            specialty="general_practice",
            reasons=["Beschwerden bestehen seit gestern."],
            limitations=[],
        )
    )


def test_fhir_export_unknown_session_returns_404(client):
    response = client.get("/fhir/export/unknown-session")

    assert response.status_code == 404
    assert response.json()["detail"] == "Chat session not found."


def test_fhir_export_session_without_medical_case_returns_409(client):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    response = client.get(f"/fhir/export/{session_id}")

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "No extracted medical case data available for this session."
    )


def test_fhir_export_profile_session_without_auth_returns_401(client):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    careena4_session_profiles[session_id] = 1

    response = client.get(f"/fhir/export/{session_id}")

    assert response.status_code == 401


def test_appointment_search_uses_fhir_bundle_and_hapi_layer(
        client,
        monkeypatch,
):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    _attach_exportable_medical_case(session_id)
    careena4_session_profiles[session_id] = 1

    app.dependency_overrides[main.get_optional_current_account] = (
        lambda: SimpleNamespace(id=7)
    )

    calls = []

    def fake_get_profile_access_role(*, account_id, profile_id, session):
        assert account_id == 7
        assert profile_id == 1
        return "owner"

    def fake_search_fhir_appointments(**kwargs):
        calls.append(kwargs)
        return AppointmentSearchResponse(
            session_id=kwargs["session_id"],
            profile_id=kwargs["profile_id"],
            postal_code=kwargs["postal_code"],
            message="HAPI-FHIR Testtermine",
            recommendation_summary={
                "specialty": "general_practice",
                "care_level": "general_practice",
                "urgency": "low",
                "next_step": "Hausarztlich abklaren lassen.",
            },
            appointments=[
                FhirAppointment(
                    id="hapi-appointment-1",
                    provider_name="Hausarztpraxis Dr. Schneider",
                    specialty="Allgemeinmedizin",
                    address="Musterstrasse 12, 68159 Mannheim",
                    distance_km=2.4,
                    date="2026-07-02",
                    time="09:30",
                    care_type="Vor-Ort-Termin",
                    urgency_match=True,
                )
            ],
        )

    monkeypatch.setattr(
        main,
        "get_profile_access_role",
        fake_get_profile_access_role,
    )
    monkeypatch.setattr(
        main,
        "search_fhir_appointments",
        fake_search_fhir_appointments,
    )

    response = client.post(
        "/appointments/search",
        json={
            "session_id": session_id,
            "profile_id": 1,
            "postal_code": "68159",
        },
    )

    assert response.status_code == 200
    assert response.json()["appointments"][0]["source"] == "hapi-fhir"

    assert calls[0]["session_id"] == session_id
    assert calls[0]["profile_id"] == 1
    assert calls[0]["fhir_bundle"]["resourceType"] == "Bundle"
    assert calls[0]["fhir_bundle"]["type"] == "collection"

    patient = next(
        entry["resource"]
        for entry in calls[0]["fhir_bundle"]["entry"]
        if entry["resource"]["resourceType"] == "Patient"
    )
    assert patient["identifier"][0]["value"] == "1"


@pytest.mark.parametrize(
    "marker, expected_specialty",
    [
        ("Kardiologie", "cardiology"),
        ("Zahnarzt", "dentistry"),
        ("Gastroenterologie", "gastroenterology"),
        ("Augenarzt", "ophthalmology"),
        ("Frauenarzt", "gynecology"),
        ("Kinderarzt", "pediatrics"),
        ("Psychiatrie", "psychiatry"),
        ("Urologie", "urology"),
    ],
)
def test_persisted_recommendation_supports_extended_specialties(
        marker,
        expected_specialty,
):
    recommendation = main._recommendation_from_history(
        recommendation=f"Bitte in einer {marker}-Praxis abklären lassen.",
        next_steps=f"Termin bei {marker} vereinbaren.",
    )

    assert recommendation.specialty == expected_specialty


def test_fhir_export_valid_session_returns_bundle(client):
    session_response = client.post("/session", json={})
    session_id = session_response.json()["session_id"]

    _attach_exportable_medical_case(session_id)

    response = client.get(f"/fhir/export/{session_id}")

    assert response.status_code == 200

    bundle = response.json()
    resources = [entry["resource"] for entry in bundle["entry"]]
    resource_types = [resource["resourceType"] for resource in resources]

    assert bundle["resourceType"] == "Bundle"
    assert "Patient" in resource_types
    assert "QuestionnaireResponse" in resource_types
    assert "Observation" in resource_types
    assert "ServiceRequest" in resource_types

    service_request = next(
        resource
        for resource in resources
        if resource["resourceType"] == "ServiceRequest"
    )

    assert service_request["extension"][0]["valueCode"] == "low"
    assert "hausärztlich" in service_request["note"][0]["text"]
