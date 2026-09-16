import os
import sys
import pytest

tests_dir = os.path.dirname(__file__) 
project_dir = os.path.abspath(os.path.join(tests_dir, os.pardir))
sys.path.insert(0, project_dir)

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
