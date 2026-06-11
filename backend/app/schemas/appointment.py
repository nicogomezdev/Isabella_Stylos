from pydantic import BaseModel, field_validator, ConfigDict
from uuid import UUID
from datetime import datetime, date, time
from app.models.appointments import AppointmentStatus
from app.schemas.user import UserResponse
from app.schemas.service import ServiceResponse

class AppointmentCreate(BaseModel):
    service_id : UUID
    appointment_date : date
    start_time : time
    notes : str | None = None

    @field_validator("appointment_date")
    @classmethod
    def date_must_be_future(cls, v):
        if v < date.today():
            raise ValueError("La fecha de la cita debe ser hoy o en el futuro")
        return v
    
class AppointmentStatusUpdate(BaseModel):
    status : AppointmentStatus

class AppointmentResponse(BaseModel):
    id : UUID
    client : UserResponse
    service : ServiceResponse
    appointment_date : date
    start_time : time
    end_time : time
    status : AppointmentStatus
    notes : str | None
    created_at :datetime

    model_config = ConfigDict(from_attributes=True)


class AvailableSlot(BaseModel):
    start_time : time
    end_time :time

class AvailableSlotsResponse(BaseModel):
    date: date
    service_id : UUID
    available_slots : list[AvailableSlot]
