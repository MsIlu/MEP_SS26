from __future__ import annotations

from careena_pipeline3.models.turn import EntryDecision, TurnContext
from careena_pipeline3.models.workflow import RecommendationResult


FOLLOWUP_TEXT_BY_SLOT: dict[str, str] = {
    "subject": "Geht es um Sie selbst oder um eine andere Person?",
    "subject_age": "Wie alt ist die betroffene Person?",
    "duration_or_onset": "Seit wann besteht die Beschwerde?",
    "injury_context": "Wie ist die Verletzung entstanden?",
    "functional_limitation": "Was ist durch die Verletzung eingeschraenkt?",
    "severity": "Wie stark ist die Beschwerde aktuell?",
}


class ResponseTextBuilder:
    """Builds user-facing response text from an already chosen response path."""

    def build(
        self,
        *,
        response_mode: str,
        context: TurnContext,
        entry_decision: EntryDecision,
        recommendation_result: RecommendationResult | None = None,
    ) -> str:
        if response_mode == "emergency":
            return (
                "Wichtiger Hinweis:\n"
                "Ihre Angaben koennen auf eine akute Notfallsituation hindeuten.\n\n"
                "Bitte waehlen Sie sofort den Notruf 112 oder holen Sie umgehend "
                "medizinische Hilfe."
            )

        if response_mode == "out_of_scope":
            return (
                "Ich kann hier nur bei gesundheitsbezogenen Anliegen helfen. "
                "Bitte beschreiben Sie eine gesundheitliche Beschwerde oder Frage."
            )

        if response_mode == "ask_followup":
            followup = context.dialogue_state.pending_followup or context.pending_followup
            if followup is None:
                if context.dialogue_state.recommendation_requested:
                    return (
                        "Fuer eine Empfehlung brauche ich noch eine kurze "
                        "Rueckfrage."
                    )
                return "Ich brauche noch eine kurze Rueckfrage, um weiterzumachen."
            if followup.kind == "conflict":
                focus_label = followup.focus_label or "die Angabe"
                return (
                    f"Ich sehe bei {focus_label} widerspruechliche Angaben. "
                    "Koennen Sie kurz klarstellen, was genau zutrifft?"
                )
            if followup.kind == "disambiguation":
                focus_label = followup.focus_label or "die Angabe"
                return (
                    f"Ich kann {focus_label} noch nicht eindeutig zuordnen. "
                    "Koennen Sie kurz praezisieren, worauf sich Ihre letzte Angabe bezieht?"
                )
            slot = followup.slot
            followup_text = FOLLOWUP_TEXT_BY_SLOT.get(
                slot,
                f"Ich brauche noch eine kurze Rueckfrage zu: {slot}",
            )
            if context.dialogue_state.recommendation_requested:
                return f"Bevor ich eine Empfehlung geben kann: {followup_text}"
            return followup_text

        if response_mode == "cannot_assess":
            if entry_decision.response_mode_hint == "out_of_scope":
                return (
                    "Ich kann hier nur bei gesundheitsbezogenen Anliegen helfen. "
                    "Bitte beschreiben Sie eine gesundheitliche Beschwerde oder Frage."
                )
            if context.dialogue_state.recommendation_requested:
                return (
                    "Ich kann noch keine Empfehlung geben, weil mir dafuer noch "
                    "keine ausreichende medizinische Beschwerde vorliegt. "
                    "Welche gesundheitliche Beschwerde steht gerade im Vordergrund?"
                )
            return (
                "Ich habe noch nicht genug konkrete medizinische Informationen. "
                "Welche gesundheitliche Beschwerde steht gerade im Vordergrund?"
            )

        if response_mode == "recommend":
            if recommendation_result is not None and recommendation_result.summary:
                return (
                    f"{recommendation_result.summary} "
                    "Die eigentliche Recommendation-Strecke ist in "
                    "`careena_pipeline3` aber noch nicht ausgebaut."
                )
            return (
                "Die Empfehlung ist angefordert und die noetigen "
                "Mindestinformationen liegen vor. Die eigentliche "
                "Recommendation-Strecke ist in `careena_pipeline3` aber noch "
                "nicht ausgebaut."
            )

        if response_mode == "guide_next_step":
            return (
                "Gibt es noch weitere Beschwerden? "
                "Wenn nicht, dann antworten Sie kurz mit nein, und ich erstelle "
                "Ihre Empfehlung."
            )

        if response_mode == "confirm_information":
            return (
                "Eine Bestaetigungsstrecke ist vorgesehen, aber in "
                "`careena_pipeline3` noch nicht aktiv eingebunden."
            )

        if response_mode == "continue":
            focus_label = (
                context.medical_case.primary_focus_label()
                if context.medical_case is not None
                else None
            )
            if focus_label:
                return f"Ich habe die Angaben zu {focus_label} aufgenommen."
            return "Verstanden. Ich habe die Angaben aufgenommen."

        return "Die Verarbeitung wurde abgeschlossen."
