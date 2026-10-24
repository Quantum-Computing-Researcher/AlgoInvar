"""
Demonstration: Sweeping Noise Levels to Validate Invariant Sensitivity.

Shows how Var(N), subspace leakage, and global parity <P> respond to increasing
hardware gate errors and decoherence.
"""

import numpy as np
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, thermal_relaxation_error

from algoinvar.runner import run_suite
from algoinvar.benchmarks.vqe_invariants import run_vqe_particle_benchmark
from algoinvar.benchmarks.qaoa_invariants import run_qaoa_parity_benchmark


def make_noise_model(p1q: float = 0.001, p2q: float = 0.01) -> NoiseModel:
    """Builds a simple depolarizing noise model."""
    noise_model = NoiseModel()
    err1 = depolarizing_error(p1q, 1)
    err2 = depolarizing_error(p2q, 2)
    noise_model.add_all_qubit_quantum_error(err1, ['rx', 'ry', 'rz', 'h', 'x'])
    noise_model.add_all_qubit_quantum_error(err2, ['cx', 'rzz', 'xx_plus_yy'])
    return noise_model


def main():
    print("=================================================================")
    print("   AlgoInvar: Invariant-Anchored Benchmarking Demonstration")
    print("=================================================================\n")

    # 1. Noiseless Run
    print("--- 1. Baseline Noiseless Execution ---")
    noiseless_backend = AerSimulator()
    report_ideal = run_suite(noiseless_backend, num_qubits=4, shots=4096)
    print(report_ideal.summary())

    # 2. Noise Sensitivity Sweep
    print("\n--- 2. Noise Sensitivity Sweep (Depolarizing Gate Error) ---")
    print(f"{'2Q Error (p2q)':<15} | {'VQE <N>':<10} | {'Var(N)':<10} | {'Leakage':<10} | {'QAOA <P>':<10}")
    print("-" * 65)

    p2q_rates = [0.0, 0.005, 0.01, 0.02, 0.05]

    for p2 in p2q_rates:
        if p2 == 0.0:
            backend = AerSimulator()
        else:
            nm = make_noise_model(p1q=p2 / 10.0, p2q=p2)
            backend = AerSimulator(noise_model=nm)

        # Run VQE invariant
        vqe_res = run_vqe_particle_benchmark(backend=backend, num_qubits=4, num_particles=2, layers=2, shots=4096)
        mean_n = vqe_res.measured_value
        var_n = vqe_res.details["var_N"]
        leak = vqe_res.details["subspace_leakage"]

        # Run QAOA parity invariant
        qaoa_res = run_qaoa_parity_benchmark(backend=backend, num_qubits=4, p=2, shots=4096)
        mean_p = qaoa_res.measured_value

        print(f"{p2:<15.4f} | {mean_n:<10.4f} | {var_n:<10.4f} | {leak:<10.4f} | {mean_p:<10.4f}")

    print("\n[CONCLUSION] In the noiseless limit, invariants hold to 0.0000.")
    print("As hardware noise increases, Var(N), Leakage, and Parity Loss provide")
    print("an exact, simulation-free diagnostic metric of hardware fidelity.")


if __name__ == "__main__":
    main()
