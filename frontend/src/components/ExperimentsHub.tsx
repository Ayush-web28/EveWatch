import React, { useState, useEffect } from 'react';
import { BarChart3, Download, RefreshCw, FileText, TrendingUp } from 'lucide-react';
import { api } from '../api/client';
import type { ExperimentDataset } from '../types/quantum';

export const ExperimentsHub: React.FC = () => {
  const [experiments, setExperiments] = useState<ExperimentDataset[]>([]);
  const [selectedExpId, setSelectedExpId] = useState<string>('exp1');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchDatasets = async () => {
      try {
        setIsLoading(true);
        const data = await api.getExperiments();
        if (isMounted) {
          setExperiments(data);
          if (data.length > 0) setSelectedExpId(data[0].id);
        }
      } catch (err: any) {
        if (isMounted) setErrorMsg(err.message || 'Failed to fetch experiment benchmarks.');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };
    fetchDatasets();
    return () => {
      isMounted = false;
    };
  }, []);

  const currentExp = experiments.find((e) => e.id === selectedExpId) || experiments[0];

  const downloadCsv = () => {
    if (!currentExp) return;
    const headers = currentExp.columns.join(',');
    const rows = currentExp.rows.map((row) => currentExp.columns.map((col) => row[col]).join(',')).join('\n');
    const csvContent = `data:text/csv;charset=utf-8,${headers}\n${rows}`;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${currentExp.id}_dataset.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <section id="experiments" className="py-20 px-4 sm:px-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-12 text-center md:text-left flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/80 pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 text-cyan-400 text-xs font-mono uppercase tracking-widest mb-2">
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Empirical Research · Section D</span>
          </div>
          <h2 className="font-heading font-extrabold text-3xl sm:text-4xl text-white tracking-tight">
            Experimental Results & Benchmark Hub
          </h2>
          <p className="text-slate-400 text-sm max-w-2xl mt-1">
            Review the 6 empirical research benchmarks produced during the study. 
            All data points reflect verified simulation trials and calibrated IBM quantum hardware models.
          </p>
        </div>

        {currentExp && (
          <button
            onClick={downloadCsv}
            className="mt-4 md:mt-0 px-4 py-2 rounded-xl text-xs font-mono bg-slate-900 border border-slate-800 hover:border-cyan-500/40 text-slate-300 hover:text-white transition-all flex items-center space-x-2 shadow-lg cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Download CSV ({currentExp.source_file})</span>
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="p-16 rounded-2xl bg-[#0B1020]/40 border border-slate-800 flex flex-col items-center justify-center text-center">
          <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin mb-3" />
          <span className="text-xs font-mono text-slate-400">Loading experimental benchmarks from disk...</span>
        </div>
      ) : errorMsg ? (
        <div className="p-6 rounded-2xl bg-rose-950/30 border border-rose-800/60 text-rose-300 text-xs font-mono">
          {errorMsg}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Experiment Navigation Tabs */}
          <div className="flex space-x-2 overflow-x-auto pb-2">
            {experiments.map((exp) => {
              const isSelected = exp.id === selectedExpId;
              return (
                <button
                  key={exp.id}
                  onClick={() => setSelectedExpId(exp.id)}
                  className={`flex-shrink-0 px-4 py-2 rounded-xl text-xs font-heading font-medium transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-gradient-to-r from-cyan-500/20 to-violet-500/20 text-cyan-300 border border-cyan-500/40 shadow-md shadow-cyan-500/10'
                      : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800/80 hover:bg-slate-800/60'
                  }`}
                >
                  {exp.title}
                </button>
              );
            })}
          </div>

          {currentExp && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              {/* Summary and Details (4 cols) */}
              <div className="lg:col-span-4 space-y-6">
                <div className="p-6 rounded-2xl bg-[#0B1020]/90 border border-slate-800/90 shadow-2xl space-y-4">
                  <div className="flex items-center space-x-2 text-xs font-mono text-cyan-400">
                    <FileText className="w-4 h-4" />
                    <span className="uppercase font-semibold">{currentExp.id.toUpperCase()}</span>
                  </div>

                  <h3 className="font-heading font-bold text-lg text-white">
                    {currentExp.title}
                  </h3>

                  <p className="text-xs text-slate-300 leading-relaxed">
                    {currentExp.description}
                  </p>

                  <div className="pt-3 border-t border-slate-800 space-y-2">
                    <span className="text-[11px] font-mono text-slate-400 uppercase">Benchmark Metadata</span>
                    <div className="space-y-1.5 font-mono text-xs">
                      <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                        <span className="text-slate-400">Total Rows:</span>
                        <strong className="text-white">{currentExp.summary.total_rows}</strong>
                      </div>
                      <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                        <span className="text-slate-400">Columns:</span>
                        <strong className="text-cyan-300">{currentExp.columns.length}</strong>
                      </div>
                      <div className="flex justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                        <span className="text-slate-400">File:</span>
                        <strong className="text-slate-300 text-[11px]">{currentExp.source_file}</strong>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Key Research Takeaway */}
                <div className="p-5 rounded-2xl bg-gradient-to-br from-cyan-950/30 to-violet-950/20 border border-cyan-800/30 space-y-2">
                  <div className="flex items-center space-x-2 text-xs font-heading font-semibold text-cyan-300">
                    <TrendingUp className="w-4 h-4" />
                    <span>Scientific Takeaway</span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {currentExp.id === 'exp1' && "Confirms the linear relationship Q = 0.25 × f. Even with 100% interception, Eve only induces 25% QBER because half her basis guesses match Alice's."}
                    {currentExp.id === 'exp2' && "Confirms Q = 0.50 × p for pure depolarizing noise. Depolarizing noise induces errors at twice the rate per unit probability compared to eavesdropping."}
                    {currentExp.id === 'exp3' && "Empirically validates the 2D surface Q(f, p) = f/4 + p/2 - f·p/4 across 121 grid points, proving the non-linear interaction when both noise and eavesdropping coexist."}
                    {currentExp.id === 'exp4' && "Demonstrates that with a sample size k ≥ 100 sifted bits, the probability of detecting an eavesdropper with f ≥ 0.20 exceeds 99.9%."}
                    {currentExp.id === 'exp5' && "Establishes that the asymptotic secret key rate drops to exactly zero at Q = 11.0%, perfectly matching the theoretical Shor-Preskill bound."}
                    {currentExp.id === 'exp6' && "Shows that physical IBM superconducting quantum hardware exhibits baseline readout and CNOT gate noise that accounts for ~3-5% intrinsic QBER even without an eavesdropper."}
                  </p>
                </div>
              </div>

              {/* Data Table (8 cols) */}
              <div className="lg:col-span-8 p-6 rounded-2xl bg-[#0B1020]/90 border border-slate-800/90 shadow-2xl">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
                  <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                    Tabular Measurements ({currentExp.rows.length} records)
                  </span>
                  <span className="text-[11px] font-mono text-cyan-400">
                    Source: results/{currentExp.source_file}
                  </span>
                </div>

                <div className="overflow-x-auto max-h-[460px] overflow-y-auto">
                  <table className="w-full text-left font-mono text-xs">
                    <thead className="sticky top-0 bg-slate-900 text-slate-300 border-b border-slate-800">
                      <tr>
                        {currentExp.columns.map((col) => (
                          <th key={col} className="px-3 py-2.5 font-semibold uppercase text-[10px] tracking-wider">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-slate-300">
                      {currentExp.rows.map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                          {currentExp.columns.map((col) => {
                            const val = row[col];
                            const isNumber = typeof val === 'number';
                            return (
                              <td key={col} className="px-3 py-2 whitespace-nowrap">
                                {isNumber ? val.toFixed(4) : String(val)}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
};
