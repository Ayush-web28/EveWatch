import React, { useEffect, useRef } from 'react';

interface QuantumCanvasProps {
  interactive?: boolean;
  intensity?: number;
  showNodes?: boolean;
  eveActive?: boolean;
}

export const QuantumCanvas: React.FC<QuantumCanvasProps> = ({
  interactive = true,
  intensity = 1.0,
  showNodes = true,
  eveActive = false,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || window.innerWidth);
    let height = (canvas.height = canvas.parentElement?.clientHeight || window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = canvas.parentElement?.clientWidth || window.innerWidth;
      height = canvas.height = canvas.parentElement?.clientHeight || window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    // Mouse tracking for wave displacement
    let mouseX = width / 2;
    let mouseY = height / 2;
    let mouseHover = false;

    const handleMouseMove = (e: MouseEvent) => {
      if (!interactive || !canvas) return;
      const rect = canvas.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;
      mouseHover = true;
    };

    const handleMouseLeave = () => {
      mouseHover = false;
    };

    if (interactive && canvas.parentElement) {
      canvas.parentElement.addEventListener('mousemove', handleMouseMove);
      canvas.parentElement.addEventListener('mouseleave', handleMouseLeave);
    }

    // Particles system
    const numParticles = Math.floor(Math.min(width, 1400) / 18);
    interface Particle {
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
      alpha: number;
      hue: number; // 180 (cyan) to 270 (violet)
      pulseSpeed: number;
      pulseOffset: number;
    }

    const particles: Particle[] = [];
    for (let i = 0; i < numParticles; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        size: Math.random() * 2 + 1,
        alpha: Math.random() * 0.5 + 0.2,
        hue: Math.random() > 0.5 ? 186 : 265, // Cyan or Violet
        pulseSpeed: 0.02 + Math.random() * 0.03,
        pulseOffset: Math.random() * Math.PI * 2,
      });
    }

    // Photon packets travelling Alice -> Channel -> Bob
    interface PhotonPacket {
      progress: number; // 0.0 to 1.0
      speed: number;
      state: string; // '|0⟩', '|1⟩', '|+⟩', '|−⟩'
      intercepted: boolean;
      color: string;
    }

    const photons: PhotonPacket[] = [];
    const states = ['|0⟩', '|1⟩', '|+⟩', '|−⟩'];

    let frame = 0;

    const render = () => {
      frame++;
      ctx.clearRect(0, 0, width, height);

      // 1. Draw subtle background probability grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
      ctx.lineWidth = 1;
      const gridSize = 80;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // 2. Draw Quantum nodes & transmission channel if enabled
      if (showNodes) {
        const aliceX = width * 0.15;
        const aliceY = height * 0.5;
        const bobX = width * 0.85;
        const bobY = height * 0.5;
        const eveX = width * 0.5;
        const eveY = height * 0.32;

        // Channel beam
        const grad = ctx.createLinearGradient(aliceX, aliceY, bobX, bobY);
        grad.addColorStop(0, 'rgba(0, 229, 255, 0.4)');
        grad.addColorStop(0.5, eveActive ? 'rgba(239, 68, 68, 0.6)' : 'rgba(139, 92, 246, 0.4)');
        grad.addColorStop(1, 'rgba(0, 229, 255, 0.4)');

        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.5;
        ctx.setLineDash([6, 6]);
        ctx.lineDashOffset = -frame * 0.8;
        ctx.beginPath();
        ctx.moveTo(aliceX, aliceY);
        ctx.lineTo(bobX, bobY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Eve interception tap if active
        if (eveActive) {
          ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)';
          ctx.lineWidth = 1.5;
          ctx.setLineDash([4, 4]);
          ctx.lineDashOffset = frame * 0.6;
          ctx.beginPath();
          ctx.moveTo(width * 0.5, height * 0.5);
          ctx.lineTo(eveX, eveY);
          ctx.stroke();
          ctx.setLineDash([]);
        }

        // Spawn traveling photons periodically
        if (frame % 45 === 0) {
          photons.push({
            progress: 0,
            speed: 0.006 + Math.random() * 0.004,
            state: states[Math.floor(Math.random() * states.length)],
            intercepted: eveActive && Math.random() < 0.7,
            color: Math.random() > 0.5 ? '#00E5FF' : '#8B5CF6',
          });
        }

        // Draw traveling photons
        for (let i = photons.length - 1; i >= 0; i--) {
          const p = photons[i];
          p.progress += p.speed;

          let px = aliceX + (bobX - aliceX) * p.progress;
          let py = aliceY + (bobY - aliceY) * p.progress;

          // If intercepted by Eve mid-flight, curve upward to Eve
          if (p.intercepted && p.progress > 0.35 && p.progress < 0.65) {
            const eveCurve = Math.sin(((p.progress - 0.35) / 0.3) * Math.PI);
            py -= eveCurve * (aliceY - eveY);
          }

          // Glow around photon
          const glow = ctx.createRadialGradient(px, py, 1, px, py, 12);
          glow.addColorStop(0, p.intercepted ? 'rgba(239, 68, 68, 0.9)' : p.color);
          glow.addColorStop(1, 'rgba(0, 0, 0, 0)');
          ctx.fillStyle = glow;
          ctx.beginPath();
          ctx.arc(px, py, 12, 0, Math.PI * 2);
          ctx.fill();

          // Photon core
          ctx.fillStyle = '#FFFFFF';
          ctx.beginPath();
          ctx.arc(px, py, 2.5, 0, Math.PI * 2);
          ctx.fill();

          // State label floating above photon
          ctx.font = '10px "JetBrains Mono", monospace';
          ctx.fillStyle = p.intercepted ? '#EF4444' : p.color;
          ctx.textAlign = 'center';
          ctx.fillText(p.state, px, py - 10);

          if (p.progress >= 1.0) {
            photons.splice(i, 1);
          }
        }
      }

      // 3. Draw background quantum particles and entanglement links
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Move
        p.x += p.vx;
        p.y += p.vy;

        // Wrap around bounds
        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        // Mouse displacement
        if (mouseHover) {
          const dx = p.x - mouseX;
          const dy = p.y - mouseY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120 && dist > 0) {
            const force = (120 - dist) / 120;
            p.x += (dx / dist) * force * 1.5;
            p.y += (dy / dist) * force * 1.5;
          }
        }

        // Particle pulse
        const pulse = Math.sin(frame * p.pulseSpeed + p.pulseOffset) * 0.3 + 0.7;
        const currentAlpha = p.alpha * pulse * intensity;

        // Draw particle
        ctx.fillStyle = p.hue === 186 
          ? `rgba(0, 229, 255, ${currentAlpha})` 
          : `rgba(139, 92, 246, ${currentAlpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();

        // Entanglement links between close particles
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 85) {
            const linkAlpha = (1 - dist / 85) * 0.15 * intensity;
            ctx.strokeStyle = `rgba(0, 229, 255, ${linkAlpha})`;
            ctx.lineWidth = 0.6;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      if (interactive && canvas.parentElement) {
        canvas.parentElement.removeEventListener('mousemove', handleMouseMove);
        canvas.parentElement.removeEventListener('mouseleave', handleMouseLeave);
      }
      cancelAnimationFrame(animationFrameId);
    };
  }, [interactive, intensity, showNodes, eveActive]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none z-0"
    />
  );
};
