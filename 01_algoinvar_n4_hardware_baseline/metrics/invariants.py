"""
This is the Exact Invariant and Subspace Metric Evaluators for AlgoInvar.

All metrics are derived directly from measurement bitstrings 
without 
requiring exponential classical statevector simulation or curve-fitting.
"""

from typing import Dict, Tuple
import numpy as np


def compute_number_operator_moments(counts: Dict[str, int]) -> Tuple[float, float, float]:
    """
    Computes <N>, <N^2>, and Var(N) 
	from computational basis counts.

    In the computational (Z) basis, each bitstring x is an eigenstate of the
    fermionic number operator N = sum_j (I - Z_j)/2 with eigenvalue equal
    to its Hamming weight wt(x).

    Args:
        counts: Dictionary of bitstring counts, e.g. {'0101': 512, '0011': 488}.

    Returns:
        (mean_N, var_N, std_err_N)
    """

    total_shots = sum(counts.values())
    if total_shots == 0:
        return 0.0, 0.0, 0.0

    # Hamming weight (number of 1s) for each measured bitstring

    weights = np.array([bitstring.count('1') for bitstring in counts.keys()], dtype=float)
    freqs = np.array(list(counts.values()), dtype=float) / total_shots

    mean_n = float(np.sum(freqs * weights))
    mean_n2 = float(np.sum(freqs * (weights ** 2)))
    var_n = float(max(0.0, mean_n2 - mean_n ** 2))
    std_err = float(np.sqrt(var_n / total_shots))

    return mean_n, var_n, std_err


def compute_subspace_leakage(counts: Dict[str, int], target_particle_number: int) -> Tuple[float, float]:

    """
    Quantifies the probability of state leakage out of the target Fock sector.

    Leakage = 1 - sum_{x: wt(x) == N_e} P(x)

    Args:
        counts: Computational basis measurement counts.
        target_particle_number: The theoretical conserved electron/particle count N_e.

    Returns:
        (leakage_prob, standard_error)
    """

    total_shots = sum(counts.values())
    if total_shots == 0:
        return 0.0, 0.0

    in_sector_shots = sum(
        count for bitstring, count in counts.items()
        if bitstring.count('1') == target_particle_number
    )
    p_in_sector = in_sector_shots / total_shots
    leakage = 1.0 - p_in_sector
    std_err = float(np.sqrt(max(0.0, leakage * (1.0 - leakage) / total_shots)))

    return float(leakage), std_err


def compute_global_parity(x_basis_counts: Dict[str, int]) -> Tuple[float, float]:

    """
    Computes the expectation value <Prod_j X_j> from X-basis measurement counts.

    In the X-basis (after applying Hadamard gates to all qubits before measurement),
    the parity operator P = X^(\\otimes n) assigns eigenvalue (-1)^(wt(y))
    to each bitstring y.

    Theoretical invariant in QAOA: <P> = +1.0 for all depths p and parameters.

    Args:
        x_basis_counts: Counts measured in the X basis.

    Returns:
        (mean_parity, standard_error)
    """

    total_shots = sum(x_basis_counts.values())
    if total_shots == 0:
        return 0.0, 0.0

    parities = np.array([(-1) ** (bitstring.count('1')) for bitstring in x_basis_counts.keys()], dtype=float)
    freqs = np.array(list(x_basis_counts.values()), dtype=float) / total_shots

    mean_p = float(np.sum(freqs * parities))
    var_p = float(max(0.0, 1.0 - mean_p ** 2))
    std_err = float(np.sqrt(var_p / total_shots))

    return mean_p, std_err
