"""Master experiment runner for EveWatch.

Executes all 5 core experiments plus hardware comparison sequentially,
saving all figures and CSV data into results/.
"""

import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import matplotlib
matplotlib.use("Agg")

from experiments.exp1_eve_fraction import run_experiment_1
from experiments.exp2_noise_level import run_experiment_2
from experiments.exp3_qber_heatmap import run_experiment_3
from experiments.exp4_detection_analysis import run_experiment_4
from experiments.exp5_key_rate import run_experiment_5
from experiments.hardware_comparison import run_hardware_comparison


def main():
    print("=" * 70)
    print("       EVEWATCH: MASTER EXPERIMENT EXECUTION PIPELINE")
    print("=" * 70)
    t_start = time.time()

    print("\n>>> [1/6] Running Experiment 1 (Eve Interception Fraction)...")
    run_experiment_1()

    print("\n>>> [2/6] Running Experiment 2 (Channel Noise Level)...")
    run_experiment_2()

    print("\n>>> [3/6] Running Experiment 3 (2D Parameter Heatmap)...")
    run_experiment_3()

    print("\n>>> [4/6] Running Experiment 4 (Detection Reliability Analysis)...")
    run_experiment_4()

    print("\n>>> [5/6] Running Experiment 5 (Secret Key Rate & Yield)...")
    run_experiment_5()

    print("\n>>> [6/6] Running Hardware Comparison...")
    run_hardware_comparison()

    total_time = time.time() - t_start
    print("\n" + "=" * 70)
    print(f"       ALL EXPERIMENTS COMPLETED IN {total_time:.1f} SECONDS!")
    print("       Figures and CSVs successfully written to results/")
    print("=" * 70)


if __name__ == "__main__":
    main()
