import React, { useState } from 'react';
import { ArrowRight, ShieldAlert, Cpu, Sparkles, Radio, Zap } from 'lucide-react';
import { QuantumCanvas } from './QuantumCanvas';

interface HeroProps {
  onLaunchLab: () => void;
  onExploreScience: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onLaunchLab, onExploreScience }) => {
  const [eveSimActive, setEveSimActive] = useState<boolean>(true);
  const [videoFailed, setVideoFailed] = useState<boolean>(false);

  return (
    <section id="hero" className="relative min-h-screen flex items-center justify-center pt-24 pb-16 px-4 sm:px-6 overflow-hidden">
      {/* Background Video with Graceful Fallback */}
      {!videoFailed && (
        <video
          autoPlay
          muted
          loop
          playsInline
          onError={() => setVideoFailed(true)}
          className="absolute inset-0 w-full h-full object-cover opacity-20 pointer-events-none mix-blend-screen"
        >
          <source src="/videos/quantum-stream.mp4" type="video/mp4" />
        </video>
      )}

      {/* Interactive Quantum Particle Canvas Layer */}
      <QuantumCanvas interactive={true} intensity={1.1} showNodes={true} eveActive={eveSimActive} />

      {/* Atmospheric Radial Gradients */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-gradient-to-b from-cyan-500/10 via-violet-600/10 to-transparent blur-3xl pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-t from-[#05070D] via-transparent to-[#05070D]/80 pointer-events-none" />

      {/* Main Content Container */}
      <div className="relative z-10 max-w-5xl mx-auto text-center flex flex-col items-center">
        {/* Eyebrow badge */}
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-cyan-500/30 text-cyan-400 text-xs font-mono uppercase tracking-widest mb-8 backdrop-blur-md shadow-lg shadow-cyan-950/40">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span>QUANTUM SECURE COMMUNICATIONS · BB84 PROTOCOL</span>
        </div>

        {/* Cinematic Headline */}
        <h1 className="font-heading font-extrabold text-4xl sm:text-6xl md:text-7xl tracking-tight text-white mb-6 leading-[1.1]">
          When Quantum Noise <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-violet-400">
            Hides the Enemy.
          </span>
        </h1>

        {/* Supporting scientific explanation */}
        <p className="max-w-2xl text-slate-300 text-base sm:text-lg font-light leading-relaxed mb-10">
          Explore the boundary between natural quantum noise and active eavesdropping. 
          EveWatch simulates <span className="text-cyan-300 font-normal">BB84 quantum key distribution</span> using real Qiskit circuits 
          to investigate when a secure channel becomes compromised.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16 w-full sm:w-auto">
          <button
            onClick={onLaunchLab}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-heading text-sm font-semibold uppercase tracking-wider text-black bg-gradient-to-r from-cyan-400 via-cyan-300 to-teal-300 hover:from-cyan-300 hover:to-white transition-all duration-200 shadow-xl shadow-cyan-500/25 flex items-center justify-center space-x-2 group active:scale-95"
          >
            <span>Launch Quantum Lab</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>

          <button
            onClick={onExploreScience}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-heading text-sm font-medium tracking-wide text-slate-200 bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 hover:border-cyan-500/40 transition-all duration-200 backdrop-blur-sm flex items-center justify-center space-x-2 active:scale-95"
          >
            <Radio className="w-4 h-4 text-cyan-400" />
            <span>Explore the Science</span>
          </button>
        </div>

        {/* Live Quantum Channel Topology Card */}
        <div className="w-full max-w-4xl p-5 sm:p-6 rounded-2xl bg-[#0B1020]/80 border border-slate-800/80 backdrop-blur-md shadow-2xl relative">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/60">
            <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span className="text-white font-semibold uppercase tracking-wider">Simulated Optical Channel</span>
              <span>· Single-Photon Regime</span>
            </div>
            <button
              onClick={() => setEveSimActive(!eveSimActive)}
              className={`text-xs font-mono px-2.5 py-1 rounded border transition-all ${
                eveSimActive
                  ? 'bg-rose-950/60 text-rose-300 border-rose-800/60 shadow-sm shadow-rose-900/30'
                  : 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60'
              }`}
            >
              {eveSimActive ? 'Eve Interception: ON' : 'Eve Interception: OFF'}
            </button>
          </div>

          {/* Interactive Topology Display */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
            {/* Alice Node */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-cyan-500/20 text-left">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-cyan-400 font-semibold uppercase">Alice (Transmitter)</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/50">Laser Source</span>
              </div>
              <p className="text-xs text-slate-300 mb-2">
                Prepares non-orthogonal states: <span className="font-mono text-cyan-300">|0⟩, |1⟩, |+⟩, |−⟩</span>
              </p>
              <div className="flex items-center space-x-2 text-[11px] font-mono text-slate-400">
                <span>Basis: <strong className="text-white">Z (+) or X (×)</strong></span>
              </div>
            </div>

            {/* Eve Intercept Node / Fiber Channel */}
            <div className={`p-4 rounded-xl border text-center transition-all ${
              eveSimActive 
                ? 'bg-rose-950/20 border-rose-500/30 shadow-lg shadow-rose-950/20' 
                : 'bg-slate-900/40 border-slate-800'
            }`}>
              <div className="flex items-center justify-center space-x-1.5 mb-2">
                <ShieldAlert className={`w-4 h-4 ${eveSimActive ? 'text-rose-400 animate-pulse' : 'text-slate-500'}`} />
                <span className={`text-xs font-mono font-semibold uppercase ${eveSimActive ? 'text-rose-300' : 'text-slate-400'}`}>
                  {eveSimActive ? 'Eve (Intercept & Resend)' : 'Quantum Fiber Channel'}
                </span>
              </div>
              <p className="text-xs text-slate-300 mb-2">
                {eveSimActive
                  ? 'Induces wavefunction collapse with ~25% QBER penalty on intercepted qubits.'
                  : 'Isolated channel with passive depolarizing fiber dispersion.'}
              </p>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-800">
                {eveSimActive ? 'Threat: Active Eavesdropping' : 'Status: Transparent Channel'}
              </span>
            </div>

            {/* Bob Node */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-violet-500/20 text-left">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-violet-400 font-semibold uppercase">Bob (Receiver)</span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-violet-950 text-violet-300 border border-violet-800/50">SPAD Detectors</span>
              </div>
              <p className="text-xs text-slate-300 mb-2">
                Measures incoming photons in independently chosen random bases.
              </p>
              <div className="flex items-center space-x-2 text-[11px] font-mono text-slate-400">
                <span>Public Sifting: <strong className="text-white">50% retention</strong></span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/60 flex flex-wrap items-center justify-between text-xs text-slate-400 font-mono">
            <div className="flex items-center space-x-2">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              <span>Shor-Preskill Security Bound: <strong className="text-cyan-300">11.0% QBER</strong></span>
            </div>
            <div className="flex items-center space-x-2 mt-1 sm:mt-0">
              <Cpu className="w-3.5 h-3.5 text-violet-400" />
              <span>Engine: Qiskit AerSimulator 2.5.2</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
