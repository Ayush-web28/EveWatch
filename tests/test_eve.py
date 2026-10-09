"""Unit tests for Eavesdropper (Eve) intercept-resend attack and scaling."""

import numpy as np
import pytest
from bb84.eve import Eavesdropper
from bb84.protocol import run_bb84


def test_eve_planning_masks():
    """Verify interception mask fractions match requested parameters."""
    eve_full = Eavesdropper(interception_fraction=1.0, seed=42)
    mask_full, bases_full = eve_full.plan_interceptions(200)
    assert np.all(mask_full), "f=1.0 must intercept all qubits"
    assert len(bases_full) == 200

    eve_none = Eavesdropper(interception_fraction=0.0, seed=42)
    mask_none, _ = eve_none.plan_interceptions(200)
    assert not np.any(mask_none), "f=0.0 must intercept zero qubits"

    eve_half = Eavesdropper(interception_fraction=0.5, seed=42)
    mask_half, _ = eve_half.plan_interceptions(1000)
    frac = np.mean(mask_half)
    assert 0.45 <= frac <= 0.55, f"Interception fraction {frac} should be close to 0.5"


def test_eve_full_interception_25_percent_qber():
    """Test: with f = 1 and no noise, QBER must be approximately 25% (within statistical tolerance)."""
    # Run across 3 seeds to ensure statistical robustness with 1000 qubits
    qbers = []
    for seed in [101, 102, 103]:
        res = run_bb84(
            num_qubits=1000,
            eve_present=True,
            eve_fraction=1.0,
            channel_noise_prob=0.0,
            sample_size=0.5,
            seed=seed,
        )
        qbers.append(res.qber_overall)

    mean_qber = float(np.mean(qbers))
    # 25% expectation: 3-sigma tolerance for 500 sifted bits is ~0.045
    assert 0.21 <= mean_qber <= 0.29, (
        f"Expected QBER ~0.25 for f=1.0, got {mean_qber:.4f}"
    )


def test_eve_qber_scaling():
    """Test: QBER should scale approximately as 0.25*f across fractions [0.2, 0.5, 0.8]."""
    fractions = [0.2, 0.5, 0.8]
    measured_qbers = []

    for f in fractions:
        trial_qbers = []
        for seed in [201, 202, 203]:
            res = run_bb84(
                num_qubits=1000,
                eve_present=True,
                eve_fraction=f,
                channel_noise_prob=0.0,
                sample_size=0.5,
                seed=seed,
            )
            trial_qbers.append(res.qber_overall)
        measured_qbers.append(float(np.mean(trial_qbers)))

    # Theoretical values: 0.05, 0.125, 0.20
    for f, q_meas in zip(fractions, measured_qbers):
        q_theo = 0.25 * f
        assert abs(q_meas - q_theo) < 0.04, (
            f"For f={f}, expected ~{q_theo:.3f}, got {q_meas:.3f}"
        )

    # Monotonic scaling: QBER(0.2) < QBER(0.5) < QBER(0.8)
    assert measured_qbers[0] < measured_qbers[1] < measured_qbers[2], (
        f"QBER must scale monotonically with f: {measured_qbers}"
    )
