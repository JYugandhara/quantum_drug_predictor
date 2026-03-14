"""
vqe_solver.py
==============
Implements the Variational Quantum Eigensolver (VQE) algorithm.

VQE is a hybrid quantum-classical algorithm:
  - Quantum part:  Prepares a parameterized quantum state (ansatz)
                   and measures the expectation value of the Hamiltonian
  - Classical part: An optimizer adjusts the ansatz parameters
                   to minimize the measured energy

The ground state energy is the minimum eigenvalue of the Hamiltonian.
This equals the most stable electronic configuration of the molecule.

Why VQE?
  - Quantum Phase Estimation (QPE) needs millions of gates (too deep)
  - VQE uses shallow circuits — works on today's noisy quantum hardware
  - Perfect for near-term quantum chemistry problems
"""

import numpy as np

from qiskit.circuit.library import TwoLocal
from qiskit.primitives import StatevectorEstimator
from qiskit_algorithms import VQE, NumPyMinimumEigensolver
from qiskit_algorithms.optimizers import COBYLA, SPSA, L_BFGS_B


# Map string names to Qiskit optimizer classes
OPTIMIZERS = {
    "COBYLA":    COBYLA,
    "SPSA":      SPSA,
    "L-BFGS-B":  L_BFGS_B,
}


def run_vqe(hamiltonian, optimizer: str = "COBYLA", max_iter: int = 150) -> float:
    """
    Run VQE to find the ground state energy of the given Hamiltonian.

    Args:
        hamiltonian:  SparsePauliOp qubit Hamiltonian
        optimizer:    Classical optimizer name (COBYLA / SPSA / L-BFGS-B)
        max_iter:     Maximum optimizer iterations

    Returns:
        float: Ground state energy in Hartree
    """
    num_qubits = hamiltonian.num_qubits

    # Build ansatz: TwoLocal is a hardware-efficient parametric circuit
    # It alternates rotation layers (Ry, Rz) and entanglement (CNOT) layers
    ansatz = TwoLocal(
        num_qubits=num_qubits,
        rotation_blocks=["ry", "rz"],
        entanglement_blocks="cx",
        entanglement="linear",
        reps=2,                    # 2 repetitions of rotation + entanglement
        insert_barriers=True,
    )

    # Choose optimizer
    optimizer_cls = OPTIMIZERS.get(optimizer, COBYLA)
    opt = optimizer_cls(maxiter=max_iter)

    # Use StatevectorEstimator for exact simulation (no noise)
    estimator = StatevectorEstimator()

    # Build and run VQE
    vqe = VQE(
        estimator=estimator,
        ansatz=ansatz,
        optimizer=opt,
    )

    result = vqe.compute_minimum_eigenvalue(hamiltonian)
    return float(np.real(result.eigenvalue))


def run_exact(hamiltonian) -> float:
    """
    Classical exact solver — used for comparison/validation.
    Finds the true minimum eigenvalue (only practical for small systems).

    Args:
        hamiltonian: SparsePauliOp qubit Hamiltonian

    Returns:
        float: Exact ground state energy in Hartree
    """
    solver = NumPyMinimumEigensolver()
    result = solver.compute_minimum_eigenvalue(hamiltonian)
    return float(np.real(result.eigenvalue))