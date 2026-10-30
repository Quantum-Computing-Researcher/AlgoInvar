"""
Unit tests for AlgoInvar exact mathematical invariants.
"""

import unittest
from qiskit_aer import AerSimulator
try:
    from algoinvar_n4_1st_exp.benchmarks.vqe_invariants import run_vqe_particle_benchmark
    from algoinvar_n4_1st_exp.benchmarks.qaoa_invariants import run_qaoa_parity_benchmark, run_qaoa_retrace_benchmark
    from algoinvar_n4_1st_exp.runner import run_suite
except ImportError:
    from algoinvar.benchmarks.vqe_invariants import run_vqe_particle_benchmark
    from algoinvar.benchmarks.qaoa_invariants import run_qaoa_parity_benchmark, run_qaoa_retrace_benchmark
    from algoinvar.runner import run_suite


class TestAlgoInvar(unittest.TestCase):
    def setUp(self):
        self.backend = AerSimulator()

    def test_vqe_particle_conservation_noiseless(self):
        # 4 qubits, 2 particles -> <N> must be 2.0, Var(N) must be 0.0, leakage must be 0.0
        res = run_vqe_particle_benchmark(
            backend=self.backend,
            num_qubits=4,
            num_particles=2,
            layers=2,
            shots=4096,
            tolerance=1e-5
        )
        self.assertAlmostEqual(res.measured_value, 2.0, places=4)
        self.assertAlmostEqual(res.details["var_N"], 0.0, places=4)
        self.assertAlmostEqual(res.details["subspace_leakage"], 0.0, places=4)
        self.assertTrue(res.is_valid)

    def test_qaoa_global_parity_noiseless(self):
        # QAOA on 4 qubits, depth 1 and 2 -> <Prod X_i> must be 1.0 identically
        for p in [1, 2]:
            res = run_qaoa_parity_benchmark(
                backend=self.backend,
                num_qubits=4,
                p=p,
                shots=4096,
                tolerance=1e-5
            )
            self.assertAlmostEqual(res.measured_value, 1.0, places=4)
            self.assertTrue(res.is_valid)

    def test_qaoa_retrace_noiseless(self):
        # Retrace U^dagger U should return to |+>^n with fidelity 1.0
        res = run_qaoa_retrace_benchmark(
            backend=self.backend,
            num_qubits=4,
            p=2,
            shots=4096,
            tolerance=1e-5
        )
        self.assertAlmostEqual(res.measured_value, 1.0, places=4)
        self.assertTrue(res.is_valid)

    def test_full_suite_runner(self):
        report = run_suite(backend=self.backend, num_qubits=4, shots=2048)
        self.assertEqual(len(report.results), 3)
        for r in report.results:
            self.assertTrue(r.is_valid)


if __name__ == "__main__":
    unittest.main()
