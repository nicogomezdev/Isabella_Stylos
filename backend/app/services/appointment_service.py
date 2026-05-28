from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from datetime import date, time, datetime, timedelta
from app.models.appointments import Appointment, AppointmentStatus
from app.models.service import Service
from app.models.business_hours import BusinessHours
from app.models.users import User
from app.schemas.appointment import AppointmentCreate, AvailableSlot

#Lógica escencial 

def get_business_hours(db : Session, day_of_week : int) -> BusinessHours:
    hours = db.query(BusinessHours).filter(
        BusinessHours.day_of_week == day_of_week
    ).first()

    if not hours or not hours.is_open:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "El salon no tiende ese día"
        )
    return hours

def get_booked_slots(db : Session, appointment_date : date) -> list[Appointment]:
    return db.query(Appointment).filter(
        Appointment.appointment_date == appointment_date,
        Appointment.status.in_([
            AppointmentStatus.pending,
            AppointmentStatus.confirmed
        ])
    ).all()

def has_time_conflict(start_new : time, end_new: time, booked : list[Appointment]) -> bool:
    
    #hay conflicto si los rangos e solapan
    for appointment in booked:
        if start_new < appointment.end_time and end_new > appointment.start_time:
            return True
        return False
    
def get_available_slots(db : Session, appointment_date : date, service_id : UUID) -> list[AvailableSlot]:
    day_of_week = appointment_date.weekday() #0-Lunes 1-Martes 2-Miercoles ...
    business_hours = get_business_hours(db, day_of_week)
    
    service = db.query(Service).filter(
        Service.id == service_id
        Service.is_active == True
    ).firts()

    if not service:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Servicio no encontrado"
        )
    
    booked = get_booked_slots(db, appointment_date)

    slots = []
    slot_start = datetime.combine(appointment_date, business_hours.open_time)
    salon_close = datetime.combine(appointment_date, business_hours.close_time)
    duration = timedelta(minutes = service.duration_minutes)

    while slot_start + duration <= salon_close:
        slot_end = slot_start + duration

        if not has_time_conflict(slot_start.time(), slot_end.time(), booked):
            slots.append(AvailableSlot(
                start_time = slot_start.time()
                end_time = slot_end.time() 
            ))
        slot_start += timedelta(minutes = 30)
    return slots

def create_Appointment(db : Session, data: AppointmentCreate, clien : User) -> Appointment:
    day_of_week = data.appotinment_date.weekday()
    business_hours = get_business_hours(db, day_of_week)

    service = db.query(Service).filter(
        Service.id == data.service_id,
        Service.is_active == True
    ).first()

    if not service:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "servicio no encontrado"
        )
    
    # Calcular end_time automáticamente
    start_dt = datetime.combine(data.appotinment_date, data.start_time)
    endt_dt = start_dt + timedelta(minutes = service.duration_minutes)
    end_time = endt_dt.time()