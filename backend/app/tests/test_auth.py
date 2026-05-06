import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)
print("TEST FILE LOADED")
def test_register_success():
    email = f"test{uuid.uuid4()}@example.com"
    response = client.post("/auth/register", json = {
        "name" : "Test User",
        "email" : email,
        "password" : "password123",
        "phone" : "3003134488"  
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == email

def test_register_duplicate_email():
    payload = {
        "name" : "Test User",
        "email" : "duplicate@example.com",
        "password" : "password123"
    }
    client.post("/auth/register",json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400

def test_login_succes():
    client.post("/auth/register", json={
        "name": "Login User",
        "email" : "login@example.com",
        "password" : "password123",
    })
    response = client.post("/auth/login", json={
        "email" : "login@example.com",
        "password" : "password123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password():
    response = client.post("/auth/login", json={
        "email" : "login@example.com",
        "password" : "WrongPassword"
    })
    assert response.status_code == 401

def  test_me_endpoint():
    email = f"test_{uuid.uuid4()}@example.com"
    register = client.post("/auth/register", json={
        "name" : "Me User",
        "email" : email,
        "password" : "password123",
    })
    assert register.status_code == 201

    token = register.json()["access_token"]
    
    response = client.get("/auth/me", headers ={ 
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["email"] == email
