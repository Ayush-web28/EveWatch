"""Automated PowerPoint Deck Builder for EveWatch.

Generates a professional 13-slide 16:9 presentation deck (presentation/EveWatch.pptx)
strictly structured around the Qiskit Fall Fest judging criteria.
Embeds real empirical research figures from results/ and includes comprehensive
speaker notes for every slide.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results"
OUTPUT_DIR = ROOT_DIR / "presentation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PPTX_FILE = OUTPUT_DIR / "EveWatch.pptx"

# Professional Theme Palette
DARK_BG = RGBColor(15, 23, 42)       # Slate 900
NAVY_HEADER = RGBColor(24, 43, 73)    # Deep Navy
TEXT_MAIN = RGBColor(30, 41, 59)      # Slate 800
TEXT_MUTED = RGBColor(100, 116, 139)  # Slate 500
CARD_BG = RGBColor(248, 250, 252)     # Slate 50
CARD_BORDER = RGBColor(226, 232, 240) # Slate 200
PRIMARY_BLUE = RGBColor(30, 136, 229) # IBM Blue
ACCENT_PURPLE = RGBColor(109, 40, 217)# Royal Purple
ACCENT_GREEN = RGBColor(46, 125, 50)  # Forest Green
ACCENT_RED = RGBColor(211, 47, 47)    # Crimson Red
WHITE = RGBColor(255, 255, 255)


def add_header(slide, title_text: str, category: str = "QISKIT FALL FEST 2026"):
    """Add a consistent, clean header bar to the slide."""
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_cat = tf.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = PRIMARY_BLUE

    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = NAVY_HEADER


def add_card(slide, left, top, width, height, fill_color=CARD_BG, border_color=CARD_BORDER):
    """Add a rounded visual card container for structured content."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)
    return shape


def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)

    # Dark background banner
    bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK_BG
    bg.line.fill.background()

    # Title box
    tbox = slide1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(3.8))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "EVEWATCH"
    p.font.size = Pt(50)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    p2 = tf1.add_paragraph()
    p2.text = "Distinguishing Quantum Eavesdroppers from Hardware Noise in BB84"
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = "Track: Quantum Secure Communication | Qiskit Fall Fest 2026 @ MPSTME, NMIMS Mumbai\n" \
              "Team: Ayush Trivedi | Built with Qiskit 2.x & IBM Quantum AerSimulator"
    p3.font.size = Pt(16)
    p3.font.color.rgb = RGBColor(148, 163, 184)
    p3.space_before = Pt(24)

    slide1.notes_slide.notes_text_frame.text = (
        "Welcome judges! Today I am presenting EveWatch, our project for the Quantum Secure Communication track "
        "at Qiskit Fall Fest 2026. EveWatch tackles a fundamental and often overlooked question in Quantum Key Distribution: "
        "When Alice and Bob detect transmission errors, can they genuinely distinguish an active eavesdropper from baseline "
        "hardware noise? Over the next 10 minutes, I will show our end-to-end Qiskit 2.x implementation, our empirical "
        "findings across hundreds of trials, and our working Streamlit prototype."
    )

    # =========================================================================
    # SLIDE 2: PROBLEM & MOTIVATION
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Why Current Cryptography is at Risk & Why Quantum?")

    # Card 1: Classical Threat
    add_card(slide2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    c1 = slide2.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.5))
    tf = c1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "The Classical Crypto Collapse"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED

    bullets_c1 = [
        "Computational Assumptions: RSA, ECC, and Diffie-Hellman depend on the mathematical hardness of integer factorization & discrete logs.",
        "Shor's Algorithm Threat: A fault-tolerant quantum computer solves these problems in polynomial time O((log N)³).",
        "Harvest Now, Decrypt Later: Adversaries are actively intercepting and storing encrypted traffic today to decrypt once quantum hardware arrives.",
    ]
    for b in bullets_c1:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(14)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(12)

    # Card 2: Quantum Solution
    add_card(slide2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    c2 = slide2.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
    tf = c2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "The Quantum Solution (QKD)"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    bullets_c2 = [
        "Information-Theoretic Security: Derived from the fundamental laws of quantum physics, not mathematical complexity.",
        "No-Cloning Theorem: An arbitrary unknown quantum state cannot be copied without perturbation.",
        "Heisenberg Uncertainty: Any eavesdropper measuring a flying qubit inevitably collapses the state, introducing detectable errors.",
        "Future-Proof: Security remains unbreakable even against adversaries with infinite computational power.",
    ]
    for b in bullets_c2:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(14)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(10)

    slide2.notes_slide.notes_text_frame.text = (
        "Slide 2 sets the foundation. We explain why classical cryptography faces an existential deadline from Shor's algorithm. "
        "Quantum Key Distribution solves this by grounding security in the No-Cloning Theorem and Heisenberg Uncertainty Principle. "
        "Any eavesdropping creates physical disturbances that Alice and Bob can observe directly in the Quantum Bit Error Rate."
    )

    # =========================================================================
    # SLIDE 3: PROBLEM STATEMENT & THE KEY QUESTION
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "The Central Research Question: The Noise vs. Eve Dilemma")

    # Callout card
    add_card(slide3, Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.0), fill_color=RGBColor(238, 242, 255), border_color=PRIMARY_BLUE)
    c_q = slide3.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(11.1), Inches(1.6))
    tf = c_q.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THE CORE QUESTION: 'Can Alice and Bob tell an eavesdropper from hardware noise?'"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    p2 = tf.add_paragraph()
    p2.text = "Textbook BB84 assumes an idealized noiseless channel where any error implies an adversary. " \
              "In real quantum networks and hardware, thermal noise, fiber attenuation, and gate infidelities continuously generate errors. " \
              "Can classical parties disentangle malicious interception from environmental noise?"
    p2.font.size = Pt(14)
    p2.font.color.rgb = TEXT_MAIN
    p2.space_before = Pt(6)

    # Lower 2 cards comparing the causes
    add_card(slide3, Inches(0.8), Inches(4.1), Inches(5.6), Inches(2.8))
    c_sub1 = slide3.shapes.add_textbox(Inches(1.1), Inches(4.3), Inches(5.0), Inches(2.4))
    tf = c_sub1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Physical Noise Realities"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = NAVY_HEADER
    for b in [
        "Optical fiber Rayleigh scattering & birefringence.",
        "Single-photon detector dark counts & readout errors.",
        "Qubit decoherence (T1 relaxation, T2 dephasing).",
        "Result: Constant baseline background QBER (2-6%).",
    ]:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(4)

    add_card(slide3, Inches(6.8), Inches(4.1), Inches(5.7), Inches(2.8))
    c_sub2 = slide3.shapes.add_textbox(Inches(7.1), Inches(4.3), Inches(5.1), Inches(2.4))
    tf = c_sub2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Adversarial Eavesdropping (Eve)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    for b in [
        "Eve intercepts a fraction f in [0, 1] of transmitted qubits.",
        "Measures in random bases (Z or X) and resends state.",
        "Introduces 25% error on intercepted sifted qubits.",
        "Result: QBER scales as 0.25 * f on a clean channel.",
    ]:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(4)

    slide3.notes_slide.notes_text_frame.text = (
        "Here is the differentiator that sets EveWatch apart from standard student projects. "
        "Most tutorials assume perfect noiseless physics where QBER > 0 immediately flags Eve. "
        "In reality, optical fibers and superconducting qubits have natural background noise. "
        "If Alice and Bob observe an 8% QBER, is that 16% channel noise, or Eve intercepting 32% of bits? "
        "This ambiguity is what EveWatch investigates mathematically and empirically."
    )

    # =========================================================================
    # SLIDE 4: BB84 PROTOCOL EXPLAINED SIMPLY
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "BB84 Protocol: 4 Steps from Photons to Secret Key")

    steps = [
        ("Step 1: State Preparation (Alice)", "Alice creates random bits {0,1} and randomly selects between Computational (Z) and Hadamard (X) bases. Encodes single qubits: |0>, |1>, |+>, |->.", PRIMARY_BLUE),
        ("Step 2: Quantum Transmission", "Photons traverse the quantum channel. If Eve intercepts, measuring collapses the wavefunction. Noise in transit introduces depolarizing perturbations.", ACCENT_PURPLE),
        ("Step 3: Bob Measures & Key Sifting", "Bob independently picks random measurement bases. Alice and Bob publicly share their bases (not bits!). Retain positions where bases match (~50% yield).", ACCENT_GREEN),
        ("Step 4: QBER Verification & Decision", "Parties reveal and sacrifice sample K. If QBER > 11.0% (Shor-Preskill security limit), ABORT! If <= 11%, apply error correction & SHA-256 privacy amplification.", ACCENT_RED),
    ]

    for idx, (title, desc, color) in enumerate(steps):
        top_y = Inches(1.8 + idx * 1.3)
        add_card(slide4, Inches(0.8), top_y, Inches(11.7), Inches(1.15))
        c_box = slide4.shapes.add_textbox(Inches(1.1), top_y + Inches(0.08), Inches(11.1), Inches(0.95))
        tf = c_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = TEXT_MAIN
        p_desc.space_before = Pt(3)

    slide4.notes_slide.notes_text_frame.text = (
        "This slide breaks down the four stages of BB84 in plain language for judges. "
        "Alice encodes random bits in conjugate bases. Bob measures in random bases. "
        "Sifting discards 50% where bases disagreed. Finally, QBER estimation tests whether the quantum channel was tapped."
    )

    # =========================================================================
    # SLIDE 5: QUANTUM APPROACH & ARCHITECTURE
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "EveWatch Quantum Approach & Modular Architecture")

    arch_blocks = [
        ("bb84.protocol", "Pure Qiskit 2.x protocol runner.\nBuilds consolidated Clifford circuits.\nPerforms sifting and sampling.\nUI-independent & deterministic."),
        ("bb84.eve", "Intercept-resend adversary.\nContinuous fraction f in [0, 1].\nRandom basis rotation.\nMeasurement collapse & resend."),
        ("bb84.noise", "Optical channel depolarizing error.\nGate infidelities & readout error.\nIBM Fake Provider integration\n(FakeBrisbane 127Q)."),
        ("bb84.analysis", "Shannon entropy H2(Q).\nShor-Preskill rate: 1 - 2*H2(Q).\nFalse Alarm Rate (FAR).\nMissed Detection Rate (MDR)."),
    ]

    for idx, (name, details) in enumerate(arch_blocks):
        left_x = Inches(0.8 + idx * 2.95)
        add_card(slide5, left_x, Inches(1.8), Inches(2.8), Inches(4.8))
        box = slide5.shapes.add_textbox(left_x + Inches(0.15), Inches(2.0), Inches(2.5), Inches(4.4))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = name
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = NAVY_HEADER

        p_det = tf.add_paragraph()
        p_det.text = details
        p_det.font.size = Pt(13)
        p_det.font.color.rgb = TEXT_MAIN
        p_det.space_before = Pt(10)

    slide5.notes_slide.notes_text_frame.text = (
        "Slide 5 illustrates our modular software engineering architecture. "
        "We separated protocol execution, adversary modeling, noise generation, and statistical analysis into decoupled, pure modules. "
        "Every function has full docstrings and type hints, and all simulation results are pinned by random seeds for strict reproducibility."
    )

    # =========================================================================
    # SLIDE 6: QISKIT IMPLEMENTATION DETAILS
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Qiskit 2.x Implementation: High-Performance Clifford Simulation")

    # Left card: Modern APIs
    add_card(slide6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    c_q1 = slide6.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.5))
    tf = c_q1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Strict Qiskit 2.x API Compliance"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    points1 = [
        "Current APIs Only: No legacy execute() or BasicAer. Uses AerSimulator directly.",
        "Stabilizer Method O(N): Because BB84 uses only Clifford operations (H, X, Id, Measure), AerSimulator(method='stabilizer') simulates 1000 qubits in 35 milliseconds!",
        "Mid-Circuit Measurement: Eve measures mid-circuit, collapsing the quantum register before Bob's basis rotation.",
        "Channel Transit: 'Id' gates placed on transit qubits expose photons to optical depolarizing Kraus noise.",
    ]
    for b in points1:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    # Right card: Noise Models
    add_card(slide6, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    c_q2 = slide6.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
    tf = c_q2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Multi-Tiered Noise Modeling"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE

    points2 = [
        "Optical Channel Depolarizing Noise: Parametric error pch on single-qubit transit.",
        "Gate Depolarizing Error: Models imperfect RF pulses during H and X rotations.",
        "Readout Assignment Error: Asymmetric or symmetric detector misidentification.",
        "IBM Fake Provider Integration: Native support for FakeBrisbane (127 qubits, calibrated physical T1, T2, readout error map).",
        "Automatic Batching: Automatically batches circuits when simulating general Kraus hardware noise.",
    ]
    for b in points2:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    slide6.notes_slide.notes_text_frame.text = (
        "Here we highlight our Qiskit implementation depth. We don't use deprecated APIs. "
        "By leveraging Aer's stabilizer method for Clifford operations, our simulations run in polynomial time O(N). "
        "We can simulate 1,000 qubits in 35 milliseconds, allowing us to run 50+ Monte Carlo trials per data point quickly and reliably."
    )

    # =========================================================================
    # SLIDE 7: EAVESDROPPER DETECTION RESULTS
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Eavesdropper Interception Results: 25% QBER Validation")

    img_p1 = RESULTS_DIR / "exp1_eve_fraction.png"
    if img_p1.exists():
        slide7.shapes.add_picture(str(img_p1), Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.0))

    add_card(slide7, Inches(7.8), Inches(1.8), Inches(4.7), Inches(5.0))
    c_r1 = slide7.shapes.add_textbox(Inches(8.0), Inches(2.0), Inches(4.3), Inches(4.5))
    tf = c_r1.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Key Empirical Findings"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    points_r1 = [
        "Theoretical Agreement: Measured QBER closely tracks Q = 0.25 * f across all interception fractions.",
        "Full Interception (f=1.0): Yielded 24.85% ± 2.80% QBER across 50 trials, perfectly confirming the 25.0% theoretical bound.",
        "The Security Abort Limit: The 11% threshold is breached at f > 0.44.",
        "The Blind Zone Risk: When f <= 0.44, Eve's presence alone produces QBER <= 11%. In a naive protocol with zero noise awareness, Eve can intercept 40% of traffic without being caught!",
    ]
    for b in points_r1:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    slide7.notes_slide.notes_text_frame.text = (
        "Slide 7 presents our first empirical results. Our simulation confirms the 25% intercept-resend error rate "
        "derived by Bennett and Brassard. Crucially, notice the blind zone: if Eve only taps 40% of qubits, the error rate stays "
        "under 11%. This proves that a simple threshold alone is insufficient when background noise exists."
    )

    # =========================================================================
    # SLIDE 8: NOISE-AWARE ANALYSIS (HEATMAP)
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Noise-Aware Analysis: 2D Parameter Heatmap")

    img_p2 = RESULTS_DIR / "exp3_qber_heatmap.png"
    if img_p2.exists():
        slide8.shapes.add_picture(str(img_p2), Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.0))

    add_card(slide8, Inches(7.8), Inches(1.8), Inches(4.7), Inches(5.0))
    c_r2 = slide8.shapes.add_textbox(Inches(8.0), Inches(2.0), Inches(4.3), Inches(4.5))
    tf = c_r2.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Mapping the Security Frontier"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE

    points_r2 = [
        "The Equifinality Problem: A measured QBER of 9% can be generated by 18% channel noise alone, OR Eve tapping 36% of bits, OR a mix.",
        "11% Secrecy Contour: The dashed cyan boundary defines the maximum allowable operational margin before Shannon leakage outpaces key generation.",
        "Combined Effects: Channel noise narrows the eavesdropper detection window, forcing Alice and Bob to dynamically calibrate link baselines.",
    ]
    for b in points_r2:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(10)

    slide8.notes_slide.notes_text_frame.text = (
        "Slide 8 displays our 2D parameter heatmap. This visualizes the joint effect of optical noise and eavesdropping. "
        "The dashed cyan contour marks the 11% Shor-Preskill limit. Everything above and to the right must be aborted. "
        "Notice the fundamental equifinality: multiple distinct combinations of noise and interception map to identical QBER values."
    )

    # =========================================================================
    # SLIDE 9: DETECTION RELIABILITY (SAMPLE SCALING)
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Detection Reliability: Resolving Ambiguity via Sample Scaling")

    img_p3 = RESULTS_DIR / "exp4_detection_analysis.png"
    if img_p3.exists():
        slide9.shapes.add_picture(str(img_p3), Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.0))

    add_card(slide9, Inches(7.8), Inches(1.8), Inches(4.7), Inches(5.0))
    c_r3 = slide9.shapes.add_textbox(Inches(8.0), Inches(2.0), Inches(4.3), Inches(4.5))
    tf = c_r3.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "How EveWatch Solves This"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED

    points_r3 = [
        "Small Sample Hazard (K=50): Finite-size binomial dispersion causes a 26.0% False Alarm Rate and a 28.0% Missed Detection Rate!",
        "1 in 4 Insecurity: At K=50, 28% of compromised keys slip past undetected.",
        "Statistical Convergence: As sample size scales to K >= 600, variance collapses as 1/sqrt(K).",
        "Zero-Error Detection: At K=1200, both False Alarms and Missed Detections drop to 0.0%, achieving mathematically verified channel trust.",
    ]
    for b in points_r3:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    slide9.notes_slide.notes_text_frame.text = (
        "Slide 9 reveals our answer to the central research question. When operating near the 11% threshold, "
        "small sample sizes of 50 bits suffer from high binomial variance, leading to 26% false alarms and 28% missed detections. "
        "By scaling the sacrificed sample size to K >= 600 bits, Alice and Bob compress the error variance and eliminate both errors to under 1%."
    )

    # =========================================================================
    # SLIDE 10: STREAMLIT PROTOTYPE
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Working Prototype: Streamlit Interactive Dashboard (app.py)")

    proto_cards = [
        ("Tab 1: Protocol Demo", "Real-time interactive BB84 simulation.\nStep-by-step table highlighting Alice bits, bases, Eve actions, and Bob measurements.\nColor-coded security verdict banners."),
        ("Tab 2: Empirical Experiments", "Embedded interactive visualizers for all 6 empirical research benchmarks.\nInspect CSV datasets, QBER curves, heatmaps, and detection error curves."),
        ("Tab 3: Secure Messaging (OTP)", "Type custom messages.\nEncrypt and decrypt with distilled quantum key using One-Time Pad (XOR).\nVisual inspection of Eve's corrupted decryption attempt."),
        ("Tab 4: How BB84 Works", "Plain-language educational guide explaining the 4 stages of BB84, conjugate bases, and quantum mechanics fundamentals for students and judges."),
    ]

    for idx, (title, desc) in enumerate(proto_cards):
        left_x = Inches(0.8 + (idx % 2) * 5.95)
        top_y = Inches(1.8 + (idx // 2) * 2.6)
        add_card(slide10, left_x, top_y, Inches(5.75), Inches(2.4))
        b = slide10.shapes.add_textbox(left_x + Inches(0.2), top_y + Inches(0.15), Inches(5.35), Inches(2.1))
        tf = b.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = TEXT_MAIN
        p_desc.space_before = Pt(6)

    slide10.notes_slide.notes_text_frame.text = (
        "Slide 10 details our interactive Streamlit prototype. It features four dedicated tabs: "
        "an interactive transmission step-by-step table, an experiment visualizer, a live One-Time Pad text encryption tool, "
        "and an educational explainer. It runs smoothly with streamlit run app.py."
    )

    # =========================================================================
    # SLIDE 11: INNOVATION & DIFFERENTIATORS
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "Innovation: What Makes EveWatch Different?")

    table_shape = slide11.shapes.add_table(6, 3, Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    table = table_shape.table
    table.columns[0].width = Inches(3.2)
    table.columns[1].width = Inches(4.2)
    table.columns[2].width = Inches(4.3)

    headers = ["Feature / Dimension", "Standard Student BB84 Project", "EveWatch (Our Project)"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_HEADER
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(14)
            p.font.color.rgb = WHITE

    rows_data = [
        ("Qiskit API Version", "Deprecated execute(), BasicAer", "Current Qiskit 2.x & AerSimulator"),
        ("Simulation Speed", "Slow 1-qubit circuits", "Aer Stabilizer Clifford scaling O(N) (1000q in 35ms)"),
        ("Adversary Modeling", "Binary On/Off toggle", "Continuous interception fraction f in [0, 1]"),
        ("Noise Modeling", "None (Idealized)", "Depolarizing, Readout, & Calibrated IBM 127Q"),
        ("Core Research Question", "'Does BB84 transfer bits?'", "'Can Alice & Bob tell noise from Eve?'"),
    ]

    for row_idx, r in enumerate(rows_data, start=1):
        for col_idx, text in enumerate(r):
            cell = table.cell(row_idx, col_idx)
            cell.text = text
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if row_idx % 2 == 1 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(12)
                p.font.color.rgb = PRIMARY_BLUE if col_idx == 2 else TEXT_MAIN
                if col_idx == 2:
                    p.font.bold = True

    slide11.notes_slide.notes_text_frame.text = (
        "Slide 11 highlights our competitive differentiation for the judges. "
        "Unlike generic student projects using legacy APIs and idealized assumptions, EveWatch delivers "
        "modern Qiskit 2.x stabilizer performance, multi-tiered hardware noise modeling, continuous adversary fractions, "
        "and statistically rigorous sample scaling analysis."
    )

    # =========================================================================
    # SLIDE 12: IMPACT, LIMITATIONS & FUTURE SCOPE
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    add_header(slide12, "Impact, Honest Limitations, and Future Roadmap")

    # Left: Limitations
    add_card(slide12, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    c_lim = slide12.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(5.0), Inches(4.5))
    tf = c_lim.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Honest Limitations"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED

    lim_items = [
        "Simulation Link: Optical links are modeled via depolarizing Kraus channels rather than physical fiber-optic lasers and SPAD detectors.",
        "Attack Model: Focuses on intercept-resend; does not model photon-number-splitting (PNS) against weak coherent pulses.",
        "Asymptotic Assumption: The 11% cutoff assumes infinite key limits; finite-key regimes impose stricter penalties.",
    ]
    for b in lim_items:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    # Right: Future Scope
    add_card(slide12, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    c_fut = slide12.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.1), Inches(4.5))
    tf = c_fut.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Future Scope & Roadmap"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    fut_items = [
        "Decoy-State Protocol: Implement vacuum + weak decoy states to neutralize PNS attacks.",
        "Entanglement-Based E91: Use Bell states and CHSH inequality tests to detect eavesdroppers without basis disclosure.",
        "Post-Quantum Hybridization: Combine BB84 quantum keys with NIST-standardized lattice algorithms (ML-KEM / Kyber).",
        "Physical Optical Testbed: Deploy on multi-node quantum optical links with physical single-photon detectors.",
    ]
    for b in fut_items:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    slide12.notes_slide.notes_text_frame.text = (
        "We believe scientific credibility requires acknowledging honest limitations. "
        "Our work is simulation-based and focuses on intercept-resend. "
        "Looking forward, we have a clear roadmap to incorporate decoy-state protocols, E91 entanglement verification, "
        "and hybrid post-quantum cryptography integration."
    )

    # =========================================================================
    # SLIDE 13: CONCLUSION & GITHUB REPOSITORY
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)

    # Dark background
    bg13 = slide13.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg13.fill.solid()
    bg13.fill.fore_color.rgb = DARK_BG
    bg13.line.fill.background()

    c_end = slide13.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11.0), Inches(4.8))
    tf_end = c_end.text_frame
    tf_end.word_wrap = True

    p = tf_end.paragraphs[0]
    p.text = "Conclusion & Submission"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    p2 = tf_end.add_paragraph()
    p2.text = "EveWatch demonstrates that while hardware noise and eavesdropping conflate at the raw QBER level, " \
              "statistical sample scaling (K >= 600) and link baseline calibration enable provable, reliable quantum security."
    p2.font.size = Pt(18)
    p2.font.color.rgb = WHITE
    p2.space_before = Pt(14)

    p3 = tf_end.add_paragraph()
    p3.text = "\n📦 Open-Source GitHub Repository:\nhttps://github.com/Ayush-web28/EveWatch\n\n" \
              "Team: Ayush Trivedi | Qiskit Fall Fest 2026 @ MPSTME, NMIMS Mumbai\n" \
              "Thank you to IBM Quantum and MPSTME mentors!"
    p3.font.size = Pt(16)
    p3.font.color.rgb = RGBColor(148, 163, 184)
    p3.space_before = Pt(16)

    slide13.notes_slide.notes_text_frame.text = (
        "To conclude: EveWatch proves that while physical errors conflate eavesdropping and hardware noise, "
        "statistical sample scaling provides the key to reliable, provable quantum communication. "
        "Our full codebase, tests, figures, and Streamlit app are open-source on GitHub at github.com/Ayush-web28/EveWatch. "
        "Thank you, and I look forward to your questions!"
    )

    prs.save(str(PPTX_FILE))
    print(f"[+] Presentation saved successfully to {PPTX_FILE}")


if __name__ == "__main__":
    build_presentation()
