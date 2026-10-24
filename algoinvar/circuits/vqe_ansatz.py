"""
Particle-Conserving Givens Rotation Ansätze for VQE State Preparation.

Preserves the total particle number N = sum_j (I - Z_j)/2 and spin projection S_z.
"""

from typing import List, Optional, Tuple
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector


def build_givens_gate(circuit: QuantumCircuit, q1: int, q2: int, theta: float, phi: float = 0.0, use_native_xx_yy: bool = False):
    """
    Applies an excitation-preserving Givens rotation between qubits q1 and q2.

    Subspace action on {|01>, |10>}:
        |01> -> cos(theta/2) |01> - i e^(-i phi) sin(theta/2) |10>
        |10> -> -i e^(i phi) sin(theta/2) |01> + cos(theta/2) |10>
    Leaves |00> and |11> completely untouched.
    """
    if use_native_xx_yy:
        from qiskit.circuit.library import XXPlusYYGate
        circuit.append(XXPlusYYGate(theta, phi), [q1, q2])
    else:
        # Elementary CNOT + single-qubit gate decomposition
        # U = CNOT(q2, q1) . C-Ry . CNOT(q2, q1)
        circuit.cx(q2, q1)
        circuit.rz(-phi, q2)
        circuit.ry(-theta / 2.0, q2)
        circuit.cx(q1, q2)
        circuit.ry(theta / 2.0, q2)
        circuit.rz(phi, q2)
        circuit.cx(q2, q1)


def build_particle_conserving_vqe_circuit(
    num_qubits: int,
    num_particles: int,
    layers: int = 2,
    parameters: Optional[List[float]] = None,
    retrace: bool = False,
    initial_pattern: str = "blocked"  # "blocked" (111000) or "alternating" (101010)
) -> Tuple[QuantumCircuit, List[float]]:
    """
    Constructs a depth-L particle-conserving brickwork ansatz.

    Args:
        num_qubits: Total number of qubits n.
        num_particles: Number of occupied fermions N_e (must be <= num_qubits).
        layers: Number of entangling layers.
        parameters: Optional list of rotation angles. If None, random angles in [0, 2pi) are generated.
        retrace: If True, appends U^dagger(theta) to form a closed cyclic loop U^dagger U = I.
        initial_pattern: Layout of initial 1s and 0s.

    Returns:
        (circuit, applied_parameters)
    """
    if num_particles > num_qubits:
        raise ValueError("num_particles cannot exceed num_qubits")

    qc = QuantumCircuit(num_qubits)

    # 1. State preparation into target Fock space sector
    if initial_pattern == "blocked":
        for i in range(num_particles):
            qc.x(i)
    elif initial_pattern == "alternating":
        placed = 0
        idx = 0
        while placed < num_particles and idx < num_qubits:
            qc.x(idx)
            placed += 1
            idx += 2
        # Fill remaining if odd
        idx = 1
        while placed < num_particles and idx < num_qubits:
            qc.x(idx)
            placed += 1
            idx += 2

    qc.barrier()

    # Calculate number of two-qubit Givens gates needed
    num_gates_per_layer = (num_qubits // 2) + ((num_qubits - 1) // 2)
    total_gates = layers * num_gates_per_layer

    if parameters is None:
        rng = np.random.default_rng(42)
        angles = rng.uniform(0.1, 2.0 * np.pi, size=total_gates).tolist()
    else:
        angles = list(parameters)
        if len(angles) < total_gates:
            raise ValueError(f"Expected {total_gates} parameters, got {len(angles)}")

    # 2. Build forward layers U(theta)
    gate_idx = 0
    forward_subcirc = QuantumCircuit(num_qubits)

    for l in range(layers):
        # Even layer: (0, 1), (2, 3), ...
        for q in range(0, num_qubits - 1, 2):
            build_givens_gate(forward_subcirc, q, q + 1, angles[gate_idx])
            gate_idx += 1

        # Odd layer: (1, 2), (3, 4), ...
        for q in range(1, num_qubits - 1, 2):
            build_givens_gate(forward_subcirc, q, q + 1, angles[gate_idx])
            gate_idx += 1

        forward_subcirc.barrier()

    qc.compose(forward_subcirc, inplace=True)

    # 3. If retrace requested, append U^dagger
    if retrace:
        qc.barrier()
        qc.compose(forward_subcirc.inverse(), inplace=True)
        qc.barrier()

    # 4. Measure all qubits in Z-basis
    qc.measure_all()

    return qc, angles
