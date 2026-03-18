"""
vqe_solver.py
==============
Implements the Variational Quantum Eigensolver (VQE) algorithm
with convergence history tracking.

VQE is a hybrid quantum-classical algorithm:
  - Quantum part:  Prepares a parameterized ansatz state |ψ(θ)⟩
                   and measures expectation value ⟨ψ(θ)|H|ψ(θ)⟩
  - Classical part: Optimizer minimizes the measured energy by
                   updating parameters θ each iteration

The convergence history records energy at every optimizer step —
showing how VQE descends toward the ground state.
"""

import numpy as np

from qiskit.circuit.library import TwoLocal
from qiskit.primitives import StatevectorEstimator
from qiskit_algorithms import VQE, NumPyMinimumEigensolver
from qiskit_algorithms.optimizers import COBYLA, SPSA, L_BFGS_B


OPTIMIZERS = {
    "COBYLA":   COBYLA,
    "SPSA":     SPSA,
    "L-BFGS-B": L_BFGS_B,
}


def run_vqe(hamiltonian, optimizer: str = "COBYLA", max_iter: int = 150) -> tuple:
    """
    Run VQE to find the ground state energy of the given Hamiltonian.

    Args:
        hamiltonian:  SparsePauliOp qubit Hamiltonian
        optimizer:    Classical optimizer name (COBYLA / SPSA / L-BFGS-B)
        max_iter:     Maximum optimizer iterations

    Returns:
        tuple: (ground_state_energy: float, convergence_history: list[float])
    """
    num_qubits = hamiltonian.num_qubits
    convergence_history = []

    # TwoLocal ansatz — rotation + entanglement layers
    ansatz = TwoLocal(
        num_qubits=num_qubits,
        rotation_blocks=["ry", "rz"],
        entanglement_blocks="cx",
        entanglement="linear",
        reps=2,
        insert_barriers=True,
    )

    optimizer_cls = OPTIMIZERS.get(optimizer, COBYLA)
    opt = optimizer_cls(maxiter=max_iter)
    estimator = StatevectorEstimator()

    # Callback records energy at every optimizer evaluation
    def callback(eval_count, params, value, meta=None):
        convergence_history.append(float(np.real(value)))

    vqe = VQE(
        estimator=estimator,
        ansatz=ansatz,
        optimizer=opt,
        callback=callback,
    )

    result = vqe.compute_minimum_eigenvalue(hamiltonian)
    return float(np.real(result.eigenvalue)), convergence_history


def run_exact(hamiltonian) -> float:
    """Classical exact solver for validation."""
    solver = NumPyMinimumEigensolver()
    result = solver.compute_minimum_eigenvalue(hamiltonian)
    return float(np.real(result.eigenvalue))