"""
AlgoInvar: Invariant-Anchored Benchmarking for Algorithmic State Preparation.

A parameter-free, simulation-free benchmark framework for VQE and QAOA quantum circuits.
"""

from .runner import run_suite
from .benchmarks.base import BenchmarkResult, SuiteReport
from .benchmarks.vqe_invariants import run_vqe_particle_benchmark
from .benchmarks.qaoa_invariants import run_qaoa_parity_benchmark, run_qaoa_retrace_benchmark

__version__ = "0.1.0"
__all__ = [
    "run_suite",
    "BenchmarkResult",
    "SuiteReport",
    "run_vqe_particle_benchmark",
    "run_qaoa_parity_benchmark",
    "run_qaoa_retrace_benchmark"
]
