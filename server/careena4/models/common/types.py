from typing import Literal


ResponseMode = Literal[
    "emergency",
    "ask_safety_question",
    "ask_followup",
    "request_case_description",
    "guide_next_step",
    "recommend",
    "out_of_scope",
]

QuestionIntent = Literal[
    "subject_clarification",
    "duration",
    "description",
    "free_description",
    "localization",
    "severity",
]

QuestionKind = Literal[
    "followup",
    "subject_clarification",
    "safety_clarification",
]

EntryMessageKind = Literal[
    "new_case_report",
    "same_case_update",
    "question_answer",
    "dialogue_only",
    "out_of_scope",
]

MedicalRelevance = Literal["medical", "non_medical", "unclear"]

SubjectScope = Literal["self", "child", "other", "unclear"]

ObservationType = Literal[
    "symptom",
]

ObservationStatus = Literal[
    "active",
    "negated",
    "historical",
    "rejected",
    "reported",
    "enriched",
    "corrected",
]

ConversationPhase = Literal[
    "intake",
    "exploration",
    "followup",
    "recommendation",
]

RecommendationReadiness = Literal["not_ready", "tentative", "ready"]

FollowupReason = Literal[
    "subject_unclear",
    "person_ref_missing",
    "duration_missing",
    "description_missing",
    "location_unclear",
    "severity_missing",
]

FollowupPriority = Literal["low", "medium", "high"]

ObservationSpecificity = Literal["low", "medium", "high"]

ObservationCompleteness = Literal["sparse", "usable", "rich"]

ObservationAmbiguity = Literal["low", "medium", "high"]

ObservationFollowupValue = Literal["none", "optional", "useful", "necessary"]

CaseWriteAction = Literal[
    "create",
    "enrich",
    "correct",
    "negate",
    "conflict",
    "ignore",
]

TurnDecisionKind = Literal[
    "out_of_scope",
    "ask_safety_question",
    "ask_followup",
    "request_case_description",
    "guide_next_step",
    "recommend",
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
