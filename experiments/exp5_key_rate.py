"""Experiment 5: Secret Key Rate & Yield vs. Channel Noise Level.

Analyzes the extractable secret key fraction (Shor-Preskill bound R = 1 - 2*H2(Q))
and net key lengths after key sifting, sampling, and privacy amplification.
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

from bb84.analysis import run_trials, asymptotic_secret_key_rate

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_experiment_5(num_trials: int = 50, num_qubits: int = 600) -> pd.DataFrame:
    """Analyze secret key rate and yield across channel noise levels."""
    noise_levels = np.linspace(0.0, 0.25, 14)
    records = []

    print(f"[*] Running Experiment 5: Key Rate & Yield Analysis ({num_trials} trials/point)...")

    for p_ch in noise_levels:
        stats = run_trials(
            num_trials=num_trials,
            num_qubits=num_qubits,
            eve_present=False,
            channel_noise_prob=p_ch,
            sample_size=0.5,
            abort_threshold=0.11,
            base_seed=int(6000 + p_ch * 1000),
        )
        q = stats["mean_qber_sample"]
        sec_rate = asymptotic_secret_key_rate(q)
        # Expected secret bits: net raw key * secret key rate (if not aborted)
        mean_net_key = stats["mean_key_length"]
        effective_secret_bits = mean_net_key * sec_rate if stats["abort_rate"] < 0.5 else 0.0

        records.append({
            "channel_noise_prob": float(p_ch),
            "mean_qber": float(q),
            "mean_raw_key_length": float(mean_net_key),
            "secret_key_rate": float(sec_rate),
            "effective_secret_bits": float(effective_secret_bits),
            "abort_rate": stats["abort_rate"],
        })
        print(f"    p_ch={p_ch:.3f} | QBER: {q:.4f} | Secret Rate: {sec_rate:.4f} | Effective Bits: {effective_secret_bits:.1f}")

    df = pd.DataFrame(records)
    csv_path = RESULTS_DIR / "exp5_key_rate.csv"
    df.to_csv(csv_path, index=False)
    print(f"[+] Saved CSV to {csv_path}")

    # Plot Dual Axis: Key Rate & Effective Secret Bits
    fig, ax1 = plt.subplots(figsize=(9, 5.5), dpi=300)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    color_rate = "#2E7D32"
    ax1.set_xlabel("Channel Depolarizing Noise Probability $p_{ch}$ (%)", fontsize=11)
    ax1.set_ylabel("Asymptotic Secret Key Rate $R$ (bits / sifted bit)", color=color_rate, fontsize=11)
    line1 = ax1.plot(
        df["channel_noise_prob"] * 100,
        df["secret_key_rate"],
        "o-",
        color=color_rate,
        linewidth=2.5,
        label=r"Secret Key Rate $R = 1 - 2 H_2(Q)$",
    )
    ax1.tick_params(axis="y", labelcolor=color_rate)
    ax1.set_ylim(-0.05, 1.05)

    # Secondary axis: Effective Secret Key Bits
    ax2 = ax1.twinx()
    color_bits = "#1565C0"
    ax2.set_ylabel(f"Final Secret Key Length (Bits out of {num_qubits} qubits)", color=color_bits, fontsize=11)
    line2 = ax2.plot(
        df["channel_noise_prob"] * 100,
        df["effective_secret_bits"],
        "s--",
        color=color_bits,
        linewidth=2.0,
        label="Net Distilled Secret Key Bits",
    )
    ax2.tick_params(axis="y", labelcolor=color_bits)
    ax2.set_ylim(-5, max(df["effective_secret_bits"].max() * 1.1, 10))

    # Critical cutoff annotation at p_ch ~ 22%
    ax1.axvline(x=22.0, color="#E53935", linestyle=":", linewidth=2, label="11% QBER Cutoff ($R=0$)")

    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper right", frameon=True)

    plt.title(f"EveWatch BB84: Secret Key Rate & Yield vs. Channel Noise ({num_qubits} Qubits)", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()

    fig_path = RESULTS_DIR / "exp5_key_rate.png"
    plt.savefig(fig_path)
    plt.close()
    print(f"[+] Saved figure to {fig_path}")

    return df


if __name__ == "__main__":
    run_experiment_5()
