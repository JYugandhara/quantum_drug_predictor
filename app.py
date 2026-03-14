"""
Quantum Drug Interaction Predictor — QuantumRx
================================================
Professional blue-themed dashboard with enhanced UI.
Uses VQE (Variational Quantum Eigensolver) to simulate
drug molecule interactions at the quantum level.
"""

import streamlit as st
import plotly.graph_objects as go
import time
from modules.molecule_fetcher import fetch_molecule_data
from modules.hamiltonian_builder import build_hamiltonian
from modules.vqe_solver import run_vqe
from modules.interaction_analyzer import analyze_interaction, get_risk_level

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuantumRx — Drug Interaction Predictor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Professional Blue CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #020B18;
    color: #CBD5E1;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1200px; }

.hero {
    background: linear-gradient(135deg, #020B18 0%, #0A1628 40%, #0D2444 100%);
    border: 1px solid #1E3A5F;
    border-radius: 16px;
    padding: 3rem 2.5rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-tag {
    display: inline-block;
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.3);
    color: #38BDF8;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 2px;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.hero h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.4rem;
    font-weight: 600;
    color: #F0F9FF;
    margin: 0.5rem 0 0.8rem;
    line-height: 1.2;
}
.hero h1 span { color: #38BDF8; }
.hero p { color: #64748B; font-size: 0.95rem; max-width: 600px; line-height: 1.7; margin: 0; }
.hero-stats { display: flex; gap: 2rem; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #1E3A5F; }
.hero-stat-label { color: #38BDF8; font-family: 'IBM Plex Mono', monospace; font-size: 1.3rem; font-weight: 600; }
.hero-stat-desc { color: #475569; font-size: 0.78rem; margin-top: 2px; }

.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 3px;
    color: #38BDF8;
    text-transform: uppercase;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1E3A5F;
}
.blue-divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, #1E3A5F, transparent); margin: 2rem 0; }

.input-card { background: #0A1628; border: 1px solid #1E3A5F; border-radius: 12px; padding: 1.5rem; }
.input-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; letter-spacing: 2px; color: #38BDF8; margin-bottom: 0.5rem; }

.stTextInput input {
    background: #020B18 !important; border: 1px solid #1E3A5F !important;
    border-radius: 8px !important; color: #F0F9FF !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.95rem !important;
    padding: 0.7rem 1rem !important;
}
.stTextInput input:focus { border-color: #2563EB !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.15) !important; }

.stButton > button {
    background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
    color: #F0F9FF !important; border: 1px solid #3B82F6 !important;
    border-radius: 10px !important; font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.9rem !important; font-weight: 600 !important;
    letter-spacing: 1px !important; padding: 0.75rem 2rem !important; width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563EB, #3B82F6) !important;
    box-shadow: 0 8px 25px rgba(37,99,235,0.35) !important;
}

.metric-card { background: #0A1628; border: 1px solid #1E3A5F; border-radius: 12px; padding: 1.2rem 1.5rem; text-align: center; }
.metric-value { font-family: 'IBM Plex Mono', monospace; font-size: 1.5rem; font-weight: 600; color: #38BDF8; }
.metric-label { color: #475569; font-size: 0.78rem; margin-top: 4px; }

.drug-info { background: #0A1628; border: 1px solid #1E3A5F; border-left: 3px solid #2563EB; border-radius: 0 12px 12px 0; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem; }
.drug-info-name { font-family: 'IBM Plex Mono', monospace; font-size: 1rem; color: #F0F9FF; font-weight: 600; margin-bottom: 0.5rem; }
.drug-info-detail { color: #64748B; font-size: 0.82rem; line-height: 1.8; }
.drug-info-detail span { color: #94A3B8; }

.result-safe { background: linear-gradient(135deg,#022C22,#064E3B); border: 1px solid #10B981; border-radius: 14px; padding: 2rem; margin: 1.5rem 0; }
.result-caution { background: linear-gradient(135deg,#1C1203,#292500); border: 1px solid #F59E0B; border-radius: 14px; padding: 2rem; margin: 1.5rem 0; }
.result-danger { background: linear-gradient(135deg,#1C0505,#2D0A0A); border: 1px solid #EF4444; border-radius: 14px; padding: 2rem; margin: 1.5rem 0; }
.result-title { font-family: 'IBM Plex Mono', monospace; font-size: 1.3rem; font-weight: 600; margin-bottom: 0.7rem; }
.result-body { font-size: 0.9rem; line-height: 1.8; opacity: 0.85; }

.energy-terminal { background: #010810; border: 1px solid #1E3A5F; border-top: 3px solid #2563EB; border-radius: 0 0 12px 12px; padding: 1.5rem; font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; color: #38BDF8; line-height: 2; }
.terminal-header { background: #0A1628; border: 1px solid #1E3A5F; border-bottom: none; border-radius: 12px 12px 0 0; padding: 0.6rem 1rem; }
.t-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }

.circuit-box { background: #010810; border: 1px solid #1E3A5F; border-radius: 12px; padding: 1.2rem; font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: #2563EB; overflow-x: auto; line-height: 1.9; }

.step-row { display: flex; gap: 0; margin: 1rem 0; }
.step-item { flex: 1; text-align: center; position: relative; }
.step-num { width: 32px; height: 32px; background: #0D2444; border: 1px solid #2563EB; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #38BDF8; }
.step-label { font-size: 0.72rem; color: #475569; margin-top: 6px; }

.sidebar-section { background: #0A1628; border: 1px solid #1E3A5F; border-radius: 10px; padding: 1rem; margin-bottom: 0.8rem; font-size: 0.82rem; color: #64748B; }
.sidebar-section strong { color: #38BDF8; display: block; margin-bottom: 4px; }

[data-testid="stSidebar"] { background: #020B18 !important; border-right: 1px solid #1E3A5F !important; }
.stProgress > div > div { background: #2563EB !important; }
</style>
""", unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">⚛ QUANTUM COMPUTING · DRUG SAFETY ANALYSIS</div>
    <h1>Quantum<span>Rx</span></h1>
    <p>First-principles quantum simulation of drug-drug interactions using the
    Variational Quantum Eigensolver (VQE). Each molecule gets a unique quantum
    energy fingerprint — no ML guessing, pure quantum physics.</p>
    <div class="hero-stats">
        <div><div class="hero-stat-label">VQE</div><div class="hero-stat-desc">Algorithm</div></div>
        <div><div class="hero-stat-label">2-Qubit</div><div class="hero-stat-desc">Quantum Circuit</div></div>
        <div><div class="hero-stat-label">PubChem</div><div class="hero-stat-desc">Live Molecule Data</div></div>
        <div><div class="hero-stat-label">Hartree</div><div class="hero-stat-desc">Energy Units</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Pipeline steps
st.markdown("""
<div class="step-row">
    <div class="step-item"><div class="step-num">01</div><div class="step-label">Fetch Molecule</div></div>
    <div class="step-item"><div class="step-num">02</div><div class="step-label">Build Hamiltonian</div></div>
    <div class="step-item"><div class="step-num">03</div><div class="step-label">Run VQE</div></div>
    <div class="step-item"><div class="step-num">04</div><div class="step-label">Compute ΔE</div></div>
    <div class="step-item"><div class="step-num">05</div><div class="step-label">Risk Report</div></div>
</div>
<div class="blue-divider"></div>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family:"IBM Plex Mono",monospace;font-size:1.1rem;font-weight:600;
    color:#F0F9FF;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #1E3A5F;'>
    ⚛ QuantumRx
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">QUANTUM SETTINGS</div>', unsafe_allow_html=True)
    backend_mode     = st.selectbox("Backend", ["Statevector (Exact)", "QASM (Noisy)", "IBM Cloud"], index=0)
    max_iterations   = st.slider("VQE Iterations", 50, 500, 150, step=50)
    optimizer_choice = st.selectbox("Optimizer", ["COBYLA", "SPSA", "L-BFGS-B"], index=0)

    st.markdown(f"""
    <div class="sidebar-section"><strong>Active Config</strong>
    Backend: {backend_mode}<br>Iterations: {max_iterations}<br>Optimizer: {optimizer_choice}
    </div>""", unsafe_allow_html=True)

    st.markdown('<br><div class="section-header">QUICK EXAMPLES</div>', unsafe_allow_html=True)
    examples = [
        ("Aspirin",    "Ibuprofen",    "⚠"),
        ("Warfarin",   "Aspirin",      "🚨"),
        ("Caffeine",   "Paracetamol",  "✅"),
        ("Metformin",  "Atorvastatin", "⚠"),
        ("Lisinopril", "Potassium",    "🚨"),
    ]
    for d1, d2, icon in examples:
        if st.button(f"{icon} {d1} + {d2}", key=f"ex_{d1}_{d2}"):
            st.session_state["drug1"] = d1
            st.session_state["drug2"] = d2

    st.markdown("""<br><div class="sidebar-section">
    <strong>Built At</strong>IISc QCTar Workshop · March 2026<br><br>
    <strong>Stack</strong>Qiskit · Streamlit · PubChem API
    </div>""", unsafe_allow_html=True)


# ── Input ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">DRUG PAIR INPUT</div>', unsafe_allow_html=True)
c1, gap, c2 = st.columns([5, 1, 5])

with c1:
    st.markdown('<div class="input-card"><div class="input-label">💊 DRUG A</div>', unsafe_allow_html=True)
    drug1 = st.text_input("Drug A", value=st.session_state.get("drug1", "Aspirin"),
                           placeholder="e.g. Aspirin", label_visibility="collapsed", key="d1")
    st.markdown('</div>', unsafe_allow_html=True)

with gap:
    st.markdown("<div style='text-align:center;padding-top:2.2rem;font-family:IBM Plex Mono;font-size:1.2rem;color:#1E3A5F'>+</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="input-card"><div class="input-label">💊 DRUG B</div>', unsafe_allow_html=True)
    drug2 = st.text_input("Drug B", value=st.session_state.get("drug2", "Ibuprofen"),
                           placeholder="e.g. Ibuprofen", label_visibility="collapsed", key="d2")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
btn_col, _ = st.columns([3, 7])
with btn_col:
    run_btn = st.button("⚛  RUN QUANTUM SIMULATION", use_container_width=True)


# ── Simulation ─────────────────────────────────────────────────────────────────
if run_btn:
    if not drug1.strip() or not drug2.strip():
        st.error("Please enter both drug names.")
        st.stop()

    st.markdown('<div class="blue-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">RUNNING PIPELINE</div>', unsafe_allow_html=True)

    prog   = st.progress(0)
    status = st.empty()

    def upd(pct, msg):
        prog.progress(pct)
        status.markdown(f"<div style='font-family:\"IBM Plex Mono\",monospace;font-size:0.82rem;color:#38BDF8;padding:0.5rem 0;'>▶ {msg}</div>", unsafe_allow_html=True)

    upd(10, f"[01/04] Querying PubChem API for {drug1} and {drug2}...")
    time.sleep(0.4)
    mol1 = fetch_molecule_data(drug1.strip())
    mol2 = fetch_molecule_data(drug2.strip())

    if not mol1:
        st.error(f"❌ Not found: **{drug1}**. Use the generic name (e.g. 'Ibuprofen' not 'Advil').")
        st.stop()
    if not mol2:
        st.error(f"❌ Not found: **{drug2}**. Use the generic name.")
        st.stop()

    upd(30, "[02/04] Building qubit Hamiltonians...")
    time.sleep(0.4)
    ham1  = build_hamiltonian(mol1)
    ham2  = build_hamiltonian(mol2)
    hamc  = build_hamiltonian(mol1, mol2, combined=True)

    upd(55, f"[03/04] Running VQE · {optimizer_choice} · {max_iterations} iterations...")
    time.sleep(0.4)
    e1    = run_vqe(ham1, optimizer=optimizer_choice, max_iter=max_iterations)
    e2    = run_vqe(ham2, optimizer=optimizer_choice, max_iter=max_iterations)
    ecomb = run_vqe(hamc, optimizer=optimizer_choice, max_iter=max_iterations)

    upd(85, "[04/04] Computing ΔE and classifying interaction risk...")
    time.sleep(0.4)
    delta_e = analyze_interaction(e1, e2, ecomb)
    risk_level, risk_label, risk_explanation = get_risk_level(delta_e)

    prog.progress(100)
    status.empty()

    # ── Results ───────────────────────────────────────────────────────────────
    st.markdown('<div class="blue-divider"></div>', unsafe_allow_html=True)

    # Molecule profiles
    st.markdown('<div class="section-header">MOLECULAR PROFILE</div>', unsafe_allow_html=True)
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown(f"""<div class="drug-info">
            <div class="drug-info-name">💊 {mol1['name'].upper()}</div>
            <div class="drug-info-detail">
                Formula &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span>{mol1['formula']}</span><br>
                Mol. Weight &nbsp;&nbsp;<span>{mol1['weight']} g/mol</span><br>
                Heavy Atoms &nbsp;&nbsp;<span>{mol1['atom_count']}</span><br>
                PubChem CID &nbsp;<span>{mol1['cid']}</span><br>
                Ground State &nbsp;<span>{e1:.6f} Ha</span>
            </div></div>""", unsafe_allow_html=True)
    with rc2:
        st.markdown(f"""<div class="drug-info">
            <div class="drug-info-name">💊 {mol2['name'].upper()}</div>
            <div class="drug-info-detail">
                Formula &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span>{mol2['formula']}</span><br>
                Mol. Weight &nbsp;&nbsp;<span>{mol2['weight']} g/mol</span><br>
                Heavy Atoms &nbsp;&nbsp;<span>{mol2['atom_count']}</span><br>
                PubChem CID &nbsp;<span>{mol2['cid']}</span><br>
                Ground State &nbsp;<span>{e2:.6f} Ha</span>
            </div></div>""", unsafe_allow_html=True)

    # Metrics
    st.markdown('<br><div class="section-header">QUANTUM METRICS</div>', unsafe_allow_html=True)
    delta_kcal = delta_e * 627.5
    binding    = "Strong" if abs(delta_e) > 0.02 else "Moderate" if abs(delta_e) > 0.005 else "Weak"
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{delta_e:.5f}</div><div class="metric-label">ΔE (Hartree)</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{delta_kcal:.2f}</div><div class="metric-label">ΔE (kcal/mol)</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{ecomb:.5f}</div><div class="metric-label">E(AB) Hartree</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{binding}</div><div class="metric-label">Binding Strength</div></div>', unsafe_allow_html=True)

    # Verdict
    st.markdown('<br><div class="section-header">INTERACTION VERDICT</div>', unsafe_allow_html=True)
    css_map   = {"SAFE": "result-safe", "CAUTION": "result-caution", "DANGEROUS": "result-danger"}
    color_map = {"SAFE": "#10B981", "CAUTION": "#F59E0B", "DANGEROUS": "#EF4444"}
    icon_map  = {"SAFE": "✅", "CAUTION": "⚠️", "DANGEROUS": "🚨"}
    st.markdown(f"""<div class="{css_map[risk_level]}">
        <div class="result-title" style="color:{color_map[risk_level]}">{icon_map[risk_level]} {risk_label}</div>
        <div class="result-body">{risk_explanation}</div>
    </div>""", unsafe_allow_html=True)

    # Energy terminal
    st.markdown('<div class="section-header">ENERGY TERMINAL</div>', unsafe_allow_html=True)
    e_col = "color:#10B981" if risk_level=="SAFE" else "color:#F59E0B" if risk_level=="CAUTION" else "color:#EF4444"
    st.markdown(f"""
    <div class="terminal-header">
        <span class="t-dot" style="background:#EF4444"></span>
        <span class="t-dot" style="background:#F59E0B"></span>
        <span class="t-dot" style="background:#10B981"></span>
        &nbsp;<span style='font-family:"IBM Plex Mono",monospace;font-size:0.72rem;color:#475569;'>
        quantumrx · {optimizer_choice} · {max_iterations} iter</span>
    </div>
    <div class="energy-terminal">
        <span style="color:#64748B">$ drug_a     │ </span><span>{mol1['name']}</span><span style="color:#64748B">  formula=</span>{mol1['formula']}<br>
        <span style="color:#64748B">$ drug_b     │ </span><span>{mol2['name']}</span><span style="color:#64748B">  formula=</span>{mol2['formula']}<br>
        <span style="color:#1E3A5F">─────────────┼──────────────────────────────────</span><br>
        <span style="color:#64748B">$ E(A)       │ </span><span>{e1:+.8f} Ha</span><br>
        <span style="color:#64748B">$ E(B)       │ </span><span>{e2:+.8f} Ha</span><br>
        <span style="color:#64748B">$ E(A)+E(B)  │ </span><span>{(e1+e2):+.8f} Ha</span><br>
        <span style="color:#64748B">$ E(AB)      │ </span><span>{ecomb:+.8f} Ha</span><br>
        <span style="color:#1E3A5F">─────────────┼──────────────────────────────────</span><br>
        <span style="color:#64748B">$ ΔE         │ </span><span style="color:#F0F9FF;font-weight:600">{delta_e:+.8f} Ha</span><span style="color:#64748B"> ({delta_kcal:+.3f} kcal/mol)</span><br>
        <span style="color:#64748B">$ risk       │ </span><span style="{e_col};font-weight:600">{risk_level}</span>
    </div>""", unsafe_allow_html=True)

    # Charts
    st.markdown('<br><div class="section-header">ENERGY VISUALISATION</div>', unsafe_allow_html=True)
    ch1, ch2 = st.columns([3, 2])

    with ch1:
        bar_c = ["#2563EB","#3B82F6",
                 "#EF4444" if risk_level=="DANGEROUS" else "#F59E0B" if risk_level=="CAUTION" else "#10B981"]
        fig = go.Figure(go.Bar(
            x=[drug1, drug2, f"{drug1}+{drug2}"],
            y=[abs(e1), abs(e2), abs(ecomb)],
            marker_color=bar_c,
            text=[f"{abs(e1):.5f}", f"{abs(e2):.5f}", f"{abs(ecomb):.5f}"],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=11, color="#94A3B8")
        ))
        fig.update_layout(
            title=dict(text="Ground State Energies (Hartree)", font=dict(family="IBM Plex Mono", color="#94A3B8", size=13)),
            paper_bgcolor="#020B18", plot_bgcolor="#0A1628",
            font=dict(color="#64748B", family="IBM Plex Mono"),
            yaxis=dict(gridcolor="#1E3A5F", title="|Energy| (Ha)", color="#64748B", title_font=dict(size=11)),
            xaxis=dict(gridcolor="#1E3A5F", color="#64748B"),
            height=320, margin=dict(t=50, b=20, l=10, r=10), showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with ch2:
        gauge_val = min(abs(delta_kcal), 20)
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=gauge_val,
            number=dict(suffix=" kcal/mol", font=dict(family="IBM Plex Mono", color="#38BDF8", size=16)),
            gauge=dict(
                axis=dict(range=[0, 20], tickfont=dict(family="IBM Plex Mono", size=10, color="#475569")),
                bar=dict(color=color_map[risk_level]),
                bgcolor="#0A1628", bordercolor="#1E3A5F",
                steps=[
                    dict(range=[0, 3.1],   color="#022C22"),
                    dict(range=[3.1, 12.6], color="#1C1203"),
                    dict(range=[12.6, 20],  color="#1C0505"),
                ]
            ),
            title=dict(text="Interaction Strength", font=dict(family="IBM Plex Mono", color="#94A3B8", size=13))
        ))
        fig2.update_layout(paper_bgcolor="#020B18", height=320, margin=dict(t=50, b=20, l=20, r=20))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # VQE circuit
    st.markdown('<div class="section-header">VQE ANSATZ CIRCUIT (TWOLOCAL · 2-QUBIT)</div>', unsafe_allow_html=True)
    st.markdown("""<div class="circuit-box">
        <span style="color:#38BDF8">q₀</span> ─┤ <span style="color:#F0F9FF">Ry(θ₀)</span> ├─┤ <span style="color:#F0F9FF">Rz(θ₁)</span> ├─<span style="color:#F0F9FF">●</span>─────────────────┤ <span style="color:#F0F9FF">Ry(θ₄)</span> ├─┤ <span style="color:#F0F9FF">Rz(θ₅)</span> ├─<span style="color:#10B981">┤M├</span><br>
        <span style="color:#38BDF8">q₁</span> ─┤ <span style="color:#F0F9FF">Ry(θ₂)</span> ├─┤ <span style="color:#F0F9FF">Rz(θ₃)</span> ├─<span style="color:#F0F9FF">⊕</span>─────────────────┤ <span style="color:#F0F9FF">Ry(θ₆)</span> ├─┤ <span style="color:#F0F9FF">Rz(θ₇)</span> ├─<span style="color:#10B981">┤M├</span><br>
        <br>
        <span style="color:#475569">  Rotation (Ry,Rz) → CNOT entanglement → Rotation → Measure</span><br>
        <span style="color:#475569">  θ₀..θ₇ optimized by </span><span style="color:#38BDF8">{}</span><span style="color:#475569"> to minimize ⟨ψ|H|ψ⟩</span>
    </div>""".format(optimizer_choice), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("⚠️ **Research Only** — Educational quantum simulation. Never use for actual medical decisions. Always consult a licensed healthcare professional.")

else:
    st.markdown("""
    <div style='text-align:center;padding:4rem 2rem;background:#0A1628;border:1px solid #1E3A5F;
    border-radius:14px;margin-top:1rem;'>
        <div style='font-size:3.5rem;margin-bottom:1rem;'>⚛</div>
        <div style='font-family:"IBM Plex Mono",monospace;font-size:1rem;color:#38BDF8;margin-bottom:0.8rem;'>
        READY TO SIMULATE</div>
        <div style='color:#475569;font-size:0.88rem;max-width:420px;margin:0 auto;line-height:1.9;'>
        Enter two drug names above and click
        <strong style="color:#2563EB">Run Quantum Simulation</strong>
        to compute their quantum-level interaction energy using VQE.
        </div>
    </div>""", unsafe_allow_html=True)