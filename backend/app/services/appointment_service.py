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
            detail = "El salon no atiende ese día"
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
        Service.id == service_id,
        Service.is_active == True
    ).first()

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
                start_time = slot_start.time(),
                end_time = slot_end.time() 
            ))
        slot_start += timedelta(minutes = 30)
    return slots

def create_Appointment(db : Session, data: AppointmentCreate, client : User) -> Appointment:
    day_of_week = data.appointment_date.weekday()
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
    start_dt = datetime.combine(data.appointment_date, data.start_time)
    endt_dt = start_dt + timedelta(minutes = service.duration_minutes)
    end_time = endt_dt.time()

    #validar si la cita está dentro del horario del salon
    if data.start_time < business_hours.open_time or end_time > business_hours.close_time:
        raise HTTPException(
            status_code = status. HTTP_400_BAD_REQUEST,
            detail = f"la cita debe estar entre {business_hours.open_time} y {business_hours.close_time}"
        )
    
    #validar que no choquen la cita con otra
    booked = get_booked_slots(db, data.appointment_date)
    if has_time_conflict(data.start_time, end_time, booked):
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = f"Este horario ya está ocupado"
        )
    
    appointment = Appointment(
        client_id = client.id,
        service_id = service.id,
        appointment_date = data.appointment_date,
        start_time = data.start_time,
        end_time = end_time,
        notes = data.notes,
        status = AppointmentStatus.pending
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment

def get_my_appointments(db : Session, client : User) ->list[Appointment]:
    return db.query(Appointment).filter(
        Appointment.client_id == client.id
    ).order_by(
        Appointment.appointment_date.desc(),
        Appointment.start_time.desc()
    ).all()

def cancel_appointment(db : Session, appointment_id : UUID, client :User) -> Appointment:
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Cita no encontrada"
        )
    
    if appointment.client_id != client.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "No puedes cancelar una cita que no es tuya"
        )
    
    if appointment.status in [AppointmentStatus.completed, AppointmentStatus.cancelled]:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"No puedes cancelar una cita con estado {appointment.status}"
        )
    
    appointment.status = AppointmentStatus.cancelled
    db.commit()
    db.refresh(appointment)
    return appointment

#busca todas las citas y las ordena por fecha y hora
def get_all_appointments(db : Session, appointment_date : date | None = None) -> list[Appointment]:
    query = db.query(Appointment)
    if appointment_date:
        query = query.filter(Appointment.appointment_date == appointment_date)
    
    return query.order_by(
        Appointment.appointment_date.asc(),
        Appointment.start_time.asc()
    ).all()

def update_appointment_status(db: Session, appointment_id : UUID, new_status : AppointmentStatus) -> Appointment:
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()
    if not appointment:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Cita no encontrada"
        )
    
    appointment.status = new_status
    db.commit()
    db.refresh(appointment)
    return appointment