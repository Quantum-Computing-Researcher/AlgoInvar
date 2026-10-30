"""
AlgoInvar: Simulation & Real Hardware Execution Driver for IBM Kingston (156Q Heron r2).

Executes the AlgoInvar benchmark suite across three distinct modes:
1. Simulation-only (Noiseless AerSimulator baseline):
   python run_ibm_kingston.py
   -> outputs to results_kingston/simulation/

2. Physical Hardware Run (156-qubit IBM Heron r2 processor):
   python run_ibm_kingston.py --hardware --token "<TOKEN>" --crn "<CRN>"
   -> outputs to results_kingston/hardware_run/

3. Reverification / Offline Re-read (Zero QPU seconds consumed):
   python run_ibm_kingston.py --job-id "<JOB_ID>" --token "<TOKEN>"
   -> outputs to results_kingston/reverification/
"""

import argparse
import json
import os
import sys

# Dynamic project root configuration
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
if os.path.basename(SCRIPT_DIR) in ["algoinvar", "01_algoinvar_n4_hardware_baseline"]:
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
else:
    PROJECT_ROOT = SCRIPT_DIR

for p in [PROJECT_ROOT, SCRIPT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from algoinvar.hardware.ibm_runner import run_algoinvar_experiments
except ImportError:
    import importlib
    sys.modules["algoinvar"] = importlib.import_module("01_algoinvar_n4_hardware_baseline")
    from algoinvar.hardware.ibm_runner import run_algoinvar_experiments

# ==============================================================================
# CONFIGURATION: IBM Kingston (156-qubit IBM Heron r2)
# ==============================================================================
IBM_TOKEN = os.getenv("IBM_TOKEN", "PASTE_YOUR_IBM_TOKEN_HERE")
IBM_CRN   = os.getenv("IBM_CRN", "PASTE_YOUR_IBM_CRN_HERE")
CHANNEL   = "ibm_cloud"          # "ibm_cloud" or "ibm_quantum_platform"
BACKEND   = "ibm_kingston"       # 156-qubit IBM Heron r2
N_QUBITS  = 4                    # Evaluated chain size
SHOTS     = 8192                 # 8192 shots for high-precision quantum statistics (~20s QPU run)
BUDGET_S  = 180.0                # Safety QPU execution budget (under 3 minutes)
JOB_ID    = ""                   # Paste existing job_id to re-read offline (0 QPU s)
# ==============================================================================


def print_comparison_table(report: dict, out_file: str, excel_file: str, fig_dir: str, mode: str):
    """Prints a clear side-by-side comparison between theory, simulation, and hardware."""
    mode_titles = {
        "simulation": "Simulation Baseline Mode",
        "hardware_run": "Physical Hardware Run Mode",
        "reverification": "Offline Job Reverification Mode"
    }

    print("\n" + "=" * 80)
    print(f"  AlgoInvar: Benchmark Results on IBM Kingston (156Q Heron r2)")
    print(f"  Execution Mode: {mode_titles.get(mode, mode.upper())}")
    print("=" * 80)
    print(f"{'Circuit / Invariant':<22} | {'Exact Ref':<10} | {'Noiseless':<12} | {'IBM Kingston':<15} | {'Verdict'}")
    print("-" * 80)

    sim = report.get("simulations", {}).get("noiseless", {})
    hw = report.get("hardware")
    hw_metrics = hw.get("metrics", {}) if hw else {}

    circuits = [
        ("vqe_particle_l2", "VQE <N> (n=4)", "2.0000", "mean_N"),
        ("vqe_particle_l2", "VQE Var(N)", "0.0000", "var_N"),
        ("vqe_retrace", "VQE Echo (F)", "1.0000", "return_fidelity"),
        ("qaoa_parity_p1", "QAOA Parity p=1", "+1.0000", "global_parity"),
        ("qaoa_parity_p2", "QAOA Parity p=2", "+1.0000", "global_parity"),
        ("qaoa_retrace_p2", "QAOA Echo p=2", "1.0000", "retrace_fidelity"),
    ]

    for circ_key, label, ref_val, metric_key in circuits:
        sim_val = sim.get(circ_key, {}).get(metric_key)
        sim_str = f"{sim_val:.4f}" if sim_val is not None else "N/A"

        if hw_metrics and circ_key in hw_metrics:
            hw_val = hw_metrics[circ_key].get(metric_key)
            hw_str = f"{hw_val:.4f}" if hw_val is not None else "Pending"
            passed = hw_metrics[circ_key].get("passed", False)
            verdict = "PASSED" if passed else "DEGRADED"
        else:
            hw_str = "Not Run"
            verdict = "SIM ONLY"

        print(f"{label:<22} | {ref_val:<10} | {sim_str:<12} | {hw_str:<15} | {verdict}")

    print("=" * 80)
    if hw:
        print(f"IBM Job ID: {hw.get('job_id')}")
        print(f"QPU Execution Time: {hw.get('qpu_seconds', 0.0):.1f} s (Reported by IBM)")
        print(f"Physical Qubits Used: {hw.get('chain')}")
    print(f"Output Directory: {os.path.dirname(out_file)}/")
    print(f"  - JSON Record: {out_file}")
    print(f"  - Excel Sheet: {excel_file}")
    print(f"  - Figures Folder: {fig_dir}/")
    print(f"      - {BACKEND}_fig1_invariant_summary.png (.pdf)")
    print(f"      - {BACKEND}_fig2_fock_confinement.png (.pdf)\n")


def main():
    parser = argparse.ArgumentParser(description="AlgoInvar: Simulation & IBM Kingston Runner")
    parser.add_argument("--hardware", action="store_true", help="Submit to physical IBM Kingston hardware")
    parser.add_argument("--job-id", type=str, default="", help="Re-read existing job ID offline (0 QPU s)")
    parser.add_argument("--token", type=str, default=IBM_TOKEN, help="IBM API Token")
    parser.add_argument("--crn", type=str, default=IBM_CRN, help="IBM Cloud Instance CRN")
    parser.add_argument("--channel", type=str, default=CHANNEL, help="IBM Runtime channel")
    parser.add_argument("--shots", type=int, default=SHOTS, help="Shots per circuit (default: 8192)")
    args = parser.parse_args()

    token = args.token if args.token != "PASTE_YOUR_IBM_TOKEN_HERE" else None
    crn = args.crn if args.crn != "PASTE_YOUR_IBM_CRN_HERE" else None
    job_id = args.job_id or JOB_ID

    run_hw = args.hardware
    if run_hw and not token and not job_id:
        print("[!] NOTICE: No valid IBM token provided. Falling back to SIMULATION-ONLY mode.")
        print("    To run on physical hardware, set IBM_TOKEN in this script or via --token.")
        run_hw = False

    # Determine execution mode and dedicated folder
    if job_id:
        mode = "reverification"
    elif run_hw:
        mode = "hardware_run"
    else:
        mode = "simulation"

    dir_in_pkg = os.path.join(SCRIPT_DIR, f"results_{BACKEND.replace('ibm_', '')}")
    dir_in_root = os.path.join(PROJECT_ROOT, f"results_{BACKEND.replace('ibm_', '')}")
    hw_base_dir = dir_in_pkg if os.path.exists(dir_in_pkg) else dir_in_root
    mode_dir = os.path.join(hw_base_dir, mode)
    out_file = os.path.join(mode_dir, f"{BACKEND}_results.json")
    excel_file = os.path.join(mode_dir, f"{BACKEND}_results.xlsx")
    fig_dir = os.path.join(mode_dir, "figures")

    os.makedirs(mode_dir, exist_ok=True)
    os.makedirs(fig_dir, exist_ok=True)

    print("=" * 80)
    print("   AlgoInvar: Simulation-Free Benchmarking of Quantum Hardware")
    print(f"   Target System: {BACKEND} (156-Qubit IBM Heron r2)")
    print(f"   Mode: {mode.upper()} -> Destination: {mode_dir}/")
    print(f"   Configured Shots: {args.shots}")
    print("=" * 80)

    report = run_algoinvar_experiments(
        ibm_token=token,
        ibm_crn=crn,
        channel=args.channel,
        backend_name=BACKEND,
        num_qubits=N_QUBITS,
        shots=args.shots,
        max_budget_seconds=BUDGET_S,
        job_id=job_id if job_id else None,
        run_hardware=run_hw,
        mode=mode,
        output_file=out_file,
        figures_dir=fig_dir
    )

    print_comparison_table(report, out_file, excel_file, fig_dir, mode)


if __name__ == "__main__":
    main()
