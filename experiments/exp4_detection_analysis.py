"""Experiment 4: Detection Analysis (False Alarm & Missed Detection Rates).

Analyzes the statistical impact of finite sample sizes on distinguishing
eavesdropping from channel noise near the 11% abort threshold.
Computes False Alarm Rate (FAR) and Missed Detection Rate (MDR) across
sample sizes [50, 150, 300, 600, 1200] over 50+ trials per point.
Saves figure and CSV to results/.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bb84.analysis import run_trials, binomial_detection_probabilities

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_experiment_4(num_trials: int = 50) -> pd.DataFrame:
    """Analyze False Alarm and Missed Detection rates across sample sizes."""
    sample_sizes = [50, 150, 300, 600, 1200]
    records = []

    # Regime 1: Noise-only near threshold (p_ch = 0.18 -> true QBER ~ 9%)
    p_ch_noise = 0.18
    q_true_noise = 0.09

    # Regime 2: Eve active slightly above threshold (f = 0.56 -> true QBER ~ 14%)
    f_eve = 0.56
    q_true_eve = 0.14

    print(f"[*] Running Experiment 4: Detection Reliability Analysis ({num_trials} trials/point)...")

    for k in sample_sizes:
        # 1. False Alarm run (no Eve, noisy channel near cutoff)
        # Note: to ensure sample size k is available, we generate 3 * k qubits
        n_qubits_fa = max(400, int(k * 3.5))
        fa_stats = run_trials(
            num_trials=num_trials,
            num_qubits=n_qubits_fa,
            eve_present=False,
            channel_noise_prob=p_ch_noise,
            sample_size=k,
            abort_threshold=0.11,
            base_seed=int(4000 + k),
        )
        theo_fa_flag, _ = binomial_detection_probabilities(k, q_true_noise, abort_threshold=0.11)

        # 2. Missed Detection run (Eve active, clean channel)
        n_qubits_md = max(400, int(k * 3.5))
        md_stats = run_trials(
            num_trials=num_trials,
            num_qubits=n_qubits_md,
            eve_present=True,
            eve_fraction=f_eve,
            channel_noise_prob=0.0,
            sample_size=k,
            abort_threshold=0.11,
            base_seed=int(5000 + k),
        )
        _, theo_md_accept = binomial_detection_probabilities(k, q_true_eve, abort_threshold=0.11)

        records.append({
            "sample_size": k,
            "false_alarm_sim": fa_stats["false_alarm_rate"],
            "false_alarm_theo": theo_fa_flag,
            "missed_detection_sim": md_stats["missed_detection_rate"],
            "missed_detection_theo": theo_md_accept,
            "qber_noise_mean": fa_stats["mean_qber_sample"],
            "qber_noise_std": fa_stats["std_qber_sample"],
            "qber_eve_mean": md_stats["mean_qber_sample"],
            "qber_eve_std": md_stats["std_qber_sample"],
        })

        print(
            f"    Sample Size K={k:4d} | FAR Sim: {fa_stats['false_alarm_rate']*100:5.1f}% (Theo: {theo_fa_flag*100:5.1f}%) "
            f"| MDR Sim: {md_stats['missed_detection_rate']*100:5.1f}% (Theo: {theo_md_accept*100:5.1f}%)"
        )

    df = pd.DataFrame(records)
    csv_path = RESULTS_DIR / "exp4_detection_analysis.csv"
    df.to_csv(csv_path, index=False)
    print(f"[+] Saved CSV to {csv_path}")

    # Plot dual-panel figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # Panel 1: False Alarm Rate
    ax1.plot(
        df["sample_size"],
        df["false_alarm_sim"] * 100,
        "o-",
        color="#D32F2F",
        linewidth=2,
        markersize=7,
        label=f"Simulated FAR ({num_trials} trials)",
    )
    ax1.plot(
        df["sample_size"],
        df["false_alarm_theo"] * 100,
        "--",
        color="#E57373",
        linewidth=2,
        label="Binomial Theory",
    )
    ax1.set_title("False Alarm Rate vs. Sample Size\n(Noise Only: $Q_{true} \\approx 9\\%$, Threshold=11%)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Sample Size $K$ (Revealed Sifted Bits)", fontsize=10)
    ax1.set_ylabel("False Alarm Rate (%)", fontsize=10)
    ax1.set_ylim(-1.0, max(45.0, df["false_alarm_sim"].max() * 100 + 5))
    ax1.axhline(5.0, color="#757575", linestyle=":", alpha=0.7, label="5% Tolerance Cutoff")
    ax1.legend(loc="upper right", frameon=True)

    # Panel 2: Missed Detection Rate
    ax2.plot(
        df["sample_size"],
        df["missed_detection_sim"] * 100,
        "s-",
        color="#1976D2",
        linewidth=2,
        markersize=7,
        label=f"Simulated MDR ({num_trials} trials)",
    )
    ax2.plot(
        df["sample_size"],
        df["missed_detection_theo"] * 100,
        "--",
        color="#64B5F6",
        linewidth=2,
        label="Binomial Theory",
    )
    ax2.set_title("Missed Detection Rate vs. Sample Size\n(Eve Present: $f=0.56, Q_{true} \\approx 14\\%$, Threshold=11%)", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Sample Size $K$ (Revealed Sifted Bits)", fontsize=10)
    ax2.set_ylabel("Missed Detection Rate (%)", fontsize=10)
    ax2.set_ylim(-1.0, max(45.0, df["missed_detection_sim"].max() * 100 + 5))
    ax2.axhline(5.0, color="#757575", linestyle=":", alpha=0.7, label="5% Tolerance Cutoff")
    ax2.legend(loc="upper right", frameon=True)

    plt.suptitle("EveWatch Detection Analysis: Eliminating Ambiguity via Statistical Sample Scaling", fontsize=13, fontweight="bold", y=1.00)
    plt.tight_layout()

    fig_path = RESULTS_DIR / "exp4_detection_analysis.png"
    plt.savefig(fig_path)
    plt.close()
    print(f"[+] Saved figure to {fig_path}")

    return df


if __name__ == "__main__":
    run_experiment_4()
