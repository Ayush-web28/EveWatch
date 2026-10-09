"""Core BB84 Quantum Key Distribution protocol implementation in Qiskit 2.x.

Implements state preparation by Alice, quantum channel transit with optional
eavesdropping by Eve and environmental noise, measurement by Bob, key sifting,
and sample-based QBER estimation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple, Union
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

from bb84.eve import Eavesdropper
from bb84.noise import create_noise_model


@dataclass
class BB84Result:
    """Encapsulates the complete execution trace and output of a BB84 protocol run."""

    num_qubits: int
    alice_bits: np.ndarray
    alice_bases: np.ndarray
    bob_bases: np.ndarray
    bob_bits: np.ndarray
    eve_intercepted: np.ndarray
    eve_bases: np.ndarray
    eve_bits: np.ndarray
    sifted_indices: np.ndarray
    alice_sifted: np.ndarray
    bob_sifted: np.ndarray
    sample_indices: np.ndarray
    sample_alice_bits: np.ndarray
    sample_bob_bits: np.ndarray
    qber_sample: float
    qber_overall: float
    key_indices: np.ndarray
    alice_key: np.ndarray
    bob_key: np.ndarray
    abort_threshold: float
    aborted: bool
    verdict: str
    metadata: dict = field(default_factory=dict)
    circuit: Optional[QuantumCircuit] = None


def generate_bits(num_bits: int, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """Generate uniform random classical bits (0 or 1)."""
    generator = rng if rng is not None else np.random.default_rng()
    return generator.integers(0, 2, size=num_bits, dtype=np.int32)


def generate_bases(num_bases: int, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """Generate uniform random measurement bases (0: Z basis, 1: X basis)."""
    generator = rng if rng is not None else np.random.default_rng()
    return generator.integers(0, 2, size=num_bases, dtype=np.int32)


def sift_keys(
    alice_bases: np.ndarray,
    bob_bases: np.ndarray,
    alice_bits: np.ndarray,
    bob_bits: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Perform key sifting by identifying matching basis positions.

    Args:
        alice_bases: Basis used by Alice (0=Z, 1=X).
        bob_bases: Basis used by Bob (0=Z, 1=X).
        alice_bits: Raw bits prepared by Alice.
        bob_bits: Raw bits measured by Bob.

    Returns:
        Tuple of (sifted_indices, alice_sifted_bits, bob_sifted_bits).
    """
    sifted_mask = alice_bases == bob_bases
    sifted_indices = np.where(sifted_mask)[0]
    alice_sifted = alice_bits[sifted_indices]
    bob_sifted = bob_bits[sifted_indices]
    return sifted_indices, alice_sifted, bob_sifted


def estimate_qber(
    alice_sifted: np.ndarray,
    bob_sifted: np.ndarray,
    sample_size: Union[int, float] = 0.5,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Estimate QBER by revealing and sacrificing a subset of the sifted key.

    Args:
        alice_sifted: Sifted bits from Alice.
        bob_sifted: Sifted bits from Bob.
        sample_size: Fraction in (0, 1) or integer bit count to sample.
        rng: Random number generator for reproducible sampling.

    Returns:
        Tuple of:
            qber: Fraction of bit mismatches in the sample [0.0, 1.0].
            sample_indices: Indices within the sifted array sacrificed for testing.
            sample_alice: Revealed Alice bits.
            sample_bob: Revealed Bob bits.
            remaining_alice_key: Secret key bits retained by Alice.
            remaining_bob_key: Secret key bits retained by Bob.
    """
    n_sifted = len(alice_sifted)
    if n_sifted == 0:
        empty = np.array([], dtype=np.int32)
        return 0.0, empty, empty, empty, empty, empty

    generator = rng if rng is not None else np.random.default_rng()

    if isinstance(sample_size, float) and 0.0 < sample_size < 1.0:
        k = max(1, int(round(sample_size * n_sifted)))
    else:
        k = max(1, min(int(sample_size), n_sifted))

    all_indices = np.arange(n_sifted)
    sample_indices = np.sort(generator.choice(all_indices, size=k, replace=False))

    key_mask = np.ones(n_sifted, dtype=bool)
    key_mask[sample_indices] = False
    key_indices = np.where(key_mask)[0]

    sample_alice = alice_sifted[sample_indices]
    sample_bob = bob_sifted[sample_indices]

    errors = np.count_nonzero(sample_alice != sample_bob)
    qber = float(errors / k) if k > 0 else 0.0

    remaining_alice_key = alice_sifted[key_indices]
    remaining_bob_key = bob_sifted[key_indices]

    return (
        qber,
        sample_indices,
        sample_alice,
        sample_bob,
        remaining_alice_key,
        remaining_bob_key,
    )


def build_bb84_circuit(
    alice_bits: np.ndarray,
    alice_bases: np.ndarray,
    bob_bases: np.ndarray,
    eve_intercepted: Optional[np.ndarray] = None,
    eve_bases: Optional[np.ndarray] = None,
    apply_channel_id: bool = True,
) -> QuantumCircuit:
    """Build a consolidated Qiskit QuantumCircuit for BB84 transmission.

    All operations are Cliffords (X, H, Id, Measure), enabling ultra-fast
    stabilizer simulation in AerSimulator.

    Args:
        alice_bits: Bits prepared by Alice (0 or 1).
        alice_bases: Bases chosen by Alice (0=Z, 1=X).
        bob_bases: Bases chosen by Bob (0=Z, 1=X).
        eve_intercepted: Optional boolean mask of qubits intercepted by Eve.
        eve_bases: Optional bases chosen by Eve (0=Z, 1=X).
        apply_channel_id: If True, inserts 'id' gate on all qubits in transit
            to expose them to channel depolarizing noise.

    Returns:
        QuantumCircuit: Complete execution circuit.
    """
    n = len(alice_bits)
    qr = QuantumRegister(n, "q")
    cr_bob = ClassicalRegister(n, "bob")

    has_eve = eve_intercepted is not None and np.any(eve_intercepted)
    if has_eve:
        cr_eve = ClassicalRegister(n, "eve")
        qc = QuantumCircuit(qr, cr_eve, cr_bob)
    else:
        cr_eve = None
        qc = QuantumCircuit(qr, cr_bob)

    # Step 1: Alice state preparation
    for i in range(n):
        if alice_bits[i] == 1:
            qc.x(qr[i])
        if alice_bases[i] == 1:
            qc.h(qr[i])

    # Step 2: Eve intercept-resend attack (if active)
    if has_eve and cr_eve is not None and eve_bases is not None:
        for i in range(n):
            if eve_intercepted[i]:
                # Rotate to Eve's basis
                if eve_bases[i] == 1:
                    qc.h(qr[i])
                # Intercept measurement
                qc.measure(qr[i], cr_eve[i])
                # Resend in Eve's measured eigenstate (H rotates back if X basis)
                if eve_bases[i] == 1:
                    qc.h(qr[i])

    # Step 3: Optical channel transit
    if apply_channel_id:
        for i in range(n):
            qc.id(qr[i])

    # Step 4: Bob measurement
    for i in range(n):
        if bob_bases[i] == 1:
            qc.h(qr[i])
        qc.measure(qr[i], cr_bob[i])

    return qc


def run_bb84(
    num_qubits: int = 500,
    eve_present: bool = False,
    eve_fraction: float = 1.0,
    noise_model: Optional[NoiseModel] = None,
    channel_noise_prob: float = 0.0,
    depolarizing_error_prob: float = 0.0,
    readout_error_prob: float = 0.0,
    sample_size: Union[int, float] = 0.5,
    abort_threshold: float = 0.11,
    seed: Optional[int] = None,
    save_circuit: bool = False,
) -> BB84Result:
    """Execute an end-to-end BB84 protocol run using Qiskit AerSimulator.

    Args:
        num_qubits: Total number of qubits Alice sends.
        eve_present: Whether an eavesdropper is listening.
        eve_fraction: Interception probability f in [0, 1].
        noise_model: Pre-built NoiseModel (e.g. from fake backend). If None,
            built from error probabilities.
        channel_noise_prob: Optical channel depolarizing probability.
        depolarizing_error_prob: Gate depolarizing probability.
        readout_error_prob: Measurement readout error probability.
        sample_size: Sifted bits fraction or count sampled for QBER estimation.
        abort_threshold: Security QBER threshold (default 11%).
        seed: Random seed for 100% reproducible execution.
        save_circuit: If True, stores the QuantumCircuit inside BB84Result.

    Returns:
        BB84Result with full execution details, keys, and security verdict.
    """
    rng = np.random.default_rng(seed)
    seed_sim = int(rng.integers(0, 2**31 - 1)) if seed is not None else None

    # 1. Classical preparation
    alice_bits = generate_bits(num_qubits, rng)
    alice_bases = generate_bases(num_qubits, rng)
    bob_bases = generate_bases(num_qubits, rng)

    # 2. Eve interception planning
    if eve_present and eve_fraction > 0.0:
        eve = Eavesdropper(interception_fraction=eve_fraction, seed=seed)
        eve_intercepted, eve_bases = eve.plan_interceptions(num_qubits)
    else:
        eve_intercepted = np.zeros(num_qubits, dtype=bool)
        eve_bases = np.zeros(num_qubits, dtype=np.int32)

    # 3. Build quantum circuit
    qc = build_bb84_circuit(
        alice_bits=alice_bits,
        alice_bases=alice_bases,
        bob_bases=bob_bases,
        eve_intercepted=eve_intercepted,
        eve_bases=eve_bases,
        apply_channel_id=True,
    )

    # 4. Resolve noise model
    active_noise = noise_model
    if active_noise is None:
        if (
            channel_noise_prob > 0.0
            or depolarizing_error_prob > 0.0
            or readout_error_prob > 0.0
        ):
            active_noise = create_noise_model(
                depolarizing_error_prob=depolarizing_error_prob,
                readout_error_prob=readout_error_prob,
                channel_noise_prob=channel_noise_prob,
            )

    # 5. Quantum Simulation via AerSimulator
    # Check if noise model contains Kraus/non-Clifford instructions
    def _is_stabilizer_compatible(nm: Optional[NoiseModel]) -> bool:
        if nm is None:
            return True
        try:
            ndict = nm.to_dict()
            for err in ndict.get("errors", []):
                for inst in err.get("instructions", []):
                    if isinstance(inst, list):
                        for sub in inst:
                            if isinstance(sub, dict) and sub.get("name") == "kraus":
                                return False
                    elif isinstance(inst, dict) and inst.get("name") == "kraus":
                        return False
        except Exception:
            return False
        return True

    use_stabilizer = _is_stabilizer_compatible(active_noise)

    if use_stabilizer:
        # Full N-qubit Clifford circuit in Aer's stabilizer method (O(N) runtime)
        simulator = AerSimulator(method="stabilizer", noise_model=active_noise)
        res = simulator.run(qc, shots=1, seed_simulator=seed_sim).result()
        counts_key = list(res.get_counts().keys())[0]

        if " " in counts_key:
            bob_str, eve_str = counts_key.split(" ")
            eve_bits = np.array([int(eve_str[num_qubits - 1 - i]) for i in range(num_qubits)], dtype=np.int32)
        else:
            bob_str = counts_key
            eve_bits = np.zeros(num_qubits, dtype=np.int32)

        bob_bits = np.array([int(bob_str[num_qubits - 1 - i]) for i in range(num_qubits)], dtype=np.int32)
    else:
        # For general Kraus / hardware noise, batch into small sub-circuits (chunk size 5)
        chunk_size = 5
        sub_circuits = []
        for start in range(0, num_qubits, chunk_size):
            end = min(start + chunk_size, num_qubits)
            sub_qc = build_bb84_circuit(
                alice_bits=alice_bits[start:end],
                alice_bases=alice_bases[start:end],
                bob_bases=bob_bases[start:end],
                eve_intercepted=eve_intercepted[start:end] if eve_intercepted is not None else None,
                eve_bases=eve_bases[start:end] if eve_bases is not None else None,
                apply_channel_id=True,
            )
            sub_circuits.append(sub_qc)

        simulator = AerSimulator(noise_model=active_noise)
        res = simulator.run(sub_circuits, shots=1, seed_simulator=seed_sim).result()

        bob_list: list[int] = []
        eve_list: list[int] = []
        for idx, sub_c in enumerate(sub_circuits):
            c_res = res.get_counts(idx)
            c_key = list(c_res.keys())[0]
            m = sub_c.num_qubits
            if " " in c_key:
                b_str, e_str = c_key.split(" ")
                e_chunk = [int(e_str[m - 1 - k]) for k in range(m)]
            else:
                b_str = c_key
                e_chunk = [0] * m
            b_chunk = [int(b_str[m - 1 - k]) for k in range(m)]
            bob_list.extend(b_chunk)
            eve_list.extend(e_chunk)

        bob_bits = np.array(bob_list, dtype=np.int32)
        eve_bits = np.array(eve_list, dtype=np.int32)

    # 6. Key Sifting
    sifted_indices, alice_sifted, bob_sifted = sift_keys(
        alice_bases=alice_bases,
        bob_bases=bob_bases,
        alice_bits=alice_bits,
        bob_bits=bob_bits,
    )

    # Compute overall QBER (for ground truth reference)
    if len(alice_sifted) > 0:
        qber_overall = float(np.mean(alice_sifted != bob_sifted))
    else:
        qber_overall = 0.0

    # 7. QBER Estimation from sacrificed sample
    (
        qber_sample,
        sample_indices_in_sifted,
        sample_alice_bits,
        sample_bob_bits,
        alice_key,
        bob_key,
    ) = estimate_qber(
        alice_sifted=alice_sifted,
        bob_sifted=bob_sifted,
        sample_size=sample_size,
        rng=rng,
    )

    # Absolute sample indices in original transmission
    sample_indices = (
        sifted_indices[sample_indices_in_sifted]
        if len(sample_indices_in_sifted) > 0
        else np.array([], dtype=np.int32)
    )

    # Key indices retained
    key_mask = np.ones(len(sifted_indices), dtype=bool)
    if len(sample_indices_in_sifted) > 0:
        key_mask[sample_indices_in_sifted] = False
    key_indices = sifted_indices[key_mask]

    # 8. Verdict & Abort decision
    aborted = bool(qber_sample > abort_threshold)
    verdict = "ABORTED (Eavesdropper or high noise detected)" if aborted else "SECURE (Channel verified)"

    return BB84Result(
        num_qubits=num_qubits,
        alice_bits=alice_bits,
        alice_bases=alice_bases,
        bob_bases=bob_bases,
        bob_bits=bob_bits,
        eve_intercepted=eve_intercepted,
        eve_bases=eve_bases,
        eve_bits=eve_bits,
        sifted_indices=sifted_indices,
        alice_sifted=alice_sifted,
        bob_sifted=bob_sifted,
        sample_indices=sample_indices,
        sample_alice_bits=sample_alice_bits,
        sample_bob_bits=sample_bob_bits,
        qber_sample=qber_sample,
        qber_overall=qber_overall,
        key_indices=key_indices,
        alice_key=alice_key,
        bob_key=bob_key,
        abort_threshold=abort_threshold,
        aborted=aborted,
        verdict=verdict,
        circuit=qc if save_circuit else None,
        metadata={
            "eve_present": eve_present,
            "eve_fraction": eve_fraction,
            "channel_noise_prob": channel_noise_prob,
            "depolarizing_error_prob": depolarizing_error_prob,
            "readout_error_prob": readout_error_prob,
            "seed": seed,
        },
    )
