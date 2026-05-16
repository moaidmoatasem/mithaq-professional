import { cn } from '@/src/lib/utils';

type PulseColor = 'green' | 'red' | 'amber' | 'cyan';

interface PulseDotProps {
  color?: PulseColor;
  label?: string;
  className?: string;
}

export function PulseDot({ color = 'green', label, className }: PulseDotProps) {
  const colors: Record<PulseColor, string> = {
    green: 'bg-hud-mint',
    red: 'bg-sev-critical',
    amber: 'bg-hud-amber',
    cyan: 'bg-hud-cyan',
  };

  return (
    <div className={cn("flex items-center gap-2", className)} aria-label={label}>
      <div className="relative flex h-2 w-2">
        <span className={cn(
          "animate-ping absolute inline-flex h-full w-full rounded-full opacity-75",
          colors[color]
        )}></span>
        <span className={cn(
          "relative inline-flex rounded-full h-2 w-2",
          colors[color]
        )}></span>
      </div>
      {label && <span className="text-[10px] font-mono text-fg2 uppercase tracking-wider">{label}</span>}
    </div>
  );
}
