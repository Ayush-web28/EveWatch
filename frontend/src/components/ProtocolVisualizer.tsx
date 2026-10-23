import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  ChevronRight, 
  ChevronLeft, 
  Activity, 
  Check, 
  X, 
  ShieldAlert, 
  Radio 
} from 'lucide-react';
import type { QubitEvent } from '../types/quantum';

interface ProtocolVisualizerProps {
  events?: QubitEvent[];
}

export const ProtocolVisualizer: React.FC<ProtocolVisualizerProps> = ({ events }) => {
  // Fallback demo events if simulation hasn't been run yet
  const defaultEvents: QubitEvent[] = [
    { index: 0, alice_bit: 0, alice_basis: 0, alice_basis_label: 'Z (+)', alice_state: '|0⟩', eve_intercepted: false, bob_basis: 0, bob_basis_label: 'Z (+)', bob_measured_bit: 0, bases_match: true, role: 'retained', is_error: false },
    { index: 1, alice_bit: 1, alice_basis: 1, alice_basis_label: 'X (×)', alice_state: '|−⟩', eve_intercepted: true, eve_basis: 0, eve_basis_label: 'Z (+)', eve_measured_bit: 0, bob_basis: 1, bob_basis_label: 'X (×)', bob_measured_bit: 0, bases_match: true, role: 'sampled', is_error: true },
    { index: 2, alice_bit: 0, alice_basis: 1, alice_basis_label: 'X (×)', alice_state: '|+⟩', eve_intercepted: false, bob_basis: 0, bob_basis_label: 'Z (+)', bob_measured_bit: 1, bases_match: false, role: 'discarded', is_error: null },
    { index: 3, alice_bit: 1, alice_basis: 0, alice_basis_label: 'Z (+)', alice_state: '|1⟩', eve_intercepted: true, eve_basis: 0, eve_basis_label: 'Z (+)', eve_measured_bit: 1, bob_basis: 0, bob_basis_label: 'Z (+)', bob_measured_bit: 1, bases_match: true, role: 'retained', is_error: false },
    { index: 4, alice_bit: 0, alice_basis: 0, alice_basis_label: 'Z (+)', alice_state: '|0⟩', eve_intercepted: false, bob_basis: 1, bob_basis_label: 'X (×)', bob_measured_bit: 0, bases_match: false, role: 'discarded', is_error: null },
    { index: 5, alice_bit: 1, alice_basis: 1, alice_basis_label: 'X (×)', alice_state: '|−⟩', eve_intercepted: false, bob_basis: 1, bob_basis_label: 'X (×)', bob_measured_bit: 1, bases_match: true, role: 'retained', is_error: false },
    { index: 6, alice_bit: 0, alice_basis: 1, alice_basis_label: 'X (×)', alice_state: '|+⟩', eve_intercepted: true, eve_basis: 1, eve_basis_label: 'X (×)', eve_measured_bit: 0, bob_basis: 1, bob_basis_label: 'X (×)', bob_measured_bit: 0, bases_match: true, role: 'sampled', is_error: false },
    { index: 7, alice_bit: 1, alice_basis: 0, alice_basis_label: 'Z (+)', alice_state: '|1⟩', eve_intercepted: true, eve_basis: 1, eve_basis_label: 'X (×)', eve_measured_bit: 0, bob_basis: 0, bob_basis_label: 'Z (+)', bob_measured_bit: 0, bases_match: true, role: 'sampled', is_error: true },
  ];

  const activeEvents = events && events.length > 0 ? events.slice(0, 30) : defaultEvents;

  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1500);

  const currentQubit = activeEvents[currentIndex] || activeEvents[0];

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (isPlaying) {
      timer = setInterval(() => {
        setCurrentIndex((prev) => (prev + 1) % activeEvents.length);
      }, playbackSpeed);
    }
    return () => clearInterval(timer);
  }, [isPlaying, activeEvents.length, playbackSpeed]);

  return (
    <section id="visualizer" className="py-20 px-4 sm:px-6 max-w-7xl mx-auto">
      {/* Section Header */}
      <div className="mb-12 text-center md:text-left flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/80 pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 text-cyan-400 text-xs font-mono uppercase tracking-widest mb-2">
            <Activity className="w-3.5 h-3.5" />
            <span>Step-by-Step Protocol · Section B</span>
          </div>
          <h2 className="font-heading font-extrabold text-3xl sm:text-4xl text-white tracking-tight">
            Alice, Eve & Bob Interactive Visualizer
          </h2>
          <p className="text-slate-400 text-sm max-w-2xl mt-1">
            Observe the quantum wavefunction travel across the channel, undergo eavesdropper interception and collapse, 
            and complete public basis sifting.
          </p>
        </div>

        {/* Playback Controls */}
        <div className="mt-4 md:mt-0 flex items-center space-x-2 bg-slate-900/90 border border-slate-800 p-1.5 rounded-xl shadow-lg">
          <button
            onClick={() => setCurrentIndex((prev) => (prev > 0 ? prev - 1 : activeEvents.length - 1))}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition-colors cursor-pointer"
            title="Previous Qubit"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className={`px-3 py-1.5 rounded-lg text-xs font-heading font-semibold uppercase tracking-wider flex items-center space-x-1.5 transition-all cursor-pointer ${
              isPlaying
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
            }`}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            <span>{isPlaying ? 'Pause' : 'Play'}</span>
          </button>

          <button
            onClick={() => setCurrentIndex((prev) => (prev + 1) % activeEvents.length)}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition-colors cursor-pointer"
            title="Next Qubit"
          >
            <ChevronRight className="w-4 h-4" />
          </button>

          <button
            onClick={() => {
              setIsPlaying(false);
              setCurrentIndex(0);
            }}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
            title="Reset"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <select
            value={playbackSpeed}
            onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
            className="bg-slate-950 text-slate-300 text-xs font-mono rounded px-2 py-1 border border-slate-800 focus:outline-none cursor-pointer"
          >
            <option value={2000}>0.5x</option>
            <option value={1200}>1.0x</option>
            <option value={600}>2.0x</option>
          </select>
        </div>
      </div>

      {/* Main Single-Qubit Step Flow Visualizer */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#0B1020]/90 border border-slate-800/90 shadow-2xl space-y-8">
        {/* Top Info Bar */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <span className="font-heading font-bold text-white text-lg">
              Photon #{currentQubit.index + 1}
            </span>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
              Sample {currentIndex + 1} of {activeEvents.length}
            </span>
          </div>

          <div className="flex items-center space-x-3 text-xs font-mono">
            <div className="flex items-center space-x-1.5">
              <span className="text-slate-500">Bases:</span>
              {currentQubit.bases_match ? (
                <span className="text-emerald-400 flex items-center space-x-1">
                  <Check className="w-3.5 h-3.5" />
                  <span>MATCH (Sifted)</span>
                </span>
              ) : (
                <span className="text-slate-500 flex items-center space-x-1">
                  <X className="w-3.5 h-3.5" />
                  <span>MISMATCH (Discarded)</span>
                </span>
              )}
            </div>

            <div className="flex items-center space-x-1.5 pl-3 border-l border-slate-800">
              <span className="text-slate-500">Pipeline Role:</span>
              <span className={`px-2 py-0.5 rounded uppercase font-semibold text-[10px] ${
                currentQubit.role === 'retained'
                  ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/50'
                  : currentQubit.role === 'sampled'
                  ? 'bg-amber-950/60 text-amber-300 border border-amber-800/50'
                  : 'bg-slate-900 text-slate-500'
              }`}>
                {currentQubit.role}
              </span>
            </div>
          </div>
        </div>

        {/* 3-Stage Diagram: Alice -> Eve -> Bob */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
          {/* Stage 1: Alice (Prep) */}
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-cyan-500/30 flex flex-col justify-between space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase text-cyan-400 font-semibold tracking-wider">
                1. Alice (Transmitter)
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/40">
                State Prep
              </span>
            </div>

            <div className="text-center py-4">
              <div className="w-20 h-20 mx-auto rounded-2xl bg-cyan-950/40 border border-cyan-500/40 flex flex-col items-center justify-center shadow-lg shadow-cyan-950/50">
                <span className="font-heading font-black text-2xl text-cyan-300">
                  {currentQubit.alice_state}
                </span>
                <span className="text-[10px] font-mono text-cyan-400/80 mt-1">
                  Bit {currentQubit.alice_bit}
                </span>
              </div>
            </div>

            <div className="space-y-1.5 text-xs font-mono pt-3 border-t border-slate-800 text-slate-400">
              <div className="flex justify-between">
                <span>Secret Bit:</span>
                <strong className="text-white">{currentQubit.alice_bit}</strong>
              </div>
              <div className="flex justify-between">
                <span>Encoding Basis:</span>
                <strong className="text-cyan-300">{currentQubit.alice_basis_label}</strong>
              </div>
            </div>
          </div>

          {/* Stage 2: Eve (Interception or Fiber Passage) */}
          <div className={`p-5 rounded-2xl border flex flex-col justify-between space-y-4 transition-all ${
            currentQubit.eve_intercepted
              ? 'bg-rose-950/20 border-rose-500/40 shadow-lg shadow-rose-950/30'
              : 'bg-slate-900/40 border-slate-800'
          }`}>
            <div className="flex items-center justify-between">
              <span className={`text-xs font-mono uppercase font-semibold tracking-wider ${
                currentQubit.eve_intercepted ? 'text-rose-400' : 'text-slate-400'
              }`}>
                2. Quantum Channel / Eve
              </span>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                currentQubit.eve_intercepted
                  ? 'bg-rose-950 text-rose-300 border-rose-800/50'
                  : 'bg-slate-900 text-slate-400 border-slate-800'
              }`}>
                {currentQubit.eve_intercepted ? 'Intercepted' : 'Transparent'}
              </span>
            </div>

            <div className="text-center py-4">
              {currentQubit.eve_intercepted ? (
                <div className="w-20 h-20 mx-auto rounded-2xl bg-rose-950/40 border border-rose-500/40 flex flex-col items-center justify-center shadow-lg shadow-rose-950/50">
                  <ShieldAlert className="w-6 h-6 text-rose-400 mb-1" />
                  <span className="text-[10px] font-mono text-rose-300">
                    Bit {currentQubit.eve_measured_bit}
                  </span>
                </div>
              ) : (
                <div className="w-20 h-20 mx-auto rounded-2xl bg-slate-900/40 border border-slate-800 flex flex-col items-center justify-center text-slate-600">
                  <Radio className="w-6 h-6 mb-1 text-slate-500" />
                  <span className="text-[10px] font-mono text-slate-500">Direct Fiber</span>
                </div>
              )}
            </div>

            <div className="space-y-1.5 text-xs font-mono pt-3 border-t border-slate-800 text-slate-400">
              <div className="flex justify-between">
                <span>Interception:</span>
                <strong className={currentQubit.eve_intercepted ? 'text-rose-400' : 'text-slate-500'}>
                  {currentQubit.eve_intercepted ? 'YES (State Collapsed)' : 'NO'}
                </strong>
              </div>
              <div className="flex justify-between">
                <span>Eve Basis:</span>
                <strong className="text-white">
                  {currentQubit.eve_basis_label || 'None'}
                </strong>
              </div>
            </div>
          </div>

          {/* Stage 3: Bob (Measurement) */}
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-violet-500/30 flex flex-col justify-between space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono uppercase text-violet-400 font-semibold tracking-wider">
                3. Bob (Receiver)
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-violet-950 text-violet-300 border border-violet-800/40">
                Measurement
              </span>
            </div>

            <div className="text-center py-4">
              <div className="w-20 h-20 mx-auto rounded-2xl bg-violet-950/40 border border-violet-500/40 flex flex-col items-center justify-center shadow-lg shadow-violet-950/50">
                <span className="font-heading font-black text-2xl text-violet-300">
                  {currentQubit.bob_measured_bit}
                </span>
                <span className="text-[10px] font-mono text-violet-400/80 mt-1">
                  Basis {currentQubit.bob_basis_label}
                </span>
              </div>
            </div>

            <div className="space-y-1.5 text-xs font-mono pt-3 border-t border-slate-800 text-slate-400">
              <div className="flex justify-between">
                <span>Measured Bit:</span>
                <strong className="text-white">{currentQubit.bob_measured_bit}</strong>
              </div>
              <div className="flex justify-between">
                <span>Error vs Alice:</span>
                <strong className={currentQubit.is_error ? 'text-rose-400' : 'text-emerald-400'}>
                  {currentQubit.is_error === null ? 'N/A (Bases Mismatched)' : currentQubit.is_error ? 'BIT ERROR (Flip)' : 'NO ERROR'}
                </strong>
              </div>
            </div>
          </div>
        </div>

        {/* Qubit Filmstrip Scroller */}
        <div className="pt-4 border-t border-slate-800">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-3">
            <span>Transmission Sequence Stream (Click any qubit to inspect):</span>
            <span>{activeEvents.length} qubits displayed</span>
          </div>

          <div className="flex space-x-2 overflow-x-auto pb-2">
            {activeEvents.map((ev, idx) => {
              const isSelected = idx === currentIndex;
              return (
                <button
                  key={ev.index}
                  onClick={() => {
                    setIsPlaying(false);
                    setCurrentIndex(idx);
                  }}
                  className={`flex-shrink-0 w-12 py-2 rounded-xl flex flex-col items-center justify-center font-mono text-xs transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-cyan-500 text-black font-bold scale-105 shadow-md shadow-cyan-500/40'
                      : ev.is_error
                      ? 'bg-rose-950/60 text-rose-300 border border-rose-800/80 hover:border-rose-500'
                      : ev.bases_match
                      ? 'bg-slate-900 text-slate-200 border border-slate-800 hover:border-cyan-500/50'
                      : 'bg-slate-950 text-slate-600 border border-slate-900'
                  }`}
                >
                  <span className="text-[10px] opacity-70">#{ev.index + 1}</span>
                  <span className="text-sm font-bold mt-0.5">{ev.alice_bit}</span>
                  <span className="text-[9px] mt-0.5">
                    {ev.bases_match ? (ev.is_error ? 'ERR' : 'OK') : 'DISC'}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};
