"""
This is the IBM Quantum Hardware Execution and 
Comparative Simulation Engine for AlgoInvar.

Optimized for 156-qubit Heron r2 processors 
(e.g., ibm_kingston, ibm_fez) with
single-job batching, 
strict execution time budgeting, 
and side-by-side simulation.
"""

import json
import os
import shutil
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

from ..circuits.vqe_ansatz import build_particle_conserving_vqe_circuit
from ..circuits.qaoa_ansatz import build_qaoa_circuit
from ..metrics.invariants import (
    compute_number_operator_moments,
    compute_subspace_leakage,
    compute_global_parity
)
from ..metrics.export import export_to_excel, export_publication_figures
from .qubit_selection import find_best_qubit_chain


def build_algoinvar_benchmark_circuits(num_qubits: int = 4) -> List[Tuple[str, QuantumCircuit]]:
    """
    Constructs the standard suite of 5 algorithmic invariant circuits:
    1. vqe_particle_l2: VQE depth-2 Givens network (Z-basis)
    2. vqe_retrace: VQE depth-2 forward + inverse U^dagger U (Z-basis)
    3. qaoa_parity_p1: QAOA depth-1 global Z2 parity (X-basis)
    4. qaoa_parity_p2: QAOA depth-2 global Z2 parity (X-basis)
    5. qaoa_retrace_p2: QAOA depth-2 forward + inverse U^dagger U (X-basis)
    """
    circuits = []

    # 1. VQE Particle Conservation (2 particles)
    vqe_c1, _ = build_particle_conserving_vqe_circuit(num_qubits=num_qubits, num_particles=2, layers=2)
    circuits.append(("vqe_particle_l2", vqe_c1))

    # 2. VQE Retrace Echo (U^dagger U = I)

    vqe_c2, _ = build_particle_conserving_vqe_circuit(num_qubits=num_qubits, num_particles=2, layers=2, retrace=True)
    circuits.append(("vqe_retrace", vqe_c2))

    # 3. QAOA Global Parity p=1

    qaoa_p1, _, _, _ = build_qaoa_circuit(num_qubits=num_qubits, p=1, measurement_basis="X", retrace=False)
    circuits.append(("qaoa_parity_p1", qaoa_p1))

    # 4. QAOA Global Parity p=2

    qaoa_p2, _, _, _ = build_qaoa_circuit(num_qubits=num_qubits, p=2, measurement_basis="X", retrace=False)
    circuits.append(("qaoa_parity_p2", qaoa_p2))

    # 5. QAOA Retrace Echo p=2

    qaoa_ret, _, _, _ = build_qaoa_circuit(num_qubits=num_qubits, p=2, measurement_basis="X", retrace=True)
    circuits.append(("qaoa_retrace_p2", qaoa_ret))

    return circuits


def analyze_circuit_results(
    circuit_name: str,
    counts: Dict[str, int],
    num_qubits: int,
    shots: int
) -> Dict[str, Any]:

    """Analyzes raw bitstring counts against exact theoretical invariants."""
    metrics = {"circuit": circuit_name, "shots": shots}

    if circuit_name == "vqe_particle_l2":
        mean_n, var_n, err_n = compute_number_operator_moments(counts)
        leakage, err_leak = compute_subspace_leakage(counts, target_particle_number=2)
        metrics.update({
            "mean_N": mean_n,
            "var_N": var_n,
            "leakage": leakage,
            "ideal_N": 2.0,
            "ideal_var": 0.0,
            "ideal_leakage": 0.0,
            "passed": abs(mean_n - 2.0) <= 0.08 and var_n <= 0.16
        })

    elif circuit_name == "vqe_retrace":
        target_bitstring = "0" * (num_qubits - 2) + "1" * 2
        return_shots = counts.get(target_bitstring, 0)
        fidelity = return_shots / shots
        metrics.update({
            "return_fidelity": fidelity,
            "ideal_fidelity": 1.0,
            "passed": fidelity >= 0.75
        })

    elif circuit_name in ("qaoa_parity_p1", "qaoa_parity_p2"):
        mean_p, err_p = compute_global_parity(counts)
        metrics.update({
            "global_parity": mean_p,
            "ideal_parity": 1.0,
            "passed": mean_p >= 0.60
        })

    elif circuit_name == "qaoa_retrace_p2":
        target_bitstring = "0" * num_qubits
        return_shots = counts.get(target_bitstring, 0)
        fidelity = return_shots / shots
        metrics.update({
            "retrace_fidelity": fidelity,
            "ideal_fidelity": 1.0,
            "passed": fidelity >= 0.60
        })

    return metrics


def run_algoinvar_experiments(
    ibm_token: Optional[str] = None,
    ibm_crn: Optional[str] = None,
    channel: str = "ibm_cloud",
    backend_name: str = "ibm_kingston",
    num_qubits: int = 4,
    shots: int = 8192,
    max_budget_seconds: float = 180.0,
    job_id: Optional[str] = None,
    run_hardware: bool = False,
    mode: Optional[str] = None,
    output_file: Optional[str] = None,
    figures_dir: Optional[str] = None
) -> Dict[str, Any]:

    """
    Main driver executing AlgoInvar on Simulation and/or Real IBM Hardware.
    """

    if mode is None:
        if job_id:
            mode = "reverification"
        elif run_hardware:
            mode = "hardware_run"
        else:
            mode = "simulation"

    if output_file is None:
        hw_folder = f"results_{backend_name.replace('ibm_', '')}"
        mode_dir = os.path.join(hw_folder, mode)
        output_file = os.path.join(mode_dir, f"{backend_name}_results.json")

    report: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "backend": backend_name,
        "mode": mode,
        "num_qubits": num_qubits,
        "shots_per_circuit": shots,
        "simulations": {},
        "hardware": None
    }

    # 1. Build circuits

    raw_circuits = build_algoinvar_benchmark_circuits(num_qubits=num_qubits)
    names = [name for name, _ in raw_circuits]
    circs = [c for _, c in raw_circuits]

    # 2. Baseline Noiseless Simulation

    print("[1/3] Running Noiseless Reference Simulation (AerSimulator)...")
    noiseless_backend = AerSimulator()
    sim_counts = {}
    for name, c in raw_circuits:
        tc = transpile(c, noiseless_backend)
        job = noiseless_backend.run(tc, shots=shots)
        sim_counts[name] = job.result().get_counts()

    noiseless_metrics = {
        name: analyze_circuit_results(name, sim_counts[name], num_qubits, shots)
        for name in names
    }
    report["simulations"]["noiseless"] = noiseless_metrics

    # 3. Hardware Execution or Offline Re-read

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

        # Calibration-guided qubit selection

        print("  Evaluating live calibration to select cleanest physical chain...")
        chain = find_best_qubit_chain(backend, num_qubits=num_qubits)
        print(f"  Selected optimal physical chain: {chain}")

        # Transpile ISA circuits

        pm = generate_preset_pass_manager(optimization_level=1, backend=backend, initial_layout=chain, seed_transpiler=42)
        isa_circuits = [pm.run(c) for c in circs]

        # Calculate estimated QPU time

        total_shots = len(isa_circuits) * shots
        est_seconds = 2.0 + 5.6e-4 * total_shots
        print(f"  Prepared {len(isa_circuits)} ISA circuits; Total shots: {total_shots}")
        print(f"  Estimated QPU time: ~{est_seconds:.1f} s (Budget limit: {max_budget_seconds:.1f} s)")

        if job_id:
            print(f"  Re-reading existing job ID: {job_id} (0 QPU seconds consumed)...")
            hw_job = service.job(job_id)
        else:
            if est_seconds > max_budget_seconds:
                raise RuntimeError(f"Estimated QPU time ({est_seconds:.1f}s) exceeds safety budget ({max_budget_seconds:.1f}s). Aborting.")

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
        hw_counts = [r.data.meas.get_counts() for r in res]

        try:
            qpu_usage = float(hw_job.usage() or 0.0)
        except Exception:
            qpu_usage = est_seconds

        hw_metrics = {
            name: analyze_circuit_results(name, hw_counts[idx], num_qubits, shots)
            for idx, name in enumerate(names)
        }

        report["hardware"] = {
            "job_id": hw_job.job_id(),
            "backend": backend_name,
            "chain": chain,
            "qpu_seconds": qpu_usage,
            "metrics": hw_metrics,
            "raw_counts": hw_counts
        }

    # 4. Save to JSON, Excel, and Publication Figures

    out_dir = os.path.dirname(output_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[3/3] Results serialized to JSON: {output_file}")

    excel_file = output_file.replace(".json", ".xlsx")
    export_to_excel(report, excel_file)
    print(f"      Multi-sheet Excel Workbook saved: {excel_file}")

    if figures_dir is None:
        figures_dir = os.path.join(out_dir, "figures") if out_dir else "figures"
    os.makedirs(figures_dir, exist_ok=True)

    figures = export_publication_figures(report, figures_dir)
    print(f"      Publication-ready Figures generated in: {figures_dir}/")
    for fig_path in figures:
        print(f"        - {fig_path}")

    # Optional: mirror figures to paper/figures 
	#if the folder exists in the project root

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    paper_fig_dir = os.path.join(project_root, "paper", "figures")
    if os.path.isdir(paper_fig_dir):
        for fig_path in figures:
            try:
                shutil.copy(fig_path, paper_fig_dir)
            except Exception:
                pass

    report["artifacts"] = {
        "json": output_file,
        "excel": excel_file,
        "figures": figures
    }

    return report
