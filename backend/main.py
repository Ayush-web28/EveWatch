"""FastAPI entrypoint for EveWatch Quantum Cybersecurity Platform.

Provides REST endpoints for Qiskit BB84 simulations, real experimental data retrieval,
One-Time Pad encryption/decryption, and system health checks.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.schemas import (
    SimulationRequest,
    SimulationResponse,
    EncryptRequest,
    EncryptResponse,
    DecryptRequest,
    DecryptResponse,
    ExperimentDataset,
)
from backend.services import (
    run_simulation_service,
    get_all_experiment_datasets,
    encrypt_message_service,
)
from bb84.postprocessing import decrypt_message_otp
import numpy as np

# Application setup
app = FastAPI(
    title="EveWatch Quantum Cybersecurity API",
    description="Scientific API for BB84 QKD simulation, eavesdropper discrimination, and noise modeling.",
    version="2.0.0",
)

# CORS Configuration
# Allows requests from local Vite dev server and production Render domain
cors_origins_env = os.environ.get("CORS_ORIGINS", "")
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",
]
if cors_origins_env:
    allowed_origins.extend([origin.strip() for origin in cors_origins_env.split(",") if origin.strip()])
else:
    # Allow all in development if not explicitly configured
    allowed_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["System"])
def health_check() -> Dict[str, Any]:
    """Health check endpoint for Render and monitoring."""
    token_present = bool(os.environ.get("IBM_QUANTUM_TOKEN"))
    return {
        "status": "healthy",
        "service": "EveWatch Quantum API",
        "version": "2.0.0",
        "qiskit_version": "2.5.2",
        "aer_simulator": "available",
        "ibm_token_configured": token_present,
    }


@app.post("/api/simulate", response_model=SimulationResponse, tags=["Quantum Simulation"])
def run_simulation(req: SimulationRequest) -> SimulationResponse:
    """Execute end-to-end BB84 simulation via Qiskit AerSimulator.

    Returns full state preparation, eavesdropper collapse, channel noise degradation,
    sifting, sample QBER, and final key rates.
    """
    try:
        return run_simulation_service(req)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quantum simulation error: {str(exc)}",
        )


@app.get("/api/experiments", response_model=List[ExperimentDataset], tags=["Research Experiments"])
def list_experiments() -> List[ExperimentDataset]:
    """Retrieve all 6 empirical research benchmark datasets with raw CSV rows and summaries."""
    datasets = get_all_experiment_datasets()
    if not datasets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No experiment datasets found in results directory.",
        )
    return datasets


@app.get("/api/experiments/{dataset_id}", response_model=ExperimentDataset, tags=["Research Experiments"])
def get_experiment_by_id(dataset_id: str) -> ExperimentDataset:
    """Retrieve a specific research dataset by ID (exp1 through exp6)."""
    datasets = get_all_experiment_datasets()
    for ds in datasets:
        if ds.id == dataset_id:
            return ds
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Experiment dataset '{dataset_id}' not found.",
    )


@app.post("/api/messaging/encrypt", response_model=EncryptResponse, tags=["Secure Messaging"])
def encrypt_message(req: EncryptRequest) -> EncryptResponse:
    """Perform One-Time Pad encryption using the distilled quantum key."""
    try:
        return encrypt_message_service(req)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption error: {str(exc)}",
        )


@app.post("/api/messaging/decrypt", response_model=DecryptResponse, tags=["Secure Messaging"])
def decrypt_message(req: DecryptRequest) -> DecryptResponse:
    """Decrypt a hex ciphertext string using the shared quantum key."""
    try:
        key_arr = np.array(req.key_bits, dtype=np.int32)
        decrypted = decrypt_message_otp(req.hex_ciphertext, key_arr)
        is_err = decrypted.startswith("[Decryption Error")
        return DecryptResponse(decrypted_message=decrypted, success=not is_err)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decryption error: {str(exc)}",
        )


# Mount static frontend if dist directory exists (e.g. in unified container)
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/", tags=["Root"])
    def root_endpoint() -> Dict[str, str]:
        return {
            "title": "EveWatch Quantum API",
            "documentation": "/docs",
            "health": "/api/health",
            "status": "Ready for frontend connections",
        }
