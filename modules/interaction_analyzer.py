"""
interaction_analyzer.py
=========================
Analyzes drug-drug interaction by comparing ground state energies.

The core physics principle:
  If two molecules A and B interact, their combined energy E(AB)
  will differ from the sum of their isolated energies E(A) + E(B).

  Interaction Energy (ΔE) = E(AB) - [E(A) + E(B)]

  - ΔE ≈ 0         → Molecules don't significantly interact → SAFE
  - ΔE slightly negative  → Mild binding/interaction → CAUTION
  - ΔE strongly negative  → Strong binding/reaction → DANGEROUS

In real quantum chemistry:
  - Negative ΔE means the combined system is MORE stable (energy released)
  - This indicates strong molecular binding — potentially altering drug effects
  - Large negative ΔE could indicate one drug inhibiting/amplifying the other
"""


# Thresholds (in Hartree — 1 Hartree ≈ 627.5 kcal/mol)
# These are tuned for the simplified simulation in this project.
# Real thresholds would be determined through experimental calibration.
SAFE_THRESHOLD      = -0.005   # Less than 3.1 kcal/mol interaction
CAUTION_THRESHOLD   = -0.020   # 3.1 to 12.6 kcal/mol interaction
# Anything beyond CAUTION_THRESHOLD is classified as DANGEROUS


def analyze_interaction(
    energy_drug1: float,
    energy_drug2: float,
    energy_combined: float
) -> float:
    """
    Calculate interaction energy between two drug molecules.

    Args:
        energy_drug1 (float):    Ground state energy of Drug 1 (Hartree)
        energy_drug2 (float):    Ground state energy of Drug 2 (Hartree)
        energy_combined (float): Ground state energy of combined system (Hartree)

    Returns:
        float: Interaction energy ΔE (Hartree)
    """
    delta_e = energy_combined - (energy_drug1 + energy_drug2)
    return delta_e


def get_risk_level(interaction_energy: float) -> tuple[str, str, str]:
    """
    Classify the drug interaction risk based on interaction energy.

    Args:
        interaction_energy (float): ΔE in Hartree

    Returns:
        tuple: (risk_level, risk_label, explanation)
               risk_level is one of: "SAFE", "CAUTION", "DANGEROUS"
    """
    ie_kcal = interaction_energy * 627.5  # Convert to kcal/mol for intuition

    if interaction_energy > SAFE_THRESHOLD:
        return (
            "SAFE",
            "✅ Low Interaction Risk",
            f"The calculated interaction energy (ΔE = {ie_kcal:.2f} kcal/mol) "
            "is very small, suggesting these drugs do not significantly bind "
            "to each other at the quantum level. The combination appears safe "
            "from an energy standpoint. Always verify with a pharmacist."
        )

    elif interaction_energy > CAUTION_THRESHOLD:
        return (
            "CAUTION",
            "⚠️ Moderate Interaction Detected",
            f"The calculated interaction energy (ΔE = {ie_kcal:.2f} kcal/mol) "
            "indicates a moderate molecular interaction. These drugs may "
            "compete for binding sites or influence each other's metabolism. "
            "Consult a healthcare professional before combining these drugs."
        )

    else:
        return (
            "DANGEROUS",
            "🚨 Strong Interaction Warning",
            f"The calculated interaction energy (ΔE = {ie_kcal:.2f} kcal/mol) "
            "indicates a significant quantum-level interaction between these "
            "molecules. This may indicate binding competition, enzyme "
            "inhibition, or synergistic toxicity. Do NOT combine without "
            "direct supervision from a qualified medical professional."
        )