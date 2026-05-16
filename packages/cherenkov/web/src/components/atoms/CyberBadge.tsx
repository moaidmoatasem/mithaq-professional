import { cn } from '@/src/lib/utils';

type BadgeType = 'safe' | 'critical' | 'high' | 'medium' | 'low' | 'info';

interface CyberBadgeProps {
  text: string;
  type?: BadgeType;
  className?: string;
}

export function CyberBadge({ text, type = 'safe', className }: CyberBadgeProps) {
  const styles: Record<BadgeType, string> = {
    safe: 'bg-hud-mint/10 border-hud-mint/40 text-hud-mint',
    critical: 'bg-sev-critical/10 border-sev-critical/40 text-sev-critical',
    high: 'bg-sev-critical/20 border-sev-critical/50 text-sev-critical',
    medium: 'bg-sev-medium/10 border-sev-medium/40 text-sev-medium',
    low: 'bg-sev-low/10 border-sev-low/40 text-sev-low',
    info: 'bg-cherenkov-accent/10 border-cherenkov-accent/40 text-cherenkov-accent',
  };

  return (
    <span className={cn(
      'px-2 py-0.5 border text-[9px] font-mono font-bold uppercase tracking-widest inline-flex items-center',
      styles[type],
      className
    )}>
      {text}
    </span>
  );
}
