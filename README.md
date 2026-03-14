# ⚛️ Quantum Drug Interaction Predictor

A first-principles quantum simulation tool that predicts drug-drug
interactions using VQE (Variational Quantum Eigensolver) — powered by
**Qiskit**, **Qiskit Nature**, and **PySCF**.

Built as a unique quantum computing project showcasing concepts from
the IISc Quantum Computing Workshop (QCTar, March 2026).

---

## 🗂️ Project Structure

```
quantum_drug_predictor/
│
├── app.py                        ← Streamlit dashboard (main entry point)
├── requirements.txt              ← All Python dependencies
├── README.md                     ← This file
│
└── modules/
    ├── __init__.py
    ├── molecule_fetcher.py       ← Fetches drug data from PubChem API
    ├── hamiltonian_builder.py    ← Builds qubit Hamiltonian via Qiskit Nature
    ├── vqe_solver.py             ← VQE algorithm + classical optimizer
    └── interaction_analyzer.py  ← Calculates ΔE and classifies risk
```

---

## 🔬 How It Works

```
User inputs two drug names
        ↓
PubChem API → molecular formula, SMILES, atom count
        ↓
Qiskit Nature → builds molecular Hamiltonian (Jordan-Wigner mapping)
        ↓
VQE runs on quantum simulator → finds ground state energy E(A), E(B), E(AB)
        ↓
Interaction Energy: ΔE = E(AB) - [E(A) + E(B)]
        ↓
Risk classification: SAFE / CAUTION / DANGEROUS
        ↓
Streamlit dashboard → visual results
```

---

## 🚀 Setup & Run

### 1. Clone or download this project
```bash
cd quantum_drug_predictor
```

### 2. Create a virtual environment (recommended)
```bash
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

Open your browser at: **http://localhost:8501**

---

## 🧪 Example Drug Pairs to Try

| Drug 1       | Drug 2        | Expected Risk    |
|--------------|---------------|------------------|
| Aspirin      | Ibuprofen     | Caution          |
| Warfarin     | Aspirin       | Dangerous        |
| Caffeine     | Paracetamol   | Low              |
| Metformin    | Atorvastatin  | Caution          |

---

## 🧠 Key Concepts Used

| Concept               | Where Used                        |
|-----------------------|-----------------------------------|
| Quantum gates         | VQE ansatz (TwoLocal circuit)     |
| Quantum circuits      | Parameterized ansatz in vqe_solver|
| Qiskit                | Core quantum framework            |
| Quantum chemistry     | Hamiltonian via Qiskit Nature     |
| VQE algorithm         | Ground state energy calculation   |

---

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**.
The molecular simulations are simplified (minimal basis set, 2-electron
active space). Do NOT use for actual medical decisions.

---

## 👨‍🔬 Acknowledgements

- IBM Qiskit team
- Qiskit Nature contributors
- IISc QCTar Workshop faculty
- PubChem open API