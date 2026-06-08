"""
Unit tests for payment-service
Run: pytest test_app.py -v --cov=app --cov-report=term-missing
"""

import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


class TestHealthEndpoints:

    def test_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_index_contains_service_name(self, client):
        data = client.get("/").get_json()
        assert data["service"] == "payment-service"

    def test_index_contains_status(self, client):
        data = client.get("/").get_json()
        assert data["status"] == "running"

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_status_is_healthy(self, client):
        data = client.get("/health").get_json()
        assert data["status"] == "healthy"

    def test_health_has_uptime(self, client):
        data = client.get("/health").get_json()
        assert "uptime_s" in data
        assert data["uptime_s"] >= 0

    def test_readiness_returns_200(self, client):
        response = client.get("/ready")
        assert response.status_code == 200

    def test_readiness_is_ready(self, client):
        data = client.get("/ready").get_json()
        assert data["ready"] is True


class TestPaymentEndpoints:

    def test_process_payment_returns_202(self, client):
        response = client.post("/payment/process")
        assert response.status_code == 202

    def test_process_payment_has_transaction_id(self, client):
        data = client.post("/payment/process").get_json()
        assert "transaction_id" in data

    def test_process_payment_status_accepted(self, client):
        data = client.post("/payment/process").get_json()
        assert data["status"] == "accepted"


class TestVersionEndpoint:

    def test_version_returns_200(self, client):
        response = client.get("/version")
        assert response.status_code == 200

    def test_version_has_version_key(self, client):
        data = client.get("/version").get_json()
        assert "version" in data

    def test_version_has_environment_key(self, client):
        data = client.get("/version").get_json()
        assert "environment" in data
