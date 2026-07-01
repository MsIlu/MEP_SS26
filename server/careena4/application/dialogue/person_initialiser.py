"""Initialises the person context for a new chat session from profile snapshots.

Responsible for two things:
  1. pre_turn  — on a fresh session, pre-populate MedicalCase.person from
                 profile snapshots and inject a profile-aware
                 person_clarification question when multiple profiles exist.
  2. post_turn — after run_turn(), match the user's message against the
                 stored profile map to apply demographic data; detect and
                 retry mistyped profile names.
"""
from __future__ import annotations

from careena4.models.domain import MedicalCase
from careena4.models.domain.dialogue import ActiveQuestion, ConversationState
from careena4.models.domain.guided_input import (
    GuidedInputContract,
    GuidedInputMode,
    GuidedInputOption,
)
from careena4.models.turn.input import ProfileSnapshot

_MAX_BUTTON_PROFILES = 4

# Words that signal a free-form description of a non-profile person.
# If the user's message contains any of these, the LLM's resolution is accepted
# rather than treating the input as a failed profile-name match.
_RELATION_HINT_WORDS = {
    "meine", "mein", "meinen", "meiner", "eine", "einen", "einer",
    "jemand", "jemanden", "für", "andere", "anderen", "anderes",
    "freund", "freundin", "oma", "opa", "kollege", "kollegin",
    "nachbar", "nachbarin", "bruder", "schwester", "mann", "frau",
}

_GENERIC_ANSWERS = {"jemand anderes", "jemand anderen", "andere person"}

# label -> (profile_id, relation, age, sex)
_PersonData = tuple[int | None, str, int | None, str | None]


def _map_relation(profile_type: str) -> str:
    if profile_type == "self":
        return "self"
    if profile_type == "child":
        return "child"
    return "other"


def _is_name_attempt(message: str) -> bool:
    """True when the message looks like a mistyped profile name rather than
    a free-form description of a non-profile person (e.g. 'meine Oma')."""
    words = message.strip().casefold().split()
    return len(words) <= 3 and not any(w in _RELATION_HINT_WORDS for w in words)


def _build_person_clarification(
    prompt: str,
    known_names: list[str],
    *,
    allows_additional_medical_info: bool,
) -> ActiveQuestion:
    options: list[GuidedInputOption] = [
        GuidedInputOption(code=f"profile:{i}", label=name)
        for i, name in enumerate(known_names[:_MAX_BUTTON_PROFILES])
    ]
    options.append(GuidedInputOption(code="other", label="Jemand anderes"))
    return ActiveQuestion(
        kind="person_clarification",
        question_intent="person_profile_selection",
        prompt_text=prompt,
        blocking=True,
        allows_additional_medical_info=allows_additional_medical_info,
        guided_input=GuidedInputContract(
            mode=GuidedInputMode.STRUCTURED_REQUIRED,
            free_text_allowed=True,
            options=options,
        ),
    )


class PersonInitialiser:
    """Translates profile snapshots into Careena4 session person state."""

    def __init__(self) -> None:
        # session_id -> {display_name -> (relation, age, sex)}
        self._person_map: dict[str, dict[str, _PersonData]] = {}
        # Holds the first medical message while profile selection is pending
        self._pending_message: dict[str, str] = {}

    def pre_turn(
        self,
        *,
        session_id: str,
        careena4_session,
        profiles: list[ProfileSnapshot],
        pending_message: str | None = None,
    ) -> bool:
        """Called before run_turn() on a fresh medical case.

        Single profile: silently pre-fills person data, no question needed.
        Multiple profiles: injects a profile-aware person_clarification question
          and stores pending_message so the caller can skip run_turn.

        Returns True when the caller should skip run_turn (profile selection
        is being shown; message will be processed after selection).
        """
        if careena4_session.medical_case is not None:
            return False
        if not profiles:
            return False

        person_map: dict[str, _PersonData] = {
            p.display_name: (p.id, _map_relation(p.profile_type), p.age, p.sex)
            for p in profiles
        }
        person_map["Jemand anderes"] = (None, "other", None, None)
        self._person_map[session_id] = person_map

        if len(profiles) == 1:
            p = profiles[0]
            mc = MedicalCase()
            mc.person.relation = _map_relation(p.profile_type)
            mc.person.age = p.age
            mc.person.sex = p.sex
            careena4_session.medical_case = mc
            return False
        else:
            known_names = [p.display_name for p in profiles]
            if careena4_session.conversation_state is None:
                careena4_session.conversation_state = ConversationState()
            careena4_session.conversation_state.active_question = (
                _build_person_clarification(
                    "Für wen ist diese Anfrage?",
                    known_names,
                    allows_additional_medical_info=False,
                )
            )
            if pending_message:
                self._pending_message[session_id] = pending_message
            return True

    def post_turn(
        self,
        *,
        session_id: str,
        careena4_session,
        message: str,
    ) -> tuple[str | None, list[str], str | None, int | None, bool]:
        """Called after run_turn() and persist.

        Returns (warning_text, reply_options, pending_message, matched_profile_id,
        resolved_non_profile).
        - warning_text: non-None when person_clarification must be retried
        - reply_options: button labels for the retry
        - pending_message: the deferred medical message to process next
        - matched_profile_id: DB id of the profile the user selected, so the
          caller can re-key the session to that profile (diary/medications)
        - resolved_non_profile: True when the "Für wen?" step was answered with a
          person that has no profile ("Jemand anderes" or a free-form relation).
          The case is then bound to nobody, so the caller must not fall back to
          the active profile's diary/medication/PDF data.
        """
        person_map = self._person_map.get(session_id)
        if not person_map or careena4_session.medical_case is None:
            return None, [], None, None, False

        mc_person = careena4_session.medical_case.person
        msg_lower = message.strip().casefold()
        is_generic = msg_lower in _GENERIC_ANSWERS

        matched: _PersonData | None = None
        if not is_generic:
            matched = next(
                (
                    v for k, v in person_map.items()
                    if k != "Jemand anderes" and k.casefold() == msg_lower
                ),
                None,
            )

        pending = self._pending_message.pop(session_id, None)

        if matched is not None:
            profile_id, rel, age, sex = matched
            mc_person.relation = rel
            if age is not None:
                mc_person.age = age
            if sex is not None:
                mc_person.sex = sex
            self._person_map.pop(session_id, None)
            return None, [], pending, profile_id, False

        if is_generic:
            mc_person.relation = "other"
            self._person_map.pop(session_id, None)
            return None, [], pending, None, True

        if _is_name_attempt(message):
            mc_person.relation = "unclear"
            mc_person.age = None
            mc_person.sex = None
            known_names = [k for k in person_map if k != "Jemand anderes"]
            names_str = ", ".join(known_names)
            warning = (
                f'Den Namen "{message.strip()}" konnte ich keinem deiner Profile zuordnen.'
                + (f" Bekannte Profile: {names_str}." if names_str else "")
                + " Bitte waehle eine Option oder tippe den Namen erneut ein."
            )
            question = _build_person_clarification(
                warning, known_names, allows_additional_medical_info=False
            )
            if careena4_session.conversation_state is None:
                careena4_session.conversation_state = ConversationState()
            careena4_session.conversation_state.active_question = question
            reply_options = [opt.label for opt in question.guided_input.options]
            # Re-save the pending message — user still hasn't resolved selection
            if pending:
                self._pending_message[session_id] = pending
            return warning, reply_options, None, None, False

        # Free-form non-profile person ("meine Oma") — accept silently.
        mc_person.relation = "other"
        self._person_map.pop(session_id, None)
        return None, [], pending, None, True

    def inject_deferred_clarification(
        self,
        *,
        session_id: str,
        careena4_session,
        profiles: list[ProfileSnapshot],
    ) -> ActiveQuestion | None:
        """Injects profile clarification when the safety bypass skipped pre_turn.

        Single profile: applies demographic data to the existing MedicalCase, returns None.
        Multi-profile: builds person_map, sets active_question, returns the question.
        Must be called AFTER post_turn() so 'Nein' is not matched as a profile name.
        """
        if not profiles:
            return None
        if len(profiles) == 1:
            p = profiles[0]
            mc = careena4_session.medical_case
            if mc is not None:
                mc.person.relation = _map_relation(p.profile_type)
                if p.age is not None:
                    mc.person.age = p.age
                if p.sex is not None:
                    mc.person.sex = p.sex
            return None
        person_map: dict[str, _PersonData] = {
            p.display_name: (p.id, _map_relation(p.profile_type), p.age, p.sex)
            for p in profiles
        }
        person_map["Jemand anderes"] = (None, "other", None, None)
        self._person_map[session_id] = person_map
        known_names = [p.display_name for p in profiles]
        if careena4_session.conversation_state is None:
            careena4_session.conversation_state = ConversationState()
        question = _build_person_clarification(
            "Für wen ist diese Anfrage?",
            known_names,
            allows_additional_medical_info=False,
        )
        careena4_session.conversation_state.active_question = question
        return question
