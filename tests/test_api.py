"""Unit tests for EveWatch FastAPI backend.
Validates simulation endpoints, experiment retrieval, and OTP messaging.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify system health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "EveWatch Quantum API"
    assert "version" in data
    assert "qiskit_version" in data


def test_simulation_clean_channel():
    """Verify simulation execution with 0% noise and no Eve."""
    payload = {
        "num_qubits": 100,
        "eve_present": False,
        "eve_fraction": 0.0,
        "channel_noise_prob": 0.0,
        "seed": 42,
        "sample_size": 0.5,
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["num_qubits"] == 100
    assert data["sifted_count"] > 0
    assert data["overall_qber"] == 0.0
    assert data["aborted"] is False
    assert "SECURE" in data["verdict"]
    assert len(data["qubit_events"]) > 0
    assert data["circuit_ascii"] is not None


def test_simulation_with_eve_detection():
    """Verify Eve is detected when eve_fraction is 1.0 (expected ~25% QBER)."""
    payload = {
        "num_qubits": 200,
        "eve_present": True,
        "eve_fraction": 1.0,
        "channel_noise_prob": 0.0,
        "seed": 101,
        "sample_size": 0.5,
    }
    response = client.post("/api/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["overall_qber"] > 0.15  # ~25% theoretical
    assert data["aborted"] is True
    assert "ABORT" in data["verdict"]


def test_experiments_endpoint():
    """Verify all 6 empirical benchmark datasets are served."""
    response = client.get("/api/experiments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
    ids = [d["id"] for d in data]
    assert "exp1" in ids
    assert "exp3" in ids
    assert "exp6" in ids


def test_experiment_single_by_id():
    """Verify fetching single dataset by id."""
    response = client.get("/api/experiments/exp1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "exp1"
    assert len(data["rows"]) > 0
    assert len(data["columns"]) > 0


def test_messaging_encrypt_decrypt_cycle():
    """Verify OTP encryption and subsequent decryption."""
    # Test encryption with synthetic key or auto-generated key
    secret_message = "TOP SECRET QUANTUM KEY 2026"
    encrypt_res = client.post("/api/messaging/encrypt", json={
        "message": secret_message,
        "estimated_qber": 0.02,
    })
    assert encrypt_res.status_code == 200
    enc_data = encrypt_res.json()
    assert enc_data["hex_ciphertext"] != ""
    assert enc_data["decrypted_bob"] == secret_message
    assert enc_data["roundtrip_verified"] is True
