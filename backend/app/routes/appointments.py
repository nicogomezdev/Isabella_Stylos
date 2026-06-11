from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AvailableSlotsResponse,AppointmentStatusUpdate
from app.services import appointment_service
from app.models import User

router = APIRouter(prefix = "/appointments", tags = ["Citas"])

@router.get("/available-slots", response_model=AvailableSlotsResponse)
def get_available_slots(
    appointment_date: date = Query(...),
    service_id: UUID = Query(...),
    db: Session = Depends(get_db)
):
    slots = appointment_service.get_available_slots(db, appointment_date, service_id)
    return AvailableSlotsResponse(
        date=appointment_date,
        service_id=service_id,
        available_slots=slots
    )


@router.get("/my", response_model = list[AppointmentResponse])
def get_my_appintments(current_user : User = Depends(get_current_user), db : Session = Depends(get_db)):
    return appointment_service.get_my_appointments(db, current_user)

@router.post("/", response_model = AppointmentResponse, status_code = 201)
def create_appointment(data : AppointmentCreate, current_user : User = Depends(get_current_user), db : Session = Depends(get_db)):
    return appointment_service.create_Appointment(db, data, current_user)

@router.patch("/{appointment_id}/cancel", response_model = AppointmentResponse)
def cancel_appointment(appointment_id : UUID, current_user : User = Depends(get_current_user), db : Session = Depends(get_db)):
    return appointment_service.cancel_appointment(db, appointment_id, current_user)

@router.get("/admin/all", response_model = list[AppointmentResponse])
def get_all_appointments(appointment_date : date | None = Query(None), db : Session = Depends(get_db), admin : User = Depends(require_admin)):
    return appointment_service.get_all_appointments(db,appointment_date)

@router.patch("/admin/{appointment_id}/status", response_model = AppointmentResponse)
def update_status(appointment_id : UUID, data : AppointmentStatusUpdate, db : Session = Depends(get_db), admin : User = Depends(require_admin)):
    return appointment_service.update_appointment_status(db, appointment_id, data.status)