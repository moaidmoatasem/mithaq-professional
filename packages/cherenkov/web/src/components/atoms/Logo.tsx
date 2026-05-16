import { cn } from '@/src/lib/utils';

interface LogoProps {
  size?: number;
  className?: string;
  variant?: 'cyan' | 'purple' | 'skeleton' | 'full';
}

export function CherenkovLogo({ size = 40, className, variant = 'cyan' }: LogoProps) {
  const colors = {
    cyan: { shield: 'url(#hex-grad-cyan)', core: '#00D2FF', cone: '#00E0FF' },
    purple: { shield: 'url(#hex-grad-purple)', core: '#9D00FF', cone: '#00E0FF' },
    skeleton: { shield: 'rgba(255,255,255,0.2)', core: 'transparent', cone: 'transparent' },
    full: { shield: 'url(#hex-grad-full)', core: '#00D2FF', cone: '#00E0FF' }
  };

  const active = colors[variant];

  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 100 100" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={cn("overflow-visible", className)}
    >
      <defs>
        <linearGradient id="hex-grad-cyan" x1="11" y1="5" x2="89" y2="95">
          <stop stopColor="#00D2FF" />
          <stop offset="1" stopColor="#2b7fff" />
        </linearGradient>
        <linearGradient id="hex-grad-purple" x1="11" y1="5" x2="89" y2="95">
          <stop stopColor="#9D00FF" />
          <stop offset="1" stopColor="#7000FF" />
        </linearGradient>
        <linearGradient id="hex-grad-full" x1="11" y1="5" x2="89" y2="95">
          <stop stopColor="#00E0FF" />
          <stop offset="0.5" stopColor="#9D00FF" />
          <stop offset="1" stopColor="#FF00D6" />
        </linearGradient>
      </defs>

      {/* Hexagonal Sentinel Shield */}
      <path 
        d="M50 5 L89 27.5 V72.5 L50 95 L11 72.5 V27.5 L50 5Z" 
        stroke={active.shield} 
        strokeLinejoin="round" 
        className={cn(variant !== 'skeleton' && "ch-reactor-shield")}
      />
      
      {/* The Reveal / Conical Wavefront Background */}
      <path 
        d="M70 30 A 25 25 0 1 0 70 70" 
        stroke="white" 
        strokeWidth="6" 
        strokeLinecap="round" 
        className="opacity-20"
      />

      {/* Wavefront Core */}
      <path 
        d="M55 50 L88 32 V68 Z" 
        fill={active.cone} 
        className={cn("transition-all duration-500", variant !== 'skeleton' && "ch-core-reveal")}
      />
      
      {/* Micro-Validation Points */}
      {variant !== 'skeleton' && (
        <>
          <circle cx="60" cy="45" r="1.5" fill="white" className="ch-data-point" style={{ animationDelay: '0.2s' }} />
          <circle cx="68" cy="52" r="1.5" fill="white" className="ch-data-point" style={{ animationDelay: '0.5s' }} />
          <circle cx="64" cy="58" r="1.5" fill="white" className="ch-data-point" style={{ animationDelay: '0.8s' }} />
        </>
      )}
      
      {/* Core Glow */}
      <circle 
        cx="64" 
        cy="50" 
        r="12" 
        fill={active.core} 
        className="opacity-40 blur-sm pointer-events-none" 
      />
    </svg>
  );
}
