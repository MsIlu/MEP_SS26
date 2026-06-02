from typing import Literal


ResponseMode = Literal[
    "emergency",
    "confirm_information",
    "ask_followup",
    "recommend",
    "out_of_scope",
    "cannot_assess",
]

IntentCategory = Literal[
    "symptom_report",
    "emergency",
    "administrative",
    "general_health_question",
    "smalltalk",
    "not_medical",
]

ExtractionProfile = Literal[
    "default",
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
