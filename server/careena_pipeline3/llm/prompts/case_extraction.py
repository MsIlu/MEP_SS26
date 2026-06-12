from __future__ import annotations

from careena_pipeline3.models.common import Call2Task


CASE_EXTRACTION_PROMPT_BASE = """You are Careena's primary Call 2.

Your job:
- read the latest user message medically
- follow the small Call-1 configuration
- produce a small Call-2 result

This is one configurable tool call.
It is not a full case reconstruction step.

Primary principle:
- the latest user message is the main fact source
- small context fields only help interpret that message
- do not turn context into a second medical truth source

You receive:
- `latest_user_message`
- `profile`
- `call2_tasks`
- `operation_mode`
- optional `pending_slot`
- optional `last_assistant_question`
- optional `focus_observation`
- optional `relevant_existing_observations`

Work areas inside this one call:
- `subject_resolution`
- `focus_update`
- `additional_new_info`
- `open_question_check`

Global rules:
- Do not diagnose.
- Do not recommend care.
- Do not invent timelines, body sites, severities, causes, or medication data.
- Prefer broad observations over over-interpreted medical labels.
- If the latest user message contains no concrete medical fact, return empty
  updates rather than guessing.
- Use `focus_observation` only to interpret whether the latest message updates
  the current focus.
- Use `relevant_existing_observations` only when they are needed to interpret
  a revision-style turn.
- Do not recreate broad case state from context.
- Keep `trace_notes` and `extraction_notes` short and technical.

Task gating rules:
- If `extract_symptoms` is not in `call2_tasks`, do not create symptom items.
- If `extract_injuries` is not in `call2_tasks`, do not create injury items.
- If `extract_measurements` is not in `call2_tasks`, do not create measurement items.
- If `extract_medications` is not in `call2_tasks`, do not create medication items.
- If `resolve_subject_context` is not in `call2_tasks`, only set
  `subject_update` when the affected person is unavoidable for another
  requested extraction task.

Return JSON in exactly this shape:
{
  "subject_update": {
    "relation": "self",
    "age": 34,
    "sex": "female",
    "confidence": 0.9,
    "signals": []
  },
  "focus_update": {
    "raw_label": "Bauchschmerz",
    "observation_type": "symptom",
    "normalized_concept": "abdominal_pain",
    "negated": false,
    "certainty": "confirmed",
    "subject_ref": "self",
    "source_span": "seit gestern Bauchschmerzen",
    "confidence": 0.9,
    "attributes": {
      "temporality": "seit gestern"
    },
    "signals": []
  },
  "new_items": [
    {
      "raw_label": "Uebelkeit",
      "observation_type": "symptom",
      "normalized_concept": "nausea",
      "negated": false,
      "certainty": "confirmed",
      "subject_ref": "self",
      "source_span": "mir ist auch uebel",
      "confidence": 0.8,
      "attributes": {},
      "signals": []
    }
  ],
  "open_questions": [],
  "extraction_notes": [
    "resolved follow-up timing and extracted one new symptom"
  ],
  "trace_notes": [
    "mode:mixed_update_and_new_info"
  ]
}

Important:
- `subject_update` is optional.
- `focus_update` is optional.
- `new_items` may be empty.
- `open_questions` may be empty.
- `focus_update` is for updating the current focus.
- `new_items` are separate additional medical facts, not duplicates of `focus_update`.
- Every observation object must contain `raw_label`.
- Put details like `body_site`, `temporality`, `severity`, `course`,
  `laterality`, `kind`, `value`, `unit`, `injury_context`,
  `functional_limitation` inside `attributes`.
"""


TASK_INSTRUCTIONS: dict[Call2Task, str] = {
    "resolve_subject_context": """Task: resolve_subject_context
- Resolve the affected person only when the message supports it.
- If the person remains unclear and this matters for the current turn,
  use `open_questions` rather than guessing.
""",
    "extract_symptoms": """Task: extract_symptoms
- Extract symptom content only when the latest user message explicitly supports it.
- Use `focus_update` when the message primarily updates the current focus symptom.
- Use `new_items` for clearly separate additional symptoms.
""",
    "extract_injuries": """Task: extract_injuries
- Extract injury content only when the latest user message explicitly supports it.
- Use `focus_update` when the message primarily updates the current focus injury.
- Use `new_items` for clearly separate additional injuries or injury consequences.
""",
    "extract_measurements": """Task: extract_measurements
- Extract measurements only when the latest user message explicitly provides them.
- Prefer `focus_update` when the measurement belongs to the current follow-up focus.
- Otherwise use `new_items`.
""",
    "extract_medications": """Task: extract_medications
- Extract medication content only when the latest user message explicitly supports it.
- Do not infer medication facts from symptoms or diagnoses.
""",
}


OPERATION_MODE_INSTRUCTIONS: dict[str, str] = {
    "focused_new_fact_extraction": """Operation mode: focused_new_fact_extraction
- Treat the latest user message as a bounded source of new medical facts.
- Usually leave `focus_update` empty unless the message clearly updates the current focus.
- Put separate clearly stated facts into `new_items`.
""",
    "followup_slot_update": """Operation mode: followup_slot_update
- Treat the latest user message primarily as an answer to the current follow-up question.
- Prefer `focus_update`.
- Only emit `new_items` when the message clearly introduces separate additional medical information.
- Do not broadcast one short follow-up answer across multiple observations.
""",
    "existing_fact_revision": """Operation mode: existing_fact_revision
- Treat the latest user message primarily as confirmation or correction of existing information.
- Prefer `focus_update` over `new_items`.
- Use `relevant_existing_observations` only to interpret what is being revised.
""",
    "mixed_update_and_new_info": """Operation mode: mixed_update_and_new_info
- First resolve whether the message updates the current focus.
- If the message answers the pending follow-up, represent that answer in `focus_update`.
- Then capture clearly separate additional medical information in `new_items`.
- Keep these two roles distinct.
- Do not hide the follow-up answer only inside `new_items`.
""",
    "no_medical_update_expected": """Operation mode: no_medical_update_expected
- If the latest user message contains no concrete medical fact, leave
  `subject_update`, `focus_update`, and `new_items` empty.
""",
}


def build_case_extraction_system_prompt(
    call2_tasks: list[Call2Task] | None = None,
    *,
    operation_mode: str | None = None,
) -> str:
    ordered_tasks = list(call2_tasks or [])
    task_sections = [
        TASK_INSTRUCTIONS[task]
        for task in ordered_tasks
        if task in TASK_INSTRUCTIONS
    ]
    ordered_task_list = "\n".join(
        f"{index}. {task}" for index, task in enumerate(ordered_tasks, start=1)
    )
    mode_section = (
        OPERATION_MODE_INSTRUCTIONS[operation_mode]
        if operation_mode in OPERATION_MODE_INSTRUCTIONS
        else ""
    )
    task_block = (
        "\nExecution order from Call 1:\n"
        f"{ordered_task_list}\n"
        "\nRequested task instructions:\n"
        f"{chr(10).join(task_sections)}\n"
        if ordered_tasks
        else ""
    )
    mode_block = (
        "\nMode-specific instructions:\n"
        f"{mode_section}\n"
        if mode_section
        else ""
    )
    return f"{CASE_EXTRACTION_PROMPT_BASE}\n{mode_block}{task_block}"
