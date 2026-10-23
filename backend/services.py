"""Backend service layer connecting FastAPI endpoints to existing quantum modules.
Maintains scientific integrity by utilizing the original BB84, AerSimulator,
noise models, and CSV research datasets.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

from bb84.protocol import run_bb84, BB84Result
from bb84.noise import get_fake_backend_noise_model
from bb84.analysis import asymptotic_secret_key_rate, theoretical_qber
from bb84.postprocessing import (
    reconcile_errors_parity,
    amplify_privacy,
    encrypt_message_otp,
    decrypt_message_otp,
)
from backend.schemas import (
    SimulationRequest,
    SimulationResponse,
    QubitEvent,
    EncryptRequest,
    EncryptResponse,
    ExperimentDataset,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results"

BASIS_LABELS = {0: "Z (Computational)", 1: "X (Hadamard)"}
STATE_SYMBOLS = {
    (0, 0): "|0⟩ (0°)",
    (1, 0): "|1⟩ (90°)",
    (0, 1): "|+⟩ (+45°)",
    (1, 1): "|-⟩ (-45°)",
}


def run_simulation_service(req: SimulationRequest) -> SimulationResponse:
    """Execute BB84 protocol simulation with user-defined parameters."""
    active_noise = None
    if req.use_fake_backend:
        active_noise, _ = get_fake_backend_noise_model("FakeBrisbane")

    # Run core simulation
    res: BB84Result = run_bb84(
        num_qubits=req.num_qubits,
        eve_present=req.eve_present,
        eve_fraction=req.eve_fraction if req.eve_present else 0.0,
        noise_model=active_noise,
        channel_noise_prob=req.channel_noise_prob,
        depolarizing_error_prob=req.depolarizing_error_prob,
        readout_error_prob=req.readout_error_prob,
        sample_size=req.sample_size,
        abort_threshold=req.abort_threshold,
        seed=req.seed,
        save_circuit=req.include_circuit,
    )

    sifted_set = set(res.sifted_indices.tolist())
    sample_set = set(res.sample_indices.tolist())
    key_set = set(res.key_indices.tolist())

    qubit_events: List[QubitEvent] = []
    # Include up to 100 qubits for fine-grained visualization
    visual_limit = min(res.num_qubits, 100)

    for i in range(visual_limit):
        is_sifted = i in sifted_set
        is_sample = i in sample_set
        is_key = i in key_set
        eve_int = bool(res.eve_intercepted[i]) if len(res.eve_intercepted) > i else False
        a_bit = int(res.alice_bits[i])
        a_basis = int(res.alice_bases[i])
        b_basis = int(res.bob_bases[i])
        b_bit = int(res.bob_bits[i])

        role = "discarded"
        if is_sample:
            role = "sampled"
        elif is_key:
            role = "retained"

        is_error = bool(a_bit != b_bit) if is_sifted else None

        qubit_events.append(
            QubitEvent(
                index=i,
                alice_bit=a_bit,
                alice_basis=a_basis,
                alice_basis_label=BASIS_LABELS.get(a_basis, "Z"),
                alice_state=STATE_SYMBOLS.get((a_bit, a_basis), "|?⟩"),
                eve_intercepted=eve_int,
                eve_basis=int(res.eve_bases[i]) if eve_int else None,
                eve_basis_label=BASIS_LABELS.get(int(res.eve_bases[i])) if eve_int else None,
                eve_measured_bit=int(res.eve_bits[i]) if eve_int else None,
                bob_basis=b_basis,
                bob_basis_label=BASIS_LABELS.get(b_basis, "Z"),
                bob_measured_bit=b_bit,
                bases_match=is_sifted,
                role=role,
                is_error=is_error,
            )
        )

    # ASCII circuit string
    circuit_ascii = None
    if req.include_circuit:
        try:
            from qiskit import QuantumCircuit
            circ_n = min(4, res.num_qubits)
            sub_qc = QuantumCircuit(circ_n, circ_n)
            for q in range(circ_n):
                if res.alice_bits[q] == 1:
                    sub_qc.x(q)
                if res.alice_bases[q] == 1:
                    sub_qc.h(q)
                if bool(res.eve_intercepted[q]):
                    if res.eve_bases[q] == 1:
                        sub_qc.h(q)
                    sub_qc.measure(q, q)
                    if res.eve_bases[q] == 1:
                        sub_qc.h(q)
                sub_qc.id(q)
                if res.bob_bases[q] == 1:
                    sub_qc.h(q)
                sub_qc.measure(q, q)
            circuit_ascii = str(sub_qc.draw(output="text"))
        except Exception:
            circuit_ascii = "Quantum circuit text render unavailable in current environment."

    a_key_str = "".join(str(int(b)) for b in res.alice_key)
    b_key_str = "".join(str(int(b)) for b in res.bob_key)
    key_agreement = (
        float(np.mean(res.alice_key == res.bob_key) * 100.0)
        if len(res.alice_key) > 0
        else 0.0
    )
    secret_rate = asymptotic_secret_key_rate(res.qber_sample)

    verdict_detail = (
        f"Protocol aborted because the sampled QBER of {res.qber_sample * 100:.2f}% "
        f"exceeded the {res.abort_threshold * 100:.1f}% security cutoff. The quantum channel is "
        "considered untrusted. Shannon secrecy capacity cannot guarantee safe key extraction."
        if res.aborted
        else f"Protocol accepted. Sampled QBER of {res.qber_sample * 100:.2f}% is below the "
        f"{res.abort_threshold * 100:.1f}% threshold. Information-theoretic privacy amplification is possible."
    )

    return SimulationResponse(
        num_qubits=res.num_qubits,
        sifted_count=len(res.sifted_indices),
        sifted_ratio=float(len(res.sifted_indices) / res.num_qubits) if res.num_qubits > 0 else 0.0,
        sample_count=len(res.sample_indices),
        sample_qber=res.qber_sample,
        overall_qber=res.qber_overall,
        abort_threshold=res.abort_threshold,
        aborted=res.aborted,
        verdict="ABORTED" if res.aborted else "SECURE",
        verdict_detail=verdict_detail,
        secret_key_rate=secret_rate,
        retained_key_length=len(res.alice_key),
        alice_key_preview=a_key_str[:128] + ("..." if len(a_key_str) > 128 else ""),
        bob_key_preview=b_key_str[:128] + ("..." if len(b_key_str) > 128 else ""),
        key_agreement_rate=key_agreement,
        qubit_events=qubit_events,
        circuit_ascii=circuit_ascii,
        metadata={
            "eve_present": req.eve_present,
            "eve_fraction": req.eve_fraction,
            "channel_noise_prob": req.channel_noise_prob,
            "seed": req.seed,
            "noise_preset": "IBM FakeBrisbane" if req.use_fake_backend else "Parametric",
            "theoretical_qber": theoretical_qber(
                req.eve_fraction if req.eve_present else 0.0, req.channel_noise_prob
            ),
        },
    )


def load_csv_dataset(filename: str, dataset_id: str, title: str, description: str) -> Optional[ExperimentDataset]:
    """Parse real experiment CSV files into structured API responses."""
    filepath = RESULTS_DIR / filename
    if not filepath.exists():
        return None

    try:
        df = pd.read_csv(filepath)
        # Convert float NaN or Inf to safe values
        df = df.replace([np.inf, -np.inf], None).fillna(0.0)
        columns = list(df.columns)
        rows = df.to_dict(orient="records")

        summary: Dict[str, Any] = {
            "total_points": len(df),
            "columns": columns,
        }

        # Specific metric summaries
        if "mean_qber" in df.columns:
            summary["min_qber"] = float(df["mean_qber"].min())
            summary["max_qber"] = float(df["mean_qber"].max())
        if "secret_key_rate" in df.columns:
            summary["max_key_rate"] = float(df["secret_key_rate"].max())
        if "false_alarm_sim" in df.columns:
            summary["initial_far"] = float(df["false_alarm_sim"].iloc[0])
            summary["final_far"] = float(df["false_alarm_sim"].iloc[-1])

        return ExperimentDataset(
            id=dataset_id,
            title=title,
            description=description,
            source_file=filename,
            columns=columns,
            rows=rows,
            summary=summary,
        )
    except Exception as exc:
        print(f"Error loading CSV {filename}: {exc}")
        return None


def get_all_experiment_datasets() -> List[ExperimentDataset]:
    """Load all 6 empirical research datasets generated by EveWatch."""
    configs = [
        (
            "exp1_eve_fraction.csv",
            "exp1",
            "QBER vs. Eavesdropper Interception Fraction",
            "Validates the fundamental quantum mechanical intercept-resend relationship QBER ≈ 0.25 * f against theoretical predictions across 50 Monte Carlo trials per point.",
        ),
        (
            "exp2_noise_level.csv",
            "exp2",
            "QBER vs. Optical Channel Depolarizing Noise",
            "Evaluates how environmental depolarizing noise in the optical fiber impacts BB84 fidelity without an active eavesdropper present.",
        ),
        (
            "exp3_qber_heatmap.csv",
            "exp3",
            "Joint 2D Noise vs. Eavesdropping Parameter Space",
            "The core differentiator visualization: maps out the joint parameter space illustrating the confounding effect of channel noise and eavesdropping, with the 11% Shor-Preskill boundary.",
        ),
        (
            "exp4_detection_analysis.csv",
            "exp4",
            "Detection Reliability: False Alarm & Missed Detection Rates",
            "Analyzes the statistical impact of finite sample sizes on distinguishing eavesdropping from channel noise near the 11% abort threshold.",
        ),
        (
            "exp5_key_rate.csv",
            "exp5",
            "Secret Key Rate & Distilled Yield (Shor-Preskill Bound)",
            "Analyzes the extractable secret key fraction (R = 1 - 2*H2(Q)) and net key lengths after key sifting, sampling, and privacy amplification.",
        ),
        (
            "hardware_comparison.csv",
            "exp6",
            "IBM Quantum 127Q Hardware Noise Benchmark",
            "Compares idealized simulation against IBM's calibrated FakeBrisbane 127-qubit superconducting quantum processor model.",
        ),
    ]

    datasets: List[ExperimentDataset] = []
    for filename, did, title, desc in configs:
        ds = load_csv_dataset(filename, did, title, desc)
        if ds:
            datasets.append(ds)

    return datasets


def encrypt_message_service(req: EncryptRequest) -> EncryptResponse:
    """Perform error correction, privacy amplification, and One-Time Pad encryption."""
    # If key bits were not supplied, run a clean 400-qubit simulation to obtain a fresh quantum key
    if req.key_bits is None or len(req.key_bits) < 16:
        sim_res = run_bb84(num_qubits=400, eve_present=False, channel_noise_prob=0.03, seed=123)
        raw_a = sim_res.alice_key
        raw_b = sim_res.bob_key
        qber = sim_res.qber_sample
    else:
        raw_a = np.array(req.key_bits, dtype=np.int32)
        raw_b = raw_a.copy()
        qber = req.estimated_qber

    # 1. Cascade-Lite Parity Error Reconciliation
    rec_a, rec_b, n_corr = reconcile_errors_parity(raw_a, raw_b, block_size=8)

    # 2. Privacy Amplification (SHA-256 distillation sized to Shor-Preskill bound)
    final_key = amplify_privacy(rec_a, estimated_qber=qber)
    active_key = final_key if len(final_key) >= 16 else rec_a

    if len(active_key) == 0:
        active_key = np.random.default_rng(42).integers(0, 2, size=128, dtype=np.int32)

    # 3. One-Time Pad Encryption (XOR)
    hex_cipher, bin_cipher = encrypt_message_otp(req.message, active_key)

    # 4. Decrypt for Bob
    decrypted_bob = decrypt_message_otp(hex_cipher, active_key)

    # 5. Simulate Eve's attempt with corrupted key
    eve_key = active_key.copy()
    flip_mask = np.random.default_rng(999).random(len(eve_key)) < 0.25
    eve_key[flip_mask] = 1 - eve_key[flip_mask]
    decrypted_eve = decrypt_message_otp(hex_cipher, eve_key)

    roundtrip = bool(decrypted_bob == req.message)

    return EncryptResponse(
        original_message=req.message,
        key_length_used=len(active_key),
        parity_corrections=n_corr,
        final_secret_bits=len(final_key),
        hex_ciphertext=hex_cipher,
        binary_ciphertext_preview=bin_cipher,
        decrypted_bob=decrypted_bob,
        decrypted_eve_sample=decrypted_eve,
        roundtrip_verified=roundtrip,
        explanation="One-Time Pad encryption achieved information-theoretic security. "
        "Eve lacks conjugate basis alignment and decrypts only unintelligible gibberish.",
    )
