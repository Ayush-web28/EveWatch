"""Unit tests for the core BB84 protocol implementation."""

import numpy as np
import pytest
from bb84.protocol import (
    generate_bits,
    generate_bases,
    sift_keys,
    estimate_qber,
    run_bb84,
)


def test_generate_bits_and_bases():
    """Verify bit and basis generation returns valid shapes and values."""
    rng = np.random.default_rng(42)
    bits = generate_bits(100, rng)
    bases = generate_bases(100, rng)

    assert len(bits) == 100
    assert len(bases) == 100
    assert set(np.unique(bits)).issubset({0, 1})
    assert set(np.unique(bases)).issubset({0, 1})


def test_sift_keys_logic():
    """Verify sifting correctly retains only matching basis positions."""
    alice_bases = np.array([0, 1, 0, 1, 0])
    bob_bases = np.array([0, 0, 0, 1, 1])
    alice_bits = np.array([1, 0, 1, 1, 0])
    bob_bits = np.array([1, 1, 1, 1, 1])

    sifted_idx, a_sift, b_sift = sift_keys(alice_bases, bob_bases, alice_bits, bob_bits)

    # Matching indices are 0 (0==0), 2 (0==0), 3 (1==1)
    np.testing.assert_array_equal(sifted_idx, [0, 2, 3])
    np.testing.assert_array_equal(a_sift, [1, 1, 1])
    np.testing.assert_array_equal(b_sift, [1, 1, 1])


def test_estimate_qber_removes_sample():
    """Verify sample estimation reveals sample and removes it from final key."""
    rng = np.random.default_rng(42)
    a_sift = np.array([0, 1, 0, 1, 0, 1, 0, 1])
    b_sift = np.array([0, 1, 0, 1, 0, 1, 0, 1])

    qber, sample_idx, sample_a, sample_b, rem_a, rem_b = estimate_qber(
        a_sift, b_sift, sample_size=4, rng=rng
    )

    assert qber == 0.0
    assert len(sample_idx) == 4
    assert len(rem_a) == 4
    assert len(rem_b) == 4
    assert len(rem_a) + len(sample_idx) == len(a_sift)
    # Remaining keys must be identical
    np.testing.assert_array_equal(rem_a, rem_b)


def test_sanity_no_eve_no_noise():
    """Sanity test: with no Eve and no noise, QBER must be exactly 0 and keys identical."""
    res = run_bb84(
        num_qubits=400,
        eve_present=False,
        channel_noise_prob=0.0,
        depolarizing_error_prob=0.0,
        readout_error_prob=0.0,
        sample_size=0.5,
        abort_threshold=0.11,
        seed=12345,
    )

    # Key sanity checks
    assert res.qber_overall == 0.0, f"Expected 0 overall QBER, got {res.qber_overall}"
    assert res.qber_sample == 0.0, f"Expected 0 sample QBER, got {res.qber_sample}"
    assert not res.aborted, "Protocol should not abort when channel is clean"
    assert "SECURE" in res.verdict
    assert len(res.alice_key) > 0, "Remaining key should be non-empty"
    np.testing.assert_array_equal(
        res.alice_key, res.bob_key, err_msg="Alice and Bob keys must be strictly identical"
    )

    # Sifting ratio should be approximately 50%
    sift_ratio = len(res.sifted_indices) / res.num_qubits
    assert 0.40 <= sift_ratio <= 0.60, f"Sifting ratio {sift_ratio} deviates from ~50%"
