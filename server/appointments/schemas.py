from datetime import datetime

from pydantic import BaseModel, Field


class AppointmentSearchRequest(BaseModel):
    session_id: str
    profile_id: int
    postal_code: str = Field(min_length=5, max_length=5)


class AppointmentRecommendationSummary(BaseModel):
    specialty: str
    care_level: str
    urgency: str
    next_step: str | None = None


class FhirAppointment(BaseModel):
    id: str
    provider_name: str
    specialty: str
    address: str
    distance_km: float
    date: str
    time: str
    care_type: str
    urgency_match: bool
    source: str = "hapi-fhir"


class AppointmentSearchResponse(BaseModel):
    session_id: str
    profile_id: int
    postal_code: str
    message: str
    recommendation_summary: AppointmentRecommendationSummary
    appointments: list[FhirAppointment]


class RecommendedAppointmentCreateRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    fhir_appointment_id: str = Field(min_length=1, max_length=120)
    note: str | None = Field(default=None, max_length=1000)


class RecommendedAppointmentRescheduleRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    replacement_fhir_appointment_id: str = Field(min_length=1, max_length=120)
    note: str | None = Field(default=None, max_length=1000)


class RecommendedAppointmentResponse(BaseModel):
    id: int
    profile_id: int
    session_id: str | None = None
    booked_by_account_id: int
    fhir_appointment_id: str
    provider_name: str
    specialty: str
    address: str
    distance_km: float
    starts_at: datetime
    care_type: str
    note: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
