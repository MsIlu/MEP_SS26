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


class SimulatedAppointment(BaseModel):
    id: str
    provider_name: str
    specialty: str
    address: str
    distance_km: float
    date: str
    time: str
    care_type: str
    urgency_match: bool


class AppointmentSearchResponse(BaseModel):
    session_id: str
    profile_id: int
    postal_code: str
    message: str
    recommendation_summary: AppointmentRecommendationSummary
    appointments: list[SimulatedAppointment]