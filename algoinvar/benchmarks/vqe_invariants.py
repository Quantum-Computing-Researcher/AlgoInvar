"""
VQE Particle Conservation & Subspace Confinement Benchmarks.
"""

from typing import Any, Dict, Optional
import numpy as np
from qiskit import transpile

from ..circuits.vqe_ansatz import build_particle_conserving_vqe_circuit
from ..metrics.invariants import compute_number_operator_moments, compute_subspace_leakage
from .base import BenchmarkResult


def run_vqe_particle_benchmark(
    backend: Any,
    num_qubits: int = 4,
    num_particles: int = 2,
    layers: int = 2,
    shots: int = 2048,
    tolerance: float = 0.05,
    seed: int = 42
) -> BenchmarkResult:
    """
    Executes the VQE Particle Conservation Benchmark.

    Invariant: <N> = N_e and Var(N) = 0 for any parameter choice in a
    particle-conserving Givens ansatz.

    Args:
        backend: Qiskit backend / Aer simulator.
        num_qubits: Total qubits (orbitals).
        num_particles: Number of occupied fermions N_e.
        layers: Depth of the Givens exchange network.
        shots: Measurement sample size.
        tolerance: Allowable deviation under noise.
        seed: Random seed for rotation angles.

    Returns:
        BenchmarkResult with measured moments and leakage.
    """
    qc, angles = build_particle_conserving_vqe_circuit(
        num_qubits=num_qubits,
        num_particles=num_particles,
        layers=layers
    )

    # Transpile circuit for the target backend
    transpiled_qc = transpile(qc, backend)

    # Run execution
    job = backend.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts()

    # Calculate exact invariant moments from Z-basis readout
    mean_n, var_n, std_err_n = compute_number_operator_moments(counts)
    leakage, std_err_leak = compute_subspace_leakage(counts, num_particles)

    # Theoretical invariant
    theoretical_n = float(num_particles)
    deviation = abs(mean_n - theoretical_n)

    # Invariant holds if deviation and variance are within tolerance
    is_valid = (deviation <= tolerance) and (var_n <= tolerance)

    details = {
        "num_particles": num_particles,
        "layers": layers,
        "var_N": var_n,
        "subspace_leakage": leakage,
        "subspace_leakage_stderr": std_err_leak,
        "top_bitstrings": dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5])
    }

    return BenchmarkResult(
        benchmark_id="vqe_particle_conservation",
        num_qubits=num_qubits,
        shots=shots,
        measured_value=mean_n,
        theoretical_value=theoretical_n,
        deviation=deviation,
        uncertainty=std_err_n,
        is_valid=is_valid,
        details=details
    )
