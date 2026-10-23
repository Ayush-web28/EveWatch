import React from 'react';
import { BookOpen, Sparkles, Shield, Binary, Zap, Lock } from 'lucide-react';

export const HowItWorks: React.FC = () => {
  const steps = [
    {
      num: '01',
      title: 'Quantum State Preparation',
      subtitle: 'Non-orthogonal conjugate bases',
      icon: Sparkles,
      content:
        'Alice generates a random bit b ∈ {0, 1} and selects a random basis: Computational Z (|0⟩, |1⟩) or Hadamard X (|+⟩, |−⟩). Because ⟨0|+⟩ = 1/√2 ≠ 0, these four states are non-orthogonal and cannot be distinguished with certainty by any measurement.',
      formula: '|0⟩ = [1, 0]ᵀ,  |1⟩ = [0, 1]ᵀ,  |+⟩ = (|0⟩+|1⟩)/√2,  |−⟩ = (|0⟩−|1⟩)/√2',
    },
    {
      num: '02',
      title: 'No-Cloning Theorem',
      subtitle: 'Fundamental physical law of quantum mechanics',
      icon: Shield,
      content:
        'Wootters, Zurek, and Dieks proved in 1982 that a unitary operator U cannot clone an arbitrary unknown quantum state |ψ⟩: U(|ψ⟩|0⟩) ≠ |ψ⟩|ψ⟩. Eve cannot duplicate incoming photons to store one copy and send the other to Bob.',
      formula: 'U |ψ⟩|s⟩ = |ψ⟩|ψ⟩  ⇒  ⟨ψ|φ⟩ = ⟨ψ|φ⟩²  ⇒  ⟨ψ|φ⟩ ∈ {0, 1}',
    },
    {
      num: '03',
      title: 'Wavefunction Collapse',
      subtitle: 'The intercept-resend disturbance signature',
      icon: Zap,
      content:
        'If Eve intercepts photon |ψ⟩ and measures in the wrong basis (which happens with 50% probability), the wavefunction projects into an eigenstate of her basis. When Bob subsequently measures in Alice’s original basis, he gets the wrong bit with 50% probability. Hence, an intercepted qubit incurs a 25% error penalty: Q = 0.25 × f.',
      formula: 'Pr(Bob error | Eve wrong basis) = |⟨0|−⟩|² · |⟨1|−⟩|² = 0.50 × 0.50 = 0.25',
    },
    {
      num: '04',
      title: 'Public Classical Sifting',
      subtitle: 'Discarding mismatched measurement bases',
      icon: Binary,
      content:
        'Bob announces his chosen measurement bases over an authenticated public classical channel (no secret bits are revealed). Alice compares Bob’s bases with hers. Whenever bases matched, they retain the bit; whenever bases differed, they discard it. On average, exactly 50% of raw qubits survive sifting.',
      formula: 'E[Sifted Key Length] = N / 2,   Pr(Match) = 0.50',
    },
    {
      num: '05',
      title: 'Parameter Estimation & Shor-Preskill Bound',
      subtitle: 'The 11.0% asymptotic security cutoff',
      icon: Lock,
      content:
        'Alice and Bob publicly reveal a random sample (e.g. 50%) of their sifted bits to estimate the Quantum Bit Error Rate (QBER). Shor and Preskill (2000) proved that as long as QBER < 11.0%, Eve’s mutual information is strictly bounded below Bob’s mutual information, guaranteeing distillable secret key.',
      formula: 'r(Q) = 1 - 2 · H₂(Q) > 0  ⟺  Q < 11.00%',
    },
    {
      num: '06',
      title: 'Reconciliation & Privacy Amplification',
      subtitle: 'Distilling pure unconditional secrecy',
      icon: BookOpen,
      content:
        'The unrevealed sifted bits undergo error correction (Cascade parity blocks or LDPC) to correct discrepancies. Finally, universal hashing (Toeplitz matrices) compresses the key, shrinking any partial Shannon information Eve might have gained down to negligible levels.',
      formula: 'Secret Bits Distilled:  K_final = n · [1 - 2 H₂(QBER)]',
    },
  ];

  return (
    <section id="how-it-works" className="py-20 px-4 sm:px-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-14 text-center max-w-3xl mx-auto">
        <div className="inline-flex items-center space-x-2 text-cyan-400 text-xs font-mono uppercase tracking-widest mb-3">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Scientific Foundation · Section F</span>
        </div>
        <h2 className="font-heading font-extrabold text-3xl sm:text-5xl text-white tracking-tight mb-4">
          How BB84 Quantum Cryptography Works
        </h2>
        <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
          First proposed by Charles Bennett and Gilles Brassard in 1984, BB84 harnesses the laws of quantum mechanics 
          rather than computational complexity to achieve unconditional communication security.
        </p>
      </div>

      {/* Steps Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <div
              key={step.num}
              className="p-6 rounded-2xl bg-[#0B1020]/90 border border-slate-800/90 shadow-xl hover:border-cyan-500/30 transition-all duration-300 flex flex-col justify-between group"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-2xl text-slate-700 group-hover:text-cyan-400/80 transition-colors">
                    {step.num}
                  </span>
                  <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-cyan-400">
                    <Icon className="w-4 h-4" />
                  </div>
                </div>

                <div>
                  <h3 className="font-heading font-bold text-white text-lg">
                    {step.title}
                  </h3>
                  <span className="text-xs font-mono text-cyan-400">
                    {step.subtitle}
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">
                  {step.content}
                </p>
              </div>

              <div className="mt-6 pt-3 border-t border-slate-800/80">
                <span className="text-[10px] font-mono uppercase text-slate-500 block mb-1">
                  Mathematical Formulation
                </span>
                <code className="text-[11px] font-mono text-cyan-300/90 bg-slate-950 p-2 rounded-lg border border-slate-800/80 block overflow-x-auto whitespace-pre">
                  {step.formula}
                </code>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
