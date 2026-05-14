from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.services import service_service
from app.models.users import User

router = APIRouter(prefix="/services", tags=["Servicios"])

@router.get("/", response_model=list[ServiceResponse])
def get_services(db: Session = Depends(get_db)):
    return service_service.get_all_services(db)


@router.get("/{service_id}", response_model = ServiceResponse)
def get_service(service_id : UUID, db: Session = Depends(get_db)):
    return service_service.get_service_by_id(db, service_id)


@router.post("/", response_model = ServiceResponse, status_code=201)
def create_service(
    data: ServiceCreate,
    db : Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return service_service.create_service(db, data)

@router.put("/{service_id}", response_model = ServiceResponse)
def update_service(
    service_id : UUID,
    data : ServiceUpdate,
    db : Session = Depends(get_db),
    admin : User = Depends(require_admin)
):
    return service_service.update_service(db, service_id, data)


@router.delete("/{service_id}")
def delete_service(
    service_id : UUID,
    db : Session = Depends(get_db),
    admin : User = Depends(require_admin)
):
    return service_service.delete_service(db,service_id)

