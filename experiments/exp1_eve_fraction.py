"""Experiment 1: QBER vs. Eve's Interception Fraction (No Noise).

Validates the fundamental quantum mechanical intercept-resend relationship
QBER ~ 0.25 * f against theoretical predictions.
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

from bb84.analysis import run_trials, theoretical_qber

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_experiment_1(num_trials: int = 50, num_qubits: int = 500) -> pd.DataFrame:
    """Run QBER vs Eve interception fraction experiment across [0.0, 1.0]."""
    fractions = np.linspace(0.0, 1.0, 11)
    records = []

    print(f"[*] Running Experiment 1: QBER vs Eve Interception Fraction ({num_trials} trials/point)...")

    for f in fractions:
        stats = run_trials(
            num_trials=num_trials,
            num_qubits=num_qubits,
            eve_present=True,
            eve_fraction=f,
            channel_noise_prob=0.0,
            base_seed=int(1000 + f * 100),
        )
        q_theo = theoretical_qber(eve_fraction=f, channel_noise_prob=0.0)

        records.append({
            "eve_fraction": float(f),
            "mean_qber": stats["mean_qber_overall"],
            "std_qber": stats["std_qber_overall"],
            "theoretical_qber": q_theo,
            "abort_rate": stats["abort_rate"],
        })
        print(f"    f={f:.2f} | Sim QBER: {stats['mean_qber_overall']:.4f} ± {stats['std_qber_overall']:.4f} | Theo: {q_theo:.4f}")

    df = pd.DataFrame(records)
    csv_path = RESULTS_DIR / "exp1_eve_fraction.csv"
    df.to_csv(csv_path, index=False)
    print(f"[+] Saved CSV to {csv_path}")

    # Plot results
    plt.figure(figsize=(9, 5.5), dpi=300)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    plt.errorbar(
        df["eve_fraction"],
        df["mean_qber"] * 100,
        yerr=df["std_qber"] * 100,
        fmt="o-",
        color="#1E88E5",
        ecolor="#90CAF9",
        elinewidth=2,
        capsize=4,
        capthick=1.5,
        label=f"Qiskit Aer Stabilizer ({num_trials} trials ± 1σ)",
        zorder=3,
    )

    plt.plot(
        df["eve_fraction"],
        df["theoretical_qber"] * 100,
        "--",
        color="#D81B60",
        linewidth=2.2,
        label=r"Theoretical Model $Q = 0.25 \times f$",
        zorder=4,
    )

    # Abort threshold line at 11%
    plt.axhline(
        y=11.0,
        color="#FB8C00",
        linestyle=":",
        linewidth=2,
        label="Security Abort Threshold (11% QBER)",
        zorder=2,
    )

    # Shade security region
    plt.axhspan(0, 11, alpha=0.12, color="#4CAF50", label="Secure Region (QBER ≤ 11%)")
    plt.axhspan(11, 30, alpha=0.12, color="#E53935", label="Compromised / Abort Region")

    # Annotate intercept at f=1.0
    f_end = df.iloc[-1]
    plt.annotate(
        f"f=1.0: QBER={f_end['mean_qber']*100:.1f}%\n(Theory: 25.0%)",
        xy=(1.0, f_end['mean_qber'] * 100),
        xytext=(0.72, 21.0),
        arrowprops=dict(facecolor="#1E88E5", shrink=0.08, width=1.5, headwidth=6),
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#E3F2FD", edgecolor="#1E88E5"),
    )

    plt.title("EveWatch BB84: QBER vs. Eavesdropper Interception Fraction", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Eve Interception Fraction $f$ (Probability of intercepting qubit)", fontsize=11)
    plt.ylabel("Quantum Bit Error Rate (QBER %)", fontsize=11)
    plt.xlim(-0.02, 1.02)
    plt.ylim(-0.5, 30.0)
    plt.legend(loc="upper left", frameon=True, framealpha=0.95)
    plt.tight_layout()

    fig_path = RESULTS_DIR / "exp1_eve_fraction.png"
    plt.savefig(fig_path)
    plt.close()
    print(f"[+] Saved figure to {fig_path}")

    return df


if __name__ == "__main__":
    run_experiment_1()
