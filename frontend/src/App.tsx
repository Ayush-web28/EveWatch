import { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { QuantumLab } from './components/QuantumLab';
import { ProtocolVisualizer } from './components/ProtocolVisualizer';
import { NoiseVsEveHeatmap } from './components/NoiseVsEveHeatmap';
import { ExperimentsHub } from './components/ExperimentsHub';
import { SecureMessaging } from './components/SecureMessaging';
import { HowItWorks } from './components/HowItWorks';
import { Footer } from './components/Footer';
import type { SimulationRequest, SimulationResponse, QubitEvent } from './types/quantum';

export function App() {
  const [activeSection, setActiveSection] = useState<string>('hero');
  const [latestQubitEvents, setLatestQubitEvents] = useState<QubitEvent[]>([]);
  const [labPreset, setLabPreset] = useState<Partial<SimulationRequest> | null>(null);

  const scrollToSection = (sectionId: string) => {
    setActiveSection(sectionId);
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleSimulationComplete = (results: SimulationResponse) => {
    if (results.qubit_events && results.qubit_events.length > 0) {
      setLatestQubitEvents(results.qubit_events);
    }
  };

  const handleLoadParametersFromHeatmap = (params: Partial<SimulationRequest>) => {
    setLabPreset(params);
    scrollToSection('lab');
  };

  return (
    <div className="min-h-screen bg-[#05070D] text-[#F4F7FF] selection:bg-[#00E5FF]/20 selection:text-[#00E5FF]">
      {/* Top Floating Navbar */}
      <Navbar onNavigate={scrollToSection} activeSection={activeSection} />

      {/* Main Sections */}
      <main className="space-y-12">
        {/* Cinematic Landing Page */}
        <Hero
          onLaunchLab={() => scrollToSection('lab')}
          onExploreScience={() => scrollToSection('noise-eve')}
        />

        {/* Section A: Quantum Lab Simulator */}
        <QuantumLab
          onSimulationComplete={handleSimulationComplete}
          externalPreset={labPreset}
        />

        {/* Section B: Alice, Eve & Bob Interactive Protocol Visualizer */}
        <ProtocolVisualizer events={latestQubitEvents} />

        {/* Section C: The Noise vs. Eve Problem (Interactive Heatmap) */}
        <NoiseVsEveHeatmap onLoadParameters={handleLoadParametersFromHeatmap} />

        {/* Section D: Empirical Research Benchmark Hub */}
        <ExperimentsHub />

        {/* Section E: One-Time Pad Secure Messaging */}
        <SecureMessaging />

        {/* Section F: How BB84 Works (Scientific Foundation) */}
        <HowItWorks />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default App;
