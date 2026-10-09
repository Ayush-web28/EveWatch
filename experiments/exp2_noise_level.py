"""Experiment 2: QBER vs. Channel Noise Level (No Eve).

Evaluates how environmental depolarizing noise in the optical channel
impacts BB84 fidelity without an eavesdropper.
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


def run_experiment_2(num_trials: int = 50, num_qubits: int = 500) -> pd.DataFrame:
    """Run QBER vs channel noise level experiment across [0.0, 0.30]."""
    noise_levels = np.linspace(0.0, 0.30, 13)
    records = []

    print(f"[*] Running Experiment 2: QBER vs Channel Noise Level ({num_trials} trials/point)...")

    for p_ch in noise_levels:
        stats = run_trials(
            num_trials=num_trials,
            num_qubits=num_qubits,
            eve_present=False,
            channel_noise_prob=p_ch,
            base_seed=int(2000 + p_ch * 1000),
        )
        q_theo = theoretical_qber(eve_fraction=0.0, channel_noise_prob=p_ch)

        records.append({
            "channel_noise_prob": float(p_ch),
            "mean_qber": stats["mean_qber_overall"],
            "std_qber": stats["std_qber_overall"],
            "theoretical_qber": q_theo,
            "abort_rate": stats["abort_rate"],
        })
        print(f"    p_ch={p_ch:.3f} | Sim QBER: {stats['mean_qber_overall']:.4f} ± {stats['std_qber_overall']:.4f} | Theo: {q_theo:.4f}")

    df = pd.DataFrame(records)
    csv_path = RESULTS_DIR / "exp2_noise_level.csv"
    df.to_csv(csv_path, index=False)
    print(f"[+] Saved CSV to {csv_path}")

    # Plot results
    plt.figure(figsize=(9, 5.5), dpi=300)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    plt.errorbar(
        df["channel_noise_prob"] * 100,
        df["mean_qber"] * 100,
        yerr=df["std_qber"] * 100,
        fmt="s-",
        color="#7B1FA2",
        ecolor="#CE93D8",
        elinewidth=2,
        capsize=4,
        capthick=1.5,
        label=f"Qiskit Aer Simulation ({num_trials} trials ± 1σ)",
        zorder=3,
    )

    plt.plot(
        df["channel_noise_prob"] * 100,
        df["theoretical_qber"] * 100,
        "--",
        color="#00897B",
        linewidth=2.2,
        label=r"Theoretical Channel Model $Q = 0.5 \times p_{ch}$",
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

    # Annotate critical noise threshold
    p_crit = 22.0  # At p_ch = 22%, QBER reaches 11%
    plt.axvline(x=p_crit, color="#E53935", linestyle="-.", alpha=0.7, label=r"Critical Noise Limit ($p_{ch} \approx 22\%$)")

    plt.axhspan(0, 11, alpha=0.12, color="#4CAF50", label="Acceptable Noise Margin")
    plt.axhspan(11, 20, alpha=0.12, color="#E53935", label="Noise-Induced Abort Zone")

    plt.title("EveWatch BB84: QBER vs. Optical Channel Noise (No Eve)", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Channel Depolarizing Noise Probability $p_{ch}$ (%)", fontsize=11)
    plt.ylabel("Quantum Bit Error Rate (QBER %)", fontsize=11)
    plt.xlim(-0.5, 30.5)
    plt.ylim(-0.5, 18.0)
    plt.legend(loc="upper left", frameon=True, framealpha=0.95)
    plt.tight_layout()

    fig_path = RESULTS_DIR / "exp2_noise_level.png"
    plt.savefig(fig_path)
    plt.close()
    print(f"[+] Saved figure to {fig_path}")

    return df


if __name__ == "__main__":
    run_experiment_2()
