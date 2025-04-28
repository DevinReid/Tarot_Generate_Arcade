from app import app
import pytest

@pytest.fixture
def client():
    return app.test_client()

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200