"""
interaction_analyzer.py
=========================
Hybrid drug interaction analyzer combining:
  1. Quantum Energy Model  — VQE-computed ΔE for direct molecular binding
  2. Clinical Pathway DB   — Known pharmacodynamic/pharmacokinetic interactions
  3. CYP450 Enzyme DB      — Metabolic enzyme competition interactions

Detection Methods:
  ┌─────────────────────────────────────────────────────┐
  │  LAYER 1: Clinical Pathway Override (highest trust) │
  │  LAYER 2: CYP450 Enzyme Interaction Check           │
  │  LAYER 3: Quantum ΔE Energy Model (base layer)      │
  └─────────────────────────────────────────────────────┘

Interaction Energy:
  ΔE = E(AB) − [E(A) + E(B)]
  Negative ΔE → molecules attract → potential binding risk
"""


# ── Thresholds (Hartree) ─────────────────────────────────────────────────────
# 1 Hartree = 627.5 kcal/mol
SAFE_THRESHOLD    = -0.005   # < 3.1 kcal/mol
CAUTION_THRESHOLD = -0.020   # 3.1 – 12.6 kcal/mol
# Beyond CAUTION_THRESHOLD → DANGEROUS


# ── LAYER 1: Clinical Pathway Database ───────────────────────────────────────
# Covers pharmacodynamic interactions that quantum energy CANNOT detect:
#   - Shared receptor/enzyme pathways
#   - Synergistic/antagonistic physiological effects
#   - Known fatal combinations from clinical literature
#
# Format: frozenset({drug_a, drug_b}) → (risk, mechanism, explanation)

PATHWAY_DB = {

    # ── cGMP / Nitric Oxide Pathway ──────────────────────────────────────────
    frozenset({"sildenafil", "isosorbide"}): (
        "DANGEROUS",
        "Shared cGMP Pathway — Hypotensive Crisis",
        "Both drugs massively amplify the cGMP signaling pathway causing "
        "catastrophic blood pressure drop (severe hypotension). "
        "Sildenafil inhibits PDE5 (preventing cGMP breakdown) while "
        "Isosorbide releases nitric oxide (triggering cGMP production). "
        "Combined effect can be fatal. Over 123 deaths reported. "
        "This is a pharmacodynamic interaction — not detectable by quantum "
        "binding energy alone. NEVER combine these drugs."
    ),
    frozenset({"sildenafil", "nitroglycerin"}): (
        "DANGEROUS",
        "Shared cGMP Pathway — Hypotensive Crisis",
        "Sildenafil (PDE5 inhibitor) combined with Nitroglycerin (nitrate) "
        "causes catastrophic synergistic vasodilation via the NO/cGMP pathway. "
        "Results in severe, potentially fatal hypotension. Absolutely contraindicated."
    ),
    frozenset({"tadalafil", "nitroglycerin"}): (
        "DANGEROUS",
        "Shared cGMP Pathway — Hypotensive Crisis",
        "PDE5 inhibitor + nitrate = fatal synergistic hypotension via cGMP pathway."
    ),
    frozenset({"tadalafil", "isosorbide"}): (
        "DANGEROUS",
        "Shared cGMP Pathway — Hypotensive Crisis",
        "PDE5 inhibitor + long-acting nitrate = fatal blood pressure crash. Contraindicated."
    ),

    # ── Serotonin Syndrome ────────────────────────────────────────────────────
    frozenset({"fluoxetine", "tramadol"}): (
        "DANGEROUS",
        "Serotonin Syndrome — Dual Serotonergic Overload",
        "Fluoxetine (SSRI) blocks serotonin reuptake while Tramadol also "
        "inhibits serotonin reuptake AND weakly activates serotonin receptors. "
        "Combined effect causes Serotonin Syndrome: agitation, rapid heart rate, "
        "high fever, muscle rigidity — potentially fatal within hours."
    ),
    frozenset({"sertraline", "tramadol"}): (
        "DANGEROUS",
        "Serotonin Syndrome — Dual Serotonergic Overload",
        "SSRI + opioid with serotonergic activity = high risk of serotonin syndrome. "
        "Can cause hyperthermia, seizures, and death."
    ),
    frozenset({"paroxetine", "tramadol"}): (
        "DANGEROUS",
        "Serotonin Syndrome + CYP2D6 Inhibition",
        "Paroxetine is a strong CYP2D6 inhibitor AND an SSRI — double danger: "
        "it raises tramadol blood levels AND triggers serotonin syndrome."
    ),
    frozenset({"phenelzine", "tramadol"}): (
        "DANGEROUS",
        "MAOI + Serotonergic Drug — Fatal Serotonin Syndrome",
        "MAO inhibitor + serotonergic opioid = extreme serotonin crisis. Absolutely contraindicated."
    ),
    frozenset({"phenelzine", "fluoxetine"}): (
        "DANGEROUS",
        "MAOI + SSRI — Fatal Serotonin Syndrome",
        "Combining MAOI with SSRI causes extreme serotonin accumulation — "
        "hyperthermia, seizures, cardiovascular collapse, death."
    ),

    # ── Anticoagulant Interactions ────────────────────────────────────────────
    frozenset({"warfarin", "aspirin"}): (
        "DANGEROUS",
        "Dual Anticoagulation — Severe Bleeding Risk",
        "Warfarin (vitamin K antagonist) + Aspirin (platelet inhibitor + GI irritant) "
        "causes synergistic bleeding risk. GI hemorrhage risk increases 15-fold. "
        "Can cause fatal internal bleeding. Requires very close medical supervision."
    ),
    frozenset({"warfarin", "ibuprofen"}): (
        "DANGEROUS",
        "NSAID Potentiates Anticoagulation — GI Bleeding",
        "Ibuprofen inhibits platelet function and damages GI mucosa while warfarin "
        "prevents clotting. Combined risk of fatal GI hemorrhage is very high."
    ),
    frozenset({"warfarin", "clarithromycin"}): (
        "DANGEROUS",
        "CYP3A4 Inhibition — Warfarin Toxicity",
        "Clarithromycin strongly inhibits CYP3A4, blocking warfarin metabolism "
        "and causing dangerous warfarin accumulation. INR can spike to fatal levels "
        "within 48-72 hours causing cerebral hemorrhage."
    ),
    frozenset({"warfarin", "metronidazole"}): (
        "DANGEROUS",
        "CYP2C9 Inhibition — Warfarin Toxicity",
        "Metronidazole inhibits CYP2C9, preventing warfarin breakdown. "
        "Warfarin levels can triple, causing life-threatening bleeding."
    ),

    # ── Cardiac Interactions ──────────────────────────────────────────────────
    frozenset({"digoxin", "amiodarone"}): (
        "DANGEROUS",
        "P-glycoprotein Inhibition — Digoxin Toxicity",
        "Amiodarone inhibits P-gp and CYP3A4, dramatically increasing digoxin "
        "plasma concentration. Digoxin has a narrow therapeutic index — "
        "toxicity causes fatal arrhythmias, heart block, and cardiac arrest."
    ),
    frozenset({"digoxin", "quinidine"}): (
        "DANGEROUS",
        "P-glycoprotein Inhibition — Digoxin Toxicity",
        "Quinidine doubles digoxin blood levels by inhibiting its renal excretion. "
        "Digoxin toxicity causes life-threatening ventricular arrhythmias."
    ),
    frozenset({"clonidine", "propranolol"}): (
        "DANGEROUS",
        "Rebound Hypertension — Fatal Crisis on Withdrawal",
        "If clonidine is stopped while taking propranolol (beta-blocker), "
        "severe rebound hypertension occurs that the beta-blocker worsens. "
        "Can cause hypertensive crisis, stroke, and death."
    ),

    # ── Hyperkalemia ──────────────────────────────────────────────────────────
    frozenset({"spironolactone", "lisinopril"}): (
        "DANGEROUS",
        "Dual Potassium Retention — Life-threatening Hyperkalemia",
        "Spironolactone (potassium-sparing diuretic) + Lisinopril (ACE inhibitor) "
        "both raise potassium levels. Combined hyperkalemia causes fatal cardiac "
        "arrhythmias — heart can stop without warning."
    ),
    frozenset({"lisinopril", "potassium"}): (
        "DANGEROUS",
        "ACE Inhibitor + Potassium Supplement — Hyperkalemia",
        "ACE inhibitors already raise potassium. Adding potassium supplements "
        "causes dangerous hyperkalemia — cardiac arrest risk."
    ),

    # ── CNS / Respiratory Depression ─────────────────────────────────────────
    frozenset({"oxycodone", "alprazolam"}): (
        "DANGEROUS",
        "CNS + Respiratory Depression — Overdose Death Risk",
        "Opioid + benzodiazepine combination causes synergistic CNS and "
        "respiratory depression. This combination is responsible for the "
        "majority of opioid overdose deaths in the US."
    ),
    frozenset({"morphine", "diazepam"}): (
        "DANGEROUS",
        "Opioid + Benzodiazepine — Respiratory Arrest",
        "Synergistic CNS depression causes respiratory arrest. "
        "Fatal at relatively low doses of each drug."
    ),

    # ── Methotrexate Toxicity ─────────────────────────────────────────────────
    frozenset({"methotrexate", "ibuprofen"}): (
        "DANGEROUS",
        "Renal Clearance Inhibition — Methotrexate Toxicity",
        "NSAIDs reduce renal blood flow, blocking methotrexate excretion. "
        "Methotrexate accumulates to toxic levels causing bone marrow "
        "suppression, mucositis, and potentially fatal organ failure."
    ),

    # ── Moderate / Caution Pairs ─────────────────────────────────────────────
    frozenset({"ciprofloxacin", "theophylline"}): (
        "CAUTION",
        "CYP1A2 Inhibition — Theophylline Toxicity",
        "Ciprofloxacin inhibits CYP1A2, reducing theophylline clearance by "
        "up to 30%. Theophylline toxicity causes nausea, tremors, seizures. "
        "Theophylline dose should be reduced when co-prescribing."
    ),
    frozenset({"omeprazole", "clopidogrel"}): (
        "CAUTION",
        "CYP2C19 Competition — Reduced Antiplatelet Effect",
        "Omeprazole inhibits CYP2C19, which activates clopidogrel into its "
        "active form. Clopidogrel loses up to 40% of its antiplatelet effect "
        "increasing risk of heart attack and stroke in high-risk patients."
    ),
    frozenset({"metformin", "contrast"}): (
        "CAUTION",
        "Renal Impairment — Lactic Acidosis Risk",
        "Iodinated contrast media can cause acute kidney injury. "
        "Metformin accumulates in renal failure causing lactic acidosis."
    ),
    frozenset({"lithium", "ibuprofen"}): (
        "CAUTION",
        "Reduced Renal Clearance — Lithium Toxicity",
        "NSAIDs reduce prostaglandin-mediated renal blood flow, "
        "decreasing lithium excretion. Lithium toxicity causes tremors, "
        "confusion, kidney damage. Monitor lithium levels closely."
    ),
    frozenset({"simvastatin", "amiodarone"}): (
        "CAUTION",
        "CYP3A4 Inhibition — Statin Myopathy Risk",
        "Amiodarone inhibits CYP3A4, raising simvastatin blood levels. "
        "Risk of myopathy and rhabdomyolysis (muscle breakdown)."
    ),

    # ── Safe Combinations ─────────────────────────────────────────────────────
    frozenset({"caffeine", "paracetamol"}): (
        "SAFE",
        "Synergistic Analgesia — Clinically Approved Combination",
        "Caffeine + Paracetamol (acetaminophen) is a well-studied combination "
        "sold commercially (e.g. Panadol Extra). Caffeine enhances paracetamol's "
        "analgesic effect by 40%. No significant safety concerns at standard doses."
    ),
    frozenset({"caffeine", "acetaminophen"}): (
        "SAFE",
        "Synergistic Analgesia — Clinically Approved Combination",
        "Caffeine enhances acetaminophen analgesic efficacy. Commercially "
        "combined in many OTC pain relievers. Safe at recommended doses."
    ),
    frozenset({"amoxicillin", "paracetamol"}): (
        "SAFE",
        "No Known Significant Interaction",
        "Amoxicillin and paracetamol have different metabolic pathways with "
        "no clinically significant pharmacokinetic or pharmacodynamic interactions."
    ),
}


# ── LAYER 2: CYP450 Enzyme Interaction Database ───────────────────────────────
# Tracks which drugs inhibit or are substrates of CYP enzymes
# If Drug A inhibits an enzyme that metabolizes Drug B → CAUTION/DANGEROUS

CYP_INHIBITORS = {
    "CYP3A4": ["clarithromycin", "erythromycin", "ketoconazole", "itraconazole",
               "ritonavir", "amiodarone", "verapamil", "diltiazem"],
    "CYP2C9": ["fluconazole", "amiodarone", "metronidazole", "miconazole",
               "sulfinpyrazone", "trimethoprim"],
    "CYP2C19":["omeprazole", "esomeprazole", "fluoxetine", "fluvoxamine",
               "ticlopidine", "cimetidine"],
    "CYP2D6": ["fluoxetine", "paroxetine", "bupropion", "quinidine",
               "amiodarone", "haloperidol"],
    "CYP1A2": ["ciprofloxacin", "fluvoxamine", "enoxacin", "mexiletine"],
}

CYP_SUBSTRATES = {
    "CYP3A4": ["warfarin", "simvastatin", "atorvastatin", "midazolam",
               "alprazolam", "sildenafil", "tadalafil", "cyclosporine"],
    "CYP2C9": ["warfarin", "phenytoin", "celecoxib", "losartan",
               "glipizide", "ibuprofen"],
    "CYP2C19":["clopidogrel", "diazepam", "omeprazole", "phenytoin",
               "voriconazole"],
    "CYP2D6": ["tramadol", "codeine", "metoprolol", "timolol",
               "haloperidol", "risperidone"],
    "CYP1A2": ["theophylline", "caffeine", "clozapine", "olanzapine",
               "tacrine"],
}


def _check_cyp_interaction(drug1: str, drug2: str) -> tuple | None:
    """
    Check if either drug inhibits the CYP enzyme that metabolizes the other.
    Returns a CAUTION tuple if found, None otherwise.
    """
    d1 = drug1.lower()
    d2 = drug2.lower()

    for enzyme, inhibitors in CYP_INHIBITORS.items():
        substrates = CYP_SUBSTRATES.get(enzyme, [])
        if d1 in inhibitors and d2 in substrates:
            return (
                "CAUTION",
                f"CYP Enzyme Interaction — {enzyme} Inhibition",
                f"{drug1} inhibits the {enzyme} enzyme that metabolizes {drug2}. "
                f"This can raise {drug2} blood levels significantly, "
                f"potentially causing toxicity. Monitor closely and consider "
                f"dose adjustment. Detected via CYP450 metabolic pathway analysis."
            )
        if d2 in inhibitors and d1 in substrates:
            return (
                "CAUTION",
                f"CYP Enzyme Interaction — {enzyme} Inhibition",
                f"{drug2} inhibits the {enzyme} enzyme that metabolizes {drug1}. "
                f"This can raise {drug1} blood levels significantly, "
                f"potentially causing toxicity. Monitor closely and consider "
                f"dose adjustment. Detected via CYP450 metabolic pathway analysis."
            )
    return None


# ── Public API ────────────────────────────────────────────────────────────────

def analyze_interaction(e1: float, e2: float, ecomb: float) -> float:
    """Calculate interaction energy ΔE = E(AB) − [E(A) + E(B)]"""
    return ecomb - (e1 + e2)


def get_risk_level(
    interaction_energy: float,
    drug1: str = "",
    drug2: str = ""
) -> tuple[str, str, str, str]:
    """
    Hybrid risk classification using 3-layer detection.

    Args:
        interaction_energy: ΔE in Hartree from VQE
        drug1: Name of first drug (for pathway lookup)
        drug2: Name of second drug (for pathway lookup)

    Returns:
        tuple: (risk_level, risk_label, explanation, detection_method)
               detection_method: "CLINICAL" | "CYP450" | "QUANTUM"
    """
    ie_kcal = interaction_energy * 627.5
    key = frozenset({drug1.lower(), drug2.lower()})

    # ── LAYER 1: Clinical Pathway Override ───────────────────────────────────
    if key in PATHWAY_DB:
        risk, mechanism, explanation = PATHWAY_DB[key]
        label_map = {
            "DANGEROUS": "🚨 Clinically Dangerous Interaction",
            "CAUTION":   "⚠️ Clinically Significant Interaction",
            "SAFE":      "✅ Clinically Verified Safe Combination",
        }
        full_explanation = (
            f"[Mechanism: {mechanism}]\n\n{explanation}\n\n"
            f"Quantum ΔE = {ie_kcal:.2f} kcal/mol (supplementary data)."
        )
        return (risk, label_map[risk], full_explanation, "CLINICAL")

    # ── LAYER 2: CYP450 Enzyme Interaction ───────────────────────────────────
    if drug1 and drug2:
        cyp_result = _check_cyp_interaction(drug1, drug2)
        if cyp_result:
            risk, mechanism, explanation = cyp_result
            full_explanation = (
                f"[Mechanism: {mechanism}]\n\n{explanation}\n\n"
                f"Quantum ΔE = {ie_kcal:.2f} kcal/mol (supplementary data)."
            )
            return (risk, f"⚠️ {mechanism}", full_explanation, "CYP450")

    # ── LAYER 3: Quantum ΔE Model ─────────────────────────────────────────────
    if interaction_energy > SAFE_THRESHOLD:
        return (
            "SAFE",
            "✅ Low Quantum Interaction",
            f"Quantum simulation shows low molecular binding energy "
            f"(ΔE = {ie_kcal:.2f} kcal/mol). No significant direct molecular "
            f"interaction detected. No known clinical pathway interactions found "
            f"in our database for this pair. Always verify with a pharmacist.",
            "QUANTUM"
        )
    elif interaction_energy > CAUTION_THRESHOLD:
        return (
            "CAUTION",
            "⚠️ Moderate Quantum Binding Detected",
            f"VQE simulation shows moderate molecular interaction energy "
            f"(ΔE = {ie_kcal:.2f} kcal/mol). These molecules may compete for "
            f"binding sites or influence each other's metabolism. "
            f"Consult a healthcare professional before combining.",
            "QUANTUM"
        )
    else:
        return (
            "DANGEROUS",
            "🚨 Strong Quantum Binding Detected",
            f"VQE simulation shows strong direct molecular binding "
            f"(ΔE = {ie_kcal:.2f} kcal/mol). This level of interaction energy "
            f"suggests significant molecular attraction that could indicate "
            f"binding competition or enzyme inhibition. Do NOT combine without "
            f"medical supervision.",
            "QUANTUM"
        )