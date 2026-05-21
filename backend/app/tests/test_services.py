import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.users import UserRole, User
from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
import uuid

Client = TestClient(app)



def get_admin_token():
    db = SessionLocal()
    admin_email = f"admin_{uuid.uuid4().hex[:8]}@test.com"
    admin = User(
        name = "Admin Test",
        email = admin_email,
        password_hash = hash_password("admin123"),
        role = UserRole.admin
    )
    db.add(admin)
    db.commit()
    db.close()

    response = Client.post("/auth/login", json={
        "email" : admin_email,
        "password" : "admin123"
    })

    return response.json()["access_token"]

def get_client_token():
    email = f"client_{uuid.uuid4().hex[:8]}@test.com"
    response = Client.post("/auth/register", json={
        "name": "Client Test",
        "email": email,
        "password": "client123"
    })
    return response.json()["access_token"]

service_payload = {
    "name": f"Manicure Test {uuid.uuid4().hex[:6]}",
    "description" : "Manicure completo",
    "duration_minutes" : 60,
    "price" : "35000"
}

def test_get_services_public():
    response = Client.get("/services/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_as_admin():
    token = get_admin_token()
    response = Client.post(
        "/services/",
        json = service_payload,
        headers = {"Authorization" : f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == service_payload["name"]
    assert data["duration_minutes"] == 60
    

def test_create_service_as_client_forbiden():
    token = get_client_token()
    forbidden_payload = {
        **service_payload, 
        "name": f"Forbidden Test {uuid.uuid4().hex[:6]}"
    }
    response = Client.post(
        "/services/",
        json = forbidden_payload, 
        headers = {"Authorization" : f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_create_service_invalid_price():
    token = get_admin_token()
    response = Client.post(
        "/services/",
        json = {**service_payload, "price" : "-1000"},
        headers = {"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422 

def test_update_service():
    token = get_admin_token()
    create = Client.post(
        "/services/",
        json={**service_payload, "name": f"Update Test {uuid.uuid4().hex[:6]}"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    service_id = create.json()["id"]

    response = Client.put(
        f"/services/{service_id}",
        json={"price": "45000"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["price"] == 45000


def test_delete_service_soft():
    token = get_admin_token()
    create = Client.post(
        "/services/",
        json = {**service_payload, "name" : f"Delete test {uuid.uuid4().hex[:6]}"},
        headers = {"Authorization" : f"Bearer {token}"}
    )

    service_id = create.json()["id"]
    response = Client.delete(
        f"/services/{service_id}",
        headers = {"Authorization" : f"Bearer {token}"}
    )

    assert response.status_code == 200
    get_response = Client.get(f"/services/{service_id}")
    assert get_response.status_code == 404