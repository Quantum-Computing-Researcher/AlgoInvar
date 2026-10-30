"""
Noise channel sweeps for algorithmic invariant validation.
Evaluates particle number conservation and parity under Kraus error models.
"""

from typing import Dict, List, Any
import os
import json
import numpy as np
import pandas as pd

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, amplitude_damping_error, phase_damping_error, ReadoutError

from circuits.vqe_givens import build_vqe_givens_circuit, build_vqe_retrace_circuit
from circuits.qaoa_maxcut import build_qaoa_circuit, build_qaoa_retrace_circuit


def calculate_hamming_statistics(counts: Dict[str, int], shots: int) -> Dict[str, Any]:
    """Computes particle-number expectation, variance, sector populations, and asymmetry."""
    sector_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    
    for bitstring, count in counts.items():
        w = bitstring.count("1")
        if w in sector_counts:
            sector_counts[w] += count
            
    p_w = {w: count / shots for w, count in sector_counts.items()}
    
    mean_n = sum(w * p_w[w] for w in range(5))
    var_n = sum(((w - mean_n) ** 2) * p_w[w] for w in range(5))
    
    p_target = p_w[2]
    leakage = 1.0 - p_target
    
    c1, c3 = sector_counts[1], sector_counts[3]
    if c3 > 0:
        r_asym = c1 / c3
        sigma_r = r_asym * np.sqrt(1.0 / c1 + 1.0 / c3) if c1 > 0 else 0.0
    else:
        r_asym = float("nan") if c1 == 0 else 999.0
        sigma_r = 0.0
        
    return {
        "mean_N": mean_n,
        "var_N": var_n,
        "p_target_w2": p_target,
        "leakage": leakage,
        "p_w0": p_w[0],
        "p_w1": p_w[1],
        "p_w2": p_w[2],
        "p_w3": p_w[3],
        "p_w4": p_w[4],
        "R_asym": r_asym,
        "sigma_R_asym": sigma_r
    }


def calculate_parity_expectation(counts: Dict[str, int], shots: int) -> float:
    """Calculates global parity <prod X_u> from X-basis readout bitstrings."""
    parity_sum = 0
    for bitstring, count in counts.items():
        sign = (-1) ** (bitstring.count("1"))
        parity_sum += sign * count
    return parity_sum / shots


def sweep_amplitude_damping(
    gamma_values: List[float],
    shots: int = 50000,
    thetas: List[float] = None
) -> List[Dict[str, Any]]:
    """Sweeps amplitude damping parameter gamma to map directional asymmetry."""
    if thetas is None:
        thetas = [0.45, 0.78, 0.32, 0.65]
        
    qc = build_vqe_givens_circuit(thetas, n_qubits=4, layers=2)
    records = []
    
    for gamma in gamma_values:
        noise_model = NoiseModel()
        if gamma > 0:
            error_1q = amplitude_damping_error(gamma)
            noise_model.add_all_qubit_quantum_error(error_1q, ["x", "ry", "rz", "h"])
            error_2q = error_1q.tensor(error_1q)
            noise_model.add_all_qubit_quantum_error(error_2q, ["cx", "cz", "rzz"])
            
        sim = AerSimulator(noise_model=noise_model)
        counts = sim.run(qc, shots=shots).result().get_counts()
        stats = calculate_hamming_statistics(counts, shots)
        stats["gamma"] = gamma
        records.append(stats)
        
    return records


def sweep_coherent_overrotations(
    delta_values: List[float],
    shots: int = 50000,
    base_thetas: List[float] = None
) -> List[Dict[str, Any]]:
    """Sweeps angle offset delta to verify particle number invariance under unitary drift."""
    if base_thetas is None:
        base_thetas = [0.45, 0.78, 0.32, 0.65]
        
    records = []
    sim = AerSimulator()
    
    for delta in delta_values:
        perturbed_thetas = [t + delta for t in base_thetas]
        
        qc_fwd = build_vqe_givens_circuit(perturbed_thetas, n_qubits=4, layers=2)
        counts_fwd = sim.run(qc_fwd, shots=shots).result().get_counts()
        stats = calculate_hamming_statistics(counts_fwd, shots)
        
        # Retrace echo circuit with forward offset delta
        qc_echo = QuantumCircuit(4, 4)
        for i in range(2):
            qc_echo.x(i)
        from circuits.vqe_givens import build_givens_gate
        for i, val in enumerate(perturbed_thetas):
            build_givens_gate(qc_echo, i % 3, (i % 3) + 1, val)
        for i, val in reversed(list(enumerate(base_thetas))):
            build_givens_gate(qc_echo, i % 3, (i % 3) + 1, -val)
        qc_echo.measure(range(4), range(4))
        
        counts_echo = sim.run(qc_echo, shots=shots).result().get_counts()
        f_echo = counts_echo.get("0011", 0) / shots
        
        stats["delta"] = delta
        stats["f_echo"] = f_echo
        records.append(stats)
        
    return records


def sweep_pure_dephasing(
    lambda_values: List[float],
    shots: int = 50000
) -> List[Dict[str, Any]]:
    """Sweeps phase damping parameter lambda for VQE and QAOA circuits."""
    vqe_thetas = [0.45, 0.78, 0.32, 0.65]
    qaoa_gammas = [0.38, 0.52]
    qaoa_betas = [0.45, 0.30]
    
    qc_vqe = build_vqe_givens_circuit(vqe_thetas, n_qubits=4, layers=2)
    qc_qaoa_p1 = build_qaoa_circuit(qaoa_gammas[:1], qaoa_betas[:1], measure_basis="X")
    qc_qaoa_p2 = build_qaoa_circuit(qaoa_gammas, qaoa_betas, measure_basis="X")
    
    records = []
    for lam in lambda_values:
        noise_model = NoiseModel()
        if lam > 0:
            error_1q = phase_damping_error(lam)
            noise_model.add_all_qubit_quantum_error(error_1q, ["x", "ry", "rz", "h", "rx"])
            error_2q = error_1q.tensor(error_1q)
            noise_model.add_all_qubit_quantum_error(error_2q, ["cx", "cz", "rzz"])
            
        sim = AerSimulator(noise_model=noise_model)
        
        counts_vqe = sim.run(qc_vqe, shots=shots).result().get_counts()
        stats_vqe = calculate_hamming_statistics(counts_vqe, shots)
        
        counts_qaoa_p1 = sim.run(qc_qaoa_p1, shots=shots).result().get_counts()
        parity_p1 = calculate_parity_expectation(counts_qaoa_p1, shots)
        
        counts_qaoa_p2 = sim.run(qc_qaoa_p2, shots=shots).result().get_counts()
        parity_p2 = calculate_parity_expectation(counts_qaoa_p2, shots)
        
        records.append({
            "lambda": lam,
            "vqe_var_N": stats_vqe["var_N"],
            "vqe_leakage": stats_vqe["leakage"],
            "vqe_mean_N": stats_vqe["mean_N"],
            "qaoa_parity_p1": parity_p1,
            "qaoa_parity_p2": parity_p2
        })
        
    return records


def sweep_spam_confusion(
    epsilon_values: List[float],
    shots: int = 50000
) -> List[Dict[str, Any]]:
    """Sweeps symmetric vs asymmetric detector confusion matrices."""
    vqe_thetas = [0.45, 0.78, 0.32, 0.65]
    qc_vqe = build_vqe_givens_circuit(vqe_thetas, n_qubits=4, layers=2)
    
    records = []
    for eps in epsilon_values:
        # Symmetric SPAM
        noise_sym = NoiseModel()
        if eps > 0:
            ro_sym = ReadoutError([[1.0 - eps, eps], [eps, 1.0 - eps]])
            noise_sym.add_all_qubit_readout_error(ro_sym)
            
        sim_sym = AerSimulator(noise_model=noise_sym)
        counts_sym = sim_sym.run(qc_vqe, shots=shots).result().get_counts()
        stats_sym = calculate_hamming_statistics(counts_sym, shots)
        
        # Asymmetric SPAM
        noise_asym = NoiseModel()
        if eps > 0:
            p01 = min(2.5 * eps, 0.95)
            p10 = eps
            ro_asym = ReadoutError([[1.0 - p10, p10], [p01, 1.0 - p01]])
            noise_asym.add_all_qubit_readout_error(ro_asym)
            
        sim_asym = AerSimulator(noise_model=noise_asym)
        counts_asym = sim_asym.run(qc_vqe, shots=shots).result().get_counts()
        stats_asym = calculate_hamming_statistics(counts_asym, shots)
        
        records.append({
            "epsilon": eps,
            "sym_R_asym": stats_sym["R_asym"],
            "sym_var_N": stats_sym["var_N"],
            "sym_leakage": stats_sym["leakage"],
            "asym_R_asym": stats_asym["R_asym"],
            "asym_var_N": stats_asym["var_N"],
            "asym_leakage": stats_asym["leakage"]
        })
        
    return records


def run_full_error_injection_suite(
    output_dir: str = "results/error_injection",
    shots: int = 50000
) -> Dict[str, Any]:
    """Runs all four noise sweeps and saves JSON and Excel files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Amplitude Damping
    gammas = np.linspace(0.0, 0.20, 21).tolist()
    ad_results = sweep_amplitude_damping(gammas, shots=shots)
    with open(os.path.join(output_dir, "amplitude_damping_sweep.json"), "w") as f:
        json.dump(ad_results, f, indent=2)
        
    # 2. Coherent Over-rotations
    deltas = np.linspace(-np.pi / 4.0, np.pi / 4.0, 21).tolist()
    coh_results = sweep_coherent_overrotations(deltas, shots=shots)
    with open(os.path.join(output_dir, "coherent_overrotation_sweep.json"), "w") as f:
        json.dump(coh_results, f, indent=2)
        
    # 3. Pure Dephasing
    lambdas = np.linspace(0.0, 0.25, 21).tolist()
    pd_results = sweep_pure_dephasing(lambdas, shots=shots)
    with open(os.path.join(output_dir, "phase_dephasing_sweep.json"), "w") as f:
        json.dump(pd_results, f, indent=2)
        
    # 4. SPAM Confusion
    epsilons = np.linspace(0.0, 0.08, 17).tolist()
    spam_results = sweep_spam_confusion(epsilons, shots=shots)
    with open(os.path.join(output_dir, "spam_confusion_sweep.json"), "w") as f:
        json.dump(spam_results, f, indent=2)
        
    excel_path = os.path.join(output_dir, "noise_injection_results.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        pd.DataFrame(ad_results).to_excel(writer, sheet_name="Amplitude_Damping_T1", index=False)
        pd.DataFrame(coh_results).to_excel(writer, sheet_name="Coherent_Angle_Drift", index=False)
        pd.DataFrame(pd_results).to_excel(writer, sheet_name="Pure_Dephasing_T2", index=False)
        pd.DataFrame(spam_results).to_excel(writer, sheet_name="SPAM_Confusion", index=False)
        
    return {
        "amplitude_damping": ad_results,
        "coherent": coh_results,
        "pure_dephasing": pd_results,
        "spam": spam_results
    }


if __name__ == "__main__":
    run_full_error_injection_suite()
