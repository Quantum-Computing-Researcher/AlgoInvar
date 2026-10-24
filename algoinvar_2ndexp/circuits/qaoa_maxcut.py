"""
Quantum Approximate Optimization Algorithm (QAOA) for Graph Max-Cut.

Constructs QAOA parameterized ansatz circuits for Max-Cut problem instances on
undirected graphs G = (V, E) and prepares single-basis transversal Hadamard readouts
to evaluate global Z2 parity <P> = <prod X_u>.
"""

from typing import List, Tuple
from qiskit import QuantumCircuit


def build_qaoa_circuit(
    gamma_list: List[float],
    beta_list: List[float],
    edges: List[Tuple[int, int]] = None,
    n_qubits: int = 4,
    measure_basis: str = "X"
) -> QuantumCircuit:
    """
    Constructs a depth-p QAOA Max-Cut circuit.
    
    Initial state: |+>^n (prepared by H^n).
    Problem Hamiltonian H_C: sum_{(u,v) in E} (I - Z_u Z_v) / 2.
    Mixer Hamiltonian H_B: sum_{u in V} X_u.
    
    If measure_basis == 'X', applies terminal Hadamards to measure in the transversal
    Pauli-X basis, enabling single-basis evaluation of <P> = <prod X_u> = +1.0000.
    """
    if edges is None:
        # Default connected 4-vertex graph: line graph 0-1-2-3 with ring closure 3-0
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        
    p = len(gamma_list)
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # 1. State initialization: |+>^n
    for i in range(n_qubits):
        qc.h(i)
        
    # 2. Alternating entangling and mixer layers
    for layer in range(p):
        gamma = gamma_list[layer]
        beta = beta_list[layer]
        
        # Problem layer: exp(-i gamma Z_u Z_v)
        for u, v in edges:
            qc.rzz(2.0 * gamma, u, v)
            
        # Mixer layer: exp(-i beta X_u)
        for u in range(n_qubits):
            qc.rx(2.0 * beta, u)
            
    # 3. Readout basis rotation
    if measure_basis.upper() == "X":
        for i in range(n_qubits):
            qc.h(i)
            
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def build_qaoa_retrace_circuit(
    gamma_list: List[float],
    beta_list: List[float],
    edges: List[Tuple[int, int]] = None,
    n_qubits: int = 4
) -> QuantumCircuit:
    """
    Constructs a QAOA unitary retrace echo circuit:
    |+>^n -> U_QAOA(gamma, beta) -> U_QAOA^dagger(gamma, beta) -> |+>^n.
    Exact theoretical invariant: Return probability to |+>^n = 1.0000.
    """
    if edges is None:
        edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
        
    p = len(gamma_list)
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # 1. Initialize |+>^n
    for i in range(n_qubits):
        qc.h(i)
        
    # 2. Forward unitary U_QAOA
    for layer in range(p):
        gamma = gamma_list[layer]
        beta = beta_list[layer]
        for u, v in edges:
            qc.rzz(2.0 * gamma, u, v)
        for u in range(n_qubits):
            qc.rx(2.0 * beta, u)
            
    # 3. Inverse unitary U_QAOA^dagger (reverse order, negated parameters)
    for layer in reversed(range(p)):
        gamma = gamma_list[layer]
        beta = beta_list[layer]
        for u in reversed(range(n_qubits)):
            qc.rx(-2.0 * beta, u)
        for u, v in reversed(edges):
            qc.rzz(-2.0 * gamma, u, v)
            
    # 4. Rotate back to computational basis to test return to |0>^n
    for i in range(n_qubits):
        qc.h(i)
        
    qc.measure(range(n_qubits), range(n_qubits))
    return qc
