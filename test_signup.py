from fastapi.testclient import TestClient 
import json
from main import auth_router

client = TestClient(auth_router)
def test_read_root():
    data ={
    "username":"Rinku Garg",
    "email":"rinku@gmail.com",
    "password":"rinku123",
    "admin":"False"
    }
    response = client.post("/signup",json.dumps(data))
    assert response.status_code == 201
    assert response.json() == {"message":"Registration Successfull"}

def test_read_root2():
    data ={
    "username":"Rinku Garg",
    "email":"abcd@gmail.com",
    "password":"rinku123",
    "admin":"False"
    }
    response = client.post("/signup",json.dumps(data))
    assert response.json()["detail"] == "User with Username already exists"
    assert response.json()["status_code"] == 400

def test_read_root1():
    data ={
    "username":"Abcd Garg",
    "email":"rinku@gmail.com",
    "password":"abcd123",
    "admin":"False"
    }
    response = client.post("/signup",json.dumps(data))
    assert response.json()["detail"] == "User with Email already exists"
    assert response.json()["status_code"] == 400