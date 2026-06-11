import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.users import User, UserRole
from app.models.business_hours import BusinessHours
from app.models.service import Service
from app.core.security import hash_password
from datetime import date, timedelta
import uuid
from datetime import time
from app.models.appointments import Appointment


client = TestClient(app)



def open_hours():
    db = SessionLocal()
    db.query(Appointment).delete()
    db.query(Service).delete()
    db.query(BusinessHours).delete()
    db.query(User).delete()

    db.commit()
    for day in range(5):  # lunes a viernes
        db.add(
            BusinessHours(
                day_of_week=day,
                open_time=time(8, 0),
                close_time=time(18, 0),
                is_open=True
            )
        )

    db.commit()

open_hours()


def get_admin_token():
    db = SessionLocal()
    email  = f"admin_{uuid.uuid4().hex[:8]}@test.com"
    admin = User(
        name = "Admin",
        email = email,
        password_hash = hash_password("admin123"),
        role = UserRole.admin
    )
    db.add(admin)
    db.commit()
    db.close()

    res = client.post("/auth/login", json= {
        "email" : email,
        "password" : "admin123"
    })

    return res.json()["access_token"]


def get_client_token():
    email = f"client_{uuid.uuid4().hex[:8]}@test.com"
    res = client.post("/auth/register", json={
        "name": "Client",
        "email": email,
        "password": "client123"
    })
    return res.json()["access_token"]

db = SessionLocal()

def create_test_service(admin_token):
    res = client.post("/services/", json={
        "name" : f"Servicio {uuid.uuid4().hex[:6]}",
        "duration_minutes" : 60,
        "price" : "50000"}, headers = {"Authorization" : f"Bearer {admin_token}"})
    return res.json()["id"]

#Retorna el proximo dia de la semana
def get_next_weekday():
    day = date.today() + timedelta(days = 1)
    while day.weekday() >= 5: #5=Sabado #6=domingo salon cierra el dia 5
        day += timedelta(days = 1)
    return day

def test_get_available_slots():
    admin_token = get_admin_token()
    service_id = create_test_service(admin_token)
    test_date = get_next_weekday()

    res = client.get("/appointments/available-slots", params = {
        "appointment_date" : str(test_date),
        "service_id" : service_id
    })
    
    assert res.status_code == 200
    data = res.json()
    assert "available_slots" in data
    assert len(data["available_slots"]) > 0

def test_create_appointment_succes():
    admin_token = get_admin_token()
    service_id = create_test_service(admin_token)
    client_token = get_client_token()
    test_date = get_next_weekday()

    slots_res = client.get("/appointments/available-slots", params = {
        "appointment_date" : str(test_date),
        "service_id" : service_id
    })
    
    first_slot = slots_res.json()["available_slots"][0]

    res = client.post("/appointments/", json = {
        "service_id" : service_id,
        "appointment_date" : str(test_date),
        "start_time" : first_slot["start_time"]
    }, headers = {"Authorization" : f"Bearer {client_token}"})

   

    assert res.status_code == 201
    assert res.json()["status"] == "pending"

def test_create_appointment_conflict():
    admin_token = get_admin_token()
    service_id = create_test_service(admin_token)
    client_token_1 = get_client_token()
    client_token_2 = get_client_token()
    test_date = get_next_weekday()

    slots_res = client.get("/appointments/available-slots", params ={
        "appointment_date" : str(test_date),
        "service_id" : service_id
    })
  
    first_slot = slots_res.json()["available_slots"][0]

    client.post("/appointments/", json={
        "service_id": service_id,
        "appointment_date": str(test_date),
        "start_time": first_slot["start_time"]
    }, headers={"Authorization": f"Bearer {client_token_1}"})


    res = client.post("/appointments/", json = {
        "service_id" : service_id,
        "appointment_date" : str(test_date),
        "start_time" : first_slot["start_time"]
    }, headers = {"Authorization": f"Bearer {client_token_2}"})

    assert res.status_code == 409

def test_create_appointment_past_date():
    admin_token = get_admin_token()
    service_id = create_test_service(admin_token)
    client_token = get_client_token()

    res = client.post("/appointments/", json = {
        "service_id" : service_id,
        "appointment_date" : "2020-01-01",
        "start_time" : "09:00:00"
    }, headers = {"Authorization" : f"Bearer {client_token}"})

    assert res.status_code == 422

def test_get_myappointments():
    client_token = get_client_token()
    res = client.get("/appointments/my", headers = {"Authorization": f"Bearer {client_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_cancel_appointment():
    admin_token = get_admin_token()
    service_id = create_test_service(admin_token)
    client_token = get_client_token()
    test_date = get_next_weekday()
    slots_res = client.get("/appointments/available-slots", params = {
        "appointment_date" : str(test_date),
        "service_id" : service_id
    })
  
    first_slot = slots_res.json()["available_slots"][0]
    
    create_res = client.post("/appointments", json = {
        "service_id" : service_id,
        "appointment_date" : str(test_date),
        "start_time" : first_slot["start_time"]
    }, headers = {"Authorization" : f"Bearer {client_token}"})

    appointment_id = create_res.json()["id"]

    cancel_res = client.patch(
        f"/appointments/{appointment_id}/cancel", headers = {"Authorization" : f"Bearer {client_token}"}
    )

    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

def test_cancel_other_users_appointment():
    admin_token = get_admin_token()
    service_id = create_test_service(admin_token)
    client_token_1 = get_client_token()
    client_token_2 = get_client_token()
    test_date = get_next_weekday()

    slots_res = client.get("/appointments/available-slots", params = {
            "appointment_date" : str(test_date),
            "service_id" : service_id
        } )
   
    first_slot = slots_res.json()["available_slots"][0]

    create_res = client.post("/appointments/", json = {
            "service_id" : service_id,
            "appointment_date" : str(test_date),
            "start_time" : first_slot["start_time"]
        }, headers = {"Authorization" : f"Bearer {client_token_1}"})
    
    appointment_id = create_res.json()["id"]
    
    
    res = client.patch(f"/appointments/{appointment_id}/cancel",
                       headers={"Authorization" : f"Bearer {client_token_2}"})
    assert res.status_code == 403

def test_admin_get_all_appointments():
    admin_token = get_admin_token()
    res = client.get("/appointments/admin/all",
                     headers = {"Authorization" : f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_admin_update_status():
    admin_token = get_admin_token()
    service_id = create_test_service(admin_token)
    client_token = get_client_token()
    test_date = get_next_weekday()

    slot_res = client.get("/appointments/available-slots", params = {
        "appointment_date" : str(test_date),
        "service_id" : service_id    
    })
    

    db = SessionLocal()
   

    first_slot = slot_res.json()["available_slots"][0]

    create_res = client.post("/appointments/", json = {
        "service_id" : service_id,
        "appointment_date" : str(test_date),
        "start_time" : first_slot["start_time"],
    }, headers = {"Authorization" : f"Bearer {client_token}"})

    appointment_id = create_res.json()["id"]

    res = client.patch(
        f"/appointments/admin/{appointment_id}/status",
        json={"status" : "confirmed"},
        headers = {"Authorization" : f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "confirmed"

    