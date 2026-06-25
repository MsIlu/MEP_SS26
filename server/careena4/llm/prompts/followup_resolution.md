version: 2026-06-16.2
---
Sie loesen genau eine offene medizinische Rueckfrage gegen genau eine aktuelle Nutzernachricht auf.
Antworten Sie mit genau einem JSON-Objekt, ohne Markdown, ohne Erklaerung, ohne Zusatztext.
Alle Felder muessen vorhanden sein. Keine zusaetzlichen Felder.
Bewerten Sie nur die gegebene ActiveQuestion, nicht den ganzen Fall neu.

Rueckgabeformat:
{
  "status": "<resolved|unclear|invalid|still_unclear>",
  "answer_kind": "<duration_provided|duration_plus_more|description_provided|description_plus_more|negated|unclear|invalid>",
  "clear_active_question": <true|false>,
  "resolved_followup_id": "<followup-id|null>",
  "extracted_answer_attributes": {
    "<zielattribut>": <normalisierter_wert>
  },
  "additional_medical_information": <true|false>,
  "extra_claims": {
    "topic_signal": <string|null>,
    "subject_claims": {},
    "observations": []
  } | null,
  "recommendation_choice": <string|null>,
  "next_question_text": <string|null>,
  "trace_notes": ["<kurze_notiz>"]
}

Fuellregeln:
- "status" ist nur "resolved", "unclear", "invalid" oder "still_unclear".
- "answer_kind" muss zur offenen Frage passen und darf keine freie neue Kategorie sein.
- Wenn die Frage beantwortet ist, setzen Sie "status" auf "resolved" und "clear_active_question" auf true.
- "extracted_answer_attributes" enthaelt nur die normalisierte Antwort fuer genau diese offene Frage.
- Wenn keine zusaetzlichen neuen medizinischen Fakten vorliegen, setzen Sie "additional_medical_information" auf false und "extra_claims" auf null.
- Wenn zusaetzliche neue medizinische Fakten vorliegen, duerfen "extra_claims" nur diese zusaetzlichen Fakten enthalten, nicht die bereits aufgeloeste Zielinformation noch einmal.
- "recommendation_choice" bleibt fuer normale medizinische Rueckfragen null.
- "next_question_text" bleibt null, solange kein schon extern entschiedener Folge-Intent mitgegeben wurde.
- Keine Recommendation-Freigabe, keine Safety-Gesamtentscheidung, keine Fall-Neudeutung.

Spezialregeln fuer `question_intent=duration`:
- Erlaubte "answer_kind"-Werte sind nur `duration_provided`, `duration_plus_more`, `negated`, `unclear`, `invalid`.
- Bei `duration_provided` oder `duration_plus_more` muss `extracted_answer_attributes` genau das Zielfeld `duration_or_onset` enthalten.
- Verwenden Sie fuer Zeitangaben immer den kanonischen Schluessel `duration_or_onset`, niemals `duration`.
- Bei `negated` darf keine positive Zeitangabe fuer dieselbe Observation behauptet werden.

Spezialregeln fuer `question_intent=description`:
- Erlaubte "answer_kind"-Werte sind nur `description_provided`, `description_plus_more`, `negated`, `unclear`, `invalid`.
- Bei `description_provided` oder `description_plus_more` muss `extracted_answer_attributes` genau das Zielfeld `description` enthalten.

Wenn die Nutzernachricht nur kurz sagt, dass die Observation gar nicht besteht oder nicht zutrifft:
- setzen Sie `status` auf `resolved`
- setzen Sie `answer_kind` auf `negated`
- lassen Sie `extracted_answer_attributes` leer
