"""
AlgoInvar: Simulation & Real Hardware Execution Driver for IBM Kingston (156Q Heron r2)
across Register Widths n = [4, 8, 12, 16, 32, 64].

Executes the AlgoInvar benchmark suite across three distinct modes:
1. Simulation-only (Noiseless AerSimulator baseline):
   python Scaled_Experiment/run_scaling_kingston.py
   -> outputs to Scaled_Experiment/results_scaling_kingston/simulation/

2. Physical Hardware Run (156-qubit IBM Heron r2 processor):
   python Scaled_Experiment/run_scaling_kingston.py --hardware --token "<TOKEN>" --crn "<CRN>"
   -> outputs to Scaled_Experiment/results_scaling_kingston/hardware_run/

3. Reverification / Offline Re-read (Zero QPU seconds consumed):
   python Scaled_Experiment/run_scaling_kingston.py --job-id "<JOB_ID>" --token "<TOKEN>"
   -> outputs to Scaled_Experiment/results_scaling_kingston/reverification/
"""

import argparse
import os
import sys

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from scaling_runner import run_scaling_benchmark

# ==============================================================================
# CONFIGURATION: IBM Kingston (156-qubit IBM Heron r2)
# ==============================================================================
IBM_TOKEN = os.getenv("IBM_TOKEN", "PASTE_YOUR_IBM_TOKEN_HERE")
IBM_CRN   = os.getenv("IBM_CRN", "PASTE_YOUR_IBM_CRN_HERE")
CHANNEL   = "ibm_cloud"          # "ibm_cloud" or "ibm_quantum_platform"
BACKEND   = "ibm_kingston"       # 156-qubit IBM Heron r2
WIDTHS    = [4, 8, 12, 16, 32, 64]
SHOTS     = 8192                 # 8192 shots per circuit
BUDGET_S  = 240.0                # Safety QPU execution budget
JOB_ID    = ""                   # Paste existing job_id to re-read offline (0 QPU s)
# ==============================================================================


def main():
    parser = argparse.ArgumentParser(description="AlgoInvar: Simulation & IBM Kingston Scaling Runner")
    parser.add_argument("--hardware", action="store_true", help="Submit to physical IBM Kingston hardware")
    parser.add_argument("--job-id", type=str, default="", help="Re-read existing job ID offline (0 QPU s)")
    parser.add_argument("--token", type=str, default=IBM_TOKEN, help="IBM API Token")
    parser.add_argument("--crn", type=str, default=IBM_CRN, help="IBM Cloud Instance CRN")
    parser.add_argument("--channel", type=str, default=CHANNEL, help="IBM Runtime channel")
    parser.add_argument("--shots", type=int, default=SHOTS, help="Shots per circuit (default: 8192)")
    parser.add_argument("--widths", type=int, nargs="+", default=WIDTHS, help="Register widths n (default: 4 8 12 16 32 64)")
    args = parser.parse_args()

    token = args.token if args.token != "PASTE_YOUR_IBM_TOKEN_HERE" else None
    crn = args.crn if args.crn != "PASTE_YOUR_IBM_CRN_HERE" else None
    job_id = args.job_id or JOB_ID

    run_hw = args.hardware
    if run_hw and not token and not job_id:
        print("[!] NOTICE: No valid IBM token provided. Falling back to SIMULATION-ONLY mode.")
        print("    To run on physical hardware, set IBM_TOKEN in this script or via --token.")
        run_hw = False

    if job_id:
        mode = "reverification"
    elif run_hw:
        mode = "hardware_run"
    else:
        mode = "simulation"

    mode_dir = os.path.join(SCRIPT_DIR, f"results_scaling_{BACKEND.replace('ibm_', '')}", mode)

    print("=" * 80)
    print("   AlgoInvar: Simulation-Free Benchmarking of Quantum Hardware")
    print(f"   Target System: {BACKEND} (156-Qubit IBM Heron r2)")
    print(f"   Evaluated Widths: {args.widths}")
    print(f"   Mode: {mode.upper()} -> Destination: {mode_dir}/")
    print(f"   Configured Shots: {args.shots}")
    print("=" * 80)

    run_scaling_benchmark(
        backend_name=BACKEND,
        qubit_widths=args.widths,
        shots=args.shots,
        ibm_token=token,
        ibm_crn=crn,
        channel=args.channel,
        run_hardware=run_hw,
        job_id=job_id if job_id else None,
        max_budget_seconds=BUDGET_S
    )


if __name__ == "__main__":
    main()
