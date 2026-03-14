"""
Quantum Drug Interaction Predictor
===================================
Main Streamlit application entry point.
Uses VQE (Variational Quantum Eigensolver) to simulate
drug molecule interactions at the quantum level.

Author: Built with Qiskit + Qiskit Nature + Streamlit
"""

import streamlit as st
import time
from modules.molecule_fetcher import fetch_molecule_data
from modules.hamiltonian_builder import build_hamiltonian
from modules.vqe_solver import run_vqe
from modules.interaction_analyzer import analyze_interaction, get_risk_level

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quantum Drug Interaction Predictor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Space Mono', monospace;
    }

    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .main-header h1 {
        color: #e0d7ff;
        font-size: 2rem;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.5px;
    }

    .main-header p {
        color: #9b92cc;
        font-size: 0.95rem;
        margin: 0;
    }

    .drug-card {
        background: #1a1a2e;
        border: 1px solid #2d2d5e;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .result-safe {
        background: linear-gradient(135deg, #0d4f0d, #1a6b1a);
        border: 1px solid #2ecc71;
        border-radius: 12px;
        padding: 1.5rem;
        color: #a8f0c0;
    }

    .result-caution {
        background: linear-gradient(135deg, #4f3d00, #6b5500);
        border: 1px solid #f39c12;
        border-radius: 12px;
        padding: 1.5rem;
        color: #fde8a0;
    }

    .result-danger {
        background: linear-gradient(135deg, #4f0d0d, #6b1a1a);
        border: 1px solid #e74c3c;
        border-radius: 12px;
        padding: 1.5rem;
        color: #f0a8a8;
    }

    .energy-box {
        background: #0f0c29;
        border: 1px solid #3d3880;
        border-radius: 10px;
        padding: 1rem;
        font-family: 'Space Mono', monospace;
        font-size: 0.85rem;
        color: #c5b8ff;
        margin-top: 1rem;
    }

    .step-badge {
        background: #302b63;
        color: #c5b8ff;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-family: 'Space Mono', monospace;
        margin-right: 8px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #302b63, #24243e);
        color: #e0d7ff;
        border: 1px solid #5048a8;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-family: 'Space Mono', monospace;
        font-size: 0.9rem;
        width: 100%;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #5048a8, #302b63);
        border-color: #c5b8ff;
        color: #ffffff;
    }

    .sidebar-info {
        background: #1a1a2e;
        border-left: 3px solid #5048a8;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.85rem;
        color: #9b92cc;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>⚛️ Quantum Drug Interaction Predictor</h1>
    <p>First-principles quantum simulation using VQE — powered by Qiskit & Qiskit Nature</p>
</div>
""", unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Quantum Settings")

    backend_mode = st.selectbox(
        "Simulation Backend",
        ["Statevector Simulator (Exact)", "QASM Simulator (Noisy)", "IBM Quantum (Real Hardware)"],
        index=0
    )

    max_iterations = st.slider("VQE Max Iterations", 50, 500, 150, step=50)

    optimizer_choice = st.selectbox(
        "Classical Optimizer",
        ["COBYLA", "SPSA", "L-BFGS-B"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 📖 How It Works")
    st.markdown('<div class="sidebar-info">1. Fetch molecule structure from PubChem API</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-info">2. Build molecular Hamiltonian using Qiskit Nature</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-info">3. Run VQE to find ground state energy</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-info">4. Compare interaction vs isolated energies</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-info">5. Classify: Safe / Caution / Dangerous</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧪 Try These Pairs")
    examples = [
        ("Aspirin", "Ibuprofen"),
        ("Warfarin", "Aspirin"),
        ("Caffeine", "Paracetamol"),
        ("Metformin", "Atorvastatin"),
    ]
    for d1, d2 in examples:
        if st.button(f"{d1} + {d2}", key=f"{d1}_{d2}"):
            st.session_state["drug1"] = d1
            st.session_state["drug2"] = d2


# ─── Main Input ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💊 Drug 1")
    drug1 = st.text_input(
        "Enter first drug name",
        value=st.session_state.get("drug1", "Aspirin"),
        placeholder="e.g. Aspirin, Warfarin, Metformin",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("### 💊 Drug 2")
    drug2 = st.text_input(
        "Enter second drug name",
        value=st.session_state.get("drug2", "Ibuprofen"),
        placeholder="e.g. Ibuprofen, Paracetamol, Atorvastatin",
        label_visibility="collapsed"
    )

st.markdown("<br>", unsafe_allow_html=True)
run_btn = st.button("⚛️ Run Quantum Simulation", use_container_width=True)


# ─── Simulation Pipeline ─────────────────────────────────────────────────────────
if run_btn:
    if not drug1.strip() or not drug2.strip():
        st.error("Please enter both drug names.")
    else:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        # STEP 1: Fetch Molecule Data
        status_text.markdown('<span class="step-badge">STEP 1/4</span> Fetching molecule data from PubChem...', unsafe_allow_html=True)
        progress_bar.progress(10)
        time.sleep(0.5)

        mol1_data = fetch_molecule_data(drug1.strip())
        mol2_data = fetch_molecule_data(drug2.strip())

        if mol1_data is None:
            st.error(f"❌ Could not find molecule data for **{drug1}**. Try a different name.")
            st.stop()
        if mol2_data is None:
            st.error(f"❌ Could not find molecule data for **{drug2}**. Try a different name.")
            st.stop()

        progress_bar.progress(25)
        status_text.markdown('<span class="step-badge">STEP 2/4</span> Building molecular Hamiltonian...', unsafe_allow_html=True)
        time.sleep(0.5)

        # STEP 2: Build Hamiltonians
        ham1 = build_hamiltonian(mol1_data)
        ham2 = build_hamiltonian(mol2_data)
        ham_combined = build_hamiltonian(mol1_data, mol2_data, combined=True)

        progress_bar.progress(50)
        status_text.markdown('<span class="step-badge">STEP 3/4</span> Running VQE quantum simulation...', unsafe_allow_html=True)
        time.sleep(0.5)

        # STEP 3: Run VQE
        energy1 = run_vqe(ham1, optimizer=optimizer_choice, max_iter=max_iterations)
        energy2 = run_vqe(ham2, optimizer=optimizer_choice, max_iter=max_iterations)
        energy_combined = run_vqe(ham_combined, optimizer=optimizer_choice, max_iter=max_iterations)

        progress_bar.progress(80)
        status_text.markdown('<span class="step-badge">STEP 4/4</span> Analyzing interaction energy...', unsafe_allow_html=True)
        time.sleep(0.5)

        # STEP 4: Analyze Interaction
        interaction_energy = analyze_interaction(energy1, energy2, energy_combined)
        risk_level, risk_label, risk_explanation = get_risk_level(interaction_energy)

        progress_bar.progress(100)
        status_text.empty()

        # ─── Results Display ─────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## 📊 Simulation Results")

        # Molecule info
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="drug-card">
                <strong style="color:#c5b8ff">💊 {drug1}</strong><br>
                <small style="color:#9b92cc">Formula: {mol1_data['formula']}</small><br>
                <small style="color:#9b92cc">Molecular Weight: {mol1_data['weight']} g/mol</small><br>
                <small style="color:#9b92cc">Atoms: {mol1_data['atom_count']}</small>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="drug-card">
                <strong style="color:#c5b8ff">💊 {drug2}</strong><br>
                <small style="color:#9b92cc">Formula: {mol2_data['formula']}</small><br>
                <small style="color:#9b92cc">Molecular Weight: {mol2_data['weight']} g/mol</small><br>
                <small style="color:#9b92cc">Atoms: {mol2_data['atom_count']}</small>
            </div>
            """, unsafe_allow_html=True)

        # Risk Result
        css_class = {"SAFE": "result-safe", "CAUTION": "result-caution", "DANGEROUS": "result-danger"}[risk_level]
        icon = {"SAFE": "✅", "CAUTION": "⚠️", "DANGEROUS": "🚨"}[risk_level]

        st.markdown(f"""
        <div class="{css_class}">
            <h3 style="margin:0 0 0.5rem 0">{icon} {risk_label}</h3>
            <p style="margin:0;font-size:0.9rem">{risk_explanation}</p>
        </div>
        """, unsafe_allow_html=True)

        # Energy breakdown
        st.markdown(f"""
        <div class="energy-box">
            <strong>🔬 Quantum Energy Analysis</strong><br><br>
            Ground State Energy ({drug1}):    {energy1:.6f} Hartree<br>
            Ground State Energy ({drug2}):    {energy2:.6f} Hartree<br>
            Combined System Energy:           {energy_combined:.6f} Hartree<br>
            ────────────────────────────────────────<br>
            Interaction Energy (ΔE):          {interaction_energy:.6f} Hartree<br>
            Interaction Energy (kcal/mol):    {interaction_energy * 627.5:.3f} kcal/mol
        </div>
        """, unsafe_allow_html=True)

        # Chart
        import plotly.graph_objects as go
        fig = go.Figure(data=[
            go.Bar(
                x=[drug1, drug2, f"{drug1}+{drug2} Combined"],
                y=[abs(energy1), abs(energy2), abs(energy_combined)],
                marker_color=["#7c6fcf", "#5048a8", "#e74c3c" if risk_level == "DANGEROUS" else "#f39c12" if risk_level == "CAUTION" else "#2ecc71"],
                text=[f"{abs(energy1):.4f}", f"{abs(energy2):.4f}", f"{abs(energy_combined):.4f}"],
                textposition="outside"
            )
        ])
        fig.update_layout(
            title="Ground State Energies (Hartree)",
            paper_bgcolor="#0f0c29",
            plot_bgcolor="#1a1a2e",
            font=dict(color="#c5b8ff", family="Space Mono"),
            yaxis=dict(gridcolor="#2d2d5e", title="|Energy| (Hartree)"),
            xaxis=dict(gridcolor="#2d2d5e"),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

        # Disclaimer
        st.info("⚠️ **Research Only**: This tool uses simplified quantum simulations for educational purposes. Do NOT use for actual medical decisions. Always consult a healthcare professional.")