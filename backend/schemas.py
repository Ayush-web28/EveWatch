"""Pydantic data schemas for EveWatch API.
Provides strict validation for simulation parameters, post-processing, and experimental datasets.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    num_qubits: int = Field(default=100, ge=10, le=1000, description="Number of qubits to transmit")
    eve_present: bool = Field(default=False, description="Whether an active eavesdropper is listening")
    eve_fraction: float = Field(default=0.5, ge=0.0, le=1.0, description="Interception fraction f in [0, 1]")
    channel_noise_prob: float = Field(default=0.0, ge=0.0, le=0.5, description="Optical channel depolarizing probability")
    depolarizing_error_prob: float = Field(default=0.0, ge=0.0, le=0.1, description="Gate depolarizing error probability")
    readout_error_prob: float = Field(default=0.0, ge=0.0, le=0.1, description="Detector readout error probability")
    abort_threshold: float = Field(default=0.11, ge=0.01, le=0.5, description="QBER security cutoff threshold (default 11%)")
    sample_size: float = Field(default=0.5, gt=0.0, lt=1.0, description="Fraction of sifted key revealed for QBER estimation")
    seed: Optional[int] = Field(default=42, description="Random seed for reproducible quantum simulation")
    use_fake_backend: bool = Field(default=False, description="Use calibrated IBM FakeBrisbane noise model")
    include_circuit: bool = Field(default=True, description="Generate ASCII quantum circuit diagram")


class QubitEvent(BaseModel):
    index: int
    alice_bit: int
    alice_basis: int  # 0: Z, 1: X
    alice_basis_label: str
    alice_state: str  # e.g. "|0⟩", "|1⟩", "|+⟩", "|-⟩"
    eve_intercepted: bool
    eve_basis: Optional[int] = None
    eve_basis_label: Optional[str] = None
    eve_measured_bit: Optional[int] = None
    bob_basis: int
    bob_basis_label: str
    bob_measured_bit: int
    bases_match: bool
    role: str  # "discarded", "sampled", "retained"
    is_error: Optional[bool] = None


class SimulationResponse(BaseModel):
    num_qubits: int
    sifted_count: int
    sifted_ratio: float
    sample_count: int
    sample_qber: float
    overall_qber: float
    abort_threshold: float
    aborted: bool
    verdict: str
    verdict_detail: str
    secret_key_rate: float
    retained_key_length: int
    alice_key_preview: str
    bob_key_preview: str
    key_agreement_rate: float
    qubit_events: List[QubitEvent]
    circuit_ascii: Optional[str] = None
    metadata: Dict[str, Any]


class EncryptRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="Plaintext message to encrypt")
    key_bits: Optional[List[int]] = Field(default=None, description="Optional raw or distilled key bits")
    estimated_qber: float = Field(default=0.03, ge=0.0, le=0.5, description="Estimated QBER for privacy amplification")


class EncryptResponse(BaseModel):
    original_message: str
    key_length_used: int
    parity_corrections: int
    final_secret_bits: int
    hex_ciphertext: str
    binary_ciphertext_preview: str
    decrypted_bob: str
    decrypted_eve_sample: str
    roundtrip_verified: bool
    explanation: str


class DecryptRequest(BaseModel):
    hex_ciphertext: str
    key_bits: List[int]


class DecryptResponse(BaseModel):
    decrypted_message: str
    success: bool


class ExperimentDataset(BaseModel):
    id: str
    title: str
    description: str
    source_file: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    summary: Dict[str, Any]
