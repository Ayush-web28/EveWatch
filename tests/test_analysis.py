"""Unit tests for information-theoretic analysis and statistical utilities."""

import pytest
from bb84.analysis import (
    binary_entropy,
    asymptotic_secret_key_rate,
    theoretical_qber,
    binomial_detection_probabilities,
    run_trials,
)


def test_binary_entropy_properties():
    """Verify Shannon binary entropy edge cases and symmetry."""
    assert binary_entropy(0.0) == 0.0
    assert binary_entropy(1.0) == 0.0
    assert binary_entropy(0.5) == 1.0
    assert abs(binary_entropy(0.11) - 0.500) < 0.01
    # Symmetry H2(p) == H2(1-p)
    assert abs(binary_entropy(0.2) - binary_entropy(0.8)) < 1e-9


def test_asymptotic_secret_key_rate_cutoff():
    """Verify Shor-Preskill secret key rate drops to 0 at 11% QBER."""
    # QBER = 0 -> rate = 1.0
    assert asymptotic_secret_key_rate(0.0) == 1.0

    # At 5% QBER -> rate > 0
    assert asymptotic_secret_key_rate(0.05) > 0.4

    # At 11.0% threshold -> rate ~ 0.0
    assert asymptotic_secret_key_rate(0.11) < 0.01

    # Above 11% threshold -> rate strictly 0
    assert asymptotic_secret_key_rate(0.12) == 0.0
    assert asymptotic_secret_key_rate(0.25) == 0.0


def test_theoretical_qber_formula():
    """Verify analytical QBER formula matching physics."""
    # No noise, no Eve -> 0.0
    assert theoretical_qber(0.0, 0.0) == 0.0

    # f=1.0, no noise -> 0.25
    assert theoretical_qber(1.0, 0.0) == 0.25

    # f=0.0, p_ch=0.2 -> 0.10
    assert theoretical_qber(0.0, 0.2) == 0.10


def test_binomial_detection_probabilities():
    """Verify finite-sample binomial probabilities for false alarm and missed detection."""
    # If sample size is 500 and true QBER is 0.05, prob of flagging (>11%) should be near zero
    p_flag, p_acc = binomial_detection_probabilities(sample_size=500, true_qber=0.05, abort_threshold=0.11)
    assert p_flag < 0.001
    assert p_acc > 0.999

    # If true QBER is 0.25 (full Eve), prob of accepting (<=11%) must be negligible
    p_flag_eve, p_acc_eve = binomial_detection_probabilities(sample_size=500, true_qber=0.25, abort_threshold=0.11)
    assert p_flag_eve > 0.999
    assert p_acc_eve < 0.001


def test_run_trials_aggregation():
    """Verify multi-trial aggregation returns expected keys and types."""
    stats = run_trials(
        num_trials=5,
        num_qubits=200,
        eve_present=True,
        eve_fraction=0.8,
        base_seed=777,
    )
    assert "mean_qber_sample" in stats
    assert "std_qber_sample" in stats
    assert "abort_rate" in stats
    assert "missed_detection_rate" in stats
    assert stats["mean_qber_sample"] > 0.10
