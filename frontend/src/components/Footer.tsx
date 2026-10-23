import React from 'react';
import { Cpu, ExternalLink } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-[#05070D] py-12 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex flex-col items-center md:items-start space-y-2">
          <div className="flex items-center space-x-2">
            <span className="font-heading font-black text-xl text-white tracking-tight">
              EveWatch
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
              QKD v2.0
            </span>
          </div>
          <p className="text-xs text-slate-500 max-w-md text-center md:text-left">
            Investigating the boundary between natural quantum noise and active eavesdropping in BB84 quantum key distribution.
          </p>
        </div>

        <div className="flex items-center space-x-6 text-xs font-mono text-slate-400">
          <a
            href="https://github.com/Ayush-web28/EveWatch"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 hover:text-cyan-400 transition-colors"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
            <span>GitHub Repository</span>
            <ExternalLink className="w-3 h-3" />
          </a>

          <div className="flex items-center space-x-1.5 text-slate-500">
            <Cpu className="w-4 h-4 text-violet-400" />
            <span>Qiskit 2.5.2 · Aer</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto mt-8 pt-6 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-[11px] font-mono text-slate-600 gap-4">
        <span>© 2026 EveWatch Project · Licensed under MIT</span>
        <span>Based on Bennett & Brassard (1984) and Shor & Preskill (2000)</span>
      </div>
    </footer>
  );
};
