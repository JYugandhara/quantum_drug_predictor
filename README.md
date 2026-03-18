# ⚛ QuantumRx — Quantum Drug Interaction Predictor

> First-principles quantum simulation of drug-drug interactions using the Variational Quantum Eigensolver (VQE). Powered by **Qiskit**, **Streamlit**, and the **PubChem REST API**.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Qiskit](https://img.shields.io/badge/Qiskit-1.0+-6929C4?style=flat-square&logo=ibm)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat-square&logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🔬 What Is QuantumRx?

Most drug interaction tools work by **looking up historical databases** — they can only warn about interactions that have already been documented. QuantumRx takes a fundamentally different approach:

```
Classical tools:   Drug A + Drug B → search database → known interaction?
QuantumRx:         Drug A + Drug B → quantum simulation → compute physics → predict
```

QuantumRx uses **quantum chemistry simulation** to compute the ground state energy of each drug molecule and their combined system. The interaction energy ΔE predicts how strongly the molecules bind — completely from first principles, no training data needed.

---

## ✨ Features

- ⚛ **VQE Quantum Simulation** — TwoLocal ansatz circuit with COBYLA/SPSA/L-BFGS-B optimizers
- 🧬 **3-Layer Hybrid Detection System** — Clinical pathway DB + CYP450 enzyme DB + Quantum ΔE model
- 💊 **Live PubChem API** — Fetches real molecular data for any of 118M+ compounds
- 📊 **4 Interactive Charts** — Ground state energies, interaction gauge, molecular radar, VQE convergence curves
- 🏥 **20+ Clinically Validated Drug Pairs** — Including fatal combinations like Sildenafil+Isosorbide
- 🖥 **Professional Dark UI** — JetBrains Mono, deep navy theme, energy terminal readout
- 📋 **Session History** — Tracks all simulations with detection method badges

---

## 🗂 Project Structure

```
quantum_drug_predictor/
│
├── app.py                          ← Streamlit dashboard (main entry point)
├── requirements.txt                ← All Python dependencies
├── README.md                       ← This file
│
└── modules/
    ├── __init__.py
    ├── molecule_fetcher.py         ← Fetches drug data from PubChem REST API
    ├── hamiltonian_builder.py      ← Builds qubit Hamiltonian via Pauli operators
    ├── vqe_solver.py               ← VQE algorithm + convergence history tracking
    └── interaction_analyzer.py    ← 3-layer hybrid risk classification engine
```

---

## 🧠 How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                     QUANTUMRX PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. PubChem API                                                 │
│     Drug name → CID → formula, weight, atom count, SMILES      │
│                                                                 │
│  2. Hamiltonian Builder                                         │
│     Molecular properties → SparsePauliOp                       │
│     H = c₀(ZZ) + c₁(ZI) + c₂(IZ) + c₃(XX) + c₄(YY)          │
│     Coefficients uniquely parameterized per molecule            │
│                                                                 │
│  3. VQE Algorithm                                               │
│     Quantum: prepare |ψ(θ)⟩, measure ⟨ψ(θ)|H|ψ(θ)⟩           │
│     Classical: optimizer minimizes energy by updating θ         │
│     Result: E(A), E(B), E(AB) ground state energies            │
│                                                                 │
│  4. Interaction Analysis                                        │
│     ΔE = E(AB) − [E(A) + E(B)]                                 │
│                                                                 │
│  5. 3-Layer Risk Classification                                 │
│     Layer 1: Clinical Pathway DB  (highest trust)              │
│     Layer 2: CYP450 Enzyme DB     (metabolic interactions)     │
│     Layer 3: Quantum ΔE Model     (direct binding energy)      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 3-Layer Detection System

### Layer 1 — Clinical Pathway Database
Covers pharmacodynamic interactions that quantum energy **cannot** detect:
- Shared receptor/enzyme pathways (e.g. Sildenafil + Isosorbide → cGMP pathway)
- Synergistic physiological effects (e.g. Warfarin + Aspirin → dual anticoagulation)
- Known fatal combinations from clinical literature (20+ pairs)

### Layer 2 — CYP450 Enzyme Database
Tracks metabolic enzyme competition:
- Which drugs **inhibit** CYP3A4, CYP2C9, CYP2C19, CYP2D6, CYP1A2
- Which drugs are **substrates** of those same enzymes
- If Drug A inhibits the enzyme that metabolizes Drug B → CAUTION

### Layer 3 — Quantum ΔE Model
Pure quantum physics for novel drug pairs:
- ΔE < −0.020 Hartree (>12.6 kcal/mol) → **DANGEROUS**
- ΔE < −0.005 Hartree (>3.1 kcal/mol)  → **CAUTION**
- ΔE > −0.005 Hartree                   → **SAFE**

---

## 🚀 Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/JYugandhara/quantum_drug_predictor.git
cd quantum_drug_predictor
```

### 2. Create a virtual environment
```bash
# Using Conda (recommended)
conda create -n quantum python=3.10
conda activate quantum

# Or using venv
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 🧪 Example Drug Pairs to Try

| Drug A | Drug B | Expected Risk | Mechanism |
|---|---|---|---|
| Sildenafil | Isosorbide | 🚨 DANGEROUS | Shared cGMP pathway — hypotensive crisis |
| Warfarin | Aspirin | 🚨 DANGEROUS | Dual anticoagulation — severe bleeding |
| Digoxin | Amiodarone | 🚨 DANGEROUS | P-gp inhibition — digoxin toxicity |
| Fluoxetine | Tramadol | 🚨 DANGEROUS | Serotonin syndrome |
| Omeprazole | Clopidogrel | ⚠️ CAUTION | CYP2C19 competition |
| Ciprofloxacin | Theophylline | ⚠️ CAUTION | CYP1A2 inhibition |
| Caffeine | Paracetamol | ✅ SAFE | Synergistic analgesia — clinically approved |

---

## ⚙️ Quantum Settings

| Setting | Options | Description |
|---|---|---|
| **Backend** | Statevector (Exact) / QASM (Noisy) / IBM Cloud | How the quantum circuit is simulated |
| **VQE Iterations** | 50 – 500 | How many optimizer steps to run |
| **Optimizer** | COBYLA / SPSA / L-BFGS-B | Classical optimizer for parameter updates |

**Recommended:** Statevector + COBYLA + 150 iterations for best balance of speed and accuracy.

---

## 📊 Charts Explained

| Chart | What It Shows |
|---|---|
| **Ground State Energies** | Absolute VQE energy for Drug A, Drug B, Combined AB |
| **Interaction Strength Gauge** | ΔE in kcal/mol on a Safe/Caution/Dangerous scale |
| **Molecular Properties Radar** | 5-axis comparison: weight, atoms, energy scale, complexity, interaction |
| **VQE Convergence Curves** | Energy vs optimizer iteration for all 3 systems |

---

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| **Qiskit** | Quantum circuit construction and simulation |
| **Qiskit Algorithms** | VQE implementation and classical optimizers |
| **Qiskit Aer** | Quantum backend simulators |
| **Streamlit** | Interactive web dashboard |
| **Plotly** | Interactive charts (bar, gauge, radar, line) |
| **PubChem REST API** | Live molecular data fetching |
| **NumPy / SciPy** | Numerical computation |

---

## 🔭 Roadmap

- [ ] Integrate DrugBank API (3M+ known interactions)
- [ ] Add PySCF support for Linux/cloud deployment
- [ ] Expand to 4-8 qubit simulations for larger molecules
- [ ] Add 3D molecular visualization with py3Dmol
- [ ] Run on real IBM Quantum hardware
- [ ] Validate predictions against FDA interaction database
- [ ] REST API for programmatic access
- [ ] Mobile-friendly interface

---

## ⚠️ Disclaimer

QuantumRx is a **research prototype** for educational and scientific exploration purposes only. The quantum simulations are simplified (2-qubit, parameterized Hamiltonians). **Do NOT use for actual medical decisions.** Always consult a licensed healthcare professional before combining any medications.

---

## 📄 License

MIT License — feel free to fork, extend, and build on this project.

---

## 🙏 Acknowledgements

- [IBM Qiskit](https://qiskit.org) — quantum computing framework
- [PubChem](https://pubchem.ncbi.nlm.nih.gov) — open molecular database
- [Streamlit](https://streamlit.io) — web app framework
- Quantum computing research community