"""
Circuit Construction Module for AlgoInvar Register-Width Scaling.

We use `build_algoinvar_benchmark_circuits` from `algoinvar.hardware.ibm_runner`
so that every register width n = 4, 8, 12, 16, 32, 64 runs the same 5-circuit
suite with fixed variational seed (42), particle number (N_e = 2), and layer depths.
"""

import os
import sys
from typing import List, Tuple
from qiskit import QuantumCircuit

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from algoinvar_n4_1st_exp.hardware.ibm_runner import build_algoinvar_benchmark_circuits
except ImportError:
    from algoinvar.hardware.ibm_runner import build_algoinvar_benchmark_circuits


def build_exact_5_circuits_for_width(num_qubits: int) -> List[Tuple[str, QuantumCircuit]]:
    """
    Constructs the standard suite of 5 algorithmic invariant circuits for width `num_qubits`:
    1. vqe_particle_l2: VQE depth-2 Givens network (Z-basis, N_e = 2)
    2. vqe_retrace:     VQE depth-2 forward + inverse U^dagger U echo (Z-basis)
    3. qaoa_parity_p1:  QAOA depth-1 global Z2 parity on 1D ring graph (X-basis)
    4. qaoa_parity_p2:  QAOA depth-2 global Z2 parity on 1D ring graph (X-basis)
    5. qaoa_retrace_p2: QAOA depth-2 forward + inverse U^dagger U echo (X-basis)
    """
    return build_algoinvar_benchmark_circuits(num_qubits=num_qubits)
