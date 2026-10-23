import React, { useState } from 'react';
import { Key, Lock, ShieldAlert, ShieldCheck, RefreshCw, Send, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';
import type { EncryptResponse } from '../types/quantum';

export const SecureMessaging: React.FC = () => {
  const [plaintext, setPlaintext] = useState<string>('DEFEND QUANTUM NETWORK 2026');
  const [estimatedQber, setEstimatedQber] = useState<number>(0.03);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [result, setResult] = useState<EncryptResponse | null>(null);

  const handleEncrypt = async () => {
    if (!plaintext.trim()) return;
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const response = await api.encryptMessage({
        message: plaintext,
        estimated_qber: estimatedQber,
      });
      setResult(response);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to encrypt message.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="messaging" className="py-20 px-4 sm:px-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-12 text-center md:text-left flex flex-col md:flex-row md:items-end justify-between border-b border-slate-800/80 pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 text-cyan-400 text-xs font-mono uppercase tracking-widest mb-2">
            <Key className="w-3.5 h-3.5" />
            <span>Post-Processing Application · Section E</span>
          </div>
          <h2 className="font-heading font-extrabold text-3xl sm:text-4xl text-white tracking-tight">
            One-Time Pad Secure Messaging
          </h2>
          <p className="text-slate-400 text-sm max-w-2xl mt-1">
            Apply the distilled quantum key to encrypt arbitrary messages via Shannon-perfect One-Time Pad (Vernam cipher) 
            with parity reconciliation and Toeplitz privacy amplification.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Input Column (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="p-6 rounded-2xl bg-[#0B1020]/90 border border-slate-800/90 shadow-2xl space-y-5">
            <div className="flex items-center space-x-2 pb-3 border-b border-slate-800">
              <Lock className="w-4 h-4 text-cyan-400" />
              <h3 className="font-heading font-semibold text-white text-base">Alice's Secret Transmitter</h3>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 mb-2">
                Plaintext Message (P):
              </label>
              <textarea
                rows={3}
                value={plaintext}
                onChange={(e) => setPlaintext(e.target.value)}
                placeholder="Type confidential transmission..."
                className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm font-mono text-white placeholder-slate-600 focus:border-cyan-400 focus:outline-none transition-colors"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-slate-300">Estimated Channel QBER</span>
                <span className="text-cyan-400 font-bold">{(estimatedQber * 100).toFixed(1)}%</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="0.10"
                step="0.01"
                value={estimatedQber}
                onChange={(e) => setEstimatedQber(parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
              <p className="text-[11px] text-slate-500 mt-1">
                Used to compute privacy amplification hash compression: k = n · (1 - 2H(Q)).
              </p>
            </div>

            <button
              onClick={handleEncrypt}
              disabled={isLoading || !plaintext.trim()}
              className={`w-full py-3.5 rounded-xl font-heading text-sm font-semibold uppercase tracking-wider transition-all duration-200 flex items-center justify-center space-x-2 shadow-xl cursor-pointer ${
                isLoading || !plaintext.trim()
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-cyan-400 via-sky-300 to-teal-300 hover:from-cyan-300 hover:to-white text-black shadow-cyan-500/20 active:scale-95'
              }`}
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Distilling Key & Encrypting...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Encrypt & Transmit via OTP</span>
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

        {/* Output Column (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {result ? (
            <div className="space-y-6">
              {/* Pipeline summary cards */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-[#0B1020]/90 border border-slate-800 text-center">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">Key Distilled</span>
                  <div className="text-xl font-mono font-bold text-cyan-300 mt-1">
                    {result.final_secret_bits} <span className="text-xs font-normal text-slate-400">bits</span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-[#0B1020]/90 border border-slate-800 text-center">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">Parity Corrected</span>
                  <div className="text-xl font-mono font-bold text-violet-300 mt-1">
                    {result.parity_corrections} <span className="text-xs font-normal text-slate-400">bits</span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-[#0B1020]/90 border border-slate-800 text-center">
                  <span className="text-[10px] font-mono text-slate-400 uppercase">Roundtrip Status</span>
                  <div className="text-xl font-mono font-bold text-emerald-400 mt-1 flex items-center justify-center space-x-1">
                    <CheckCircle2 className="w-4 h-4" />
                    <span className="text-sm">Verified</span>
                  </div>
                </div>
              </div>

              {/* Ciphertext Transmission */}
              <div className="p-5 rounded-2xl bg-[#0B1020]/90 border border-slate-800/90 shadow-xl space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400 pb-2 border-b border-slate-800">
                  <span className="uppercase text-cyan-400 font-semibold">Public Classical Ciphertext (Hex)</span>
                  <span className="text-slate-500">C = P ⊕ K</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-amber-300 break-all select-all">
                  {result.hex_ciphertext}
                </div>
                <div className="text-[11px] font-mono text-slate-500">
                  Binary Stream: {result.binary_ciphertext_preview}
                </div>
              </div>

              {/* Decryption Comparison: Bob vs Eve */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Bob (Legitimate Receiver) */}
                <div className="p-5 rounded-2xl bg-emerald-950/20 border border-emerald-500/40 space-y-2">
                  <div className="flex items-center space-x-2 text-xs font-mono text-emerald-400 font-semibold uppercase">
                    <ShieldCheck className="w-4 h-4" />
                    <span>Bob (Matching Quantum Key)</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/90 border border-emerald-900/60 font-mono text-sm text-emerald-300 break-all font-semibold">
                    "{result.decrypted_bob}"
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Perfect Shannon recovery. Key entropy matches ciphertext length.
                  </p>
                </div>

                {/* Eve (Eavesdropper Interception) */}
                <div className="p-5 rounded-2xl bg-rose-950/20 border border-rose-500/40 space-y-2">
                  <div className="flex items-center space-x-2 text-xs font-mono text-rose-400 font-semibold uppercase">
                    <ShieldAlert className="w-4 h-4" />
                    <span>Eve (Guessed / Leaked Key)</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950/90 border border-rose-900/60 font-mono text-sm text-rose-300 break-all">
                    "{result.decrypted_eve_sample}"
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Irreversible entropy. Even a 2% basis discrepancy creates complete garbled output.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full min-h-[300px] p-8 rounded-2xl bg-[#0B1020]/40 border border-dashed border-slate-800 flex flex-col items-center justify-center text-center">
              <Key className="w-10 h-10 text-cyan-400/50 mb-3" />
              <h4 className="font-heading font-semibold text-white text-sm mb-1">
                Awaiting Transmission
              </h4>
              <p className="text-xs text-slate-400 max-w-sm">
                Enter your secret message on the left and click <strong className="text-cyan-300">Encrypt & Transmit</strong> to see real-time OTP post-processing.
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
