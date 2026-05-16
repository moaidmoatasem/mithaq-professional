import { StatCard } from '../atoms/StatCard';
import { cn } from '@/src/lib/utils';

interface Stat {
  label: string;
  value: string | number;
  id: string;
  accent?: string;
}

interface StatGridProps {
  stats: Stat[];
  className?: string;
}

export function StatGrid({ stats, className }: StatGridProps) {
  return (
    <div className={cn("grid grid-cols-2 md:grid-cols-4 gap-4", className)}>
      {stats.map((stat) => (
        <StatCard 
          key={stat.id}
          label={stat.label}
          value={stat.value}
          id={stat.id}
          accent={stat.accent}
        />
      ))}
    </div>
  );
}
