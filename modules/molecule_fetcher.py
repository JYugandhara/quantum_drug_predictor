"""
molecule_fetcher.py
====================
Fetches drug molecule data from the PubChem public API.
Returns molecular formula, weight, SMILES string, and atom count.

PubChem API Docs: https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest
"""

import requests


PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


def fetch_molecule_data(drug_name: str) -> dict | None:
    """
    Fetch molecule data for a given drug name from PubChem.

    Args:
        drug_name (str): Common drug name e.g. "Aspirin", "Warfarin"

    Returns:
        dict with keys: name, formula, weight, smiles, atom_count
        Returns None if drug not found.
    """
    try:
        # Step 1: Get CID (Compound ID) from drug name
        cid_url = f"{PUBCHEM_BASE}/compound/name/{drug_name}/cids/JSON"
        cid_resp = requests.get(cid_url, timeout=10)

        if cid_resp.status_code != 200:
            return None

        cid = cid_resp.json()["IdentifierList"]["CID"][0]

        # Step 2: Fetch molecular properties using CID
        props_url = (
            f"{PUBCHEM_BASE}/compound/cid/{cid}/property/"
            f"MolecularFormula,MolecularWeight,IsomericSMILES,HeavyAtomCount/JSON"
        )
        props_resp = requests.get(props_url, timeout=10)

        if props_resp.status_code != 200:
            return None

        props = props_resp.json()["PropertyTable"]["Properties"][0]

        return {
            "name": drug_name,
            "cid": cid,
            "formula": props.get("MolecularFormula", "N/A"),
            "weight": props.get("MolecularWeight", 0.0),
            "smiles": props.get("IsomericSMILES", ""),
            "atom_count": props.get("HeavyAtomCount", 0),
        }

    except (requests.RequestException, KeyError, IndexError):
        return None