"""
Calibration-Guided Qubit Selection for IBM Quantum Processors.

We use this module to find connected 1D chains of physical qubits on 156-qubit
IBM Heron r2 processors (ibm_kingston and ibm_fez) that minimize cumulative
readout assignment errors and two-qubit CZ gate errors across register widths
n = 4, 8, 12, 16, 32, and 64.
"""

import csv
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np


def find_best_qubit_chain_scaled(
    backend: Any = None,
    num_qubits: int = 4,
    avoid_qubits: Optional[Set[int]] = None,
    max_readout_error: float = 0.04,
    tries: int = 5000,
    seed: int = 42,
    calibration_csv: Optional[str] = None
) -> Tuple[List[int], Dict[str, float]]:
    """
    Finds the cleanest connected 1D chain of `num_qubits` physical qubits on the backend.

    We evaluate candidate paths using the cumulative error cost:
        cost = sum(readout_errors[q]) + sum(two_qubit_errors[(chain[i], chain[i+1])])

    For smaller widths (n <= 12), we use a weighted random walk over the coupling map.
    For larger widths (n = 16, 32, 64) where random walks can get trapped in degree-2/3
    corners of the Heavy-Hex lattice, we deploy a degree-ordered backtracking search (DFS)
    guided by the same calibration cost function.
    """
    avoid = set(avoid_qubits or set())
    readout_errors: Dict[int, float] = {}
    two_qubit_errors: Dict[Tuple[int, int], float] = {}

    # 1. Extract live readout and 2-qubit gate calibration errors from the IBM backend target
    if backend is not None and hasattr(backend, "target"):
        target = backend.target
        total_physical_qubits = getattr(
            backend, "num_qubits", target.num_qubits if hasattr(target, "num_qubits") else 156
        )

        # Readout assignment errors per physical qubit
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

        # Filter out qubits whose readout error exceeds our threshold (default: 4%)
        bad_qubits = avoid | {q for q, err in readout_errors.items() if err > max_readout_error}

        # Extract native 2-qubit gate errors (CZ on Heron r2, or ECR/CX on other devices)
        for gate_name in ["cz", "ecr", "cx"]:
            if gate_name in target:
                for (a, b), prop in target[gate_name].items():
                    if prop is not None and getattr(prop, "error", None) is not None:
                        if a not in bad_qubits and b not in bad_qubits:
                            two_qubit_errors[(a, b)] = float(prop.error)
                            two_qubit_errors[(b, a)] = float(prop.error)
                break

    # 2. If running offline with a saved calibration CSV snapshot, parse readout and CZ errors
    elif calibration_csv is not None:
        with open(calibration_csv, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            q = int(r["Qubit"])
            ro = float(r.get("Readout assignment error") or 1.0)
            readout_errors[q] = ro
        bad_qubits = avoid | {q for q, err in readout_errors.items() if err > max_readout_error}
        for r in rows:
            a = int(r["Qubit"])
            if a in bad_qubits:
                continue
            for pair in r.get("CZ error", "").split(";"):
                if ":" in pair:
                    b_s, val_s = pair.split(":")
                    b = int(b_s)
                    err = float(val_s)
                    if b not in bad_qubits and err < 0.5:
                        two_qubit_errors[(a, b)] = err
                        two_qubit_errors[(b, a)] = err
    else:
        # Fallback nominal values when no backend or CSV is supplied
        for q in range(max(156, num_qubits)):
            readout_errors[q] = 0.004
        for q in range(max(156, num_qubits) - 1):
            two_qubit_errors[(q, q + 1)] = 0.002
            two_qubit_errors[(q + 1, q)] = 0.002

    # Build the hardware adjacency list from active two-qubit couplings
    neighbors: Dict[int, List[int]] = {}
    for (a, b) in two_qubit_errors:
        neighbors.setdefault(a, []).append(b)

    if not neighbors:
        chain = list(range(num_qubits))
        return chain, {"mean_cz_error": 0.002, "mean_readout_error": 0.004}

    def compute_cost(ch: List[int]) -> float:
        """Computes total chain error cost (sum of readout errors + sum of active link errors)."""
        return sum(readout_errors.get(q, 0.01) for q in ch) + sum(
            two_qubit_errors.get((ch[i], ch[i + 1]), 0.01) for i in range(len(ch) - 1)
        )

    best_cost = np.inf
    best_chain: Optional[List[int]] = None

    # Stage 1: Weighted random walk search
    # At each step, we bias next-hop selection toward neighbors with lower gate + readout error
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
            cost = compute_cost(chain)
            if cost < best_cost:
                best_cost = cost
                best_chain = chain

    # Stage 2: Backtracking search (DFS) for longer chains on the Heavy-Hex coupling map
    # On Heavy-Hex lattices, random walks frequently hit dead-ends for n >= 16.
    # Here we use backtracking DFS ordered by node degree and link fidelity.
    if best_chain is None:
        for relax_ro in [max_readout_error, 0.06, 0.10, 0.25]:
            # If strict 4% readout filtering disconnects the graph for n = 32 or 64,
            # we progressively relax the readout cutoff so a contiguous path can be formed.
            if relax_ro > max_readout_error:
                if backend is not None and hasattr(backend, "target"):
                    target = backend.target
                    bad_q = avoid | {q for q, err in readout_errors.items() if err > relax_ro}
                    two_qubit_errors.clear()
                    for gate_name in ["cz", "ecr", "cx"]:
                        if gate_name in target:
                            for (a, b), prop in target[gate_name].items():
                                if prop is not None and getattr(prop, "error", None) is not None:
                                    if a not in bad_q and b not in bad_q and float(prop.error) < 0.5:
                                        two_qubit_errors[(a, b)] = float(prop.error)
                                        two_qubit_errors[(b, a)] = float(prop.error)
                            break
                elif calibration_csv is not None:
                    bad_q = avoid | {q for q, err in readout_errors.items() if err > relax_ro}
                    two_qubit_errors.clear()
                    with open(calibration_csv, "r", encoding="utf-8") as f:
                        for r in csv.DictReader(f):
                            a = int(r["Qubit"])
                            if a in bad_q:
                                continue
                            for pair in r.get("CZ error", "").split(";"):
                                if ":" in pair:
                                    b_s, val_s = pair.split(":")
                                    b = int(b_s)
                                    err = float(val_s)
                                    if b not in bad_q and err < 0.5:
                                        two_qubit_errors[(a, b)] = err
                                        two_qubit_errors[(b, a)] = err
                neighbors.clear()
                for (a, b) in two_qubit_errors:
                    neighbors.setdefault(a, []).append(b)

            degrees = {u: len(nbs) for u, nbs in neighbors.items()}
            starts = sorted(neighbors.keys(), key=lambda q: (degrees.get(q, 3), readout_errors.get(q, 0.01)))

            for s in starts[:30]:
                visited = {s}
                path = [s]
                budget = [15000]  # Bound backtracking steps per starting node to keep search fast

                def dfs(u: int) -> bool:
                    nonlocal best_chain, best_cost
                    if len(path) == num_qubits:
                        c = compute_cost(path)
                        if c < best_cost:
                            best_cost = c
                            best_chain = list(path)
                        return num_qubits >= 32
                    if budget[0] <= 0:
                        return False
                    budget[0] -= 1
                    nbs = [v for v in neighbors.get(u, []) if v not in visited]
                    # Prioritize degree-2 bridge nodes first so we don't strand segments of the lattice
                    nbs.sort(key=lambda v: (
                        degrees.get(v, 3),
                        two_qubit_errors.get((u, v), 0.01) + readout_errors.get(v, 0.01)
                    ))
                    for v in nbs:
                        visited.add(v)
                        path.append(v)
                        if dfs(v):
                            return True
                        path.pop()
                        visited.remove(v)
                        if budget[0] <= 0:
                            return False
                    return False

                dfs(s)
                if best_chain is not None and num_qubits >= 32:
                    break
            if best_chain is not None:
                break

    if best_chain is None:
        best_chain = list(range(num_qubits))

    cz_list = [two_qubit_errors.get((best_chain[i], best_chain[i + 1]), 0.002) for i in range(len(best_chain) - 1)]
    ro_list = [readout_errors.get(q, 0.005) for q in best_chain]
    diag = {
        "num_qubits": num_qubits,
        "mean_cz_error": float(np.mean(cz_list)) if cz_list else 0.002,
        "mean_readout_error": float(np.mean(ro_list)) if ro_list else 0.005,
        "total_cost": float(best_cost) if np.isfinite(best_cost) else 0.0
    }
    return best_chain, diag
