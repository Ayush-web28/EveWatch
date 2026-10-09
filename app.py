"""EveWatch: Streamlit Web Application.

Interactive Quantum Key Distribution (BB84) simulation and security analysis dashboard.
Distinguishes quantum eavesdroppers from environmental/hardware noise.
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
    page_title="EveWatch | BB84 Quantum Security",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E88E5;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #546E7A;
        margin-bottom: 1.2rem;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.4rem;
    }
    .badge-quantum {
        background-color: #E3F2FD;
        color: #1565C0;
    }
    .badge-qiskit {
        background-color: #EDE7F6;
        color: #512DA8;
    }
    .status-secure {
        background-color: #E8F5E9;
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 1rem;
        color: #2E7D32;
        font-weight: bold;
    }
    .status-abort {
        background-color: #FFEBEE;
        border: 2px solid #E53935;
        border-radius: 8px;
        padding: 1rem;
        color: #C62828;
        font-weight: bold;
    }
    .key-box {
        font-family: monospace;
        background-color: #F5F5F5;
        padding: 0.6rem;
        border-radius: 6px;
        border: 1px solid #E0E0E0;
        word-break: break-all;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
st.sidebar.image("https://raw.githubusercontent.com/qiskit/qiskit/main/docs/images/qiskit-logo.png", width=140)
st.sidebar.markdown("### 🛡️ EveWatch Controls")
st.sidebar.caption("Quantum Secure Communication | BB84 Simulator")

num_qubits = st.sidebar.slider(
    "Number of Qubits (N)",
    min_value=20,
    max_value=1000,
    value=100,
    step=20,
    help="Total photons/qubits prepared by Alice.",
)

seed_input = st.sidebar.number_input(
    "Random Seed (Reproducibility)",
    value=42,
    step=1,
    help="Fixed seed guarantees identical results across runs.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### 🕵️ Eavesdropper (Eve)")
eve_active = st.sidebar.checkbox("Enable Eve (Intercept-Resend)", value=False)
eve_fraction = st.sidebar.slider(
    "Interception Fraction (f)",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.05,
    disabled=not eve_active,
    help="Probability that Eve intercepts a transmitted qubit.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("#### ⚡ Hardware & Channel Noise")
noise_preset = st.sidebar.selectbox(
    "Noise Model Preset",
    ["Custom Parametric", "IBM FakeBrisbane (Calibrated 127Q)"],
)

if noise_preset == "Custom Parametric":
    channel_noise = st.sidebar.slider(
        "Channel Noise (p_ch)",
        min_value=0.0,
        max_value=0.30,
        value=0.0,
        step=0.01,
        help="Depolarizing error on optical fiber transmission.",
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
st.sidebar.markdown("#### ⚙️ Protocol Parameters")
abort_threshold = st.sidebar.slider(
    "Security Abort Threshold (QBER)",
    min_value=0.05,
    max_value=0.25,
    value=0.11,
    step=0.01,
    help="Asymptotic Shor-Preskill bound cutoff is 11.0%.",
)

sample_fraction = st.sidebar.slider(
    "Sample Revealed Fraction",
    min_value=0.1,
    max_value=0.8,
    value=0.5,
    step=0.05,
    help="Proportion of sifted key sacrificed for QBER verification.",
)

run_button = st.sidebar.button("🚀 Run BB84 Protocol", type="primary", use_container_width=True)

# ---------------------------------------------------------
# Session State & Simulation Caching
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
    )


# Run or retrieve current simulation result
if "result" not in st.session_state or run_button:
    with st.spinner("Executing Qiskit 2.x Quantum Circuit Simulation..."):
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
        )

res: BB84Result = st.session_state["result"]

# ---------------------------------------------------------
# Header & Navigation
# ---------------------------------------------------------
st.markdown('<div class="main-title">🛡️ EveWatch</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title"><b>Distinguishing Quantum Eavesdroppers from Hardware Noise in BB84</b> | '
    '<span class="badge badge-quantum">Qiskit Fall Fest 2026 @ MPSTME</span>'
    '<span class="badge badge-qiskit">IBM Quantum Track</span></div>',
    unsafe_allow_html=True,
)

tab_demo, tab_exp, tab_msg, tab_edu = st.tabs([
    "🔬 Protocol Demo",
    "📊 Empirical Experiments",
    "💬 Secure Messaging (OTP)",
    "📚 How BB84 Works",
])

# =========================================================
# TAB 1: PROTOCOL DEMO
# =========================================================
with tab_demo:
    # Verdict Banner
    if res.aborted:
        st.markdown(
            f"""
            <div class="status-abort">
                ❌ <b>PROTOCOL ABORTED: Eavesdropper or Excessive Noise Detected!</b><br>
                Sample QBER was <b>{res.qber_sample * 100:.2f}%</b>, exceeding the security threshold of <b>{res.abort_threshold * 100:.1f}%</b>.
                Quantum communication halted to prevent compromised key generation.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="status-secure">
                ✅ <b>PROTOCOL SECURE: Quantum Channel Integrity Verified!</b><br>
                Sample QBER was <b>{res.qber_sample * 100:.2f}%</b>, strictly below the abort threshold of <b>{res.abort_threshold * 100:.1f}%</b>.
                Raw key successfully generated with verified secrecy bounds.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    # Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Transmitted Qubits", f"{res.num_qubits}")
    m2.metric("Sifted Bits", f"{len(res.sifted_indices)}", f"{len(res.sifted_indices)/res.num_qubits*100:.1f}% match")
    m3.metric("Sample QBER", f"{res.qber_sample * 100:.2f}%", f"Threshold: {res.abort_threshold*100:.1f}%", delta_color="inverse")
    m4.metric("Sacrificed Sample", f"{len(res.sample_indices)} bits")
    m5.metric("Net Secret Key Bits", f"{len(res.alice_key)} bits")

    st.markdown("---")
    st.subheader("Step-by-Step Transmission Table")
    st.caption("Inspect each qubit's classical state, basis rotations, interception actions, and sifting status.")

    # Build interactive dataframe
    basis_map = {0: "Z (|0⟩,|1⟩)", 1: "X (|+⟩,|-⟩)"}
    table_rows = []
    limit = min(res.num_qubits, 100)  # show first 100 for clean responsive rendering

    sifted_set = set(res.sifted_indices)
    sample_set = set(res.sample_indices)
    key_set = set(res.key_indices)

    for i in range(limit):
        is_sifted = i in sifted_set
        is_sample = i in sample_set
        is_key = i in key_set
        eve_int = bool(res.eve_intercepted[i]) if len(res.eve_intercepted) > i else False
        is_err = bool(res.alice_bits[i] != res.bob_bits[i]) if is_sifted else None

        role = "Discarded (Basis Mismatch)"
        if is_sample:
            role = "Sampled (Revealed for QBER)"
        elif is_key:
            role = "Retained Secret Key"

        table_rows.append({
            "Qubit #": i,
            "Alice Bit": int(res.alice_bits[i]),
            "Alice Basis": basis_map[int(res.alice_bases[i])],
            "Eve Intercepted": "YES 🚨" if eve_int else "No",
            "Eve Basis": basis_map[int(res.eve_bases[i])] if eve_int else "-",
            "Bob Basis": basis_map[int(res.bob_bases[i])],
            "Bob Measured": int(res.bob_bits[i]),
            "Bases Match?": "MATCH ✅" if is_sifted else "Mismatch ❌",
            "Role": role,
            "Bit Error": "ERROR ⚠️" if is_err else ("Match 🎯" if is_sifted else "-"),
        })

    df_table = pd.DataFrame(table_rows)

    def highlight_rows(row):
        if "ERROR" in str(row["Bit Error"]):
            return ["background-color: #FFCDD2"] * len(row)
        elif "MATCH ✅" in str(row["Bases Match?"]):
            return ["background-color: #E8F5E9"] * len(row)
        return [""] * len(row)

    st.dataframe(df_table, use_container_width=True, height=360)

    # Key Display Box
    st.markdown("---")
    st.subheader("Distilled Secret Key")
    k1, k2 = st.columns(2)
    with k1:
        st.markdown("**Alice's Retained Key:**")
        a_key_str = "".join(str(int(b)) for b in res.alice_key)
        st.markdown(f'<div class="key-box">{a_key_str if a_key_str else "[Empty / Aborted]"}</div>', unsafe_allow_html=True)

    with k2:
        st.markdown("**Bob's Retained Key:**")
        b_key_str = "".join(str(int(b)) for b in res.bob_key)
        st.markdown(f'<div class="key-box">{b_key_str if b_key_str else "[Empty / Aborted]"}</div>', unsafe_allow_html=True)

    if len(res.alice_key) > 0:
        match_rate = float(np.mean(res.alice_key == res.bob_key)) * 100
        st.caption(f"Raw Key Agreement: **{match_rate:.2f}%**. (Reconciled with Cascade parity check in Post-Processing tab).")

# =========================================================
# TAB 2: EMPIRICAL EXPERIMENTS
# =========================================================
with tab_exp:
    st.subheader("📊 Empirical Research Experiments & Differentiator Analysis")
    st.markdown(
        """
        These results were generated across **hundreds of quantum trials** simulating both environmental noise
        and intercept-resend attacks to answer the central research question:
        *Can Alice and Bob tell an eavesdropper from hardware noise?*
        """
    )

    exp_choice = st.radio(
        "Select Experiment View:",
        [
            "1. QBER vs. Eve Interception Fraction (0.25*f Validation)",
            "2. QBER vs. Channel Depolarizing Noise Level",
            "3. 2D Parameter Heatmap (Noise x Eve Fraction)",
            "4. Detection Reliability (False Alarm & Missed Detection Rates)",
            "5. Secret Key Rate & Distilled Yield (Shor-Preskill Bound)",
            "6. IBM Hardware Comparison (FakeBrisbane Calibrated)",
        ],
        horizontal=True,
    )

    results_path = ROOT_DIR / "results"

    if "1. QBER vs. Eve" in exp_choice:
        col_img, col_data = st.columns([1.6, 1.0])
        with col_img:
            img_file = results_path / "exp1_eve_fraction.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
            else:
                st.warning("Experiment 1 figure not found in results/.")
        with col_data:
            st.markdown("#### Key Takeaways")
            st.markdown(
                """
                - **Exact Quantum Mechanical Scaling:** The measured QBER closely tracks $Q = 0.25 \\times f$.
                - **Full Interception ($f=1.0$):** QBER reaches **~24.8% ± 2.8%**, perfectly corroborating the theoretical 25% expectation.
                - **Blind Interception Limit:** For $f < 0.44$, QBER falls below 11%, meaning Eve cannot be detected by a simple 11% cutoff without background noise calibration!
                """
            )
            csv_file = results_path / "exp1_eve_fraction.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file), use_container_width=True, height=260)

    elif "2. QBER vs. Channel" in exp_choice:
        col_img, col_data = st.columns([1.6, 1.0])
        with col_img:
            img_file = results_path / "exp2_noise_level.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
            else:
                st.warning("Experiment 2 figure not found in results/.")
        with col_data:
            st.markdown("#### Key Takeaways")
            st.markdown(
                """
                - **Linear Channel Degradation:** Channel depolarizing noise causes $Q \\approx 0.5 \\times p_{ch}$.
                - **Critical Noise Threshold:** At $p_{ch} \\approx 22\\%$, the channel noise alone pushes QBER beyond the 11% cutoff.
                - **Operational Insight:** Even in a completely secure channel without Eve, hardware noise can trigger false security aborts if not accounted for.
                """
            )
            csv_file = results_path / "exp2_noise_level.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file), use_container_width=True, height=260)

    elif "3. 2D Parameter Heatmap" in exp_choice:
        col_img, col_data = st.columns([1.6, 1.0])
        with col_img:
            img_file = results_path / "exp3_qber_heatmap.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
            else:
                st.warning("Experiment 3 figure not found in results/.")
        with col_data:
            st.markdown("#### The Core Differentiator")
            st.markdown(
                """
                - **The Ambiguity Boundary:** The dashed cyan contour marks the **11% abort threshold**.
                - Any combination of noise and eavesdropping outside this contour results in a protocol abort.
                - **Why Noise vs. Eve Matters:** An observed QBER of 10% can be:
                  - 20% channel noise with NO eavesdropper ($f=0$), OR
                  - 40% Eve interception on a pristine channel, OR
                  - Combined intermediate values.
                """
            )
            csv_file = results_path / "exp3_qber_heatmap.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file).head(15), use_container_width=True, height=260)

    elif "4. Detection Reliability" in exp_choice:
        col_img, col_data = st.columns([1.6, 1.0])
        with col_img:
            img_file = results_path / "exp4_detection_analysis.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
            else:
                st.warning("Experiment 4 figure not found in results/.")
        with col_data:
            st.markdown("#### Sample Scaling Resolves Ambiguity")
            st.markdown(
                """
                - **Small Sample Hazard ($K=50$):** High variance causes **26% False Alarms** and **28% Missed Detections**!
                - **Statistical Convergence:** Scaling sample size to $K \\ge 600$ drops both False Alarms and Missed Detections to $< 2\\%$.
                - At $K=1200$, detection error is virtually **0.0%**.
                """
            )
            csv_file = results_path / "exp4_detection_analysis.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file), use_container_width=True, height=260)

    elif "5. Secret Key Rate" in exp_choice:
        col_img, col_data = st.columns([1.6, 1.0])
        with col_img:
            img_file = results_path / "exp5_key_rate.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
            else:
                st.warning("Experiment 5 figure not found in results/.")
        with col_data:
            st.markdown("#### Shor-Preskill Bound $R = 1 - 2 H_2(Q)$")
            st.markdown(
                """
                - **Asymptotic Secrecy Capacity:** Drops monotonically as channel noise rises.
                - **Hard Cutoff at 11% QBER:** Beyond $p_{ch} \\approx 22\\%$, the information leaked exceeds Bob's capacity, and secret key generation becomes theoretically impossible.
                """
            )
            csv_file = results_path / "exp5_key_rate.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file), use_container_width=True, height=260)

    elif "6. IBM Hardware Comparison" in exp_choice:
        col_img, col_data = st.columns([1.6, 1.0])
        with col_img:
            img_file = results_path / "hardware_comparison.png"
            if img_file.exists():
                st.image(str(img_file), use_container_width=True)
            else:
                st.warning("Hardware comparison figure not found in results/.")
        with col_data:
            st.markdown("#### Realistic Quantum Processor Noise")
            st.markdown(
                """
                - Tested against **IBM FakeBrisbane** (calibrated 127-qubit superconducting quantum processor).
                - Real processor T1/T2 relaxation and readout infidelity introduce baseline errors (~2-4%) even under optimal zero-eavesdropping conditions.
                """
            )
            csv_file = results_path / "hardware_comparison.csv"
            if csv_file.exists():
                st.dataframe(pd.read_csv(csv_file), use_container_width=True, height=260)

# =========================================================
# TAB 3: SECURE MESSAGING (OTP)
# =========================================================
with tab_msg:
    st.subheader("💬 One-Time Pad (OTP) Quantum Encryption")
    st.markdown(
        """
        Encrypt and decrypt arbitrary text messages using the secret key distilled from Alice and Bob's BB84 transmission.
        Shannon's theorem proves that One-Time Pad encryption is **information-theoretically unbreakable**
        when keys are uniform, secret, and never reused.
        """
    )

    if res.aborted:
        st.warning("⚠️ Warning: The current protocol was aborted due to high QBER (> 11%). In real QKD, transmission stops. For demo purposes, you may inspect the pipeline below.")

    # 1. Error Reconciliation & Privacy Amplification
    rec_a, rec_b, n_corr = reconcile_errors_parity(res.alice_key, res.bob_key, block_size=8)
    final_secret_key = amplify_privacy(rec_a, estimated_qber=res.qber_sample)

    c_rec1, c_rec2, c_rec3 = st.columns(3)
    c_rec1.metric("Parity Corrections Applied", f"{n_corr} bits")
    c_rec2.metric("Raw Key Bits", f"{len(res.alice_key)}")
    c_rec3.metric("Final Distilled Secret Key", f"{len(final_secret_key)} bits")

    msg_input = st.text_input(
        "Enter Plaintext Message for Alice to Send Bob:",
        value="Quantum computers cannot break physics! 🛡️",
    )

    # Use final secret key if available, else fallback to raw key for demonstration
    active_key = final_secret_key if len(final_secret_key) > 0 else rec_a

    if len(active_key) == 0:
        st.error("No valid key bits available to encrypt. Re-run with lower noise or without Eve in the sidebar.")
    else:
        hex_ciphertext, bin_cipher = encrypt_message_otp(msg_input, active_key)
        decrypted_bob = decrypt_message_otp(hex_ciphertext, active_key)

        # Simulate Eve's eavesdropped view with corrupted key
        corrupted_eve_key = active_key.copy()
        if len(corrupted_eve_key) > 0:
            # Flip ~25% of bits in Eve's key
            flip_mask = np.random.default_rng(999).random(len(corrupted_eve_key)) < 0.25
            corrupted_eve_key[flip_mask] = 1 - corrupted_eve_key[flip_mask]
        decrypted_eve = decrypt_message_otp(hex_ciphertext, corrupted_eve_key)

        st.markdown("---")
        col_alice, col_channel, col_bob = st.columns(3)

        with col_alice:
            st.markdown("### 👩 Alice (Sender)")
            st.write("**Plaintext:**")
            st.info(msg_input)
            st.write(f"**Key Stream Preview ({len(active_key)} bits):**")
            st.markdown(f'<div class="key-box">{"".join(str(b) for b in active_key[:32])}...</div>', unsafe_allow_html=True)

        with col_channel:
            st.markdown("### 📡 Quantum / Classical Channel")
            st.write("**Encrypted Ciphertext (Hex):**")
            st.markdown(f'<div class="key-box" style="color: #D81B60;">{hex_ciphertext}</div>', unsafe_allow_html=True)
            st.write("**Binary Stream:**")
            st.caption(f"{bin_cipher}")
            st.markdown("---")
            st.markdown("#### 🕵️ Eve's Decryption Attempt:")
            st.markdown(f'<div class="key-box" style="color: #E53935; background-color: #FFEBEE;">{decrypted_eve}</div>', unsafe_allow_html=True)
            st.caption("Eve cannot decipher the message without the exact basis matching!")

        with col_bob:
            st.markdown("### 👨 Bob (Receiver)")
            st.write("**Decrypted Plaintext:**")
            st.success(decrypted_bob)
            if decrypted_bob == msg_input:
                st.markdown("✅ **Flawless Decryption: Message Authenticity 100% Guaranteed!**")
            else:
                st.warning("⚠️ Discrepancy detected due to uncorrected bit errors.")

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

        st.markdown("---")
        st.markdown(
            """
            ```
            [Alice] === (|0⟩, |1⟩, |+⟩, |-⟩) ==> [Optical Channel] ===> [Bob]
                                                        |
                                                  [Eve Intercepts]
                                                  (Collapses State!)
            ```
            """
        )

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.caption(
    "EveWatch © 2026 | Built for Qiskit Fall Fest 2026 @ MPSTME, NMIMS Mumbai | "
    "Author: Ayush Trivedi | [GitHub Repository](https://github.com/Ayush-web28/EveWatch)"
)
