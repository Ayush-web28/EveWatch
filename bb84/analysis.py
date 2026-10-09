"""Analytical and statistical tools for BB84 QKD security analysis.

Includes Shannon entropy, Shor-Preskill asymptotic secret key rates,
theoretical QBER models, detection reliability metrics (false-alarm / missed-detection),
and multi-trial statistical aggregation.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats

from bb84.protocol import run_bb84, BB84Result


def binary_entropy(p: float) -> float:
    """Compute the binary Shannon entropy H2(p) = -p log2(p) - (1-p) log2(1-p).

    Args:
        p: Probability in [0, 1].

    Returns:
        Shannon entropy in bits [0.0, 1.0].
    """
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return float(-p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p))


def asymptotic_secret_key_rate(qber: float) -> float:
    """Compute asymptotic secret key rate R = max(0, 1 - 2*H2(QBER)).

    This is the celebrated Shor-Preskill security bound against general
    coherent attacks in BB84. For QBER >= 11.0%, the rate drops to zero.

    Args:
        qber: Quantum Bit Error Rate in [0, 1].

    Returns:
        Fraction of secret bits extractable per sifted bit [0.0, 1.0].
    """
    if qber < 0.0 or qber >= 0.5:
        return 0.0
    h2 = binary_entropy(qber)
    rate = 1.0 - 2.0 * h2
    return max(0.0, float(rate))


def theoretical_qber(eve_fraction: float, channel_noise_prob: float) -> float:
    """Theoretical QBER under intercept-resend Eve and channel depolarizing noise.

    Derivation:
        - Intercepted sifted qubits suffer 25% error: e_eve = 0.25 * eve_fraction.
        - Channel depolarizing noise flips a bit with probability e_ch = channel_noise_prob / 2.
        - Total error is the union of independent flips:
          Q = e_eve * (1 - e_ch) + (1 - e_eve) * e_ch
    """
    e_eve = 0.25 * float(np.clip(eve_fraction, 0.0, 1.0))
    e_ch = 0.5 * float(np.clip(channel_noise_prob, 0.0, 1.0))
    return float(np.clip(e_eve * (1.0 - e_ch) + (1.0 - e_eve) * e_ch, 0.0, 0.5))


def run_trials(
    num_trials: int = 50,
    num_qubits: int = 500,
    eve_present: bool = False,
    eve_fraction: float = 1.0,
    channel_noise_prob: float = 0.0,
    depolarizing_error_prob: float = 0.0,
    readout_error_prob: float = 0.0,
    sample_size: float = 0.5,
    abort_threshold: float = 0.11,
    base_seed: int = 100,
) -> Dict[str, float]:
    """Run multiple independent BB84 trials and aggregate metrics.

    Args:
        num_trials: Number of trials (default 50).
        num_qubits: Number of qubits per trial.
        eve_present: Whether Eve is active.
        eve_fraction: Interception fraction f in [0, 1].
        channel_noise_prob: Channel depolarizing error parameter.
        depolarizing_error_prob: Gate depolarizing error.
        readout_error_prob: Readout measurement error.
        sample_size: Fraction or count of sifted bits sampled for QBER.
        abort_threshold: Abort QBER cutoff (default 0.11).
        base_seed: Deterministic base seed for trials.

    Returns:
        Dictionary of aggregated statistics (mean, std, FAR, MDR, key rates).
    """
    qber_samples: List[float] = []
    qber_overalls: List[float] = []
    aborts: List[bool] = []
    key_lengths: List[int] = []

    for trial_idx in range(num_trials):
        trial_seed = base_seed + trial_idx
        res = run_bb84(
            num_qubits=num_qubits,
            eve_present=eve_present,
            eve_fraction=eve_fraction,
            channel_noise_prob=channel_noise_prob,
            depolarizing_error_prob=depolarizing_error_prob,
            readout_error_prob=readout_error_prob,
            sample_size=sample_size,
            abort_threshold=abort_threshold,
            seed=trial_seed,
        )
        qber_samples.append(res.qber_sample)
        qber_overalls.append(res.qber_overall)
        aborts.append(res.aborted)
        key_lengths.append(len(res.alice_key))

    qber_arr = np.array(qber_samples)
    abort_arr = np.array(aborts, dtype=float)

    mean_qber = float(np.mean(qber_arr))
    std_qber = float(np.std(qber_arr))
    abort_rate = float(np.mean(abort_arr))

    # False alarm: no Eve, but aborted
    # Missed detection: Eve present (f > 0), but NOT aborted
    if not eve_present or eve_fraction == 0.0:
        false_alarm_rate = abort_rate
        missed_detection_rate = 0.0
    else:
        false_alarm_rate = 0.0
        missed_detection_rate = float(1.0 - abort_rate)

    return {
        "mean_qber_sample": mean_qber,
        "std_qber_sample": std_qber,
        "mean_qber_overall": float(np.mean(qber_overalls)),
        "std_qber_overall": float(np.std(qber_overalls)),
        "abort_rate": abort_rate,
        "false_alarm_rate": false_alarm_rate,
        "missed_detection_rate": missed_detection_rate,
        "mean_key_length": float(np.mean(key_lengths)),
        "std_key_length": float(np.std(key_lengths)),
        "secret_key_rate": asymptotic_secret_key_rate(mean_qber),
    }


def binomial_detection_probabilities(
    sample_size: int,
    true_qber: float,
    abort_threshold: float = 0.11,
) -> Tuple[float, float]:
    """Calculate theoretical false alarm and missed detection probabilities.

    Given a sample size K and true underlying error probability Q:
    Let X ~ Binomial(K, Q) be the number of observed errors.
    The test flags an abort if X / K > abort_threshold.

    Returns:
        Tuple of (p_flag, p_accept):
            p_flag = P(X > K * abort_threshold)  [FAR if Eve absent, detection prob if Eve present]
            p_accept = P(X <= K * abort_threshold) [MDR if Eve present]
    """
    if sample_size <= 0:
        return 0.0, 1.0

    k_cutoff = int(math.floor(sample_size * abort_threshold))
    # Cumulative distribution function P(X <= k_cutoff)
    p_accept = float(stats.binom.cdf(k_cutoff, sample_size, true_qber))
    p_flag = float(1.0 - p_accept)
    return p_flag, p_accept
