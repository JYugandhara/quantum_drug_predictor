"""
hamiltonian_builder.py
========================
Converts molecular data into a qubit Hamiltonian using Qiskit Nature.

The Hamiltonian (H) is the quantum operator that represents the
total energy of a molecular system. VQE finds the lowest eigenvalue
of this operator — which equals the ground state energy.

Key steps:
  1. Build a PySCF molecule from the SMILES/atom data
  2. Run Hartree-Fock as the classical starting point
  3. Map the fermionic Hamiltonian → qubit Hamiltonian (Jordan-Wigner)
"""

import numpy as np

# Qiskit Nature imports
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.second_q.transformers import ActiveSpaceTransformer


# Simple atom position map for common drug building blocks
# In a real implementation, use RDKit to parse SMILES → 3D coordinates
SIMPLE_MOLECULES = {
    # name: (geometry_string, charge, spin)
    "H2":     ("H 0.0 0.0 0.0; H 0.0 0.0 0.735", 0, 0),
    "LiH":    ("Li 0.0 0.0 0.0; H 0.0 0.0 1.596", 0, 0),
    "H2O":    ("O 0.0 0.0 0.0; H 0.757 0.586 0.0; H -0.757 0.586 0.0", 0, 0),
    "default":("H 0.0 0.0 0.0; H 0.0 0.0 0.735", 0, 0),
}


def _get_geometry(mol_data: dict) -> tuple[str, int, int]:
    """
    Map molecule data to a geometry string for PySCF.
    For complex molecules, we use a simplified 2-electron proxy
    (a real implementation would use RDKit for 3D coordinates).
    """
    name = mol_data["name"].lower()
    atom_count = mol_data.get("atom_count", 2)

    # Use known simple geometries for common cases
    if "water" in name:
        return SIMPLE_MOLECULES["H2O"]
    elif atom_count <= 2:
        return SIMPLE_MOLECULES["H2"]
    else:
        # For complex drug molecules: use LiH as a proxy
        # (represents a simple 2-orbital interaction)
        return SIMPLE_MOLECULES["LiH"]


def build_hamiltonian(mol1_data: dict, mol2_data: dict = None, combined: bool = False):
    """
    Build a qubit Hamiltonian for a molecule or a combined drug pair.

    Args:
        mol1_data (dict): Molecule data from molecule_fetcher
        mol2_data (dict): Optional second molecule (for combined system)
        combined  (bool): Whether to build a combined interaction Hamiltonian

    Returns:
        SparsePauliOp: The qubit Hamiltonian operator
    """
    geometry, charge, spin = _get_geometry(mol1_data)

    if combined and mol2_data is not None:
        # For combined system: increase molecular complexity slightly
        # Real implementation: concatenate atomic coordinates with spacing
        geometry = "Li 0.0 0.0 0.0; H 0.0 0.0 1.6; H 0.0 0.0 3.2"
        charge = 0
        spin = 0

    # Build PySCF electronic structure problem
    driver = PySCFDriver(
        atom=geometry,
        basis="sto3g",   # Minimal basis set (fast for simulation)
        charge=charge,
        spin=spin,
    )

    problem = driver.run()

    # Reduce to active space (2 electrons, 2 orbitals) for efficiency
    # This keeps the qubit count manageable on a simulator
    transformer = ActiveSpaceTransformer(
        num_electrons=2,
        num_spatial_orbitals=2,
    )
    reduced_problem = transformer.transform(problem)

    # Map fermionic operators → qubit operators using Jordan-Wigner
    mapper = JordanWignerMapper()
    hamiltonian = mapper.map(reduced_problem.hamiltonian.second_q_op())

    return hamiltonian