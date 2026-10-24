"""
AlgoInvar Suite Runner
Top Level API
"""

from typing import Any, List, Optional
from qiskit_aer import AerSimulator

from .benchmarks.base import SuiteReport
from .benchmarks.vqe_invariants import run_vqe_particle_benchmark
from .benchmarks.qaoa_invariants import run_qaoa_parity_benchmark, run_qaoa_retrace_benchmark


def run_suite(
    backend: Optional[Any] = None,
    num_qubits: int = 4,
    shots: int = 2048,
    vqe_particles: int = 2,
    vqe_layers: int = 2,
    qaoa_depth: int = 2,
    only: Optional[List[str]] = None
) -> SuiteReport:

    """
    Runs the AlgoInvar benchmark suite against a target backend.

    Args:
        backend: Qiskit Backend / AerSimulator. If None, default noiseless AerSimulator is used.
        num_qubits: System size (must be >= 2).
        shots: Shots per benchmark circuit.
        vqe_particles: Occupied electron count N_e.
        vqe_layers: Depth of Givens exchange layers.
        qaoa_depth: QAOA layer depth p.
        only: Optional list of benchmark IDs to run (e.g. ['qaoa_z2_parity']).

    Returns:
        SuiteReport containing all individual benchmark outcomes.
    """

    if backend is None:
        backend = AerSimulator()

    backend_name = getattr(backend, "name", "AerSimulator")
    report = SuiteReport(backend_name=backend_name, total_shots=0)

    # 1. VQE Particle Conservation

    if only is None or "vqe_particle_conservation" in only:
        res_vqe = run_vqe_particle_benchmark(
            backend=backend,
            num_qubits=num_qubits,
            num_particles=vqe_particles,
            layers=vqe_layers,
            shots=shots
        )
        report.results.append(res_vqe)
        report.total_shots += shots

    # 2. QAOA Z_2 Global Parity

    if only is None or "qaoa_z2_parity" in only:
        res_qaoa_parity = run_qaoa_parity_benchmark(
            backend=backend,
            num_qubits=num_qubits,
            p=qaoa_depth,
            shots=shots
        )
        report.results.append(res_qaoa_parity)
        report.total_shots += shots

    # 3. QAOA Retrace Echo

    if only is None or "qaoa_retrace_echo" in only:
        res_qaoa_retrace = run_qaoa_retrace_benchmark(
            backend=backend,
            num_qubits=num_qubits,
            p=qaoa_depth,
            shots=shots
        )
        report.results.append(res_qaoa_retrace)
        report.total_shots += shots

    return report
