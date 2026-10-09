"""Eavesdropper (Eve) module for EveWatch BB84 simulation.

Implements the intercept-resend attack with a configurable interception
fraction f in [0, 1]. In this attack, Eve measures intercepted qubits
in a randomly selected basis (Z or X) and retransmits the post-measurement
state to Bob.
"""

from __future__ import annotations

import numpy as np
from typing import Tuple


class Eavesdropper:
    """Intercept-Resend Eavesdropper with configurable interception fraction."""

    def __init__(self, interception_fraction: float = 1.0, seed: int | None = None):
        """Initialize Eavesdropper.

        Args:
            interception_fraction: Probability f in [0, 1] of intercepting each qubit.
            seed: Optional random seed for reproducible interception choices.
        """
        self.fraction = min(max(float(interception_fraction), 0.0), 1.0)
        self.rng = np.random.default_rng(seed)

    def plan_interceptions(self, num_qubits: int) -> Tuple[np.ndarray, np.ndarray]:
        """Decide which qubits to intercept and choose measurement bases.

        Args:
            num_qubits: Total number of transmitted qubits.

        Returns:
            Tuple of:
                intercept_mask: Boolean array of length num_qubits (True if intercepted).
                eve_bases: Integer array of length num_qubits with bases (0=Z, 1=X).
        """
        if self.fraction <= 0.0:
            intercept_mask = np.zeros(num_qubits, dtype=bool)
        elif self.fraction >= 1.0:
            intercept_mask = np.ones(num_qubits, dtype=bool)
        else:
            intercept_mask = self.rng.random(num_qubits) < self.fraction

        eve_bases = self.rng.integers(0, 2, size=num_qubits)
        return intercept_mask, eve_bases

    @staticmethod
    def theoretical_qber(interception_fraction: float, channel_error: float = 0.0) -> float:
        """Calculate theoretical QBER resulting from Eve and independent channel noise.

        Theoretical derivation:
            Eve introduces error with probability 0.25 on intercepted qubits.
            Channel noise introduces bit-flip error with probability e_ch = channel_error / 2.
            Combined error on sifted bits:
            Q = e_eve * f * (1 - e_ch) + (1 - e_eve * f) * e_ch

        Args:
            interception_fraction: Interception rate f in [0, 1].
            channel_error: Channel depolarizing error parameter.

        Returns:
            Expected QBER in [0, 0.5].
        """
        f = min(max(float(interception_fraction), 0.0), 1.0)
        e_eve = 0.25 * f
        e_ch = 0.5 * channel_error
        # Combined probability of an odd number of flips
        q = e_eve * (1.0 - e_ch) + (1.0 - e_eve) * e_ch
        return float(np.clip(q, 0.0, 0.5))
