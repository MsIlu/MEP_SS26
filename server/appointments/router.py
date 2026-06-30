from fastapi import APIRouter, Depends
from sqlmodel import Session

from appointments.schemas import (
    RecommendedAppointmentCreateRequest,
    RecommendedAppointmentResponse,
)
from appointments.service import (
    list_recommended_appointments,
    save_recommended_appointment,
)
from auth.security import get_current_account, get_session
from database.models import User
from fhir_mapper.hapi_client import HapiFhirClient


router = APIRouter(
    prefix="/profiles/{profile_id}/appointments",
    tags=["appointments"],
)


def get_hapi_fhir_client() -> HapiFhirClient:
    return HapiFhirClient()


@router.get("/recommended", response_model=list[RecommendedAppointmentResponse])
def get_profile_recommended_appointments(
        profile_id: int,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    return list_recommended_appointments(
        profile_id=profile_id,
        current_user=current_user,
        session=session,
    )


@router.post("/recommended", response_model=RecommendedAppointmentResponse)
def post_profile_recommended_appointment(
        profile_id: int,
        request: RecommendedAppointmentCreateRequest,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
        fhir_client: HapiFhirClient = Depends(get_hapi_fhir_client),
):
    return save_recommended_appointment(
        profile_id=profile_id,
        request=request,
        current_user=current_user,
        session=session,
        fhir_client=fhir_client,
    )
