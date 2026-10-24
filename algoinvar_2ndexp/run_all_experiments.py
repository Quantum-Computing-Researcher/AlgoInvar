"""
Runner script for noise response sweeps, symmetry mitigation, and figure generation.
"""

import sys
import os
import argparse
import shutil
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from simulation.error_injection import run_full_error_injection_suite
from simulation.symmetry_mitigation import run_full_symmetry_mitigation_suite
from simulation.benchmarking_comparison import run_benchmarking_comparison
from analysis.plot_noise_calibration import run_all_plots


def main():
    parser = argparse.ArgumentParser(description="Noise sweeps and symmetry mitigation runner")
    parser.add_argument("--all", action="store_true", default=True, help="Run all simulations and plots")
    parser.add_argument("--noise-sweeps", action="store_true", help="Run noise sweeps only")
    parser.add_argument("--mitigation", action="store_true", help="Run symmetry mitigation only")
    parser.add_argument("--comparison", action="store_true", help="Run benchmarking comparison only")
    parser.add_argument("--plots", action="store_true", help="Generate figures only")
    parser.add_argument("--shots", type=int, default=50000, help="Measurement shots per circuit")
    args = parser.parse_args()

    t0 = time.time()
    noise_dir = os.path.join(BASE_DIR, "results", "error_injection")
    mitigation_dir = os.path.join(BASE_DIR, "results", "symmetry_mitigation")
    tax_dir = os.path.join(BASE_DIR, "results", "device_calibration")
    fig_dir = os.path.join(BASE_DIR, "results", "figures")
    paper_fig_dir = os.path.join(BASE_DIR, "figures")

    if args.all or args.noise_sweeps:
        print("Running noise channel sweeps...")
        run_full_error_injection_suite(output_dir=noise_dir, shots=args.shots)

    if args.all or args.mitigation:
        print("Running symmetry-filtered error mitigation...")
        run_full_symmetry_mitigation_suite(output_dir=mitigation_dir, shots=args.shots)

    if args.all or args.comparison:
        print("Evaluating benchmarking comparison metrics...")
        run_benchmarking_comparison(output_dir=tax_dir)

    if args.all or args.plots:
        print("Generating figures...")
        run_all_plots(noise_dir=noise_dir, mitigation_dir=mitigation_dir, output_dir=fig_dir)
        
        os.makedirs(paper_fig_dir, exist_ok=True)
        for fname in os.listdir(fig_dir):
            src = os.path.join(fig_dir, fname)
            dst = os.path.join(paper_fig_dir, fname)
            if os.path.isfile(src):
                shutil.copy2(src, dst)

    elapsed = time.time() - t0
    print(f"Done in {elapsed:.1f} s.")


if __name__ == "__main__":
    main()
