from typing import Literal


ResponseMode = Literal[
    "emergency",
    "confirm_information",
    "ask_safety_question",
    "ask_followup",
    "guide_next_step",
    "recommend",
    "out_of_scope",
    "cannot_assess",
    "continue",
    "not_implemented",
]

IntentCategory = Literal[
    "symptom_report",
    "emergency",
    "administrative",
    "general_health_question",
    "smalltalk",
    "not_medical",
]

ExtractionProfile = Literal["default"]

Call2Task = Literal[
    "resolve_subject_context",
    "extract_symptoms",
    "extract_injuries",
    "extract_measurements",
    "extract_medications",
]

Call2OperationMode = Literal[
    "focused_new_fact_extraction",
    "followup_slot_update",
    "existing_fact_revision",
    "mixed_update_and_new_info",
    "no_medical_update_expected",
]

ObservationType = Literal[
    "symptom",
    "medication",
    "diagnosis",
    "injury",
    "measurement",
    "risk_factor",
    "concern",
    "administrative",
    "observation",
]

Urgency = Literal[
    "unknown",
    "self_observation",
    "routine",
    "soon",
    "today",
    "emergency",
]

UrgencyAssessment = Literal[
    "low",
    "medium",
    "high",
    "emergency",
    "unclear",
]

CareLevel = Literal[
    "self_care",
    "pharmacy",
    "general_practice",
    "specialist",
    "116117",
    "emergency_department",
    "112",
    "unknown",
]

Specialty = Literal[
    "unknown",
    "general_practice",
    "orthopedics",
    "dermatology",
    "neurology",
    "ent",
    "emergency_medicine",
]

ObservationStatus = Literal[
    "extracted",
    "user_confirmed",
    "user_corrected",
    "user_rejected",
]

ProvenanceSource = Literal[
    "user_message",
    "user_confirmation",
    "system_inference",
    "red_flag_rule",
]

SubjectRelation = Literal[
    "self",
    "child",
    "relative",
    "other_person",
    "unknown",
]

RecommendationGateAction = Literal[
    "ask_followup",
    "confirm_information",
    "recommend",
]

MessageRole = Literal[
    "new_information",
    "answer_to_followup",
    "confirmation",
    "correction",
    "recommendation_request",
    "topic_shift",
    "non_medical",
]

DialogueTopicStatus = Literal[
    "single_topic",
    "possible_topic_shift",
    "ambiguous",
]

PlannerModule = Literal[
    "topic_disambiguation",
    "requirement_resolution",
    "confirmation_check",
    "recommendation_readiness",
    "single_followup_generation",
    "routing_recommendation",
]
