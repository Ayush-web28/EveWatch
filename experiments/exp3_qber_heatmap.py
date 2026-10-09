"""Experiment 3: 2D Heatmap of QBER over (Channel Noise x Eve Fraction).

The core differentiator visualization: maps out the joint parameter space
illustrating the confounding effect of channel noise and eavesdropping,
highlighting the critical 11% Shor-Preskill abort boundary.
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

from bb84.analysis import run_trials

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_experiment_3(num_trials: int = 25, num_qubits: int = 400) -> pd.DataFrame:
    """Generate 2D grid of QBER across Eve fraction and Channel Noise."""
    eve_fractions = np.linspace(0.0, 1.0, 11)
    noise_levels = np.linspace(0.0, 0.25, 11)

    print(f"[*] Running Experiment 3: 2D Parameter Heatmap ({len(eve_fractions)}x{len(noise_levels)} grid, {num_trials} trials/cell)...")

    qber_matrix = np.zeros((len(noise_levels), len(eve_fractions)))
    abort_matrix = np.zeros((len(noise_levels), len(eve_fractions)))
    records = []

    for i, p_ch in enumerate(noise_levels):
        for j, f in enumerate(eve_fractions):
            stats = run_trials(
                num_trials=num_trials,
                num_qubits=num_qubits,
                eve_present=bool(f > 0.0),
                eve_fraction=float(f),
                channel_noise_prob=float(p_ch),
                abort_threshold=0.11,
                base_seed=int(3000 + i * 100 + j),
            )
            q = stats["mean_qber_overall"]
            ab_rate = stats["abort_rate"]
            qber_matrix[i, j] = q
            abort_matrix[i, j] = ab_rate

            records.append({
                "channel_noise_prob": float(p_ch),
                "eve_fraction": float(f),
                "mean_qber": float(q),
                "abort_rate": float(ab_rate),
            })

        print(f"    Completed Noise Row {i+1}/{len(noise_levels)}: p_ch={p_ch:.3f}")

    df = pd.DataFrame(records)
    csv_path = RESULTS_DIR / "exp3_qber_heatmap.csv"
    df.to_csv(csv_path, index=False)
    print(f"[+] Saved CSV to {csv_path}")

    # Plot 2D Heatmap with contour overlay
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    X, Y = np.meshgrid(eve_fractions, noise_levels * 100)
    Z = qber_matrix * 100

    # Smooth contour filled mesh
    c = ax.contourf(X, Y, Z, levels=np.linspace(0, 32, 33), cmap="inferno", alpha=0.9)
    cbar = fig.colorbar(c, ax=ax, label="Quantum Bit Error Rate (QBER %)")

    # Overlay critical 11% abort threshold contour in bright cyan/yellow
    cs_11 = ax.contour(X, Y, Z, levels=[11.0], colors=["#00E5FF"], linewidths=[3.0], linestyles=["--"])
    ax.clabel(cs_11, inline=True, fontsize=11, fmt={11.0: "11% (Abort Limit)"})

    # Other contours
    cs_other = ax.contour(X, Y, Z, levels=[5.0, 15.0, 20.0, 25.0], colors=["#FFFFFF"], linewidths=[1.0], alpha=0.6)
    ax.clabel(cs_other, inline=True, fontsize=8, fmt="%d%%")

    # Annotate key regions
    ax.text(
        0.12,
        3.0,
        "SECURE OPERATIONAL ZONE\n(QBER ≤ 11%)",
        color="#00E5FF",
        fontweight="bold",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#000000", alpha=0.7, edgecolor="#00E5FF"),
    )

    ax.text(
        0.55,
        18.0,
        "UNCONDITIONAL ABORT ZONE\n(High Noise + Eavesdropper)",
        color="#FF5252",
        fontweight="bold",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#000000", alpha=0.7, edgecolor="#FF5252"),
    )

    ax.set_title("EveWatch: Joint Impact of Channel Noise & Eavesdropping on QBER", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Eve Interception Fraction $f$", fontsize=11)
    ax.set_ylabel("Optical Channel Depolarizing Noise $p_{ch}$ (%)", fontsize=11)
    plt.tight_layout()

    fig_path = RESULTS_DIR / "exp3_qber_heatmap.png"
    plt.savefig(fig_path)
    plt.close()
    print(f"[+] Saved figure to {fig_path}")

    return df


if __name__ == "__main__":
    run_experiment_3()
