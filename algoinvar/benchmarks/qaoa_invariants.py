"""
QAOA Symmetries & Retrace Invariant Benchmarks.
"""

from typing import Any, Dict, List, Optional, Tuple
from qiskit import transpile

from ..circuits.qaoa_ansatz import build_qaoa_circuit
from ..metrics.invariants import compute_global_parity
from .base import BenchmarkResult


def run_qaoa_parity_benchmark(
    backend: Any,
    num_qubits: int = 4,
    p: int = 2,
    edges: Optional[List[Tuple[int, int]]] = None,
    shots: int = 2048,
    tolerance: float = 0.08
) -> BenchmarkResult:
    """
    Executes the QAOA Global Z_2 Parity Invariant Benchmark.

    Invariant: <Prod_j X_j> = +1.0 identically for all graphs, depths p, and
    variational parameters (gamma, beta).

    Args:
        backend: Qiskit backend or Aer simulator.
        num_qubits: Total number of vertices/qubits.
        p: QAOA depth.
        edges: Graph topology. Defaults to cycle graph.
        shots: Measurement sample size.
        tolerance: Allowable deviation under noise.

    Returns:
        BenchmarkResult for global parity.
    """
    qc, applied_edges, gammas, betas = build_qaoa_circuit(
        num_qubits=num_qubits,
        edges=edges,
        p=p,
        measurement_basis="X",
        retrace=False
    )

    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts()

    mean_parity, std_err_parity = compute_global_parity(counts)

    theoretical_parity = 1.0
    deviation = abs(mean_parity - theoretical_parity)
    is_valid = deviation <= tolerance

    details = {
        "p": p,
        "gammas": gammas,
        "betas": betas,
        "num_edges": len(applied_edges),
        "parity_loss": 1.0 - mean_parity,
        "even_parity_shots": sum(c for b, c in counts.items() if b.count('1') % 2 == 0),
        "odd_parity_shots": sum(c for b, c in counts.items() if b.count('1') % 2 == 1)
    }

    return BenchmarkResult(
        benchmark_id="qaoa_z2_parity",
        num_qubits=num_qubits,
        shots=shots,
        measured_value=mean_parity,
        theoretical_value=theoretical_parity,
        deviation=deviation,
        uncertainty=std_err_parity,
        is_valid=is_valid,
        details=details
    )


def run_qaoa_retrace_benchmark(
    backend: Any,
    num_qubits: int = 4,
    p: int = 2,
    edges: Optional[List[Tuple[int, int]]] = None,
    shots: int = 2048,
    tolerance: float = 0.10
) -> BenchmarkResult:
    """
    Executes the QAOA Retrace (Unitary Inversion) Benchmark.

    Applies U^dagger(p) U(p) and measures identity return fidelity F = |<+_n| U^dagger U |+_n>|^2.
    Theoretical invariant: F = 1.0.

    Args:
        backend: Qiskit backend or Aer simulator.
        num_qubits: Total number of vertices/qubits.
        p: QAOA depth.
        edges: Graph topology.
        shots: Measurement sample size.
        tolerance: Allowable deviation under noise.

    Returns:
        BenchmarkResult for retrace return fidelity.
    """
    qc, applied_edges, gammas, betas = build_qaoa_circuit(
        num_qubits=num_qubits,
        edges=edges,
        p=p,
        measurement_basis="X",
        retrace=True
    )

    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts()

    # In X-basis, initial state |+>^n maps to bitstring '0'*n
    target_bitstring = '0' * num_qubits
    return_shots = counts.get(target_bitstring, 0)
    fidelity = return_shots / shots
    std_err = (fidelity * (1.0 - fidelity) / shots) ** 0.5

    theoretical_fidelity = 1.0
    deviation = abs(fidelity - theoretical_fidelity)
    is_valid = deviation <= tolerance

    details = {
        "p": p,
        "target_bitstring": target_bitstring,
        "return_shots": return_shots,
        "total_shots": shots,
        "retrace_loss": 1.0 - fidelity
    }

    return BenchmarkResult(
        benchmark_id="qaoa_retrace_echo",
        num_qubits=num_qubits,
        shots=shots,
        measured_value=fidelity,
        theoretical_value=theoretical_fidelity,
        deviation=deviation,
        uncertainty=std_err,
        is_valid=is_valid,
        details=details
    )
