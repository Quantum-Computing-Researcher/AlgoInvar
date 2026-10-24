"""
Defines the basic data structures used to store benchmark results
and generate a report for the AlgoInvar benchmark suite.
Base classes and result data structures for AlgoInvar benchmarks.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BenchmarkResult:
    """Stores the execution outcome and metric comparison for a single benchmark."""
    benchmark_id: str
    num_qubits: int
    shots: int
    measured_value: float
    theoretical_value: float
    deviation: float
    uncertainty: float
    is_valid: bool

    # Store any additional information related to this benchmark.
    details: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        status = "PASSED" if self.is_valid else "FAILED"
        return (
            f"[{status}] {self.benchmark_id} (n={self.num_qubits}, shots={self.shots}):\n"
            f"  Measured: {self.measured_value:.5f} +/- {self.uncertainty:.5f}\n"
            f"  Reference (Exact Invariant): {self.theoretical_value:.5f}\n"
            f"  Absolute Deviation: {self.deviation:.5f}"
        )


@dataclass
class SuiteReport:
    """Summary report across all executed benchmarks in the suite."""
    backend_name: str
    total_shots: int
    results: List[BenchmarkResult] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "=" * 70,
            f" AlgoInvar Benchmark Suite Report — Backend: {self.backend_name}",
            f" Total Shots Executed: {self.total_shots}",
            "=" * 70,
        ]
        for r in self.results:
            lines.append(r.summary())
            lines.append("-" * 70)
        passed = sum(1 for r in self.results if r.is_valid)
        total = len(self.results)
        lines.append(f" Overall Score: {passed}/{total} Invariants Preserved")
        lines.append("=" * 70)
        return "\n".join(lines)
