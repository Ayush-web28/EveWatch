import React, { useState } from 'react';
import { ExternalLink, Info, CheckCircle2, AlertOctagon } from 'lucide-react';
import type { SimulationRequest } from '../types/quantum';

interface NoiseVsEveHeatmapProps {
  onLoadParameters: (params: Partial<SimulationRequest>) => void;
}

export const NoiseVsEveHeatmap: React.FC<NoiseVsEveHeatmapProps> = ({ onLoadParameters }) => {
  // Matrix dimensions
  // Noise p from 0.0 to 0.40 in steps of 0.04
  const noiseValues = [0.0, 0.04, 0.08, 0.12, 0.16, 0.20, 0.24, 0.28, 0.32, 0.36, 0.40];
  // Eve fraction f from 1.0 down to 0.0 in steps of 0.1
  const eveValues = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0];

  // Selected cell
  const [selectedCell, setSelectedCell] = useState<{ f: number; p: number }>({ f: 0.5, p: 0.08 });

  // Calculate theoretical QBER: Q = f/4 + p/2 - (f*p)/4
  const calculateQber = (f: number, p: number) => {
    return (f / 4.0) + (p / 2.0) - ((f * p) / 4.0);
  };

  // Binary entropy H2(p)
  const h2 = (p: number) => {
    if (p <= 0 || p >= 1) return 0;
    return -p * Math.log2(p) - (1 - p) * Math.log2(1 - p);
  };

  // Secret key rate: r = max(0, 1 - 2*H2(Q))
  const calculateKeyRate = (qber: number) => {
    if (qber >= 0.11) return 0;
    return Math.max(0, 1.0 - 2.0 * h2(qber));
  };

  const selectedQber = calculateQber(selectedCell.f, selectedCell.p);
  const selectedKeyRate = calculateKeyRate(selectedQber);
  const isSecure = selectedQber < 0.11;

  // Color mapping based on QBER
  const getCellColor = (qber: number) => {
    if (qber < 0.05) return 'bg-emerald-950/80 border-emerald-800/40 text-emerald-300';
    if (qber < 0.11) return 'bg-cyan-950/80 border-cyan-800/40 text-cyan-300';
    if (qber < 0.20) return 'bg-amber-950/80 border-amber-800/40 text-amber-300';
    return 'bg-rose-950/90 border-rose-800/50 text-rose-300';
  };

  return (
    <section id="noise-eve" className="py-20 px-4 sm:px-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-12 text-center md:text-left flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/80 pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 text-cyan-400 text-xs font-mono uppercase tracking-widest mb-2">
            <Info className="w-3.5 h-3.5" />
            <span>Core Differentiator · Section C</span>
          </div>
          <h2 className="font-heading font-extrabold text-3xl sm:text-4xl text-white tracking-tight">
            The Noise vs. Eve Problem
          </h2>
          <p className="text-slate-400 text-sm max-w-2xl mt-1">
            Both environmental channel noise and active intercept-resend eavesdropping introduce bit flips in BB84.
            Explore the 2D parameter space and inspect the fundamental Shor-Preskill security boundary.
          </p>
        </div>

        {/* Legend */}
        <div className="mt-4 md:mt-0 flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded bg-cyan-900 border border-cyan-500" />
            <span className="text-slate-300">Secure (&lt; 11%)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded bg-rose-950 border border-rose-500" />
            <span className="text-slate-300">Compromised (≥ 11%)</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Heatmap Grid (8 cols) */}
        <div className="lg:col-span-8 p-6 rounded-2xl bg-[#0B1020]/90 border border-slate-800/90 shadow-2xl">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
              2D Error Response Surface: QBER(f, p)
            </span>
            <span className="text-[11px] font-mono text-slate-500">
              Hover or click cells to inspect
            </span>
          </div>

          <div className="overflow-x-auto">
            <div className="min-w-[550px]">
              {/* Top X-Axis label */}
              <div className="text-center text-xs font-mono text-cyan-400 mb-2 font-semibold">
                Optical Channel Depolarizing Noise (p) →
              </div>

              {/* Heatmap Matrix */}
              <div className="grid grid-cols-12 gap-1.5 items-center">
                {/* Y-axis label column */}
                <div className="col-span-1 text-[10px] font-mono text-rose-400 font-semibold text-right pr-2">
                  Eve (f)
                </div>

                {/* Column header values */}
                <div className="col-span-11 grid grid-cols-11 gap-1 text-center text-[10px] font-mono text-slate-400 pb-1">
                  {noiseValues.map((p) => (
                    <span key={p}>{(p * 100).toFixed(0)}%</span>
                  ))}
                </div>

                {/* Rows for each Eve fraction */}
                {eveValues.map((f) => (
                  <React.Fragment key={f}>
                    <div className="col-span-1 text-[10px] font-mono text-slate-400 text-right pr-2">
                      {(f * 100).toFixed(0)}%
                    </div>
                    <div className="col-span-11 grid grid-cols-11 gap-1">
                      {noiseValues.map((p) => {
                        const qber = calculateQber(f, p);
                        const isSelected = selectedCell.f === f && selectedCell.p === p;
                        const isBoundary = Math.abs(qber - 0.11) < 0.02;

                        return (
                          <button
                            key={`${f}-${p}`}
                            onClick={() => setSelectedCell({ f, p })}
                            className={`h-9 rounded font-mono text-[10px] font-medium border flex items-center justify-center transition-all cursor-pointer ${getCellColor(
                              qber
                            )} ${
                              isSelected
                                ? 'ring-2 ring-cyan-400 scale-105 z-10 shadow-lg shadow-cyan-400/40 font-bold'
                                : 'hover:scale-105 hover:z-10'
                            } ${isBoundary ? 'border-dashed border-white/60' : ''}`}
                            title={`f=${f}, p=${p} → QBER: ${(qber * 100).toFixed(1)}%`}
                          >
                            {(qber * 100).toFixed(0)}%
                          </button>
                        );
                      })}
                    </div>
                  </React.Fragment>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] font-mono text-slate-400 flex items-center justify-between">
            <span>Dashed cells indicate proximity to the critical 11.0% Shor-Preskill threshold.</span>
            <span className="text-cyan-400">Formula: Q = f/4 + p/2 - f·p/4</span>
          </div>
        </div>

        {/* Inspector Panel (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          <div className="p-6 rounded-2xl bg-[#0B1020]/90 border border-slate-800/90 shadow-2xl space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <span className="font-heading font-semibold text-white text-base">Point Inspector</span>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                isSecure ? 'bg-emerald-950 text-emerald-300 border border-emerald-800' : 'bg-rose-950 text-rose-300 border border-rose-800'
              }`}>
                {isSecure ? 'SECURE' : 'ABORT REQUIRED'}
              </span>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Eve Interception (f):</span>
                <strong className="text-rose-400">{(selectedCell.f * 100).toFixed(1)}%</strong>
              </div>
              <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Channel Noise (p):</span>
                <strong className="text-violet-400">{(selectedCell.p * 100).toFixed(1)}%</strong>
              </div>
              <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Theoretical QBER:</span>
                <strong className={isSecure ? 'text-cyan-300' : 'text-rose-400'}>
                  {(selectedQber * 100).toFixed(2)}%
                </strong>
              </div>
              <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                <span className="text-slate-400">Secret Key Rate (r):</span>
                <strong className={selectedKeyRate > 0 ? 'text-emerald-400' : 'text-slate-500'}>
                  {selectedKeyRate.toFixed(4)}
                </strong>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/40 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
              {isSecure ? (
                <div className="flex items-start space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span>
                    QBER is strictly below 11.0%. After Cascade error correction and privacy amplification, 
                    Alice and Bob distill an information-theoretically secure key at rate <strong>{selectedKeyRate.toFixed(3)}</strong>.
                  </span>
                </div>
              ) : (
                <div className="flex items-start space-x-2">
                  <AlertOctagon className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                  <span>
                    QBER exceeds the 11.0% asymptotic limit. Eve's mutual information exceeds Bob's mutual information: 
                    no secure key can be distilled, protocol MUST abort.
                  </span>
                </div>
              )}
            </div>

            <button
              onClick={() => onLoadParameters({
                num_qubits: 150,
                eve_present: selectedCell.f > 0,
                eve_fraction: selectedCell.f,
                channel_noise_prob: selectedCell.p,
              })}
              className="w-full py-2.5 rounded-xl font-heading text-xs font-semibold uppercase tracking-wider bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 hover:border-cyan-500/60 transition-all flex items-center justify-center space-x-2 cursor-pointer"
            >
              <span>Load into Quantum Lab</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Scientific Insight Card */}
          <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-2">
            <div className="flex items-center space-x-2 text-xs font-heading font-semibold text-white">
              <Info className="w-4 h-4 text-cyan-400" />
              <span>Why Noise Mimics Eve</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              When Eve measures in the wrong basis, she collapses the quantum state, resulting in a 50% bit flip error on conjugate bases. 
              Similarly, depolarizing channel noise randomly rotates photon polarization. From the single scalar QBER metric alone, 
              Alice and Bob cannot determine whether errors arise from physical fiber loss or an eavesdropper without calibrated hardware baselines.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
