"""Noise modeling module for EveWatch BB84 simulation.

Provides configurable noise models representing gate infidelities,
measurement readout errors, optical channel depolarizing noise,
and realistic IBM Quantum hardware noise from fake backends.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

logger = logging.getLogger(__name__)


def create_noise_model(
    depolarizing_error_prob: float = 0.0,
    readout_error_prob: float = 0.0,
    channel_noise_prob: float = 0.0,
) -> NoiseModel:
    """Create a configurable Qiskit Aer NoiseModel for BB84 simulations.

    Args:
        depolarizing_error_prob: Depolarizing error probability for single-qubit
            gates ('x', 'h'). Range [0.0, 1.0].
        readout_error_prob: Symmetric measurement readout error probability.
            Range [0.0, 1.0].
        channel_noise_prob: Depolarizing error on the transmission channel
            ('id' gate representing optical fiber/free-space link). Range [0.0, 1.0].

    Returns:
        NoiseModel: Configured Aer noise model.
    """
    noise_model = NoiseModel()

    # Gate depolarizing error
    if depolarizing_error_prob > 0.0:
        p_gate = min(max(depolarizing_error_prob, 0.0), 0.75)
        gate_err = depolarizing_error(p_gate, 1)
        noise_model.add_all_qubit_quantum_error(gate_err, ["x", "h"])

    # Channel depolarizing error (applied to 'id' gate placed during quantum transit)
    if channel_noise_prob > 0.0:
        p_ch = min(max(channel_noise_prob, 0.0), 0.75)
        channel_err = depolarizing_error(p_ch, 1)
        noise_model.add_all_qubit_quantum_error(channel_err, ["id"])

    # Readout error
    if readout_error_prob > 0.0:
        p_ro = min(max(readout_error_prob, 0.0), 0.5)
        ro_matrix = [[1.0 - p_ro, p_ro], [p_ro, 1.0 - p_ro]]
        readout_err = ReadoutError(ro_matrix)
        noise_model.add_all_qubit_readout_error(readout_err)

    return noise_model


def get_fake_backend_noise_model(
    backend_name: str = "FakeBrisbane",
) -> Tuple[Optional[NoiseModel], str]:
    """Load a calibrated noise model from an IBM fake backend with fallback.

    Args:
        backend_name: Name of fake provider backend (e.g. 'FakeBrisbane',
            'FakeSherbrooke', 'FakeCairoV2').

    Returns:
        Tuple of (NoiseModel or None, description_str).
    """
    try:
        import qiskit_ibm_runtime.fake_provider as fake_provider

        if hasattr(fake_provider, backend_name):
            backend_cls = getattr(fake_provider, backend_name)
            backend_instance = backend_cls()
            noise_model = NoiseModel.from_backend(backend_instance)
            desc = f"{backend_name} ({backend_instance.num_qubits} qubits, calibrated IBM Quantum processor)"
            return noise_model, desc
        else:
            # Fallback to FakeBrisbane or FakeSherbrooke
            for fallback_name in ["FakeBrisbane", "FakeSherbrooke", "FakeCairoV2"]:
                if hasattr(fake_provider, fallback_name):
                    backend_cls = getattr(fake_provider, fallback_name)
                    backend_instance = backend_cls()
                    noise_model = NoiseModel.from_backend(backend_instance)
                    desc = f"{fallback_name} (fallback: {backend_instance.num_qubits} qubits)"
                    return noise_model, desc

            return None, "No suitable IBM fake backend found in fake_provider"
    except Exception as exc:
        logger.warning("Failed to load fake backend: %s", exc)
        return None, f"Fake backend unavailable ({exc})"
