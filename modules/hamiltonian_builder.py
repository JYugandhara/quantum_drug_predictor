"""
hamiltonian_builder.py
========================
Builds a qubit Hamiltonian WITHOUT PySCF (Windows compatible).
Uses Qiskit's SparsePauliOp to directly construct
molecular Hamiltonians parameterized by drug properties.

Each drug gets a unique Hamiltonian based on:
  - Molecular weight  → energy scale
  - Atom count        → interaction complexity
  - Formula           → unique molecular fingerprint
"""

import numpy as np
from qiskit.quantum_info import SparsePauliOp


def _mol_fingerprint(mol_data: dict) -> float:
    """Generate a unique float fingerprint from molecular formula."""
    formula = mol_data.get("formula", "H2")
    weight  = float(mol_data.get("weight", 2.0))
    atoms   = int(mol_data.get("atom_count", 1))
    formula_hash = sum(ord(c) * (i + 1) for i, c in enumerate(formula))
    return (formula_hash % 1000) / 10000.0 + weight / 10000.0 + atoms / 1000.0


def _build_single_hamiltonian(mol_data: dict) -> SparsePauliOp:
    """
    Build a 2-qubit Hamiltonian for a single molecule.
    Coefficients are scaled by molecular properties so
    each drug produces a unique energy landscape.
    """
    fp = _mol_fingerprint(mol_data)
    weight = float(mol_data.get("weight", 2.0))
    atoms  = int(mol_data.get("atom_count", 1))

    scale = -weight / 500.0

    h = SparsePauliOp.from_list([
        ("ZZ", scale * (1.0 + fp)),
        ("ZI", scale * 0.5 * (1.0 + atoms / 20.0)),
        ("IZ", scale * 0.3 * (1.0 + fp * 2)),
        ("XX", scale * 0.2 * (1.0 - fp)),
        ("YY", scale * 0.15),
        ("IX", scale * 0.1 * fp),
    ])
    return h


def _build_combined_hamiltonian(mol1_data: dict, mol2_data: dict) -> SparsePauliOp:
    """
    Build a 2-qubit Hamiltonian for the combined drug system.
    """
    fp1 = _mol_fingerprint(mol1_data)
    fp2 = _mol_fingerprint(mol2_data)

    w1 = float(mol1_data.get("weight", 2.0))
    w2 = float(mol2_data.get("weight", 2.0))
    a1 = int(mol1_data.get("atom_count", 1))
    a2 = int(mol2_data.get("atom_count", 1))

    scale = -(w1 + w2) / 1000.0
    interaction = abs(fp1 - fp2) + abs(a1 - a2) / 50.0

    h = SparsePauliOp.from_list([
        ("ZZ", scale * (1.0 + interaction)),
        ("ZI", scale * 0.5 * (1.0 + fp1)),
        ("IZ", scale * 0.5 * (1.0 + fp2)),
        ("XX", scale * 0.3 * (1.0 + interaction * 1.5)),
        ("YY", scale * 0.25 * (1.0 + interaction)),
        ("XI", scale * 0.15 * fp1),
        ("IX", scale * 0.15 * fp2),
        ("ZX", scale * 0.1 * interaction),
        ("XZ", scale * 0.1 * interaction),
    ])
    return h


def build_hamiltonian(mol1_data: dict, mol2_data: dict = None, combined: bool = False) -> SparsePauliOp:
    """
    Main entry point — builds Hamiltonian for single or combined drug system.

    Args:
        mol1_data (dict): Molecule data from molecule_fetcher
        mol2_data (dict): Optional second molecule (for combined system)
        combined  (bool): If True, builds combined interaction Hamiltonian

    Returns:
        SparsePauliOp: The qubit Hamiltonian operator
    """
    if combined and mol2_data is not None:
        return _build_combined_hamiltonian(mol1_data, mol2_data)
    return _build_single_hamiltonian(mol1_data)