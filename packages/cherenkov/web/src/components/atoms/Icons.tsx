export function MeissnerIcon({ size = 24, className }: { size?: number; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className={className}>
      <path d="M12 2L4 7v10l8 5 8-5V7l-8-5z" strokeOpacity="0.3" />
      <path d="M12 6L7 9v6l5 3 5-3V9l-5-3z" />
      <rect x="10" y="10" width="4" height="4" strokeWidth="2" />
      <path d="M4 7l8 5 8-5M12 22V12" strokeOpacity="0.3" />
    </svg>
  );
}

export function AblationIcon({ size = 24, className }: { size?: number; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className={className}>
      <circle cx="12" cy="12" r="2" fill="currentColor" />
      <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
      <path d="M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2" strokeOpacity="0.5" />
      <path d="M12 8a4 4 0 014 4M8 12a4 4 0 004 4" strokeDasharray="2 2" />
    </svg>
  );
}

export function TokamakIcon({ size = 24, className }: { size?: number; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className={className}>
      <circle cx="12" cy="12" r="10" strokeOpacity="0.2" />
      <circle cx="12" cy="12" r="7" />
      <circle cx="12" cy="12" r="4" strokeWidth="2" />
      <path d="M12 2s-4 4-4 10 4 10 4 10 4-4 4-10-4-10-4-10z" strokeOpacity="0.3" />
    </svg>
  );
}
