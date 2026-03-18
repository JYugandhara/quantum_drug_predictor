"""
QuantumRx — Quantum Drug Interaction Predictor
================================================
Premium professional UI with animations, rich visualizations,
comparison history, radar charts, and full quantum pipeline.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import time
import pandas as pd
from modules.molecule_fetcher import fetch_molecule_data
from modules.hamiltonian_builder import build_hamiltonian
from modules.vqe_solver import run_vqe
from modules.interaction_analyzer import analyze_interaction, get_risk_level

st.set_page_config(
    page_title="QuantumRx",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #03070F;
    color: #94A3B8;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 4rem; max-width: 1280px; }

/* ═══════════════════════ HERO ═══════════════════════ */
.qrx-hero {
    position: relative;
    padding: 4rem 3rem 3rem;
    margin-bottom: 2.5rem;
    overflow: hidden;
    border-bottom: 1px solid rgba(30,58,95,0.6);
}
.qrx-hero-grid {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(37,99,235,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(37,99,235,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
    mask-image: radial-gradient(ellipse 80% 60% at 50% 0%, black 40%, transparent 100%);
}
.qrx-hero-glow {
    position: absolute;
    top: -120px; left: 50%; transform: translateX(-50%);
    width: 700px; height: 400px;
    background: radial-gradient(ellipse, rgba(37,99,235,0.12) 0%, rgba(56,189,248,0.06) 40%, transparent 70%);
    pointer-events: none;
}
.qrx-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(37,99,235,0.08);
    border: 1px solid rgba(37,99,235,0.25);
    color: #60A5FA;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; letter-spacing: 2.5px;
    padding: 5px 14px; border-radius: 100px;
    margin-bottom: 1.5rem;
}
.qrx-badge::before { content: '●'; color: #22D3EE; font-size: 0.5rem; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

.qrx-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3.2rem; font-weight: 600;
    color: #F8FAFC; letter-spacing: -1px;
    line-height: 1.1; margin-bottom: 1rem;
}
.qrx-title .accent { 
    color: transparent;
    background: linear-gradient(135deg, #38BDF8, #2563EB);
    -webkit-background-clip: text; background-clip: text;
}
.qrx-subtitle {
    font-size: 1rem; color: #64748B;
    max-width: 580px; line-height: 1.8;
    margin-bottom: 2.5rem;
}
.qrx-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.qrx-chip {
    background: rgba(15,23,42,0.8);
    border: 1px solid #1E3A5F;
    border-radius: 8px;
    padding: 6px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; color: #475569;
}
.qrx-chip b { color: #38BDF8; }

/* ═══════════════════════ CARDS ═══════════════════════ */
.card {
    background: #080F1E;
    border: 1px solid #0F2037;
    border-radius: 16px;
    padding: 1.8rem;
    transition: border-color 0.2s;
}
.card:hover { border-color: #1E3A5F; }
.card-sm {
    background: #080F1E;
    border: 1px solid #0F2037;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
}
.card-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; letter-spacing: 3px;
    color: #2563EB; text-transform: uppercase;
    margin-bottom: 1rem;
    display: flex; align-items: center; gap: 8px;
}
.card-title::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, #0F2037, transparent);
}

/* ═══════════════════════ INPUT ═══════════════════════ */
.drug-input-wrapper {
    position: relative;
}
.drug-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; letter-spacing: 2px;
    color: #2563EB; margin-bottom: 6px;
}
.stTextInput > div > div > input {
    background: #03070F !important;
    border: 1px solid #1E3A5F !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1rem !important;
    padding: 0.85rem 1.1rem !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12), 0 0 20px rgba(37,99,235,0.08) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: #1E3A5F !important; }

/* ═══════════════════════ BUTTON ═══════════════════════ */
.stButton > button {
    position: relative; overflow: hidden;
    background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 50%, #1D4ED8 100%) !important;
    background-size: 200% auto !important;
    color: #fff !important;
    border: 1px solid rgba(96,165,250,0.3) !important;
    border-radius: 12px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important; font-weight: 600 !important;
    letter-spacing: 2px !important;
    padding: 0.9rem 2rem !important;
    width: 100% !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    background-position: right center !important;
    box-shadow: 0 0 30px rgba(37,99,235,0.4), 0 8px 32px rgba(0,0,0,0.4) !important;
    transform: translateY(-1px) !important;
    border-color: rgba(96,165,250,0.6) !important;
}

/* ═══════════════════════ METRICS ═══════════════════════ */
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 1.5rem 0; }
.metric-box {
    background: #080F1E;
    border: 1px solid #0F2037;
    border-radius: 14px;
    padding: 1.3rem;
    text-align: center;
    position: relative; overflow: hidden;
    transition: all 0.2s;
}
.metric-box::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #2563EB, transparent);
}
.metric-box:hover { border-color: #1E3A5F; transform: translateY(-2px); }
.metric-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem; font-weight: 600;
    color: #38BDF8; display: block; margin-bottom: 4px;
}
.metric-lbl { font-size: 0.72rem; color: #334155; letter-spacing: 0.5px; }

/* ═══════════════════════ RISK CARDS ═══════════════════════ */
.verdict-card {
    border-radius: 16px; padding: 2.5rem;
    margin: 1.5rem 0; position: relative; overflow: hidden;
}
.verdict-card::before {
    content: ''; position: absolute;
    top: -50px; right: -50px;
    width: 200px; height: 200px;
    border-radius: 50%;
    opacity: 0.08;
}
.verdict-safe { background: #020F08; border: 1px solid rgba(16,185,129,0.4); }
.verdict-safe::before { background: #10B981; }
.verdict-caution { background: #0D0900; border: 1px solid rgba(245,158,11,0.4); }
.verdict-caution::before { background: #F59E0B; }
.verdict-danger { background: #0F0404; border: 1px solid rgba(239,68,68,0.4); }
.verdict-danger::before { background: #EF4444; }

.verdict-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem; font-weight: 600; margin-bottom: 0.8rem;
}
.verdict-text { font-size: 0.9rem; line-height: 1.9; color: #64748B; }

/* ═══════════════════════ TERMINAL ═══════════════════════ */
.qrx-terminal {
    background: #020509;
    border: 1px solid #0F2037;
    border-radius: 14px;
    overflow: hidden;
    font-family: 'JetBrains Mono', monospace;
}
.terminal-bar {
    background: #080F1E;
    border-bottom: 1px solid #0F2037;
    padding: 10px 16px;
    display: flex; align-items: center; gap: 6px;
}
.td { width:11px;height:11px;border-radius:50%;display:inline-block; }
.terminal-body {
    padding: 1.5rem;
    font-size: 0.8rem;
    line-height: 2.1;
    color: #334155;
}
.tl-key { color: #1E3A5F; }
.tl-val { color: #38BDF8; }
.tl-hi  { color: #F1F5F9; font-weight: 600; }
.tl-sep { color: #0F2037; }
.tl-safe { color: #10B981; font-weight: 600; }
.tl-warn { color: #F59E0B; font-weight: 600; }
.tl-danger { color: #EF4444; font-weight: 600; }
.tl-dim { color: #0F2037; }

/* ═══════════════════════ MOLECULE CARD ═══════════════════════ */
.mol-card {
    background: #080F1E;
    border: 1px solid #0F2037;
    border-radius: 14px;
    padding: 1.5rem;
    border-left: 3px solid #2563EB;
    transition: all 0.2s;
}
.mol-card:hover { border-color: #2563EB; border-left-color: #38BDF8; }
.mol-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem; font-weight: 600;
    color: #F1F5F9; margin-bottom: 1rem;
    letter-spacing: -0.3px;
}
.mol-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #080F1E; }
.mol-key { font-size: 0.78rem; color: #334155; }
.mol-val { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #64748B; }

/* ═══════════════════════ CIRCUIT ═══════════════════════ */
.qrx-circuit {
    background: #020509;
    border: 1px solid #0F2037;
    border-radius: 14px;
    padding: 2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem; line-height: 2.2;
    overflow-x: auto;
}

/* ═══════════════════════ HISTORY ═══════════════════════ */
.history-row {
    display: flex; align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #080F1E;
    transition: background 0.15s;
    font-size: 0.82rem;
}
.history-row:hover { background: #080F1E; }
.history-drugs { font-family: 'JetBrains Mono', monospace; color: #94A3B8; flex: 1; }
.history-de { font-family: 'JetBrains Mono', monospace; color: #475569; width: 140px; }
.history-badge {
    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem;
    padding: 3px 10px; border-radius: 100px; font-weight: 600;
}
.badge-safe { background: rgba(16,185,129,0.1); color: #10B981; border: 1px solid rgba(16,185,129,0.2); }
.badge-caution { background: rgba(245,158,11,0.1); color: #F59E0B; border: 1px solid rgba(245,158,11,0.2); }
.badge-danger { background: rgba(239,68,68,0.1); color: #EF4444; border: 1px solid rgba(239,68,68,0.2); }

/* ═══════════════════════ PROGRESS ═══════════════════════ */
.stProgress > div > div { background: linear-gradient(90deg, #1D4ED8, #38BDF8) !important; border-radius: 4px !important; }

/* ═══════════════════════ SIDEBAR ═══════════════════════ */
[data-testid="stSidebar"] {
    background: #03070F !important;
    border-right: 1px solid #0F2037 !important;
}
[data-testid="stSidebar"] .stSelectbox > div, [data-testid="stSidebar"] .stSlider { }
.sb-head {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem; font-weight: 600; color: #F1F5F9;
    padding-bottom: 1rem; margin-bottom: 1.5rem;
    border-bottom: 1px solid #0F2037;
    display: flex; align-items: center; gap: 8px;
}
.sb-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; letter-spacing: 3px; color: #1E3A5F;
    text-transform: uppercase; margin: 1.5rem 0 0.8rem;
}
.sb-info {
    background: #080F1E; border: 1px solid #0F2037;
    border-radius: 10px; padding: 0.9rem 1rem;
    font-size: 0.78rem; color: #334155; margin-bottom: 6px;
    line-height: 1.7;
}
.sb-info b { color: #2563EB; display: block; margin-bottom: 2px; font-size: 0.7rem; letter-spacing: 1px; }

.stSelectbox select { background: #080F1E !important; }
div[data-testid="stSelectbox"] > div { background: #080F1E !important; border-color: #0F2037 !important; }

/* ═══════════════════════ DIVIDER ═══════════════════════ */
.qrx-div { height: 1px; background: linear-gradient(90deg, transparent, #0F2037 20%, #0F2037 80%, transparent); margin: 2rem 0; }

/* Plotly transparent bg */
.js-plotly-plot .plotly { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "drug1" not in st.session_state:
    st.session_state.drug1 = "Aspirin"
if "drug2" not in st.session_state:
    st.session_state.drug2 = "Ibuprofen"


# ── HERO ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="qrx-hero">
    <div class="qrx-hero-grid"></div>
    <div class="qrx-hero-glow"></div>
    <div class="qrx-badge">QUANTUM · CHEMISTRY · VQE · DRUG SAFETY</div>
    <div class="qrx-title">Quantum<span class="accent">Rx</span></div>
    <div class="qrx-subtitle">
        First-principles quantum simulation of drug-drug interactions.
        Every molecule receives a unique quantum energy fingerprint — 
        no statistical ML, pure quantum physics.
    </div>
    <div class="qrx-chips">
        <div class="qrx-chip"><b>Algorithm</b> VQE</div>
        <div class="qrx-chip"><b>Circuit</b> TwoLocal 2-Qubit</div>
        <div class="qrx-chip"><b>Mapper</b> Pauli Operators</div>
        <div class="qrx-chip"><b>Data</b> PubChem REST API</div>
        <div class="qrx-chip"><b>Units</b> Hartree / kcal·mol⁻¹</div>
        <div class="qrx-chip"><b>Backend</b> Qiskit Statevector</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-head">⚛ QuantumRx</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-section">QUANTUM ENGINE</div>', unsafe_allow_html=True)
    backend   = st.selectbox("Backend", ["Statevector (Exact)", "QASM (Noisy)", "IBM Quantum Cloud"], index=0, label_visibility="collapsed")
    max_iter  = st.slider("VQE Iterations", 50, 500, 150, step=50, label_visibility="collapsed")
    optimizer = st.selectbox("Optimizer", ["COBYLA", "SPSA", "L-BFGS-B"], index=0, label_visibility="collapsed")

    st.markdown(f"""
    <div class="sb-info"><b>BACKEND</b>{backend}</div>
    <div class="sb-info"><b>OPTIMIZER</b>{optimizer} · {max_iter} iterations</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">EXAMPLE PAIRS</div>', unsafe_allow_html=True)
    examples = [
        ("Aspirin",    "Ibuprofen",    "⚠", "caution"),
        ("Warfarin",   "Aspirin",      "🚨", "danger"),
        ("Caffeine",   "Paracetamol",  "✅", "safe"),
        ("Metformin",  "Atorvastatin", "⚠", "caution"),
        ("Lisinopril", "Potassium",    "🚨", "danger"),
        ("Omeprazole", "Clopidogrel",  "⚠", "caution"),
    ]
    for d1, d2, icon, _ in examples:
        if st.button(f"{icon}  {d1} + {d2}", key=f"ex_{d1}_{d2}"):
            st.session_state.drug1 = d1
            st.session_state.drug2 = d2
            st.rerun()

    st.markdown('<div class="sb-section">PROJECT INFO</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-info"><b>BUILT AT</b>IISc QCTar Workshop<br>March 2026 · Bengaluru</div>
    <div class="sb-info"><b>STACK</b>Qiskit · Streamlit<br>Plotly · PubChem API</div>
    <div class="sb-info"><b>DISCLAIMER</b>Educational research only.<br>Not for medical decisions.</div>
    """, unsafe_allow_html=True)


# ── INPUT ──────────────────────────────────────────────────────────────────────
col_a, col_plus, col_b, col_btn = st.columns([4, 0.5, 4, 2.5])

with col_a:
    st.markdown('<div class="card-title">DRUG  A</div>', unsafe_allow_html=True)
    drug1 = st.text_input("d1", value=st.session_state.drug1,
                           placeholder="e.g. Aspirin, Warfarin, Metformin",
                           label_visibility="collapsed", key="inp_d1")

with col_plus:
    st.markdown("<div style='padding-top:1.5rem;text-align:center;font-family:JetBrains Mono;font-size:1.5rem;color:#0F2037'>+</div>", unsafe_allow_html=True)

with col_b:
    st.markdown('<div class="card-title">DRUG  B</div>', unsafe_allow_html=True)
    drug2 = st.text_input("d2", value=st.session_state.drug2,
                           placeholder="e.g. Ibuprofen, Paracetamol, Atorvastatin",
                           label_visibility="collapsed", key="inp_d2")

with col_btn:
    st.markdown("<div style='padding-top:1.25rem'>", unsafe_allow_html=True)
    run = st.button("⚛  SIMULATE", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── SIMULATION ─────────────────────────────────────────────────────────────────
if run:
    if not drug1.strip() or not drug2.strip():
        st.error("Enter both drug names.")
        st.stop()

    st.markdown('<div class="qrx-div"></div>', unsafe_allow_html=True)

    # Pipeline progress
    prog   = st.progress(0)
    status = st.empty()

    def tick(pct, txt):
        prog.progress(pct)
        status.markdown(f"<div style='font-family:JetBrains Mono;font-size:0.78rem;color:#1E3A5F;padding:6px 0'>▸ {txt}</div>", unsafe_allow_html=True)

    tick(8,  f"Querying PubChem API · {drug1.strip()}")
    mol1 = fetch_molecule_data(drug1.strip())
    tick(16, f"Querying PubChem API · {drug2.strip()}")
    mol2 = fetch_molecule_data(drug2.strip())

    if not mol1:
        st.error(f"❌ Could not find **{drug1}**. Use the generic name (e.g. 'Ibuprofen' not 'Advil').")
        st.stop()
    if not mol2:
        st.error(f"❌ Could not find **{drug2}**. Use the generic name.")
        st.stop()

    tick(30, f"Building qubit Hamiltonian · {mol1['name']}")
    ham1  = build_hamiltonian(mol1)
    tick(40, f"Building qubit Hamiltonian · {mol2['name']}")
    ham2  = build_hamiltonian(mol2)
    tick(50, "Building combined interaction Hamiltonian")
    hamc  = build_hamiltonian(mol1, mol2, combined=True)

    tick(60, f"Running VQE · {optimizer} · {mol1['name']}")
    e1    = run_vqe(ham1, optimizer=optimizer, max_iter=max_iter)
    tick(72, f"Running VQE · {optimizer} · {mol2['name']}")
    e2    = run_vqe(ham2, optimizer=optimizer, max_iter=max_iter)
    tick(84, "Running VQE · Combined system")
    ecomb = run_vqe(hamc, optimizer=optimizer, max_iter=max_iter)

    tick(94, "Calculating ΔE and classifying risk level")
    time.sleep(0.3)
    delta_e = analyze_interaction(e1, e2, ecomb)
    risk_level, risk_label, risk_explanation = get_risk_level(delta_e)

    prog.progress(100)
    status.empty()
    time.sleep(0.2)
    prog.empty()

    delta_kcal = delta_e * 627.5
    binding    = "Strong" if abs(delta_e) > 0.02 else "Moderate" if abs(delta_e) > 0.005 else "Weak"

    css_map   = {"SAFE": "verdict-safe",    "CAUTION": "verdict-caution",  "DANGEROUS": "verdict-danger"}
    color_map = {"SAFE": "#10B981",         "CAUTION": "#F59E0B",           "DANGEROUS": "#EF4444"}
    icon_map  = {"SAFE": "✅",              "CAUTION": "⚠️",               "DANGEROUS": "🚨"}
    badge_map = {"SAFE": "badge-safe",      "CAUTION": "badge-caution",     "DANGEROUS": "badge-danger"}

    # ── Save history ──────────────────────────────────────────────────────────
    st.session_state.history.insert(0, {
        "drugs": f"{mol1['name']} + {mol2['name']}",
        "delta_e": delta_e,
        "delta_kcal": delta_kcal,
        "risk": risk_level,
        "binding": binding,
    })
    if len(st.session_state.history) > 8:
        st.session_state.history = st.session_state.history[:8]


    # ══════════════════════ SECTION: MOLECULAR PROFILES ══════════════════════
    st.markdown('<div class="card-title" style="margin-top:2rem">MOLECULAR PROFILES</div>', unsafe_allow_html=True)
    p1, p2 = st.columns(2)

    def mol_card(mol, energy, col):
        with col:
            st.markdown(f"""
            <div class="mol-card">
                <div class="mol-name">💊 {mol['name'].upper()}</div>
                <div class="mol-row"><span class="mol-key">Molecular Formula</span><span class="mol-val">{mol['formula']}</span></div>
                <div class="mol-row"><span class="mol-key">Molecular Weight</span><span class="mol-val">{mol['weight']} g/mol</span></div>
                <div class="mol-row"><span class="mol-key">Heavy Atoms</span><span class="mol-val">{mol['atom_count']}</span></div>
                <div class="mol-row"><span class="mol-key">PubChem CID</span><span class="mol-val">{mol['cid']}</span></div>
                <div class="mol-row" style="border:none"><span class="mol-key">VQE Ground State</span>
                    <span style="font-family:JetBrains Mono;font-size:0.78rem;color:#38BDF8">{energy:+.6f} Ha</span>
                </div>
            </div>""", unsafe_allow_html=True)

    mol_card(mol1, e1, p1)
    mol_card(mol2, e2, p2)


    # ══════════════════════ SECTION: METRICS ══════════════════════
    st.markdown('<div class="card-title" style="margin-top:2rem">QUANTUM METRICS</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-box">
            <span class="metric-num">{delta_e:+.5f}</span>
            <span class="metric-lbl">ΔE  (Hartree)</span>
        </div>
        <div class="metric-box">
            <span class="metric-num">{delta_kcal:+.2f}</span>
            <span class="metric-lbl">ΔE  (kcal · mol⁻¹)</span>
        </div>
        <div class="metric-box">
            <span class="metric-num">{ecomb:+.5f}</span>
            <span class="metric-lbl">E(AB)  Combined</span>
        </div>
        <div class="metric-box">
            <span class="metric-num" style="color:{'#10B981' if risk_level=='SAFE' else '#F59E0B' if risk_level=='CAUTION' else '#EF4444'}">{binding}</span>
            <span class="metric-lbl">Binding Strength</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # ══════════════════════ SECTION: VERDICT ══════════════════════
    st.markdown('<div class="card-title">INTERACTION VERDICT</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="verdict-card {css_map[risk_level]}">
        <div class="verdict-label" style="color:{color_map[risk_level]}">{icon_map[risk_level]} {risk_label}</div>
        <div class="verdict-text">{risk_explanation}</div>
    </div>""", unsafe_allow_html=True)


    # ══════════════════════ SECTION: CHARTS ══════════════════════
    st.markdown('<div class="card-title" style="margin-top:2rem">ENERGY ANALYSIS</div>', unsafe_allow_html=True)
    ch1, ch2, ch3 = st.columns([2.5, 2, 2])

    PLOT_BG   = "rgba(0,0,0,0)"
    PAPER_BG  = "rgba(0,0,0,0)"
    FONT      = dict(family="JetBrains Mono", color="#334155", size=11)
    GRID      = "#0A1628"

    # Bar chart
    with ch1:
        fig_bar = go.Figure()
        labels = [mol1['name'], mol2['name'], "Combined AB"]
        vals   = [abs(e1), abs(e2), abs(ecomb)]
        bar_c  = ["#2563EB", "#3B82F6",
                  "#10B981" if risk_level=="SAFE" else "#F59E0B" if risk_level=="CAUTION" else "#EF4444"]
        for i, (lbl, val, c) in enumerate(zip(labels, vals, bar_c)):
            fig_bar.add_trace(go.Bar(
                name=lbl, x=[lbl], y=[val],
                marker=dict(color=c, opacity=0.85, line=dict(width=0)),
                text=[f"{val:.5f} Ha"], textposition="outside",
                textfont=dict(family="JetBrains Mono", size=10, color="#334155"),
            ))
        fig_bar.update_layout(
            title=dict(text="Ground State Energies", font=dict(family="JetBrains Mono", size=12, color="#1E3A5F")),
            paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
            font=FONT, showlegend=False, barmode="group",
            yaxis=dict(gridcolor=GRID, title="|E| (Ha)", title_font=dict(size=10, color="#1E3A5F"),
                       tickfont=dict(size=9), color="#1E3A5F"),
            xaxis=dict(tickfont=dict(size=10), color="#1E3A5F"),
            height=300, margin=dict(t=40, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # Gauge
    with ch2:
        gauge_val = min(abs(delta_kcal), 20)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=gauge_val,
            delta=dict(reference=3.1, valueformat=".2f",
                       font=dict(family="JetBrains Mono", size=12),
                       increasing=dict(color="#EF4444"), decreasing=dict(color="#10B981")),
            number=dict(suffix=" kcal/mol", font=dict(family="JetBrains Mono", color=color_map[risk_level], size=15)),
            gauge=dict(
                axis=dict(range=[0, 20], tickfont=dict(family="JetBrains Mono", size=9, color="#334155"),
                          dtick=5, tickcolor="#0F2037"),
                bar=dict(color=color_map[risk_level], thickness=0.25),
                bgcolor="rgba(0,0,0,0)", borderwidth=0,
                steps=[
                    dict(range=[0, 3.1],   color="rgba(16,185,129,0.06)"),
                    dict(range=[3.1, 12.6], color="rgba(245,158,11,0.06)"),
                    dict(range=[12.6, 20],  color="rgba(239,68,68,0.06)"),
                ],
                threshold=dict(line=dict(color=color_map[risk_level], width=2), thickness=0.75, value=gauge_val)
            ),
            title=dict(text="Interaction Strength", font=dict(family="JetBrains Mono", color="#1E3A5F", size=12))
        ))
        fig_g.update_layout(paper_bgcolor=PAPER_BG, height=300, margin=dict(t=40, b=0, l=20, r=20))
        st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False})

    # Radar chart — molecular property comparison
    with ch3:
        w_max = max(float(mol1['weight']), float(mol2['weight']), 1)
        a_max = max(mol1['atom_count'], mol2['atom_count'], 1)
        cats  = ['Mol. Weight', 'Atom Count', 'Energy Scale', 'Complexity', 'Interaction']
        r1 = [
            float(mol1['weight'])/w_max,
            mol1['atom_count']/a_max,
            min(abs(e1)/0.5, 1),
            min(mol1['atom_count']/30, 1),
            min(abs(delta_e)*50, 1)
        ]
        r2 = [
            float(mol2['weight'])/w_max,
            mol2['atom_count']/a_max,
            min(abs(e2)/0.5, 1),
            min(mol2['atom_count']/30, 1),
            min(abs(delta_e)*50, 1)
        ]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=r1+[r1[0]], theta=cats+[cats[0]],
            fill='toself', name=mol1['name'],
            line=dict(color='#2563EB', width=1.5),
            fillcolor='rgba(37,99,235,0.08)'))
        fig_r.add_trace(go.Scatterpolar(r=r2+[r2[0]], theta=cats+[cats[0]],
            fill='toself', name=mol2['name'],
            line=dict(color='#38BDF8', width=1.5),
            fillcolor='rgba(56,189,248,0.06)'))
        fig_r.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0,1], tickfont=dict(size=8, color="#1E3A5F"),
                                gridcolor="#0A1628", linecolor="#0A1628"),
                angularaxis=dict(tickfont=dict(family="JetBrains Mono", size=9, color="#334155"),
                                 linecolor="#0F2037", gridcolor="#0F2037"),
            ),
            paper_bgcolor=PAPER_BG,
            showlegend=True,
            legend=dict(font=dict(family="JetBrains Mono", size=9, color="#334155"),
                        bgcolor="rgba(0,0,0,0)", x=0.8, y=1.1),
            title=dict(text="Molecular Properties", font=dict(family="JetBrains Mono", color="#1E3A5F", size=12)),
            height=300, margin=dict(t=40, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar": False})


    # ══════════════════════ SECTION: ENERGY TERMINAL ══════════════════════
    st.markdown('<div class="card-title" style="margin-top:2rem">ENERGY TERMINAL</div>', unsafe_allow_html=True)
    risk_cls = {"SAFE": "tl-safe", "CAUTION": "tl-warn", "DANGEROUS": "tl-danger"}[risk_level]
    st.markdown(f"""
    <div class="qrx-terminal">
        <div class="terminal-bar">
            <span class="td" style="background:#FF5F57"></span>
            <span class="td" style="background:#FEBC2E"></span>
            <span class="td" style="background:#28C840"></span>
            <span style="font-family:JetBrains Mono;font-size:0.68rem;color:#1E3A5F;margin-left:8px">
                quantumrx · vqe_engine · {optimizer} · {max_iter}iter
            </span>
        </div>
        <div class="terminal-body">
<span class="tl-dim">╔══════════════════════════════════════════════════════════╗</span>
<span class="tl-dim">║</span>  <span class="tl-key">session</span>    <span class="tl-val">quantum_drug_analysis</span>                         <span class="tl-dim">║</span>
<span class="tl-dim">╚══════════════════════════════════════════════════════════╝</span>

<span class="tl-key">molecule_a   </span><span class="tl-dim">│</span> <span class="tl-val">{mol1['name']}</span>
<span class="tl-key">  formula    </span><span class="tl-dim">│</span> <span class="tl-val">{mol1['formula']}</span>
<span class="tl-key">  weight     </span><span class="tl-dim">│</span> <span class="tl-val">{mol1['weight']} g/mol</span>

<span class="tl-key">molecule_b   </span><span class="tl-dim">│</span> <span class="tl-val">{mol2['name']}</span>
<span class="tl-key">  formula    </span><span class="tl-dim">│</span> <span class="tl-val">{mol2['formula']}</span>
<span class="tl-key">  weight     </span><span class="tl-dim">│</span> <span class="tl-val">{mol2['weight']} g/mol</span>

<span class="tl-dim">──────────────┬──────────────────────────────────────────────</span>
<span class="tl-key">E(A)          </span><span class="tl-dim">│</span> <span class="tl-val">{e1:+.10f} Ha</span>
<span class="tl-key">E(B)          </span><span class="tl-dim">│</span> <span class="tl-val">{e2:+.10f} Ha</span>
<span class="tl-key">E(A) + E(B)   </span><span class="tl-dim">│</span> <span class="tl-val">{(e1+e2):+.10f} Ha</span>
<span class="tl-key">E(AB)         </span><span class="tl-dim">│</span> <span class="tl-val">{ecomb:+.10f} Ha</span>
<span class="tl-dim">──────────────┼──────────────────────────────────────────────</span>
<span class="tl-key">ΔE (Ha)       </span><span class="tl-dim">│</span> <span class="tl-hi">{delta_e:+.10f} Ha</span>
<span class="tl-key">ΔE (kcal/mol) </span><span class="tl-dim">│</span> <span class="tl-hi">{delta_kcal:+.4f} kcal · mol⁻¹</span>
<span class="tl-key">binding       </span><span class="tl-dim">│</span> <span class="tl-val">{binding}</span>
<span class="tl-key">risk_level    </span><span class="tl-dim">│</span> <span class="{risk_cls}">{risk_level}</span>
        </div>
    </div>""", unsafe_allow_html=True)


    # ══════════════════════ SECTION: VQE CIRCUIT ══════════════════════
    st.markdown('<div class="card-title" style="margin-top:2rem">VQE ANSATZ CIRCUIT</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="qrx-circuit">
        <span style="color:#1E3A5F">  TwoLocal Ansatz  ·  2 qubits  ·  reps=2  ·  linear entanglement</span>
        <br><br>
        <span style="color:#38BDF8">  q₀</span><span style="color:#1E3A5F"> ─</span>┤<span style="color:#F1F5F9">Ry(θ₀)</span>├─┤<span style="color:#F1F5F9">Rz(θ₁)</span>├─<span style="color:#F1F5F9">●</span>───────────────────┤<span style="color:#F1F5F9">Ry(θ₄)</span>├─┤<span style="color:#F1F5F9">Rz(θ₅)</span>├─<span style="color:#10B981">┤M├</span>─
        <br>
        <span style="color:#1E3A5F">        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│</span>
        <br>
        <span style="color:#38BDF8">  q₁</span><span style="color:#1E3A5F"> ─</span>┤<span style="color:#F1F5F9">Ry(θ₂)</span>├─┤<span style="color:#F1F5F9">Rz(θ₃)</span>├─<span style="color:#F1F5F9">⊕</span>───────────────────┤<span style="color:#F1F5F9">Ry(θ₆)</span>├─┤<span style="color:#F1F5F9">Rz(θ₇)</span>├─<span style="color:#10B981">┤M├</span>─
        <br><br>
        <span style="color:#1E3A5F">  Parameters  θ₀..θ₇  optimized by  </span><span style="color:#38BDF8">{optimizer}</span><span style="color:#1E3A5F">  to minimize  ⟨ψ(θ)|H|ψ(θ)⟩</span>
        <br>
        <span style="color:#1E3A5F">  Convergence  ·  max_iter={max_iter}  ·  backend={backend}</span>
    </div>""", unsafe_allow_html=True)


    # ══════════════════════ SECTION: HISTORY ══════════════════════
    if len(st.session_state.history) > 1:
        st.markdown('<div class="card-title" style="margin-top:2rem">SIMULATION HISTORY</div>', unsafe_allow_html=True)
        st.markdown('<div class="card" style="padding:0;overflow:hidden">', unsafe_allow_html=True)
        st.markdown("""
        <div class="history-row" style="border-bottom:1px solid #0F2037">
            <span style="font-family:JetBrains Mono;font-size:0.65rem;letter-spacing:2px;color:#1E3A5F;flex:1">DRUG PAIR</span>
            <span style="font-family:JetBrains Mono;font-size:0.65rem;letter-spacing:2px;color:#1E3A5F;width:180px">ΔE</span>
            <span style="font-family:JetBrains Mono;font-size:0.65rem;letter-spacing:2px;color:#1E3A5F;width:100px">RISK</span>
        </div>""", unsafe_allow_html=True)
        for h in st.session_state.history:
            st.markdown(f"""
            <div class="history-row">
                <span class="history-drugs">{h['drugs']}</span>
                <span class="history-de">{h['delta_e']:+.5f} Ha &nbsp;·&nbsp; {h['delta_kcal']:+.2f} kcal/mol</span>
                <span class="history-badge {badge_map[h['risk']]}">{h['risk']}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("⚠️ **Research Only** — Simplified quantum simulation for educational purposes. Never use for actual medical decisions. Always consult a licensed healthcare professional.")


# ── LANDING STATE ──────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style='text-align:center;padding:5rem 2rem;background:#080F1E;
    border:1px solid #0F2037;border-radius:18px;margin-top:1.5rem;'>
        <div style='font-size:4rem;margin-bottom:1.5rem;opacity:0.4'>⚛</div>
        <div style='font-family:JetBrains Mono;font-size:0.85rem;letter-spacing:3px;
        color:#1E3A5F;margin-bottom:1rem;'>AWAITING SIMULATION</div>
        <div style='color:#1E3A5F;font-size:0.88rem;max-width:420px;
        margin:0 auto;line-height:2;font-family:JetBrains Mono;'>
        Enter two drug names above<br>
        and click <span style="color:#2563EB">⚛ SIMULATE</span><br>
        to run the quantum pipeline
        </div>
    </div>""", unsafe_allow_html=True)