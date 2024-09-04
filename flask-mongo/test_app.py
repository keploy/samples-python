import pytest
from flask import Flask, json
from pymongo import MongoClient
from app import app as flask_app  # Assuming your Flask app is saved as app.py

@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client


def test_get_nonexistent_student(client):
    student_id = '999'
    response = client.get(f'/students/{student_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data is None


def test_update_nonexistent_student(client):
    student_id = '999'
    updated_student = {
        "name": "Nonexistent Student",
        "age": 30,
        "major": "Physics"
    }
    response = client.put(f'/students/{student_id}', json=updated_student)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Student updated successfully"


def test_update_nonexistent_student(client):
    student_id = '999'
    updated_student = {
        "name": "Nonexistent Student",
        "age": 30,
        "major": "Physics"
    }
    response = client.put(f'/students/{student_id}', json=updated_student)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Student updated successfully"




def test_create_student(client):
    new_student = {
        "student_id": "2",
        "name": "New Student",
        "age": 22,
        "major": "Mathematics"
    }
    response = client.post('/students', json=new_student)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Student created successfully"


def test_delete_student(client):
    # Insert a test student
    test_student = {
        "student_id": "3",
        "name": "Delete Student",
        "age": 23,
        "major": "History"
    }
    client.post('/students', json=test_student)

    # Delete the test student
    response = client.delete(f'/students/{test_student["student_id"]}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Student deleted successfully"

