"""
Calibration-Guided Qubit Selection for IBM Quantum Processors.
Finds connected chains of physical qubits that 
minimize readout and 2-qubit gate errors.
"""

from typing import Dict, List, Optional, Set, Tuple
import numpy as np


def find_best_qubit_chain(
    backend: any,
    num_qubits: int,
    avoid_qubits: Optional[Set[int]] = None,
    max_readout_error: float = 0.04,
    tries: int = 5000,
    seed: int = 42
) -> List[int]:

    """
    Finds the cleanest connected chain of physical qubits on the backend.
    """
    target = getattr(backend, "target", backend)
    total_physical_qubits = getattr(backend, "num_qubits", target.num_qubits if hasattr(target, "num_qubits") else 156)

    avoid = set(avoid_qubits or set())

    # 1. Readout errors per qubit

    readout_errors: Dict[int, float] = {}
    if "measure" in target:
        for q in range(total_physical_qubits):
            prop = target["measure"].get((q,))
            if prop is not None and getattr(prop, "error", None) is not None:
                readout_errors[q] = float(prop.error)
            else:
                readout_errors[q] = 1.0
    else:
        for q in range(total_physical_qubits):
            readout_errors[q] = 0.01

    # Filter out bad qubits

    bad_qubits = avoid | {q for q, err in readout_errors.items() if err > max_readout_error}

    # 2. Extract 2-qubit gate errors (CZ, ECR, or CX)

    two_qubit_errors: Dict[Tuple[int, int], float] = {}
    for gate_name in ["cz", "ecr", "cx"]:
        if gate_name in target:
            for (a, b), prop in target[gate_name].items():
                if prop is not None and getattr(prop, "error", None) is not None:
                    if a not in bad_qubits and b not in bad_qubits:
                        two_qubit_errors[(a, b)] = float(prop.error)
                        two_qubit_errors[(b, a)] = float(prop.error)
            break

    # Construct adjacency graph

    neighbors: Dict[int, List[int]] = {}
    for (a, b) in two_qubit_errors:
        neighbors.setdefault(a, []).append(b)

    if not neighbors:
        return list(range(num_qubits))

    best_cost = np.inf
    best_chain = None
    rng = np.random.default_rng(seed)
    start_nodes = list(neighbors.keys())

    for _ in range(tries):
        start = int(rng.choice(start_nodes))
        chain = [start]

        while len(chain) < num_qubits:
            candidates = [nb for nb in neighbors.get(chain[-1], []) if nb not in chain]
            if not candidates:
                break
            weights = np.array([
                1.0 / (two_qubit_errors.get((chain[-1], c), 0.01) + readout_errors.get(c, 0.01) + 1e-4)
                for c in candidates
            ])
            chosen = int(rng.choice(candidates, p=weights / weights.sum()))
            chain.append(chosen)

        if len(chain) == num_qubits:
            cost = sum(readout_errors.get(q, 0.01) for q in chain) + sum(
                two_qubit_errors.get((chain[i], chain[i + 1]), 0.01) for i in range(num_qubits - 1)
            )
            if cost < best_cost:
                best_cost = cost
                best_chain = chain

    if best_chain is None:
        return list(range(num_qubits))

    return best_chain
