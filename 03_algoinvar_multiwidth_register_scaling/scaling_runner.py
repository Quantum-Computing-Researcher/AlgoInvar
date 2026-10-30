"""
This is the IBM Quantum Hardware Execution and
Comparative Simulation Engine for AlgoInvar Register-Width Scaling.

We use this runner on 156-qubit Heron r2 processors
(e.g., ibm_kingston, ibm_fez) with
single-job batching across n = [4, 8, 12, 16, 32, 64],
strict execution time budgeting,
and side-by-side simulation.
"""

import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from qiskit import transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
EXP1_DIR = os.path.join(PROJECT_ROOT, "01_algoinvar_n4_hardware_baseline")
for p in [PROJECT_ROOT, EXP1_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from algoinvar.hardware.ibm_runner import (
        build_algoinvar_benchmark_circuits,
        analyze_circuit_results
    )
except ImportError:
    import importlib
    sys.modules["algoinvar"] = importlib.import_module("01_algoinvar_n4_hardware_baseline")
    from algoinvar.hardware.ibm_runner import (
        build_algoinvar_benchmark_circuits,
        analyze_circuit_results
    )
from qubit_chain_scaling import find_best_qubit_chain_scaled
from scaling_metrics import export_scaling_to_excel, export_scaling_publication_figures

DEFAULT_SCALING_WIDTHS = [4, 8, 12, 16, 32, 64]


def run_scaling_benchmark(
    backend_name: str = "ibm_kingston",
    qubit_widths: Optional[List[int]] = None,
    shots: int = 8192,
    ibm_token: Optional[str] = None,
    ibm_crn: Optional[str] = None,
    channel: str = "ibm_cloud",
    run_hardware: bool = False,
    job_id: Optional[str] = None,
    max_budget_seconds: float = 240.0
) -> Dict[str, Any]:
    """
    Main driver executing AlgoInvar across register widths on Simulation and/or Real IBM Hardware.

    We evaluate all 5 benchmark circuits at 8,192 shots per circuit for each width n in `qubit_widths`.
    Output files are saved into mode-specific subfolders (`simulation/`, `hardware_run/`, `reverification/`)
    with explicit `scaling_sim`, `scaling_hw`, or `scaling_verification` filenames.
    """
    widths = sorted(qubit_widths or list(DEFAULT_SCALING_WIDTHS))
    short = backend_name.replace("ibm_", "")

    if job_id:
        mode = "reverification"
    elif run_hardware:
        mode = "hardware_run"
    else:
        mode = "simulation"

    # We tag output filenames by both processor and execution mode to avoid any ambiguity
    mode_tag = {"simulation": "sim", "hardware_run": "hw", "reverification": "verification"}.get(mode, mode)
    out_dir = os.path.join(SCRIPT_DIR, f"results_scaling_{short}", mode)
    os.makedirs(out_dir, exist_ok=True)
    json_file = os.path.join(out_dir, f"{backend_name}_scaling_{mode_tag}_results.json")
    excel_file = os.path.join(out_dir, f"{backend_name}_scaling_{mode_tag}_results.xlsx")
    fig_dir = os.path.join(out_dir, "figures")

    report: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "backend": backend_name,
        "mode": mode,
        "qubit_widths": widths,
        "shots_per_circuit": shots,
        "results_by_width": {}
    }

    # 1. Baseline Noiseless Simulation
    # We use Statevector AerSimulator for n <= 20 and Matrix Product State (MPS) for n = 32, 64
    # so that all 6 widths can be simulated locally at 8,192 shots without exceeding system RAM.
    print("[1/3] Running Noiseless Reference Simulation (AerSimulator)...")
    statevec_backend = AerSimulator()
    mps_backend = AerSimulator(method="matrix_product_state")

    raw_circuits_by_width: Dict[int, List[Tuple[str, Any]]] = {}

    for n in widths:
        raw_circuits = build_algoinvar_benchmark_circuits(num_qubits=n)
        raw_circuits_by_width[n] = raw_circuits
        names = [name for name, _ in raw_circuits]

        sim_backend = statevec_backend if n <= 20 else mps_backend
        sim_counts = {}
        for name, c in raw_circuits:
            tc = transpile(c, sim_backend) if n <= 20 else c
            job = sim_backend.run(tc, shots=shots)
            sim_counts[name] = job.result().get_counts()

        noiseless_metrics = {
            name: analyze_circuit_results(name, sim_counts[name], n, shots)
            for name in names
        }

        report["results_by_width"][str(n)] = {
            "num_qubits": n,
            "shots_per_circuit": shots,
            "simulations": {"noiseless": noiseless_metrics},
            "hardware": None
        }

    # 2. Hardware Execution or Offline Re-read
    # When --hardware or --job-id is passed, we connect to IBM Quantum and batch all 30 ISA circuits
    # (6 widths x 5 circuits) into a single SamplerV2 job to minimize queue overhead.
    if run_hardware or job_id:
        print(f"[2/3] Connecting to IBM Quantum Service ({channel})...")
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

        service = None
        for ch in ([channel] if channel else ["ibm_cloud", "ibm_quantum_platform"]):
            try:
                service = QiskitRuntimeService(channel=ch, token=ibm_token, instance=ibm_crn)
                print(f"  Connected via channel: {ch}")
                break
            except Exception as e:
                print(f"  Channel {ch} connection notice: {e}")

        if service is None:
            raise RuntimeError("Could not connect to QiskitRuntimeService. Check IBM_TOKEN and IBM_CRN.")

        backend = service.backend(backend_name)
        print(f"  Target processor: {backend.name} ({backend.num_qubits} qubits)")

        # Calibration-guided qubit selection and ISA transpilation for each width n
        print("  Evaluating live calibration to select cleanest physical chains...")
        isa_circuits = []
        batched_order: List[Tuple[int, str, List[int]]] = []

        for n in widths:
            chain, _ = find_best_qubit_chain_scaled(backend=backend, num_qubits=n)
            print(f"  Selected optimal physical chain (n={n}): {chain}")
            pm = generate_preset_pass_manager(
                optimization_level=1,
                backend=backend,
                initial_layout=chain,
                seed_transpiler=42
            )
            for name, c in raw_circuits_by_width[n]:
                isa_circuits.append(pm.run(c))
                batched_order.append((n, name, chain))

        # Estimate QPU execution time and enforce safety budget before submitting
        total_shots = len(isa_circuits) * shots
        est_seconds = 2.0 + 3.2e-4 * total_shots
        print(f"  Prepared {len(isa_circuits)} ISA circuits; Total shots: {total_shots}")
        print(f"  Estimated QPU time: ~{est_seconds:.1f} s (Budget limit: {max_budget_seconds:.1f} s)")

        if job_id:
            print(f"  Re-reading existing job ID: {job_id} (0 QPU seconds consumed)...")
            hw_job = service.job(job_id)
        else:
            if est_seconds > max_budget_seconds:
                raise RuntimeError(
                    f"Estimated QPU time ({est_seconds:.1f}s) exceeds safety budget ({max_budget_seconds:.1f}s). Aborting."
                )

            print("  Submitting single batched job via SamplerV2...")
            sampler = SamplerV2(mode=backend)
            try:
                sampler.options.environment.job_tags = ["algoinvar-benchmark"]
            except Exception:
                pass

            hw_job = sampler.run([(c, None, shots) for c in isa_circuits])
            print(f"  Submitted successfully! Job ID: {hw_job.job_id()}")
            print("  Waiting for completion from IBM Quantum...")

        res = hw_job.result()
        hw_counts_all = [r.data.meas.get_counts() for r in res]

        try:
            qpu_usage = float(hw_job.usage() or 0.0)
        except Exception:
            qpu_usage = est_seconds

        # Unpack batched SamplerV2 results back into each width n and evaluate invariant metrics
        grouped_counts: Dict[int, List[Tuple[str, Dict[str, int], List[int]]]] = {}
        for idx, (n, name, chain) in enumerate(batched_order):
            grouped_counts.setdefault(n, []).append((name, hw_counts_all[idx], chain))

        for n, items in grouped_counts.items():
            chain_n = items[0][2]
            hw_metrics_n = {
                name: analyze_circuit_results(name, cnts, n, shots)
                for name, cnts, _ in items
            }
            raw_counts_n = [cnts for _, cnts, _ in items]
            report["results_by_width"][str(n)]["hardware"] = {
                "job_id": hw_job.job_id(),
                "backend": backend_name,
                "chain": chain_n,
                "qpu_seconds": qpu_usage,
                "metrics": hw_metrics_n,
                "raw_counts": raw_counts_n
            }

    # 3. Save to JSON, Multi-Sheet Excel Workbook, and Publication Figures
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[3/3] Results serialized to JSON: {json_file}")

    export_scaling_to_excel(report, excel_file)
    print(f"      Multi-sheet Excel Workbook saved: {excel_file}")

    figures = export_scaling_publication_figures(report, fig_dir)
    print(f"      Publication-ready Figures generated in: {fig_dir}/")
    for fig_path in figures:
        print(f"        - {fig_path}")

    report["artifacts"] = {
        "json": json_file,
        "excel": excel_file,
        "figures": figures
    }

    print_comparison_table(report, json_file, excel_file, fig_dir, mode)
    return report


def print_comparison_table(report: dict, out_file: str, excel_file: str, fig_dir: str, mode: str):
    """
    We print a formatted terminal summary table comparing Exact Reference,
    Noiseless Simulation, and IBM Hardware across all evaluated register widths n.
    """
    mode_titles = {
        "simulation": "Simulation Baseline Mode",
        "hardware_run": "Physical Hardware Run Mode",
        "reverification": "Offline Job Reverification Mode"
    }
    backend_name = report.get("backend", "ibm_kingston")
    backend_title = "IBM Kingston" if "kingston" in backend_name else "IBM Fez"
    widths = report.get("qubit_widths", [])
    by_width = report.get("results_by_width", {})

    print("\n" + "=" * 80)
    print(f"  AlgoInvar: Benchmark Results on {backend_title} (156Q Heron r2)")
    print(f"  Execution Mode: {mode_titles.get(mode, mode.upper())}")
    print("=" * 80)
    print(f"{'Circuit / Invariant':<24} | {'Exact Ref':<10} | {'Noiseless':<12} | {backend_title:<15} | {'Verdict'}")
    print("-" * 80)

    for n in widths:
        w_entry = by_width.get(str(n), {})
        sim = w_entry.get("simulations", {}).get("noiseless", {})
        hw = w_entry.get("hardware")
        hw_metrics = hw.get("metrics", {}) if hw else {}

        circuits = [
            ("vqe_particle_l2", f"VQE <N> (n={n})", "2.0000", "mean_N"),
            ("vqe_particle_l2", f"VQE Var(N) (n={n})", "0.0000", "var_N"),
            ("vqe_retrace", f"VQE Echo (F) (n={n})", "1.0000", "return_fidelity"),
            ("qaoa_parity_p1", f"QAOA Parity p=1 (n={n})", "+1.0000", "global_parity"),
            ("qaoa_parity_p2", f"QAOA Parity p=2 (n={n})", "+1.0000", "global_parity"),
            ("qaoa_retrace_p2", f"QAOA Echo p=2 (n={n})", "1.0000", "retrace_fidelity"),
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

            print(f"{label:<24} | {ref_val:<10} | {sim_str:<12} | {hw_str:<15} | {verdict}")
        print("-" * 80)

    print("=" * 80)
    print(f"Output Directory: {os.path.dirname(out_file)}/")
    print(f"  - JSON Record: {out_file}")
    print(f"  - Excel Sheet: {excel_file}")
    print(f"  - Figures Folder: {fig_dir}/\n")
