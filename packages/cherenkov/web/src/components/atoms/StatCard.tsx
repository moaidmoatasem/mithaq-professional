import { cn } from '@/src/lib/utils';

export interface StatCardProps {
  label: string;
  value: string | number;
  id: string;
  accent?: string;
  className?: string;
  key?: string | number;
}

export function StatCard({ label, value, id, accent, className }: StatCardProps) {
  return (
    <div 
      id={id}
      className={cn(
        "hud-bracket bg-bg-surface p-4 flex flex-col gap-1 border border-white/5",
        className
      )}
    >
      <span className="text-[9px] font-mono text-fg2 uppercase tracking-[0.2em]">
        {label}
      </span>
      <span 
        className={cn(
          "text-2xl font-mono font-bold tracking-tighter",
          accent ? `text-[${accent}]` : "text-cherenkov-accent"
        )}
        style={accent ? { color: accent } : {}}
      >
        {value}
      </span>
    </div>
  );
}
