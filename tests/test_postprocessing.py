"""Unit tests for classical post-processing: reconciliation, privacy amplification, and OTP."""

import numpy as np
import pytest
from bb84.postprocessing import (
    reconcile_errors_parity,
    amplify_privacy,
    encrypt_message_otp,
    decrypt_message_otp,
)


def test_parity_error_reconciliation():
    """Verify parity bisection corrects single-bit mismatches in blocks."""
    alice_key = np.array([1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1])
    bob_key = alice_key.copy()
    # Introduce bit flips in different blocks
    bob_key[3] = 1 - bob_key[3]
    bob_key[11] = 1 - bob_key[11]

    assert not np.array_equal(alice_key, bob_key)

    rec_a, rec_b, corrections = reconcile_errors_parity(alice_key, bob_key, block_size=8)
    assert corrections == 2
    np.testing.assert_array_equal(rec_a, rec_b, err_msg="Keys must match after reconciliation")


def test_privacy_amplification():
    """Verify privacy amplification hashes and compresses raw keys appropriately."""
    raw_key = np.random.default_rng(42).integers(0, 2, size=100)
    # With 5% QBER, extractable fraction is ~ 1 - 2*H2(0.05) ~ 0.428 -> ~42 bits
    secure_key = amplify_privacy(raw_key, estimated_qber=0.05)
    assert len(secure_key) > 30
    assert len(secure_key) < 60
    assert set(np.unique(secure_key)).issubset({0, 1})

    # With high QBER >= 11%, extractable length should be 0
    insecure_key = amplify_privacy(raw_key, estimated_qber=0.15)
    assert len(insecure_key) == 0


def test_otp_encryption_roundtrip():
    """Verify One-Time Pad encryption and decryption restores exact plaintext."""
    message = "Quantum Secure Communication @ Qiskit Fall Fest 2026!"
    key_bits = np.random.default_rng(123).integers(0, 2, size=256)

    hex_cipher, bin_preview = encrypt_message_otp(message, key_bits)
    assert len(hex_cipher) > 0
    assert len(bin_preview) > 0

    decrypted = decrypt_message_otp(hex_cipher, key_bits)
    assert decrypted == message, f"Expected '{message}', got '{decrypted}'"
