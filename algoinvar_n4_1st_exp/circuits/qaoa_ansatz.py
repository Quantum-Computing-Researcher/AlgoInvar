"""
QAOA Ansätze and Symmetry-Measurement Circuits.

Evaluates global Z_2 parity conservation <Prod_j X_j> = +1 and retrace fidelity.
"""

from typing import List, Optional, Tuple, Set
import networkx as nx
from qiskit import QuantumCircuit


def build_qaoa_circuit(
    num_qubits: int,
    edges: Optional[List[Tuple[int, int]]] = None,
    p: int = 1,
    gammas: Optional[List[float]] = None,
    betas: Optional[List[float]] = None,
    measurement_basis: str = "X",  # "X" for global parity invariant, "Z" for standard cost
    retrace: bool = False
) -> Tuple[QuantumCircuit, List[Tuple[int, int]], List[float], List[float]]:
    """
    Constructs a depth-p QAOA Max-Cut circuit.

    Args:
        num_qubits: Number of vertices/qubits n.
        edges: List of edges (u, v). If None, a ring graph (cycle) is used.
        p: QAOA depth.
        gammas: List of p cost unitary parameters.
        betas: List of p mixer unitary parameters.
        measurement_basis: "X" (to verify parity invariant <Prod X_i> = 1) or "Z".
        retrace: If True, appends U^dagger(gamma, beta) to test identity return.

    Returns:
        (circuit, edges, gammas, betas)
    """
    if edges is None:
        # Default: 1D ring (cycle graph)
        edges = [(i, (i + 1) % num_qubits) for i in range(num_qubits)]

    if gammas is None:
        gammas = [0.39 * (i + 1) for i in range(p)]
    if betas is None:
        betas = [0.25 * (i + 1) for i in range(p)]

    qc = QuantumCircuit(num_qubits)

    # 1. Initial state: |+>^n
    for q in range(num_qubits):
        qc.h(q)
    qc.barrier()

    # 2. Build forward QAOA unitaries U(p)
    qaoa_block = QuantumCircuit(num_qubits)
    for layer in range(p):
        gamma = gammas[layer]
        beta = betas[layer]

        # Problem unitary: e^(-i gamma Z_u Z_v)
        for u, v in edges:
            qaoa_block.rzz(2.0 * gamma, u, v)

        qaoa_block.barrier()

        # Mixer unitary: e^(-i beta X_u)
        for u in range(num_qubits):
            qaoa_block.rx(2.0 * beta, u)

        qaoa_block.barrier()

    qc.compose(qaoa_block, inplace=True)

    # 3. Retrace loop if requested
    if retrace:
        qc.barrier()
        qc.compose(qaoa_block.inverse(), inplace=True)
        qc.barrier()

    # 4. Measurement
    if measurement_basis.upper() == "X":
        # Rotate X -> Z with Hadamard gates
        for q in range(num_qubits):
            qc.h(q)

    qc.measure_all()

    return qc, edges, gammas, betas
