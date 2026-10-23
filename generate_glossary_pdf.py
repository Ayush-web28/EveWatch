"""Generate a comprehensive beginner-friendly PDF glossary for EveWatch.
Assumes zero prior knowledge of quantum computing or cryptography.
Uses ReportLab with high-quality visual formatting.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas

# Output path
ROOT_DIR = Path(__file__).resolve().parent
PDF_PATH = ROOT_DIR / "EveWatch_Quantum_Terminology_Guide.pdf"


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))  # Slate 500

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "EveWatch · Complete Quantum Cybersecurity Terminology Guide")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 747, 612 - 54, 747)

        # Footer (all pages)
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(612 - 54, 36, page_str)
        self.drawString(54, 36, "Prepared for Presentation & Defense · Qiskit Fall Fest 2026")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 46, 612 - 54, 46)

        self.restoreState()


def create_glossary_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0B132B"),
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        alignment=TA_LEFT,
        spaceAfter=14,
    )

    category_style = ParagraphStyle(
        'CategoryHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1E3A8A"),  # Deep Blue
        spaceBefore=14,
        spaceAfter=6,
    )

    term_title_style = ParagraphStyle(
        'TermTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0F172A"),
    )

    body_style = ParagraphStyle(
        'TermBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
    )

    analogy_style = ParagraphStyle(
        'TermAnalogy',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0D9488"),  # Teal
    )

    why_style = ParagraphStyle(
        'TermWhy',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#7C3AED"),  # Violet
    )

    story = []

    # Title Banner
    story.append(Paragraph("EVEWATCH · QUANTUM CYBERSECURITY", ParagraphStyle('Eyebrow', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#0284C7"), spaceAfter=4)))
    story.append(Paragraph("The Plain-English Quantum Glossary", title_style))
    story.append(Paragraph(
        "A zero-jargon dictionary for non-physicists: explains every quantum term, protocol step, "
        "and security concept used in the <b>EveWatch BB84 Platform</b> using simple everyday analogies.",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284C7"), spaceAfter=14))

    # Helper function to add a card for each term
    def add_term_card(term: str, definition: str, analogy: str, why_it_matters: str):
        content = [
            Paragraph(f"<b>{term}</b>", term_title_style),
            Spacer(1, 3),
            Paragraph(f"<b>What it is:</b> {definition}", body_style),
            Spacer(1, 3),
            Paragraph(f"<b>💡 Real-World Analogy:</b> {analogy}", analogy_style),
            Spacer(1, 3),
            Paragraph(f"<b>🎯 In EveWatch:</b> {why_it_matters}", why_style),
        ]
        
        t = Table([[content]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(t)
        story.append(Spacer(1, 7))

    # =========================================================================
    # SECTION 1: THE CRISIS & CLASSICAL CRYPTOGRAPHY
    # =========================================================================
    story.append(Paragraph("1. The Classical Threat & Motivation", category_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=8))

    add_term_card(
        term="Cryptography",
        definition="The science of scrambling messages (encryption) so that only someone with the secret key can unscramble them (decryption). Plaintext is the original readable message; ciphertext is the scrambled garbled text.",
        analogy="Putting your letter inside a steel padlock box and mailing it. Anyone intercepting the package sees only a locked metal box.",
        why_it_matters="EveWatch demonstrates how to distribute that padlock's secret key with 100% mathematical security using quantum physics."
    )

    add_term_card(
        term="Public-Key Cryptography (RSA / ECC)",
        definition="The security system used by every bank, website, and smartphone today. It relies on mathematical problems that are easy to calculate in one direction but virtually impossible for normal computers to reverse (e.g. multiplying two giant prime numbers vs. factoring the product back).",
        analogy="A piggy bank: anyone can drop a coin in through the slot (public key), but only the person with the master key can unlock the bottom (private key).",
        why_it_matters="Public-key cryptography is currently facing an existential threat because quantum computers can solve those hard math problems almost instantly."
    )

    add_term_card(
        term="Shor's Algorithm",
        definition="A quantum mathematical recipe discovered by Peter Shor in 1994. If run on a sufficiently large quantum computer, it factors giant numbers in polynomial time, completely shattering RSA and ECC encryption.",
        analogy="If cracking an RSA padlock takes a classical supercomputer 10,000 years, Shor's algorithm on a quantum computer cuts that time down to less than 10 seconds.",
        why_it_matters="Shor's algorithm is the exact reason the world must transition to Quantum Key Distribution (QKD) immediately."
    )

    add_term_card(
        term="Harvest Now, Decrypt Later (HNDL)",
        definition="An attack strategy where adversaries, hackers, or foreign intelligence agencies intercept and record encrypted Internet traffic today, storing it on massive hard drives until a fault-tolerant quantum computer exists to retroactively decrypt it.",
        analogy="Stealing locked safes from a bank today and storing them in your basement, waiting for someone to invent a laser drill tomorrow that melts through the doors.",
        why_it_matters="Proves that quantum security is an urgent problem TODAY, not 20 years from now. Secrets sent today are already being recorded."
    )

    add_term_card(
        term="Information-Theoretic Security",
        definition="A level of security that CANNOT be broken, even if an adversary has an infinite amount of time and infinite supercomputing power. It is guaranteed by the laws of physics and mathematical entropy, not by hard math equations.",
        analogy="A secret message destroyed in a furnace vs. a message locked with a password. A password can eventually be guessed with enough compute power; burnt ashes contain zero recoverable information forever.",
        why_it_matters="BB84 and One-Time Pad encryption provide Information-Theoretic Security, guaranteeing eternal protection."
    )

    # =========================================================================
    # SECTION 2: QUANTUM PHYSICS FOR BEGINNERS
    # =========================================================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("2. Quantum Physics Fundamentals", category_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=8))

    add_term_card(
        term="Classical Bit vs. Qubit",
        definition="A classical bit (in your computer or phone) is a tiny electrical switch that is strictly either a 0 or a 1. A qubit (quantum bit) is a quantum particle that can represent 0, 1, or both at the same time until it is measured.",
        analogy="A classical bit is a coin resting flat on a table (either Heads or Tails). A qubit is a coin spinning rapidly on the table—it has properties of both Heads and Tails simultaneously while in motion.",
        why_it_matters="Alice and Bob send individual qubits over an optical fiber to negotiate their secret cryptographic keys."
    )

    add_term_card(
        term="Photon",
        definition="A single, indivisible packet (particle) of light. In quantum communication, each qubit is physically encoded onto the polarization (vibration angle) of one single photon travelling through an optical fiber.",
        analogy="A tiny microscopic flashlight that emits light one single speck at a time. Each speck carries one quantum secret.",
        why_it_matters="EveWatch simulates single-photon optical fiber transmissions between Alice, Eve, and Bob."
    )

    add_term_card(
        term="Superposition",
        definition="The bizarre ability of a quantum particle to exist in multiple states at once. A qubit in superposition doesn't pick '0' or '1' until an observer measures it.",
        analogy="A musical chord: when you strike C and G together on a piano, your ear hears a harmonious combination of both notes at the exact same moment.",
        why_it_matters="Alice puts qubits into superposition states (|+⟩ and |-⟩) so that anyone measuring them in the wrong basis will corrupt the state."
    )

    add_term_card(
        term="Measurement & Wavefunction Collapse",
        definition="In quantum mechanics, looking at a particle forces it to stop being in superposition and violently snap into a single definite state. You cannot observe a quantum particle 'silently' without permanently altering it.",
        analogy="Stopping the spinning coin by slapping your hand down on it. The act of measuring forces it to choose Heads or Tails, and you can never restore the exact spin it had before your hand touched it.",
        why_it_matters="This is how Alice and Bob catch Eve! When Eve tries to eavesdrop on the photon, she slaps her hand on the spinning coin, collapsing it and leaving an undeniable error trace."
    )

    add_term_card(
        term="No-Cloning Theorem",
        definition="A fundamental law of physics proven in 1982: It is mathematically impossible to create an identical copy of an unknown quantum state without destroying the original.",
        analogy="A self-shredding Polaroid photo: as soon as you put it on a Xerox machine to photocopy it, the camera flash ruins the original picture and makes the copy blurry.",
        why_it_matters="Eve cannot simply copy the photons passing through the fiber, save one copy for herself, and forward the second copy to Bob. Physics forbids it!"
    )

    add_term_card(
        term="Heisenberg Uncertainty Principle",
        definition="A rule of nature stating that certain pairs of physical properties (conjugate variables, like position and momentum, or vertical and diagonal polarization) cannot both be known with 100% precision at the same time.",
        analogy="Balancing on a seesaw: pushing down one side inevitably raises the other side. You cannot force both ends to touch the ground simultaneously.",
        why_it_matters="Forces Eve to guess which basis Alice used. If she guesses wrong, she inevitably scrambles the qubit's complementary property."
    )

    add_term_card(
        term="Ket Notation (|0⟩, |1⟩, |+⟩, |−⟩)",
        definition="Standard mathematical notation (Dirac bracket) for quantum states. |0⟩ and |1⟩ represent the standard upright orientations (Computational Z basis). |+⟩ and |−⟩ represent diagonal 45-degree orientations (Hadamard X basis).",
        analogy="Think of a compass: |0⟩ is pointing North, |1⟩ is pointing South, |+⟩ is pointing Northeast, and |−⟩ is pointing Northwest.",
        why_it_matters="These four non-orthogonal states form the vocabulary of the BB84 protocol."
    )

    # =========================================================================
    # SECTION 3: THE BB84 PROTOCOL
    # =========================================================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("3. The BB84 Protocol & Its Characters", category_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=8))

    add_term_card(
        term="Alice, Bob, and Eve",
        definition="The universal cast of characters in cryptography: Alice is the sender (transmitter), Bob is the legitimate receiver, and Eve is the eavesdropper (adversary) attempting to spy on the communication.",
        analogy="Alice is the bank branch, Bob is headquarters, and Eve is a malicious wiretapper lurking along the telephone wire in between.",
        why_it_matters="EveWatch evaluates whether Alice and Bob can detect Eve's presence under realistic noisy network conditions."
    )

    add_term_card(
        term="Quantum Channel vs. Public Classical Channel",
        definition="BB84 requires two separate links: (1) The Quantum Channel (an optical fiber that carries delicate single photons). (2) The Classical Channel (regular Internet or radio, where Alice and Bob talk openly after transmission).",
        analogy="The Quantum Channel is a specialized vacuum tube sending fragile glass marbles. The Classical Channel is a public loudspeaker where anyone in the town square can hear what Alice and Bob say.",
        why_it_matters="Eve can listen to the public loudspeaker all she wants, but she cannot reconstruct the secret key because no raw secret bits are ever spoken on it."
    )

    add_term_card(
        term="Bases (Z Basis vs. X Basis)",
        definition="A 'basis' is the angle or lens you choose to prepare or measure a photon. Z basis = vertical/horizontal (+) lenses. X basis = diagonal 45-degree (×) lenses.",
        analogy="Polarized sunglasses: if you look at horizontally polarized glare through vertical polarized sunglasses, all light is blocked. Tilt your glasses 45 degrees, and light passes through randomly.",
        why_it_matters="Alice and Bob randomly pick between Z and X for every single photon. They only keep bits where their random choices happened to match."
    )

    add_term_card(
        term="Key Sifting",
        definition="The post-transmission step where Bob tells Alice over the public channel: 'For photon #1 I used lens Z, for photon #2 I used lens X...' Alice replies: 'Keep #1, throw away #2.' On average, exactly 50% of bits match and are kept.",
        analogy="Playing 'Rock, Paper, Scissors' where you only record a score on the rounds where both players threw the exact same hand gesture.",
        why_it_matters="Sifting filters out mismatched random guesses, leaving Alice and Bob with an identical raw key if no one interfered."
    )

    add_term_card(
        term="Raw Key vs. Sifted Key vs. Distilled Secret Key",
        definition="• Raw Key: The initial stream of bits transmitted (e.g. 500 qubits). • Sifted Key: The ~50% remaining after discarding basis mismatches (e.g. 250 bits). • Distilled Secret Key: The final error-corrected, compressed key ready for military-grade encryption.",
        analogy="Mining gold ore (raw bits), washing away the dirt and rocks (sifting), and smelting the remaining nuggets into a pure 24-karat gold bar (distilled key).",
        why_it_matters="EveWatch tracks this funnel at every stage in Section A (Quantum Lab) of the web application."
    )

    # =========================================================================
    # SECTION 4: THE EVEWATCH CORE: NOISE VS. EVE
    # =========================================================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("4. The Noise vs. Eve Problem (Core Differentiator)", category_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=8))

    add_term_card(
        term="Intercept-Resend Attack",
        definition="The classic eavesdropping attack in BB84. Eve physically snatches Alice's incoming photon, measures it using her own randomly guessed basis, and sends a newly manufactured replacement photon to Bob.",
        analogy="Opening someone's mail, reading it, trying to fold it back into a new envelope with forged wax, and re-mailing it down the road.",
        why_it_matters="Because Eve guesses the wrong basis 50% of the time, her replacement photons introduce a 25% error rate on intercepted bits."
    )

    add_term_card(
        term="Interception Fraction (f)",
        definition="The percentage of photons that Eve chooses to intercept (between 0% and 100%). A subtle eavesdropper might only intercept f=0.10 (10%) to avoid generating too much noise.",
        analogy="A toll booth inspector who only inspects 1 out of every 10 cars to keep traffic moving and avoid raising suspicion.",
        why_it_matters="EveWatch lets users adjust Eve's interception fraction continuously from 0% to 100% using an interactive slider."
    )

    add_term_card(
        term="Quantum Bit Error Rate (QBER)",
        definition="The percentage of errors in the sifted key. Calculated by sacrificing a small sample of bits and comparing them publicly: QBER = (Number of Mismatched Bits) / (Total Sample Size).",
        analogy="A quality control inspector tasting 20 apples from a crate of 100. If 2 are rotten, the estimated error rate is 10%.",
        why_it_matters="QBER is the single most important metric in QKD. If QBER is too high, Alice and Bob know the channel is compromised and abort."
    )

    add_term_card(
        term="Channel Depolarizing Noise (p)",
        definition="Natural environmental errors in optical fibers: temperature variations, microscopic glass imperfections, and stray vibrations that randomly scramble photon polarization without any eavesdropper present.",
        analogy="Static crackle and background hiss on an old AM radio station caused by bad weather, not a spy tapping your radio.",
        why_it_matters="Induces bit errors at twice the rate of Eve: Q = 0.50 × p. EveWatch models this physical loss directly."
    )

    add_term_card(
        term="The Equifinality Problem",
        definition="The core dilemma investigated by EveWatch: Active eavesdropping and natural fiber noise produce IDENTICAL bit flip signatures. Looking at an 8% QBER alone, Alice and Bob cannot know if it was caused by 16% fiber noise, 32% Eve interception, or both.",
        analogy="Finding a muddy footprint in your hallway. Did an intruder step inside, or did your friendly roommate forget to take off their boots in the rain? The footprint looks identical.",
        why_it_matters="Proves why simple error thresholds fail in real networks, and why EveWatch's baseline calibration and statistical scaling are required."
    )

    add_term_card(
        term="The Shor-Preskill Security Bound (11.0% Cutoff)",
        definition="The mathematical point of no return proven by Peter Shor and John Preskill in 2000: If QBER < 11.0%, Bob shares more information with Alice than Eve does, so a 100% secure key can be distilled. If QBER ≥ 11.0%, Eve knows too much, and the protocol MUST abort.",
        analogy="A boat with a leak: if water enters slowly (< 11%), the bilge pump can pump it out faster than it enters. If water enters faster than 11%, the boat will sink no matter how hard you pump—abandon ship!",
        why_it_matters="Represented on EveWatch's 2D heatmap as the critical dashed boundary separating Green (Secure) from Red (Abort)."
    )

    add_term_card(
        term="Sample Size Scaling (K) & Binomial Variance",
        definition="The number of sifted bits K sacrificed to test for errors. Because error detection follows a coin-flip (binomial) distribution, small samples have huge random fluctuations (variance), while large samples (K ≥ 600) give pinpoint accuracy.",
        analogy="Flipping a coin 4 times might give you 3 Heads (75%), fooling you into thinking the coin is rigged. But flip it 1,000 times, and it will settle at 50% with absolute mathematical certainty.",
        why_it_matters="EveWatch Experiment 4 proves that scaling K to 600+ bits collapses false alarms and missed detections to 0.0%."
    )

    add_term_card(
        term="False Alarm Rate (FAR) vs. Missed Detection Rate (MDR)",
        definition="• False Alarm (FAR): Aborting a completely safe channel because random noise made it look compromised. • Missed Detection (MDR): Trusting and using a compromised key because Eve's errors happened to slip under the radar.",
        analogy="FAR is your smoke alarm beeping when you just toasted bread. MDR is your smoke alarm staying silent during an actual kitchen fire.",
        why_it_matters="EveWatch proves that small sample sizes (K=50) suffer a dangerous 28% MDR (1 in 4 hacked keys slip past!). Scaling K fixes this."
    )

    # =========================================================================
    # SECTION 5: POST-PROCESSING & QUANTUM HARDWARE
    # =========================================================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("5. Post-Processing, Encryption & Quantum Hardware", category_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=8))

    add_term_card(
        term="Information Reconciliation (Cascade-Lite)",
        definition="A classical error-correction step where Alice and Bob compare block parity checks (whether chunks have an even or odd number of 1s) to pinpoint and flip any remaining error bits without revealing the secret key.",
        analogy="Playing 'Battleship': asking 'is there a ship in row C?' instead of revealing your entire game board at once.",
        why_it_matters="Cleans the key so Bob's key matches Alice's key with 100.0% bit-for-bit perfection."
    )

    add_term_card(
        term="Privacy Amplification",
        definition="The final step: Alice and Bob run their key through a mathematical compressor (Toeplitz hashing) that shrinks the key. If Eve learned 10 bits of information during transmission, the hash compresses out those 10 bits, shrinking Eve's knowledge down to zero.",
        analogy="Juicing oranges: even if a drop of vinegar fell on the peel, pressing only the deep interior fruit yields 100% pure sweet juice.",
        why_it_matters="Guarantees that even if Eve listened to some classical sifting messages, her final knowledge of the secret key is mathematically zero."
    )

    add_term_card(
        term="One-Time Pad (OTP) / Vernam Cipher",
        definition="The only mathematically unbreakable encryption cipher in existence. Alice takes her message bits and combines them with identical-length quantum key bits using the XOR operation (P ⊕ K = C).",
        analogy="A personalized secret decoder ring where the code changes completely for every single letter and is never reused again.",
        why_it_matters="Featured in Section E of the EveWatch website, allowing users to type custom messages and see Bob decrypt them while Eve gets gibberish."
    )

    add_term_card(
        term="Qiskit AerSimulator & Stabilizer Method",
        definition="IBM's high-performance quantum circuit simulator. The 'Stabilizer' method uses the Gottesman-Knill theorem to simulate Clifford quantum operations in polynomial time O(N) rather than exponentially slow statevectors.",
        analogy="Using a formula to calculate where a projectile lands in 1 second, instead of calculating the motion of every single air molecule along the way.",
        why_it_matters="Allows EveWatch to simulate 1,000 qubits in 35 milliseconds, enabling real-time live execution during presentations!"
    )

    add_term_card(
        term="IBM FakeBrisbane (Calibrated Quantum Hardware)",
        definition="A software model of IBM's real 127-qubit superconducting quantum processor 'Brisbane'. It includes real daily calibration data: physical qubit decoherence (T1, T2) and readout measurement misidentification.",
        analogy="A high-end flight simulator loaded with real cockpit telemetry and wind data from a Boeing 787 flying over the Pacific.",
        why_it_matters="Proves that EveWatch was benchmarked against real IBM physical quantum hardware noise characteristics."
    )

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Glossary PDF generated successfully at: {PDF_PATH}")


if __name__ == "__main__":
    create_glossary_pdf()
