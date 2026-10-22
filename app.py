"""EveWatch: Streamlit Web Application (Enhanced Edition).

Interactive Quantum Key Distribution (BB84) simulation, real-time security operations
dashboard, dynamic quantum channel visualization, and threat detection visualizer.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from bb84.protocol import run_bb84, BB84Result
from bb84.noise import get_fake_backend_noise_model
from bb84.analysis import (
    asymptotic_secret_key_rate,
    theoretical_qber,
    binomial_detection_probabilities,
)
from bb84.postprocessing import (
    reconcile_errors_parity,
    amplify_privacy,
    encrypt_message_otp,
    decrypt_message_otp,
)

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="EveWatch | Quantum Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 0.8rem;">
        <div style="font-size: 2.2rem; filter: drop-shadow(0 0 10px #00e5ff);">🛡️⚡</div>
        <div style="font-size: 1.4rem; font-weight: 800; background: linear-gradient(135deg, #00e5ff, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            EVEWATCH SOC
        </div>
        <div style="font-size: 0.75rem; letter-spacing: 1.5px; color: #94a3b8; text-transform: uppercase;">
            Quantum Security Console
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("### 🎛️ Simulation Parameters")

num_qubits = st.sidebar.slider(
    "Total Transmitted Qubits (N)",
    min_value=20,
    max_value=1000,
    value=100,
    step=20,
    help="Total single-photon pulses prepared by Alice.",
)

seed_input = st.sidebar.number_input(
    "Random Seed (Reproducibility)",
    value=42,
    step=1,
    help="Fixed seed guarantees 100% deterministic results across runs.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### 🕵️ Adversary / Eavesdropper (Eve)")
eve_active = st.sidebar.checkbox("Activate Eve (Intercept-Resend)", value=False)
eve_fraction = st.sidebar.slider(
    "Interception Fraction (f)",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.05,
    disabled=not eve_active,
    help="Probability that Eve intercepts a transmitted flying qubit.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### ⚡ Optical & Hardware Noise")
noise_preset = st.sidebar.selectbox(
    "Noise Model Preset",
    ["Custom Parametric", "IBM FakeBrisbane (Calibrated 127Q)"],
)

if noise_preset == "Custom Parametric":
    channel_noise = st.sidebar.slider(
        "Optical Channel Noise (p_ch)",
        min_value=0.0,
        max_value=0.30,
        value=0.0,
        step=0.01,
        help="Depolarizing noise on the optical fiber transmission.",
    )
    depol_gate = st.sidebar.slider(
        "Gate Depolarizing Error",
        min_value=0.0,
        max_value=0.05,
        value=0.0,
        step=0.005,
    )
    readout_error = st.sidebar.slider(
        "Measurement Readout Error",
        min_value=0.0,
        max_value=0.05,
        value=0.0,
        step=0.005,
    )
    fake_backend_noise = None
else:
    channel_noise = 0.0
    depol_gate = 0.0
    readout_error = 0.0
    fake_backend_noise, desc = get_fake_backend_noise_model("FakeBrisbane")
    st.sidebar.info(f"Loaded: {desc}")

st.sidebar.markdown("---")
st.sidebar.markdown("#### ⚙️ Security Thresholds")
abort_threshold = st.sidebar.slider(
    "Security Abort Threshold (QBER)",
    min_value=0.05,
    max_value=0.25,
    value=0.11,
    step=0.01,
    help="Asymptotic Shor-Preskill bound cutoff is 11.0%.",
)

sample_fraction = st.sidebar.slider(
    "Sacrificed Sample Ratio",
    min_value=0.1,
    max_value=0.8,
    value=0.5,
    step=0.05,
    help="Proportion of sifted key sacrificed for QBER verification.",
)

st.sidebar.markdown("---")
show_bg_animation = st.sidebar.checkbox("🌌 Quantum Particle Background", value=True)
show_circuit_diagram = st.sidebar.checkbox("📐 Compile Qiskit Circuit Diagram", value=True)

run_button = st.sidebar.button("🚀 Run BB84 Protocol", type="primary", use_container_width=True)

# ---------------------------------------------------------
# Dynamic Cyberpunk / Quantum Theme & Animated Canvas
# ---------------------------------------------------------
bg_canvas_html = """
<div id="quantum-bg-canvas-wrap">
    <canvas id="quantum-canvas"></canvas>
    <div class="quantum-scanlines"></div>
</div>
<script>
(function() {
    const canvas = document.getElementById('quantum-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const count = Math.min(50, Math.floor(width / 30));
    for (let i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.8,
            vy: (Math.random() - 0.5) * 0.8,
            radius: Math.random() * 2 + 1,
            color: Math.random() > 0.5 ? 'rgba(0, 229, 255, ' : 'rgba(168, 85, 247, '
        });
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0) p.x = width;
            if (p.x > width) p.x = 0;
            if (p.y < 0) p.y = height;
            if (p.y > height) p.y = 0;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.color + '0.7)';
            ctx.shadowBlur = 8;
            ctx.shadowColor = p.color + '0.9)';
            ctx.fill();

            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 130) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    const alpha = (1 - dist / 130) * 0.25;
                    ctx.strokeStyle = p.color + alpha + ')';
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }
    animate();
})();
</script>
""" if show_bg_animation else ""

st.markdown(
    f"""
    <style>
    /* Dark Glassmorphic Theme Overrides */
    .stApp {{
        background: radial-gradient(circle at 50% 15%, #0f172a 0%, #030712 100%) !important;
        color: #f1f5f9;
    }}
    
    #quantum-bg-canvas-wrap {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 0;
        pointer-events: none;
        overflow: hidden;
    }}
    
    #quantum-canvas {{
        width: 100%;
        height: 100%;
        opacity: 0.65;
    }}

    .quantum-scanlines {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
        background-size: 100% 3px, 4px 100%;
        pointer-events: none;
    }}

    /* Card styling */
    .glass-card {{
        background: rgba(15, 23, 42, 0.72) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 229, 255, 0.18);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 15px rgba(0, 229, 255, 0.04);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .glass-card:hover {{
        border-color: rgba(0, 229, 255, 0.4);
    }}

    .hero-title {{
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00e5ff 0%, #38bdf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
        letter-spacing: -0.5px;
    }}

    .hero-badge {{
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-right: 0.4rem;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }}
    .badge-cyber {{
        background: rgba(0, 229, 255, 0.12);
        color: #38bdf8;
        border-color: rgba(56, 189, 248, 0.4);
    }}
    .badge-purple {{
        background: rgba(168, 85, 247, 0.12);
        color: #c084fc;
        border-color: rgba(192, 132, 252, 0.4);
    }}

    .pulse-orb {{
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 6px;
        box-shadow: 0 0 8px currentColor;
        animation: pulse 1.8s infinite;
    }}
    @keyframes pulse {{
        0% {{ transform: scale(0.95); opacity: 0.7; }}
        50% {{ transform: scale(1.3); opacity: 1; }}
        100% {{ transform: scale(0.95); opacity: 0.7; }}
    }}

    .status-banner-secure {{
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 78, 59, 0.3));
        border: 1.5px solid #10b981;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        color: #34d399;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
    }}
    .status-banner-abort {{
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(127, 29, 29, 0.3));
        border: 1.5px solid #ef4444;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        color: #f87171;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.3);
    }}

    .key-display {{
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        background: rgba(3, 7, 18, 0.85);
        color: #00e5ff;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        border: 1px solid rgba(0, 229, 255, 0.3);
        word-break: break-all;
        font-size: 0.95rem;
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.8);
    }}

    .photon-node {{
        display: inline-block;
        padding: 0.3rem 0.6rem;
        margin: 2px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.8rem;
    }}
    </style>
    {bg_canvas_html}
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Simulation Caching
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def execute_simulation(
    n: int,
    eve_on: bool,
    f: float,
    ch_noise: float,
    gate_noise: float,
    ro_noise: float,
    threshold: float,
    s_fraction: float,
    seed: int,
    use_fake: bool,
    save_circ: bool,
) -> BB84Result:
    """Run cached BB84 protocol execution."""
    active_noise = None
    if use_fake:
        active_noise, _ = get_fake_backend_noise_model("FakeBrisbane")

    return run_bb84(
        num_qubits=n,
        eve_present=eve_on,
        eve_fraction=f if eve_on else 0.0,
        noise_model=active_noise,
        channel_noise_prob=ch_noise,
        depolarizing_error_prob=gate_noise,
        readout_error_prob=ro_noise,
        sample_size=s_fraction,
        abort_threshold=threshold,
        seed=seed,
        save_circuit=save_circ,
    )


if "result" not in st.session_state or run_button:
    with st.spinner("⚡ Running Qiskit 2.x Clifford Circuit Simulation..."):
        st.session_state["result"] = execute_simulation(
            n=num_qubits,
            eve_on=eve_active,
            f=eve_fraction,
            ch_noise=channel_noise,
            gate_noise=depol_gate,
            ro_noise=readout_error,
            threshold=abort_threshold,
            s_fraction=sample_fraction,
            seed=seed_input,
            use_fake=(noise_preset != "Custom Parametric"),
            save_circ=show_circuit_diagram,
        )

res: BB84Result = st.session_state["result"]

# ---------------------------------------------------------
# Threat Speedometer Gauge Generator
# ---------------------------------------------------------
def create_threat_gauge(qber_val: float, threshold: float = 0.11) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=qber_val * 100,
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": "<b>QBER THREAT METER</b><br><span style='font-size:0.75em;color:#94a3b8'>Quantum Channel Error Level</span>",
                "font": {"size": 16, "color": "#f8fafc"},
            },
            delta={
                "reference": threshold * 100,
                "increasing": {"color": "#ef4444"},
                "decreasing": {"color": "#10b981"},
                "suffix": "% vs Cutoff",
            },
            number={
                "suffix": "%",
                "font": {
                    "size": 36,
                    "color": "#38bdf8" if qber_val <= threshold else "#f87171",
                },
            },
            gauge={
                "axis": {
                    "range": [0, 30],
                    "tickwidth": 1,
                    "tickcolor": "#94a3b8",
                    "ticksuffix": "%",
                },
                "bar": {
                    "color": "#ef4444" if qber_val > threshold else "#10b981",
                    "thickness": 0.28,
                },
                "bgcolor": "rgba(15, 23, 42, 0.6)",
                "borderwidth": 1.5,
                "bordercolor": "#334155",
                "steps": [
                    {"range": [0, 5], "color": "rgba(16, 185, 129, 0.2)"},
                    {"range": [5, 11], "color": "rgba(245, 158, 11, 0.2)"},
                    {"range": [11, 30], "color": "rgba(239, 68, 68, 0.28)"},
                ],
                "threshold": {
                    "line": {"color": "#f43f5e", "width": 3},
                    "thickness": 0.85,
                    "value": threshold * 100,
                },
            },
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc", "family": "sans-serif"},
        height=240,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    return fig


# ---------------------------------------------------------
# Header & Navigation
# ---------------------------------------------------------
col_title, col_meta = st.columns([2.5, 1.0])
with col_title:
    st.markdown('<div class="hero-title">🛡️ EVEWATCH</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size: 1.15rem; color: #94a3b8; margin-bottom: 0.8rem;">'
        '<b>Distinguishing Quantum Eavesdroppers from Hardware Noise in BB84</b>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <span class="hero-badge badge-cyber">Qiskit Fall Fest 2026</span>
        <span class="hero-badge badge-purple">IBM Quantum Track</span>
        <span class="hero-badge badge-cyber">MPSTME, NMIMS Mumbai</span>
        """,
        unsafe_allow_html=True,
    )

with col_meta:
    if res.aborted:
        st.markdown(
            """
            <div style="text-align: right; margin-top: 0.8rem;">
                <span class="pulse-orb" style="color: #ef4444; background: #ef4444;"></span>
                <span style="font-weight: 800; color: #f87171; letter-spacing: 1px;">THREAT DETECTED / HALTED</span>
                <div style="font-size: 0.8rem; color: #94a3b8;">Channel untrusted (QBER > 11%)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="text-align: right; margin-top: 0.8rem;">
                <span class="pulse-orb" style="color: #10b981; background: #10b981;"></span>
                <span style="font-weight: 800; color: #34d399; letter-spacing: 1px;">QUANTUM SECURE ACTIVE</span>
                <div style="font-size: 0.8rem; color: #94a3b8;">Link Integrity Verified (QBER ≤ 11%)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

tab_demo, tab_exp, tab_msg, tab_edu = st.tabs([
    "🔬 Interactive Quantum Run",
    "📊 Empirical Research Benchmarks",
    "💬 Secure One-Time Pad Chat",
    "📚 How BB84 Works (Simple Guide)",
])

# =========================================================
# TAB 1: PROTOCOL DEMO
# =========================================================
with tab_demo:
    # Top Row: Visual Channel Pipeline Diagram
    eve_status_color = "#ef4444" if (eve_active and eve_fraction > 0) else "#10b981"
    eve_status_text = f"INTERCEPTING ({eve_fraction*100:.0f}%)" if (eve_active and eve_fraction > 0) else "BYPASSED / SAFE"
    
    st.markdown(
        f"""
        <div class="glass-card" style="padding: 1rem 1.5rem; margin-bottom: 1.2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <!-- Alice Node -->
                <div style="flex: 1; min-width: 180px; text-align: center; border-right: 1px dashed rgba(255,255,255,0.15); padding-right: 1rem;">
                    <div style="font-size: 1.6rem;">👩‍💻</div>
                    <div style="font-weight: 800; color: #38bdf8;">ALICE (SENDER)</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Laser Pulse Prep</div>
                    <div style="font-size: 0.85rem; color: #38bdf8; font-weight: 600; margin-top: 4px;">{res.num_qubits} Qubits Encoded</div>
                </div>
                <!-- Transit Channel & Eve -->
                <div style="flex: 2; min-width: 280px; text-align: center; padding: 0 1rem;">
                    <div style="font-size: 0.85rem; letter-spacing: 1px; color: #94a3b8; margin-bottom: 4px;">
                        OPTICAL FIBER CHANNEL (λ = 1550nm)
                    </div>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                        <span style="height: 3px; flex: 1; background: linear-gradient(90deg, #38bdf8, {eve_status_color}); border-radius: 2px;"></span>
                        <span style="border: 1px solid {eve_status_color}; background: rgba(15,23,42,0.9); padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; color: {eve_status_color};">
                            🕵️ EVE: {eve_status_text}
                        </span>
                        <span style="height: 3px; flex: 1; background: linear-gradient(90deg, {eve_status_color}, #c084fc); border-radius: 2px;"></span>
                    </div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">
                        Channel Noise: {channel_noise*100:.1f}% | Mode: {noise_preset}
                    </div>
                </div>
                <!-- Bob Node -->
                <div style="flex: 1; min-width: 180px; text-align: center; border-left: 1px dashed rgba(255,255,255,0.15); padding-left: 1rem;">
                    <div style="font-size: 1.6rem;">👨‍💻</div>
                    <div style="font-weight: 800; color: #c084fc;">BOB (RECEIVER)</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">SPAD Detector & Sifting</div>
                    <div style="font-size: 0.85rem; color: #c084fc; font-weight: 600; margin-top: 4px;">{len(res.sifted_indices)} Sifted Bits ({len(res.sifted_indices)/res.num_qubits*100:.1f}%)</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Row 2: Status Banner & Speedometer Threat Gauge
    col_banner, col_gauge = st.columns([1.5, 1.0])
    with col_banner:
        if res.aborted:
            st.markdown(
                f"""
                <div class="status-banner-abort">
                    <div style="font-size: 1.3rem; font-weight: 900; margin-bottom: 0.3rem;">
                        🚨 PROTOCOL ABORTED: Threat Detected!
                    </div>
                    <div>
                        Observed sample QBER of <b>{res.qber_sample * 100:.2f}%</b> breached the security cutoff of <b>{res.abort_threshold * 100:.1f}%</b>.
                    </div>
                    <div style="font-size: 0.85rem; color: #fca5a5; margin-top: 0.5rem;">
                        • The mutual information leaked to Eve or channel exceeds allowable bounds.<br>
                        • Quantum transmission was unconditionally aborted to prevent compromised keys.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="status-banner-secure">
                    <div style="font-size: 1.3rem; font-weight: 900; margin-bottom: 0.3rem;">
                        ✅ PROTOCOL SECURE: Quantum Channel Trusted!
                    </div>
                    <div>
                        Observed sample QBER of <b>{res.qber_sample * 100:.2f}%</b> is strictly within the <b>{res.abort_threshold * 100:.1f}%</b> security limit.
                    </div>
                    <div style="font-size: 0.85rem; color: #6ee7b7; margin-top: 0.5rem;">
                        • Information-theoretic secrecy guarantees zero meaningful eavesdropping.<br>
                        • Raw key successfully prepared for classical error correction & OTP encryption.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        # 4 Mini Metric Cards
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Transmitted Qubits", f"{res.num_qubits}")
        k2.metric("Sifted Matches", f"{len(res.sifted_indices)}", f"{len(res.sifted_indices)/res.num_qubits*100:.0f}% yield")
        k3.metric("Sacrificed Sample", f"{len(res.sample_indices)} bits")
        k4.metric("Net Secret Bits", f"{len(res.alice_key)} bits")

    with col_gauge:
        st.plotly_chart(create_threat_gauge(res.qber_sample, res.abort_threshold), use_container_width=True)

    st.markdown("---")

    # Step-by-Step Table with Single-Qubit Inspector
    st.subheader("🔍 Transmission Log & Single-Photon Inspector")
    st.caption("Inspect individual quantum states, basis rotations, eavesdropper collapse, and measurement outcomes.")

    # Single-Qubit Inspector Slider
    inspect_idx = st.slider(
        "Inspect Specific Qubit Index (#):",
        min_value=0,
        max_value=res.num_qubits - 1,
        value=0,
        help="Select any photon to inspect its exact quantum state and transformations.",
    )

    basis_names = {0: "Z (Computational: |0⟩ / |1⟩)", 1: "X (Hadamard: |+⟩ / |-⟩)"}
    a_bit = int(res.alice_bits[inspect_idx])
    a_basis = int(res.alice_bases[inspect_idx])
    b_basis = int(res.bob_bases[inspect_idx])
    b_bit = int(res.bob_bits[inspect_idx])
    eve_int = bool(res.eve_intercepted[inspect_idx]) if len(res.eve_intercepted) > inspect_idx else False
    eve_b = int(res.eve_bases[inspect_idx]) if eve_int else None
    eve_m = int(res.eve_bits[inspect_idx]) if eve_int else None

    state_symbols = {
        (0, 0): "|0⟩ (Vertical Polarization 0°)",
        (1, 0): "|1⟩ (Horizontal Polarization 90°)",
        (0, 1): "|+⟩ (Diagonal Polarization +45°)",
        (1, 1): "|-⟩ (Anti-Diagonal Polarization -45°)",
    }

    c_ins1, c_ins2, c_ins3 = st.columns(3)
    with c_ins1:
        st.markdown(
            f"""
            <div class="glass-card" style="border-color: #38bdf8;">
                <div style="font-weight: 800; color: #38bdf8;">👩‍💻 ALICE'S EMISSION (Qubit #{inspect_idx})</div>
                <div style="font-size: 1.1rem; margin-top: 6px;"><b>Bit:</b> <code>{a_bit}</code> | <b>Basis:</b> <code>{basis_names[a_basis]}</code></div>
                <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">Prepared State: <b>{state_symbols.get((a_bit, a_basis), "Unknown")}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_ins2:
        eve_card_border = "#ef4444" if eve_int else "#334155"
        eve_info = f"<b>Intercepted:</b> YES 🚨<br><b>Eve Basis:</b> <code>{basis_names[eve_b]}</code><br><b>Eve Measured:</b> <code>{eve_m}</code> (Wavefunction collapsed!)" if eve_int else "<b>Intercepted:</b> No (Transmitted undisturbed)"
        st.markdown(
            f"""
            <div class="glass-card" style="border-color: {eve_card_border};">
                <div style="font-weight: 800; color: {'#ef4444' if eve_int else '#94a3b8'};">🕵️ EVE'S ACTION</div>
                <div style="font-size: 0.95rem; margin-top: 6px;">{eve_info}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_ins3:
        match_status = "MATCH ✅ (Retained during sifting)" if a_basis == b_basis else "MISMATCH ❌ (Discarded during sifting)"
        err_status = "BIT ERROR ⚠️" if (a_basis == b_basis and a_bit != b_bit) else "NO ERROR 🎯"
        st.markdown(
            f"""
            <div class="glass-card" style="border-color: #c084fc;">
                <div style="font-weight: 800; color: #c084fc;">👨‍💻 BOB'S MEASUREMENT</div>
                <div style="font-size: 0.95rem; margin-top: 6px;"><b>Bob Basis:</b> <code>{basis_names[b_basis]}</code></div>
                <div style="font-size: 0.95rem;"><b>Bob Measured:</b> <code>{b_bit}</code> | <b>Result:</b> {err_status}</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">Sifting: {match_status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Full Transmission Table
    table_rows = []
    limit = min(res.num_qubits, 100)
    sifted_set = set(res.sifted_indices)
    sample_set = set(res.sample_indices)
    key_set = set(res.key_indices)

    for i in range(limit):
        is_sifted = i in sifted_set
        is_sample = i in sample_set
        is_key = i in key_set
        eve_int_i = bool(res.eve_intercepted[i]) if len(res.eve_intercepted) > i else False
        is_err = bool(res.alice_bits[i] != res.bob_bits[i]) if is_sifted else None

        role = "Discarded (Basis Mismatch)"
        if is_sample:
            role = "Sampled (Sacrificed for QBER)"
        elif is_key:
            role = "Retained Secret Key"

        table_rows.append({
            "Qubit #": i,
            "Alice Bit": int(res.alice_bits[i]),
            "Alice Basis": "Z (0)" if res.alice_bases[i] == 0 else "X (1)",
            "Eve Tapped": "YES 🚨" if eve_int_i else "No",
            "Eve Basis": ("Z" if res.eve_bases[i] == 0 else "X") if eve_int_i else "-",
            "Bob Basis": "Z (0)" if res.bob_bases[i] == 0 else "X (1)",
            "Bob Measured": int(res.bob_bits[i]),
            "Sifted?": "MATCH ✅" if is_sifted else "Mismatch ❌",
            "Role": role,
            "Error Check": "ERROR ⚠️" if is_err else ("Match 🎯" if is_sifted else "-"),
        })

    df_table = pd.DataFrame(table_rows)
    st.dataframe(df_table, use_container_width=True, height=320)

    # Secret Key Display Box
    st.markdown("---")
    st.subheader("🔑 Final Distilled Secret Keys")
    k_col1, k_col2 = st.columns(2)
    with k_col1:
        st.markdown("**Alice's Retained Secret Key:**")
        a_key_str = "".join(str(int(b)) for b in res.alice_key)
        st.markdown(f'<div class="key-display">{a_key_str if a_key_str else "[Protocol Aborted / Key Emptied]"}</div>', unsafe_allow_html=True)

    with k_col2:
        st.markdown("**Bob's Retained Secret Key:**")
        b_key_str = "".join(str(int(b)) for b in res.bob_key)
        st.markdown(f'<div class="key-display">{b_key_str if b_key_str else "[Protocol Aborted / Key Emptied]"}</div>', unsafe_allow_html=True)

    if len(res.alice_key) > 0:
        match_rate = float(np.mean(res.alice_key == res.bob_key)) * 100
        st.caption(f"Raw Key Agreement: **{match_rate:.2f}%** | Distilled Key Length: **{len(res.alice_key)} bits**.")

    # Collapsible Qiskit Circuit Diagram
    if res.circuit is not None:
        with st.expander("📐 View Actual Qiskit Quantum Circuit (First 4 Qubits)"):
            try:
                from qiskit import QuantumCircuit
                # Render a clean sub-circuit of first 4 qubits for readability
                sub_qc = QuantumCircuit(4, 4)
                for q in range(min(4, res.num_qubits)):
                    if res.alice_bits[q] == 1:
                        sub_qc.x(q)
                    if res.alice_bases[q] == 1:
                        sub_qc.h(q)
                    if bool(res.eve_intercepted[q]):
                        if res.eve_bases[q] == 1:
                            sub_qc.h(q)
                        sub_qc.measure(q, q)
                        if res.eve_bases[q] == 1:
                            sub_qc.h(q)
                    sub_qc.id(q)
                    if res.bob_bases[q] == 1:
                        sub_qc.h(q)
                    sub_qc.measure(q, q)

                circ_text = str(sub_qc.draw(output="text"))
                st.code(circ_text, language="text")
                st.caption("Qiskit 2.x Clifford Circuit Architecture (Alice Encoding → Eve Mid-Circuit Interception → Channel Transit → Bob Measurement)")
            except Exception as e:
                st.warning(f"Circuit visualization notice: {e}")

# =========================================================
# TAB 2: EMPIRICAL EXPERIMENTS
# =========================================================
with tab_exp:
    st.subheader("📊 Empirical Research Benchmarks & Differentiator Analysis")
    st.markdown(
        """
        These results were generated across **hundreds of Monte Carlo quantum trials** simulating both
        environmental noise and intercept-resend attacks to answer the hackathon's differentiator question:
        *Can Alice and Bob tell an eavesdropper from hardware noise?*
        """
    )

    exp_choice = st.radio(
        "Select Empirical Benchmark to Inspect:",
        [
            "1. QBER vs. Eve Interception Fraction (0.25*f Validation)",
            "2. QBER vs. Channel Depolarizing Noise Level",
            "3. 2D Parameter Space Heatmap (Noise x Eve Fraction)",
            "4. Detection Reliability (False Alarm & Missed Detection Rates)",
            "5. Secret Key Rate & Distilled Yield (Shor-Preskill Bound)",
            "6. IBM Hardware Comparison (FakeBrisbane Calibrated)",
        ],
        horizontal=True,
    )

    results_path = ROOT_DIR / "results"

    if "1. QBER vs. Eve" in exp_choice:
        c_left, c_right = st.columns([1.5, 1.0])
        with c_left:
            img_file = results_path / "exp1_eve_fraction.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
        with c_right:
            st.markdown(
                """
                <div class="glass-card">
                    <div style="font-weight: 800; color: #38bdf8; font-size: 1.1rem; margin-bottom: 0.5rem;">
                        Key Empirical Findings
                    </div>
                    <ul style="font-size: 0.9rem; line-height: 1.6; padding-left: 1.2rem;">
                        <li><b>Theoretical Confirmation:</b> Measured QBER tracks <code>Q = 0.25 × f</code> perfectly.</li>
                        <li><b>Full Interception (f=1.0):</b> Yields <b>24.85% ± 2.80% QBER</b> across 50 trials.</li>
                        <li><b>The Blind Zone Risk:</b> When <code>f ≤ 0.44</code>, QBER remains below 11%. Eve can intercept 40% of traffic unnoticed without baseline noise calibration!</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            csv_file = results_path / "exp1_eve_fraction.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file), use_container_width=True, height=220)

    elif "2. QBER vs. Channel" in exp_choice:
        c_left, c_right = st.columns([1.5, 1.0])
        with c_left:
            img_file = results_path / "exp2_noise_level.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
        with c_right:
            st.markdown(
                """
                <div class="glass-card">
                    <div style="font-weight: 800; color: #c084fc; font-size: 1.1rem; margin-bottom: 0.5rem;">
                        Key Empirical Findings
                    </div>
                    <ul style="font-size: 0.9rem; line-height: 1.6; padding-left: 1.2rem;">
                        <li><b>Linear Degradation:</b> Depolarizing noise causes <code>Q ≈ 0.5 × p_ch</code>.</li>
                        <li><b>Critical Noise Limit:</b> At <code>p_ch ≈ 22.0%</code>, channel noise alone exceeds the 11% cutoff.</li>
                        <li><b>False Alarms:</b> In noisy fibers, legitimate transmissions get falsely aborted if noise isn't distinguished.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            csv_file = results_path / "exp2_noise_level.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file), use_container_width=True, height=220)

    elif "3. 2D Parameter Space" in exp_choice:
        c_left, c_right = st.columns([1.5, 1.0])
        with c_left:
            img_file = results_path / "exp3_qber_heatmap.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
        with c_right:
            st.markdown(
                """
                <div class="glass-card">
                    <div style="font-weight: 800; color: #f59e0b; font-size: 1.1rem; margin-bottom: 0.5rem;">
                        The Core Differentiator
                    </div>
                    <ul style="font-size: 0.9rem; line-height: 1.6; padding-left: 1.2rem;">
                        <li><b>The Ambiguity Frontier:</b> The dashed cyan contour marks the 11% Shor-Preskill limit.</li>
                        <li><b>Equifinality Dilemma:</b> A 9% QBER can be 18% channel noise (0% Eve) OR Eve tapping 36% of traffic on a clean line.</li>
                        <li><b>Resolution:</b> Physical error rates alone are ambiguous; statistical sample scaling is required.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            csv_file = results_path / "exp3_qber_heatmap.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file).head(12), use_container_width=True, height=220)

    elif "4. Detection Reliability" in exp_choice:
        c_left, c_right = st.columns([1.5, 1.0])
        with c_left:
            img_file = results_path / "exp4_detection_analysis.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
        with c_right:
            st.markdown(
                """
                <div class="glass-card">
                    <div style="font-weight: 800; color: #ef4444; font-size: 1.1rem; margin-bottom: 0.5rem;">
                        Sample Scaling Resolves Ambiguity
                    </div>
                    <ul style="font-size: 0.9rem; line-height: 1.6; padding-left: 1.2rem;">
                        <li><b>Small Sample Risk (K=50):</b> High variance produces <b>26% False Alarms</b> and <b>28% Missed Detections</b>!</li>
                        <li><b>Large Sample Power (K≥600):</b> Variance collapses as <code>1/√K</code>, reducing errors to <b>&lt; 2%</b>.</li>
                        <li>At <code>K=1200</code>, detection error is virtually <b>0.0%</b>.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            csv_file = results_path / "exp4_detection_analysis.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file), use_container_width=True, height=220)

    elif "5. Secret Key Rate" in exp_choice:
        c_left, c_right = st.columns([1.5, 1.0])
        with c_left:
            img_file = results_path / "exp5_key_rate.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
        with c_right:
            st.markdown(
                """
                <div class="glass-card">
                    <div style="font-weight: 800; color: #10b981; font-size: 1.1rem; margin-bottom: 0.5rem;">
                        Shor-Preskill Bound R = 1 - 2*H2(Q)
                    </div>
                    <ul style="font-size: 0.9rem; line-height: 1.6; padding-left: 1.2rem;">
                        <li><b>Asymptotic Secrecy Capacity:</b> Drops smoothly as channel noise rises.</li>
                        <li><b>Hard Cutoff at 11% QBER:</b> Beyond 11%, leaked Shannon information exceeds Bob's capacity, making key extraction impossible.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            csv_file = results_path / "exp5_key_rate.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file), use_container_width=True, height=220)

    elif "6. IBM Hardware Comparison" in exp_choice:
        c_left, c_right = st.columns([1.5, 1.0])
        with c_left:
            img_file = results_path / "hardware_comparison.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
        with c_right:
            st.markdown(
                """
                <div class="glass-card">
                    <div style="font-weight: 800; color: #38bdf8; font-size: 1.1rem; margin-bottom: 0.5rem;">
                        IBM Quantum 127Q Processor Benchmark
                    </div>
                    <ul style="font-size: 0.9rem; line-height: 1.6; padding-left: 1.2rem;">
                        <li>Evaluated against <b>IBM FakeBrisbane</b> (calibrated 127-qubit quantum processor).</li>
                        <li>Physical T1/T2 coherence decay and readout errors introduce a baseline QBER of <b>2.5% - 3.8%</b> even under optimal zero-eavesdropping conditions.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
            csv_file = results_path / "hardware_comparison.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file), use_container_width=True, height=220)

# =========================================================
# TAB 3: SECURE MESSAGING (OTP)
# =========================================================
with tab_msg:
    st.subheader("💬 One-Time Pad (OTP) Live Quantum Encryption")
    st.markdown(
        """
        Encrypt and decrypt text messages using the distilled secret key produced by our BB84 quantum circuits.
        Shannon's Information Theory proves One-Time Pad encryption is **mathematically unbreakable**
        when keys are uniform, secret, and never reused.
        """
    )

    if res.aborted:
        st.warning("⚠️ Warning: The current protocol was aborted due to high QBER (> 11%). For demonstration purposes, you can inspect the post-processing pipeline below.")

    # Error Reconciliation & Privacy Amplification
    rec_a, rec_b, n_corr = reconcile_errors_parity(res.alice_key, res.bob_key, block_size=8)
    final_secret_key = amplify_privacy(rec_a, estimated_qber=res.qber_sample)

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Parity Corrections Applied", f"{n_corr} bits")
    m_col2.metric("Raw Key Bits", f"{len(res.alice_key)}")
    m_col3.metric("Distilled Secret Key", f"{len(final_secret_key)} bits")

    msg_input = st.text_input(
        "Enter Plaintext Message for Alice to Send Bob:",
        value="Quantum computers cannot break physics! 🛡️",
    )

    active_key = final_secret_key if len(final_secret_key) > 0 else rec_a

    if len(active_key) == 0:
        st.error("No valid key bits available to encrypt. Re-run with lower noise or without Eve in the sidebar.")
    else:
        hex_ciphertext, bin_cipher = encrypt_message_otp(msg_input, active_key)
        decrypted_bob = decrypt_message_otp(hex_ciphertext, active_key)

        corrupted_eve_key = active_key.copy()
        if len(corrupted_eve_key) > 0:
            flip_mask = np.random.default_rng(999).random(len(corrupted_eve_key)) < 0.25
            corrupted_eve_key[flip_mask] = 1 - corrupted_eve_key[flip_mask]
        decrypted_eve = decrypt_message_otp(hex_ciphertext, corrupted_eve_key)

        st.markdown("---")
        col_alice, col_channel, col_bob = st.columns(3)

        with col_alice:
            st.markdown(
                f"""
                <div class="glass-card" style="border-color: #38bdf8;">
                    <div style="font-weight: 800; color: #38bdf8; font-size: 1.1rem;">👩‍💻 ALICE (SENDER)</div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">Original Plaintext:</div>
                    <div style="background: rgba(3,7,18,0.7); padding: 8px 12px; border-radius: 6px; font-weight: 600; margin-top: 4px;">
                        {msg_input}
                    </div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 10px;">Quantum Key Stream Preview:</div>
                    <div class="key-display" style="font-size: 0.8rem; margin-top: 4px;">
                        {"".join(str(b) for b in active_key[:28])}...
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_channel:
            st.markdown(
                f"""
                <div class="glass-card" style="border-color: #f43f5e;">
                    <div style="font-weight: 800; color: #f43f5e; font-size: 1.1rem;">📡 OPTICAL LINK & HACKER TERMINAL</div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">Encrypted Ciphertext (Hex):</div>
                    <div class="key-display" style="color: #f43f5e; border-color: rgba(244,63,94,0.4); font-size: 0.85rem; margin-top: 4px;">
                        {hex_ciphertext}
                    </div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 10px;">🕵️ Eve's Decryption Attempt:</div>
                    <div style="background: rgba(127,29,29,0.4); border: 1px solid #ef4444; border-radius: 6px; padding: 8px 12px; color: #fca5a5; font-family: monospace; font-size: 0.85rem; margin-top: 4px;">
                        {decrypted_eve}
                    </div>
                    <div style="font-size: 0.75rem; color: #fca5a5; margin-top: 4px;">⚠️ Result: Unreadable gibberish (Eve lacks conjugate bases!)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_bob:
            st.markdown(
                f"""
                <div class="glass-card" style="border-color: #10b981;">
                    <div style="font-weight: 800; color: #10b981; font-size: 1.1rem;">👨‍💻 BOB (RECEIVER)</div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">Decrypted Plaintext:</div>
                    <div style="background: rgba(6,78,59,0.4); border: 1px solid #10b981; border-radius: 6px; padding: 8px 12px; color: #34d399; font-weight: 700; margin-top: 4px;">
                        {decrypted_bob}
                    </div>
                    <div style="font-size: 0.85rem; color: #34d399; margin-top: 10px;">
                        ✅ <b>Authenticity 100% Guaranteed!</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# =========================================================
# TAB 4: HOW BB84 WORKS
# =========================================================
with tab_edu:
    st.subheader("📚 Quantum Key Distribution (BB84) Explained Simply")

    c_edu1, c_edu2 = st.columns([1.2, 1.0])

    with c_edu1:
        st.markdown(
            """
            ### 1. Why Current Cryptography is at Risk
            Modern asymmetric encryption (RSA, ECC, Diffie-Hellman) relies on computational hardness assumptions
            (e.g., factoring large integers, discrete logarithms). In 1994, Peter Shor formulated a quantum algorithm
            that solves these problems in **polynomial time**, rendering classical public-key cryptography obsolete
            once fault-tolerant quantum computers arrive.

            ### 2. The Quantum Solution (Physics vs. Math)
            Quantum Key Distribution (QKD) achieves **information-theoretic security** guaranteed by the laws of physics:
            - **No-Cloning Theorem:** An unknown quantum state cannot be copied without perturbation.
            - **Heisenberg Uncertainty Principle:** Measuring a qubit in the wrong basis irrevocably alters its quantum state.

            ### 3. The 4 Stages of the BB84 Protocol
            1. **Alice Prepares Qubits:** Alice encodes random bits into single photons using two conjugate bases:
               - **Z Basis (Computational):** $|0\\rangle$, $|1\\rangle$
               - **X Basis (Hadamard):** $|+\\rangle = \\frac{|0\\rangle+|1\\rangle}{\\sqrt{2}}$, $|-\\rangle = \\frac{|0\\rangle-|1\\rangle}{\\sqrt{2}}$
            2. **Bob Measures:** Bob picks random bases independently and measures each qubit.
            3. **Key Sifting:** Alice and Bob publicly announce *only their bases* (never bits). They keep positions where bases matched (~50%).
            4. **Error Estimation (QBER):** They publicly sacrifice a random sample of sifted bits. If the error rate exceeds **11.0%**, they abort.
            """
        )

    with c_edu2:
        st.markdown(
            """
            ### 🔍 The Core Research Question
            > *"Can Alice and Bob tell an eavesdropper from hardware noise?"*

            In classical textbooks, any QBER > 0 implies an eavesdropper.
            In real quantum networks:
            - **Optical fibers suffer absorption and birefringence.**
            - **Superconducting transmon qubits experience T1 relaxation and dephasing.**
            - **Single-photon detectors have non-ideal dark count rates.**

            **EveWatch's Key Insight:**
            1. At the physical layer, a scalar QBER conflates channel noise and eavesdropping.
            2. Small sample sizes create a massive blind zone (up to 30% Missed Detection Rate).
            3. By calibrating background hardware noise and scaling the statistical sample ($K \\ge 600$), Alice and Bob can eliminate false alarms and detect eavesdroppers with mathematical confidence.
            """
        )

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 1rem 0;">
        <b>EveWatch</b> © 2026 | Built for <b>Qiskit Fall Fest 2026 @ MPSTME, NMIMS Mumbai</b> | 
        Author: <b>Ayush Trivedi</b> | 
        <a href="https://github.com/Ayush-web28/EveWatch" target="_blank" style="color: #38bdf8; text-decoration: none;">GitHub Repository</a>
    </div>
    """,
    unsafe_allow_html=True,
)
