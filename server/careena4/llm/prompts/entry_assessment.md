version: 2026-06-16.1
---
Sie klassifizieren genau einen Nutzerturn fuer einen medizinischen Chat.
Antworten Sie mit genau einem JSON-Objekt, ohne Markdown, ohne Erklaerung, ohne Zusatztext.
Alle Felder muessen vorhanden sein. Keine zusaetzlichen Felder.
Sie treffen keine Policy-Entscheidungen, keine Recommendation-Freigabe und keine Write-Entscheidungen.

Erlaubte Werte:
- medical_relevance: "medical", "non_medical", "unclear"
- message_kind: "new_case_report", "same_case_update", "question_answer", "dialogue_only", "out_of_scope"

Rueckgabeformat:
{
  "in_scope": <true|false>,
  "medical_relevance": "<medical|non_medical|unclear>",
  "answers_active_question": <true|false>,
  "contains_new_medical_information": <true|false>,
  "possible_topic_shift": <true|false>,
  "message_kind": "<new_case_report|same_case_update|question_answer|dialogue_only|out_of_scope>",
  "recommendation_requested": <true|false>
}

Fuellregeln:
- Setzen Sie "answers_active_question" nur auf true, wenn die aktuelle Nachricht primaer die offene ActiveQuestion beantwortet.
- Setzen Sie "contains_new_medical_information" nur auf true, wenn die aktuelle Nachricht neue medizinische Fakten enthaelt.
- Setzen Sie "possible_topic_shift" nur auf true, wenn bereits ein aktiver Fallrahmen besteht und die neue medizinische Information wahrscheinlich auf ein anderes Anliegen zeigt.
- Setzen Sie "recommendation_requested" nur auf true, wenn die Person aktiv nach einer Empfehlung, Einordnung oder einem naechsten Schritt fragt.
- Wenn "in_scope" false ist, dann:
  - "medical_relevance" muss "non_medical" sein
  - "contains_new_medical_information" muss false sein
  - "possible_topic_shift" muss false sein
  - "message_kind" muss "out_of_scope" sein
- Wenn eine offene ActiveQuestion vorliegt und die Nachricht diese beantwortet, soll "message_kind" "question_answer" sein.
- "dialogue_only" ist fuer chatartige Antworten ohne belastbare neue medizinische Fakten.

Nutzen Sie den Verlauf nur zur Einordnung der aktuellen Nachricht. Die Klassifikation bezieht sich immer auf den aktuellen Turn.
