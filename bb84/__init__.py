"""EveWatch: Distinguishing Quantum Eavesdroppers from Hardware Noise in BB84.

Core library providing BB84 protocol simulation in Qiskit 2.x,
intercept-resend eavesdropping modeling, realistic hardware and channel noise,
statistical detection analysis, error reconciliation, and privacy amplification.
"""

from bb84.protocol import (
    BB84Result,
    run_bb84,
    build_bb84_circuit,
    sift_keys,
    estimate_qber,
    generate_bits,
    generate_bases,
)
from bb84.eve import Eavesdropper
from bb84.noise import create_noise_model, get_fake_backend_noise_model
from bb84.analysis import (
    binary_entropy,
    asymptotic_secret_key_rate,
    theoretical_qber,
    run_trials,
    binomial_detection_probabilities,
)
from bb84.postprocessing import (
    reconcile_errors_parity,
    amplify_privacy,
    encrypt_message_otp,
    decrypt_message_otp,
)

__version__ = "1.0.0"
__author__ = "Ayush Trivedi"
__all__ = [
    "BB84Result",
    "run_bb84",
    "build_bb84_circuit",
    "sift_keys",
    "estimate_qber",
    "generate_bits",
    "generate_bases",
    "Eavesdropper",
    "create_noise_model",
    "get_fake_backend_noise_model",
    "binary_entropy",
    "asymptotic_secret_key_rate",
    "theoretical_qber",
    "run_trials",
    "binomial_detection_probabilities",
    "reconcile_errors_parity",
    "amplify_privacy",
    "encrypt_message_otp",
    "decrypt_message_otp",
]
