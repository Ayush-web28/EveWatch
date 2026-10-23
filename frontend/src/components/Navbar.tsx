import React, { useEffect, useState } from 'react';
import { ShieldCheck, Activity, Cpu, Key, BarChart3, BookOpen, Layers } from 'lucide-react';
import { api } from '../api/client';
import type { SystemHealth } from '../types/quantum';

interface NavbarProps {
  onNavigate: (sectionId: string) => void;
  activeSection: string;
}

export const Navbar: React.FC<NavbarProps> = ({ onNavigate, activeSection }) => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    const checkStatus = async () => {
      try {
        const data = await api.getHealth();
        if (isMounted) {
          setHealth(data);
          setIsConnected(true);
        }
      } catch {
        if (isMounted) setIsConnected(false);
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { id: 'hero', label: 'Overview', icon: Layers },
    { id: 'lab', label: 'Quantum Lab', icon: Cpu },
    { id: 'visualizer', label: 'Protocol Visualizer', icon: Activity },
    { id: 'noise-eve', label: 'Noise vs Eve', icon: ShieldCheck },
    { id: 'experiments', label: 'Experiments', icon: BarChart3 },
    { id: 'messaging', label: 'OTP Messaging', icon: Key },
    { id: 'how-it-works', label: 'Theory', icon: BookOpen },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 px-4 sm:px-8 py-3 transition-all duration-300">
      <div className="max-w-7xl mx-auto backdrop-blur-md bg-[#05070D]/80 border border-slate-800/80 rounded-2xl px-5 py-2.5 flex items-center justify-between shadow-2xl shadow-cyan-950/20">
        {/* Brand */}
        <div 
          onClick={() => onNavigate('hero')}
          className="flex items-center space-x-3 cursor-pointer group"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-600 to-violet-500 p-[1.5px] transition-transform duration-300 group-hover:scale-105 shadow-lg shadow-cyan-500/20">
            <div className="w-full h-full bg-[#05070D] rounded-[10px] flex items-center justify-center">
              <span className="font-heading font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-violet-400 text-sm tracking-wider">
                EW
              </span>
            </div>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center space-x-1.5">
              <span className="font-heading font-bold text-lg tracking-tight text-white group-hover:text-cyan-400 transition-colors">
                EveWatch
              </span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/60 font-semibold">
                v2.0
              </span>
            </div>
            <span className="text-[10px] text-slate-400 font-mono tracking-widest uppercase hidden sm:block">
              BB84 · QKD Research
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="hidden lg:flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                  isActive
                    ? 'text-cyan-400 bg-cyan-950/40 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/40'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right side: Backend health & Launch button */}
        <div className="flex items-center space-x-3">
          <div className="hidden sm:flex items-center space-x-2 text-[11px] font-mono px-2.5 py-1 rounded-md bg-slate-900/90 border border-slate-800">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
            <span className="text-slate-400">
              {isConnected ? (health?.aer_simulator ? 'Aer 2.5' : 'Connected') : 'Connecting...'}
            </span>
          </div>

          <button
            onClick={() => onNavigate('lab')}
            className="relative group px-4 py-1.5 rounded-xl font-heading text-xs font-semibold uppercase tracking-wider text-black bg-gradient-to-r from-cyan-400 to-cyan-300 hover:from-cyan-300 hover:to-white transition-all duration-200 shadow-md shadow-cyan-500/20 active:scale-95 cursor-pointer"
          >
            Launch Lab
          </button>
        </div>
      </div>
    </header>
  );
};
