import React, { useState } from 'react';
import { 
  Cpu, 
  Play, 
  RefreshCw, 
  ShieldAlert, 
  ShieldCheck, 
  Terminal, 
  Sliders, 
  Binary
} from 'lucide-react';
import { api } from '../api/client';
import type { SimulationRequest, SimulationResponse } from '../types/quantum';

interface QuantumLabProps {
  onSimulationComplete?: (results: SimulationResponse) => void;
  externalPreset?: Partial<SimulationRequest> | null;
}

export const QuantumLab: React.FC<QuantumLabProps> = ({ 
  onSimulationComplete,
  externalPreset,
}) => {
  // Configuration State
  const [numQubits, setNumQubits] = useState<number>(100);
  const [evePresent, setEvePresent] = useState<boolean>(true);
  const [eveFraction, setEveFraction] = useState<number>(0.5);
  const [channelNoise, setChannelNoise] = useState<number>(0.0);
  const [depolError, setDepolError] = useState<number>(0.0);
  const [readoutError, setReadoutError] = useState<number>(0.0);
  const [abortThreshold, setAbortThreshold] = useState<number>(0.11);
  const [sampleSize, setSampleSize] = useState<number>(0.5);
  const [seed, setSeed] = useState<number>(42);
  const [useFakeBackend, setUseFakeBackend] = useState<boolean>(false);
  const [showCircuit, setShowCircuit] = useState<boolean>(false);

  // Execution State
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [results, setResults] = useState<SimulationResponse | null>(null);

  // Apply external presets if passed (e.g. from the Heatmap click)
  React.useEffect(() => {
    if (externalPreset) {
      if (externalPreset.num_qubits !== undefined) setNumQubits(externalPreset.num_qubits);
      if (externalPreset.eve_present !== undefined) setEvePresent(externalPreset.eve_present);
      if (externalPreset.eve_fraction !== undefined) setEveFraction(externalPreset.eve_fraction);
      if (externalPreset.channel_noise_prob !== undefined) setChannelNoise(externalPreset.channel_noise_prob);
    }
  }, [externalPreset]);

  const handleRunSimulation = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const payload: SimulationRequest = {
        num_qubits: numQubits,
        eve_present: evePresent,
        eve_fraction: eveFraction,
        channel_noise_prob: channelNoise,
        depolarizing_error_prob: depolError,
        readout_error_prob: readoutError,
        abort_threshold: abortThreshold,
        sample_size: sampleSize,
        seed: seed || undefined,
        use_fake_backend: useFakeBackend,
        include_circuit: true,
      };

      const response = await api.simulate(payload);
      setResults(response);
      if (onSimulationComplete) {
        onSimulationComplete(response);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to execute quantum simulation.');
    } finally {
      setIsLoading(false);
    }
  };

  const applyPreset = (presetName: string) => {
    switch (presetName) {
      case 'ideal':
        setEvePresent(false);
        setEveFraction(0.0);
        setChannelNoise(0.0);
        setDepolError(0.0);
        setReadoutError(0.0);
        setUseFakeBackend(false);
        break;
      case 'subtle_eve':
        setEvePresent(true);
        setEveFraction(0.2);
        setChannelNoise(0.01);
        setDepolError(0.0);
        setReadoutError(0.0);
        setUseFakeBackend(false);
        break;
      case 'heavy_eve':
        setEvePresent(true);
        setEveFraction(0.8);
        setChannelNoise(0.0);
        setDepolError(0.0);
        setReadoutError(0.0);
        setUseFakeBackend(false);
        break;
      case 'fiber_noise':
        setEvePresent(false);
        setEveFraction(0.0);
        setChannelNoise(0.12);
        setDepolError(0.0);
        setReadoutError(0.0);
        setUseFakeBackend(false);
        break;
      case 'ibm_hardware':
        setEvePresent(false);
        setEveFraction(0.0);
        setChannelNoise(0.0);
        setUseFakeBackend(true);
        break;
    }
  };

  return (
    <section id="lab" className="py-20 px-4 sm:px-6 max-w-7xl mx-auto">
      {/* Section Header */}
      <div className="mb-12 text-center md:text-left flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/80 pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 text-cyan-400 text-xs font-mono uppercase tracking-widest mb-2">
            <Cpu className="w-3.5 h-3.5" />
            <span>Interactive Simulator · Section A</span>
          </div>
          <h2 className="font-heading font-extrabold text-3xl sm:text-4xl text-white tracking-tight">
            Quantum Key Distribution Lab
          </h2>
          <p className="text-slate-400 text-sm max-w-2xl mt-1">
            Configure state preparation, eavesdropping strategy, and physical noise channels. 
            All simulations are calculated directly by Qiskit AerSimulator.
          </p>
        </div>

        {/* Quick Presets */}
        <div className="mt-4 md:mt-0 flex flex-wrap gap-2">
          <span className="text-xs font-mono text-slate-500 self-center mr-1">Presets:</span>
          <button
            onClick={() => applyPreset('ideal')}
            className="text-xs font-mono px-2.5 py-1 rounded bg-slate-900 border border-slate-800 hover:border-cyan-500/50 text-slate-300 hover:text-cyan-400 transition-colors cursor-pointer"
          >
            Ideal Channel
          </button>
          <button
            onClick={() => applyPreset('subtle_eve')}
            className="text-xs font-mono px-2.5 py-1 rounded bg-slate-900 border border-slate-800 hover:border-amber-500/50 text-slate-300 hover:text-amber-400 transition-colors cursor-pointer"
          >
            Subtle Eve (20%)
          </button>
          <button
            onClick={() => applyPreset('heavy_eve')}
            className="text-xs font-mono px-2.5 py-1 rounded bg-slate-900 border border-slate-800 hover:border-rose-500/50 text-slate-300 hover:text-rose-400 transition-colors cursor-pointer"
          >
            Heavy Eve (80%)
          </button>
          <button
            onClick={() => applyPreset('fiber_noise')}
            className="text-xs font-mono px-2.5 py-1 rounded bg-slate-900 border border-slate-800 hover:border-violet-500/50 text-slate-300 hover:text-violet-400 transition-colors cursor-pointer"
          >
            Fiber Noise (12%)
          </button>
          <button
            onClick={() => applyPreset('ibm_hardware')}
            className="text-xs font-mono px-2.5 py-1 rounded bg-slate-900 border border-slate-800 hover:border-cyan-500/50 text-slate-300 hover:text-cyan-400 transition-colors cursor-pointer"
          >
            IBM Brisbane Noise
          </button>
        </div>
      </div>

      {/* Main Grid: Controls (Left) vs Results (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Controls Column */}
        <div className="lg:col-span-5 space-y-6">
          <div className="p-6 rounded-2xl bg-[#0B1020]/90 border border-slate-800/90 shadow-xl space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <Sliders className="w-4 h-4 text-cyan-400" />
                <h3 className="font-heading font-semibold text-white text-base">Channel & Attack Parameters</h3>
              </div>
              <button 
                onClick={() => setSeed(Math.floor(Math.random() * 10000))} 
                title="Randomize Seed" 
                className="text-xs text-slate-400 hover:text-cyan-400 flex items-center space-x-1 cursor-pointer"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Seed: {seed}</span>
              </button>
            </div>

            {/* Qubit Count */}
            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-slate-300">Transmitted Qubits (N)</span>
                <span className="text-cyan-400 font-bold">{numQubits}</span>
              </div>
              <input
                type="range"
                min="50"
                max="500"
                step="25"
                value={numQubits}
                onChange={(e) => setNumQubits(parseInt(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
                <span>50</span>
                <span>250</span>
                <span>500 qubits</span>
              </div>
            </div>

            {/* Eve Interception Controls */}
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <ShieldAlert className={`w-4 h-4 ${evePresent ? 'text-rose-400' : 'text-slate-500'}`} />
                  <span className="text-xs font-heading font-medium text-white">Eve Eavesdropper</span>
                </div>
                <button
                  onClick={() => setEvePresent(!evePresent)}
                  className={`text-xs font-mono px-3 py-1 rounded-full font-semibold transition-all cursor-pointer ${
                    evePresent 
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' 
                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}
                >
                  {evePresent ? 'Active' : 'Disabled'}
                </button>
              </div>

              {evePresent && (
                <div>
                  <div className="flex justify-between text-xs font-mono mb-1">
                    <span className="text-slate-400">Interception Fraction (f)</span>
                    <span className="text-rose-400 font-bold">{(eveFraction * 100).toFixed(0)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={eveFraction}
                    onChange={(e) => setEveFraction(parseFloat(e.target.value))}
                    className="w-full accent-rose-400 cursor-pointer"
                  />
                  <p className="text-[11px] text-slate-400 mt-1">
                    Fraction of channel photons measured by Eve in random conjugate bases.
                  </p>
                </div>
              )}
            </div>

            {/* Noise Parameters */}
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs font-mono mb-1">
                  <span className="text-slate-300">Channel Depolarizing Noise (p)</span>
                  <span className="text-violet-400 font-bold">{(channelNoise * 100).toFixed(1)}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="0.4"
                  step="0.01"
                  value={channelNoise}
                  onChange={(e) => setChannelNoise(parseFloat(e.target.value))}
                  className="w-full accent-violet-400 cursor-pointer"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Optical fiber depolarizing probability. Induces random bit and phase errors.
                </p>
              </div>

              {/* Hardware Noise Model Checkbox */}
              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/40 border border-slate-800/80">
                <div className="flex flex-col">
                  <span className="text-xs font-medium text-slate-200">IBM FakeBrisbane Backend</span>
                  <span className="text-[10px] text-slate-500">Calibrated real quantum hardware noise characteristics</span>
                </div>
                <input
                  type="checkbox"
                  checked={useFakeBackend}
                  onChange={(e) => setUseFakeBackend(e.target.checked)}
                  className="w-4 h-4 accent-cyan-400 rounded cursor-pointer"
                />
              </div>

              {/* Advanced Parameters Collapse / Slider */}
              <div className="grid grid-cols-2 gap-3 pt-2">
                <div>
                  <label className="block text-[11px] font-mono text-slate-400 mb-1">
                    Abort Cutoff QBER
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    max="0.5"
                    value={abortThreshold}
                    onChange={(e) => setAbortThreshold(parseFloat(e.target.value))}
                    className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1 text-xs font-mono text-white focus:border-cyan-400 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono text-slate-400 mb-1">
                    Sample Reveal Ratio
                  </label>
                  <input
                    type="number"
                    step="0.05"
                    min="0.1"
                    max="0.9"
                    value={sampleSize}
                    onChange={(e) => setSampleSize(parseFloat(e.target.value))}
                    className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1 text-xs font-mono text-white focus:border-cyan-400 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            {/* Action Button */}
            <button
              onClick={handleRunSimulation}
              disabled={isLoading}
              className={`w-full py-3.5 rounded-xl font-heading text-sm font-semibold uppercase tracking-wider transition-all duration-200 flex items-center justify-center space-x-2 shadow-xl cursor-pointer ${
                isLoading
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-cyan-400 via-sky-300 to-teal-300 hover:from-cyan-300 hover:to-white text-black shadow-cyan-500/20 active:scale-95'
              }`}
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Computing Quantum Circuits...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Execute BB84 Simulation</span>
                </>
              )}
            </button>

            {errorMsg && (
              <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-800/80 text-rose-300 text-xs">
                {errorMsg}
              </div>
            )}
          </div>
        </div>

        {/* Results Column */}
        <div className="lg:col-span-7 space-y-6">
          {results ? (
            <div className="space-y-6">
              {/* Verdict Banner */}
              <div className={`p-6 rounded-2xl border backdrop-blur-md shadow-2xl relative overflow-hidden ${
                results.aborted
                  ? 'bg-rose-950/20 border-rose-500/40 shadow-rose-950/20'
                  : 'bg-emerald-950/20 border-emerald-500/40 shadow-emerald-950/20'
              }`}>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2.5 rounded-xl ${results.aborted ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                      {results.aborted ? <ShieldAlert className="w-6 h-6" /> : <ShieldCheck className="w-6 h-6" />}
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className={`font-heading font-bold text-lg ${results.aborted ? 'text-rose-400' : 'text-emerald-400'}`}>
                          {results.verdict}
                        </span>
                        <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                          {results.aborted ? 'Channel Compromised' : 'Key Exchange Valid'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 mt-1 max-w-xl">
                        {results.verdict_detail}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] font-mono uppercase text-slate-500">Security Cutoff</span>
                    <div className="text-xs font-mono font-bold text-slate-300">
                      {(results.abort_threshold * 100).toFixed(1)}% QBER
                    </div>
                  </div>
                </div>
              </div>

              {/* Metric Cards Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {/* QBER Metric */}
                <div className="p-4 rounded-xl bg-[#0B1020]/90 border border-slate-800 text-center">
                  <span className="text-[11px] font-mono text-slate-400 uppercase">Observed QBER</span>
                  <div className={`text-2xl font-mono font-bold mt-1 ${
                    results.sample_qber >= results.abort_threshold ? 'text-rose-400' : 'text-cyan-400'
                  }`}>
                    {(results.sample_qber * 100).toFixed(1)}%
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">
                    Theory: {(results.metadata.theoretical_qber * 100).toFixed(1)}%
                  </span>
                </div>

                {/* Sifted Bits */}
                <div className="p-4 rounded-xl bg-[#0B1020]/90 border border-slate-800 text-center">
                  <span className="text-[11px] font-mono text-slate-400 uppercase">Sifted Key</span>
                  <div className="text-2xl font-mono font-bold text-white mt-1">
                    {results.sifted_count} <span className="text-xs font-normal text-slate-400">bits</span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {(results.sifted_ratio * 100).toFixed(1)}% retained
                  </span>
                </div>

                {/* Secret Key Rate */}
                <div className="p-4 rounded-xl bg-[#0B1020]/90 border border-slate-800 text-center">
                  <span className="text-[11px] font-mono text-slate-400 uppercase">Secret Key Rate</span>
                  <div className={`text-2xl font-mono font-bold mt-1 ${
                    results.secret_key_rate > 0 ? 'text-emerald-400' : 'text-slate-500'
                  }`}>
                    {results.secret_key_rate.toFixed(3)}
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">
                    r = 1 - 2H(Q)
                  </span>
                </div>

                {/* Retained Key Length */}
                <div className="p-4 rounded-xl bg-[#0B1020]/90 border border-slate-800 text-center">
                  <span className="text-[11px] font-mono text-slate-400 uppercase">Distilled Key</span>
                  <div className="text-2xl font-mono font-bold text-white mt-1">
                    {results.retained_key_length} <span className="text-xs font-normal text-slate-400">bits</span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">
                    Post-estimation
                  </span>
                </div>
              </div>

              {/* Key Preview Box */}
              <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <div className="flex items-center space-x-2">
                    <Binary className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Key Agreement Check: <strong className="text-white">{(results.key_agreement_rate * 100).toFixed(1)}%</strong></span>
                  </div>
                  <span className="text-[11px] text-slate-500">First 32 sample bits</span>
                </div>
                <div className="space-y-1 font-mono text-xs">
                  <div className="flex items-center space-x-2">
                    <span className="text-cyan-400 w-12 text-[11px]">Alice:</span>
                    <span className="text-slate-200 tracking-wider bg-slate-950 px-2 py-0.5 rounded border border-slate-800/80">
                      {results.alice_key_preview || 'None'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-violet-400 w-12 text-[11px]">Bob:</span>
                    <span className="text-slate-200 tracking-wider bg-slate-950 px-2 py-0.5 rounded border border-slate-800/80">
                      {results.bob_key_preview || 'None'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Circuit Preview Toggle */}
              {results.circuit_ascii && (
                <div className="rounded-xl border border-slate-800 overflow-hidden">
                  <button
                    onClick={() => setShowCircuit(!showCircuit)}
                    className="w-full p-3 bg-slate-900/60 hover:bg-slate-900 flex items-center justify-between text-xs font-mono text-slate-300 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center space-x-2">
                      <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Qiskit Quantum Circuit Diagram (Qubit 0)</span>
                    </div>
                    <span className="text-cyan-400">{showCircuit ? 'Hide Circuit' : 'View Circuit'}</span>
                  </button>
                  {showCircuit && (
                    <div className="p-4 bg-slate-950 border-t border-slate-800 overflow-x-auto">
                      <pre className="font-mono text-xs text-cyan-300 leading-relaxed whitespace-pre">
                        {results.circuit_ascii}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            /* Empty State */
            <div className="h-full min-h-[380px] p-8 rounded-2xl bg-[#0B1020]/40 border border-dashed border-slate-800 flex flex-col items-center justify-center text-center">
              <div className="w-14 h-14 rounded-2xl bg-cyan-950/50 border border-cyan-800/40 flex items-center justify-center text-cyan-400 mb-4 shadow-lg shadow-cyan-950/50">
                <Cpu className="w-7 h-7" />
              </div>
              <h3 className="font-heading font-bold text-lg text-white mb-2">
                Awaiting Simulation Execution
              </h3>
              <p className="text-slate-400 text-xs max-w-md leading-relaxed mb-6">
                Adjust parameters on the left or select a preset, then click <strong className="text-cyan-300">Execute BB84 Simulation</strong> to run the Qiskit quantum circuit simulator.
              </p>
              <div className="flex items-center space-x-4 text-xs font-mono text-slate-500">
                <span>· 100% Python Qiskit Backend</span>
                <span>· No Mock Data</span>
                <span>· Real Error Statistics</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
