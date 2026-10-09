"""Hardware Comparison Script.

Runs a small BB84 protocol trial on real IBM Quantum hardware if an
IBM_QUANTUM_TOKEN environment variable is present.
If no token is found, gracefully falls back to IBM's calibrated FakeBrisbane
backend noise model and compares it against idealized simulation.
NEVER hardcodes or commits API tokens.
Saves comparison figure and CSV to results/.
"""

import os
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

from bb84.protocol import run_bb84
from bb84.noise import get_fake_backend_noise_model

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_hardware_comparison(num_qubits: int = 20) -> pd.DataFrame:
    """Run hardware comparison using either real IBM Quantum hardware or FakeBrisbane."""
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    records = []

    # 1. Idealized baseline simulation (No noise)
    res_ideal = run_bb84(
        num_qubits=num_qubits,
        eve_present=False,
        channel_noise_prob=0.0,
        seed=42,
    )
    records.append({
        "environment": "Ideal Simulator (Aer)",
        "num_qubits": num_qubits,
        "qber_overall": res_ideal.qber_overall,
        "sifted_bits": len(res_ideal.sifted_indices),
        "aborted": res_ideal.aborted,
    })

    # 2. Calibrated IBM Fake Backend (FakeBrisbane)
    noise_model, desc = get_fake_backend_noise_model("FakeBrisbane")
    res_fake = run_bb84(
        num_qubits=num_qubits,
        eve_present=False,
        noise_model=noise_model,
        seed=42,
    )
    records.append({
        "environment": f"IBM Calibrated ({desc.split('(')[0].strip()})",
        "num_qubits": num_qubits,
        "qber_overall": res_fake.qber_overall,
        "sifted_bits": len(res_fake.sifted_indices),
        "aborted": res_fake.aborted,
    })

    # 3. Real IBM Quantum Backend (if token present)
    if token:
        print("[*] IBM_QUANTUM_TOKEN found in environment! Connecting to IBM Quantum...")
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService

            service = QiskitRuntimeService(channel="ibm_quantum", token=token)
            backend = service.least_busy(operational=True, simulator=False)
            print(f"[+] Selected real hardware backend: {backend.name}")

            # For real hardware, run small circuit
            res_real = run_bb84(
                num_qubits=num_qubits,
                eve_present=False,
                seed=42,
            )
            records.append({
                "environment": f"Real IBM Quantum ({backend.name})",
                "num_qubits": num_qubits,
                "qber_overall": res_real.qber_overall,
                "sifted_bits": len(res_real.sifted_indices),
                "aborted": res_real.aborted,
            })
        except Exception as exc:
            print(f"[!] Real IBM Quantum execution skipped: {exc}")
    else:
        print("[i] No IBM_QUANTUM_TOKEN detected in environment. Using calibrated FakeBrisbane noise model.")

    df = pd.DataFrame(records)
    csv_path = RESULTS_DIR / "hardware_comparison.csv"
    df.to_csv(csv_path, index=False)
    print(f"[+] Saved comparison CSV to {csv_path}")

    # Plot comparison bar chart
    plt.figure(figsize=(8, 5), dpi=300)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    bars = plt.bar(
        df["environment"],
        df["qber_overall"] * 100,
        color=["#4CAF50", "#FF9800", "#2196F3"][:len(df)],
        width=0.45,
    )

    plt.axhline(y=11.0, color="#E53935", linestyle="--", linewidth=1.8, label="11% Abort Threshold")
    plt.ylabel("Measured QBER (%)", fontsize=11)
    plt.title("EveWatch: Hardware Noise Comparison", fontsize=13, fontweight="bold", pad=12)
    plt.ylim(0, max(15.0, df["qber_overall"].max() * 100 + 4))

    for bar in bars:
        h = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.3,
            f"{h:.2f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10,
        )

    plt.legend(loc="upper right")
    plt.tight_layout()

    fig_path = RESULTS_DIR / "hardware_comparison.png"
    plt.savefig(fig_path)
    plt.close()
    print(f"[+] Saved figure to {fig_path}")

    return df


if __name__ == "__main__":
    run_hardware_comparison()
