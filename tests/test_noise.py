"""Unit tests for noise modeling and realistic hardware noise in BB84."""

import numpy as np
import pytest
from bb84.noise import create_noise_model, get_fake_backend_noise_model
from bb84.protocol import run_bb84


def test_channel_noise_scaling():
    """Verify that channel noise alone without Eve increases QBER linearly (Q ~ p_ch / 2)."""
    p_ch_values = [0.06, 0.16]
    measured = []

    for p in p_ch_values:
        trial_qbers = []
        for seed in [301, 302, 303]:
            res = run_bb84(
                num_qubits=1000,
                eve_present=False,
                channel_noise_prob=p,
                seed=seed,
            )
            trial_qbers.append(res.qber_overall)
        measured.append(float(np.mean(trial_qbers)))

    # Theoretical: p=0.06 -> 0.03; p=0.16 -> 0.08
    assert abs(measured[0] - 0.03) < 0.02, f"Expected ~0.03, got {measured[0]}"
    assert abs(measured[1] - 0.08) < 0.02, f"Expected ~0.08, got {measured[1]}"
    assert measured[0] < measured[1], "Higher channel noise must yield higher QBER"


def test_gate_and_readout_noise():
    """Verify depolarizing gate and readout errors produce non-zero QBER."""
    res = run_bb84(
        num_qubits=500,
        eve_present=False,
        depolarizing_error_prob=0.04,
        readout_error_prob=0.03,
        seed=401,
    )
    assert res.qber_overall > 0.01, f"Expected non-zero QBER from noise, got {res.qber_overall}"


def test_fake_ibm_backend_noise_model():
    """Verify that fake IBM backend noise model loads and runs gracefully."""
    noise_model, desc = get_fake_backend_noise_model("FakeBrisbane")
    assert noise_model is not None, "Failed to load FakeBrisbane noise model"
    assert "Brisbane" in desc

    res = run_bb84(
        num_qubits=50,
        eve_present=False,
        noise_model=noise_model,
        seed=501,
    )
    assert res.qber_overall >= 0.0, "Execution with fake IBM backend noise should succeed"
    assert isinstance(res.aborted, bool)
