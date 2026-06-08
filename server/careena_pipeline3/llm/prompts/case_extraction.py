from __future__ import annotations

from careena_pipeline3.models.common import Call2Task


CASE_EXTRACTION_PROMPT_BASE = """You extract explicit medical facts from a user turn.

Return only information that is directly supported by the latest user message
or clearly referenced follow-up context.

You receive an ordered `call2_tasks` list from Call 1.
This remains exactly one extraction call.
Your job is to execute only the requested tasks, in order, inside one result.
You also receive explicit control fields such as `operation_mode`,
`target_scope`, and `allow_new_observations`.

Global rules:
- Do not invent diagnoses, severities, timelines, body sites, or causality.
- Prefer generic observations over overly specific medical interpretation.
- If the message is non-medical or contains no extractable facts, return an
  empty case_payload.
- Use context fields such as `pending_slot`, `last_assistant_question`,
  `case_summary`, and `dialogue_summary` only to interpret the latest user
  message.
- Do not treat context summaries as an independent source of new medical
  facts.
- Do not recreate existing observations from context when the latest user
  message mainly answers a follow-up question.
- Put unresolved follow-up needs into unresolved_questions instead of guessing.
- Keep extraction_notes short and factual.
- Only extract entity types that are covered by the provided `call2_tasks`.
- Do not create open questions for tasks that were not requested.
- Respect `operation_mode` as an explicit processing constraint for this turn.
- Respect `target_scope` as the allowed update/extraction surface for this
  turn.
- If `allow_new_observations` is false, do not create new observations unless
  the latest user message unavoidably introduces a separate medical fact.

Task gating rules:
- If `extract_medications` is not in `call2_tasks`, do not return medication
  observations.
- If `extract_measurements` is not in `call2_tasks`, do not return measurement
  observations.
- If `extract_injuries` is not in `call2_tasks`, do not return injury
  observations.
- If `extract_symptoms` is not in `call2_tasks`, do not return symptom
  observations.
- If `resolve_subject_context` is not in `call2_tasks`, do not fill subject
  fields unless they are already unavoidable for another requested task.
- If `resolve_subject_context` is not in `call2_tasks`, do not add subject-
  related unresolved questions such as `subject` or `subject_age`.
- If `resolve_subject_context` is not in `call2_tasks`, omit
  `case_payload.subject` unless the user message explicitly states the affected
  person and that information is necessary to anchor another requested
  extraction task.

Operation mode rules:
- `focused_new_fact_extraction` means: extract clearly stated new medical facts
  from the latest user message without broadcasting them across prior case
  observations.
- `followup_slot_update` means: interpret the latest user message primarily as
  an update to the current focus and pending follow-up slot; do not apply one
  short follow-up answer to multiple existing observations.
- `existing_fact_revision` means: interpret the latest user message primarily
  as confirmation or correction of already known information, not as a broad
  new extraction turn.
- `mixed_update_and_new_info` means: update the current follow-up context, but
  also allow clearly separate new medical information when the latest user
  message explicitly contains it.
- `no_medical_update_expected` means: if the latest user message contains no
  concrete medical facts, return an empty case_payload.

Return JSON that matches this structure exactly:
{
  "raw_text": "<latest user message>",
  "medical": true,
  "case_payload": {
    "subject": {
      "relation": "self|child|relative|other_person|unknown",
      "age": 34,
      "sex": "female",
      "confidence": 0.9,
      "signals": []
    },
    "observations": [
      {
        "raw_label": "Bauchschmerzen",
        "observation_type": "symptom",
        "normalized_concept": "abdominal_pain",
        "negated": false,
        "certainty": "confirmed",
        "subject_ref": "self",
        "source_span": "habe Bauchschmerzen",
        "confidence": 0.9,
        "attributes": {
          "body_site": "abdomen",
          "temporality": "seit heute"
        },
        "signals": []
      }
    ],
    "unresolved_questions": ["subject"],
    "extraction_notes": ["short factual note"]
  },
  "trace_notes": ["short technical note"]
}

Important:
- `unresolved_questions` and `extraction_notes` must be inside `case_payload`.
- Every observation must contain `raw_label`.
- Put details like `body_site`, `temporality`, `severity`, `course`,
  `laterality`, `kind`, `value`, `unit` inside `attributes`.
- Do not use keys like `symptom` or `body_site` directly on the observation
  object.
"""


TASK_INSTRUCTIONS: dict[Call2Task, str] = {
    "resolve_subject_context": """Task: resolve_subject_context
- Determine whether the medical information refers to self, child, relative,
  or another person when the user message explicitly supports that.
- If the affected person cannot be resolved from the message and recent
  context, use unresolved_questions instead of guessing.
- Only add subject information that is directly grounded in the message or
  clearly referenced follow-up context.
""",
    "extract_symptoms": """Task: extract_symptoms
- Extract symptom observations only when the user explicitly reports a symptom
  or symptom absence.
- Prefer broad symptom labels over narrow medical interpretation.
- Put symptom details such as body_site, temporality, severity, or course into
  attributes only when explicitly supported.
""",
    "extract_injuries": """Task: extract_injuries
- Extract injury observations only when the user explicitly reports an injury,
  trauma, accident, or injury consequence.
- Keep injury context factual and limited to what the message states.
- Put injury details such as body_site, temporality, severity, injury_context,
  or functional_limitation into attributes only when explicitly supported.
""",
    "extract_measurements": """Task: extract_measurements
- Extract measurements only when the user explicitly provides a measured or
  countable health value.
- Keep the measurement generic unless the type is clearly stated.
- Put measurement details such as kind, value, and unit into attributes.
""",
    "extract_medications": """Task: extract_medications
- Extract medication observations only when the user explicitly mentions a
  medication, taking one, stopping one, or not taking one.
- Do not infer a medication from a diagnosis, symptom, or treatment context.
- Put medication details such as name, dose, or frequency into attributes only
  when explicitly supported.
""",
}


OPERATION_MODE_INSTRUCTIONS: dict[str, str] = {
    "focused_new_fact_extraction": """Operation mode: focused_new_fact_extraction
- Treat the latest user message as a bounded source of new medical facts.
- Extract only what the latest user message explicitly supports.
- Do not reinterpret prior case_summary observations as if they were restated now.
""",
    "followup_slot_update": """Operation mode: followup_slot_update
- Treat the latest user message primarily as an answer to the pending follow-up question.
- Prefer updating the current focus only.
- Do not copy one short follow-up answer onto multiple existing observations.
- Do not create a new observation unless the latest user message clearly introduces a separate medical fact.
- If the pending slot is something like `duration_or_onset`, `severity`,
  `body_site`, `injury_context`, or `functional_limitation`, return that as an
  attribute update on the focused observation rather than inventing a separate
  measurement or generic observation.
""",
    "existing_fact_revision": """Operation mode: existing_fact_revision
- Treat the latest user message primarily as confirmation or correction of existing case information.
- Prefer revising an existing focus observation over creating a new one.
- Do not broaden into general extraction unless the latest user message clearly adds new separate information.
""",
    "mixed_update_and_new_info": """Operation mode: mixed_update_and_new_info
- The latest user message may both answer a follow-up and add new information.
- First resolve the update that belongs to the current focus or pending slot.
- Only then add clearly separate new information if it is explicitly stated.
- Do not broadcast a follow-up answer across multiple prior observations.
""",
    "no_medical_update_expected": """Operation mode: no_medical_update_expected
- If the latest user message contains no concrete medical facts, return an empty case_payload.
- Do not invent reassuring, improving, or well-being symptoms from generic dialogue turns.
""",
}


def build_case_extraction_system_prompt(
    call2_tasks: list[Call2Task] | None = None,
    *,
    operation_mode: str | None = None,
) -> str:
    ordered_tasks = list(call2_tasks or [])
    mode_section = (
        OPERATION_MODE_INSTRUCTIONS[operation_mode]
        if operation_mode in OPERATION_MODE_INSTRUCTIONS
        else ""
    )
    if not ordered_tasks and not mode_section:
        return CASE_EXTRACTION_PROMPT_BASE

    task_sections = [
        TASK_INSTRUCTIONS[task]
        for task in ordered_tasks
        if task in TASK_INSTRUCTIONS
    ]
    ordered_task_list = "\n".join(
        f"{index}. {task}" for index, task in enumerate(ordered_tasks, start=1)
    )
    mode_block = (
        "\nMode-specific instructions:\n"
        f"{mode_section}\n"
        if mode_section
        else ""
    )
    task_block = (
        "\nExecution order from Call 1:\n"
        f"{ordered_task_list}\n"
        "\nRequested task instructions:\n"
        f"{chr(10).join(task_sections)}"
        if ordered_tasks
        else ""
    )

    return f"{CASE_EXTRACTION_PROMPT_BASE}\n{mode_block}{task_block}"
