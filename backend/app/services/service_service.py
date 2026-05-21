from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate

def get_all_services(db: Session, include_inactive:bool=False) -> list[Service]:
    query = db.query(Service)
    if not include_inactive:
        query = query.filter(Service.is_active == True)
    return query.order_by(Service.name).all()

def get_service_by_id(db: Session, service_id: UUID) -> Service:
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Servicio no encontrado"
        )
    return service

def create_service(db: Session, data: ServiceCreate) ->Service:
    existing = db.query(Service).filter(Service.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail ="Un servicio con este nombre ya existe"
        )
    service = Service(**data.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

def update_service(db:Session, service_id: UUID, data:ServiceUpdate) -> Service:
    service = get_service_by_id(db, service_id) 
    
    updated_fields = data.model_dump(exclude_unset = True)
    for field, value in updated_fields.items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)
    return service 

def delete_service(db : Session, service_id : UUID) -> dict:
    service = get_service_by_id(db, service_id)
    service.is_active = False
    db.commit()
    db.refresh(service)
    return {"message": f"Servicio '{service.name}' desactivado correctamente"}