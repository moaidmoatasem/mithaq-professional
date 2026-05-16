import { ReactNode } from 'react';
import { cn } from '@/src/lib/utils';

interface MainLayoutProps {
  header: ReactNode;
  content: ReactNode;
  sidebar: ReactNode;
  className?: string;
}

export function MainLayout({ header, content, sidebar, className }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-bg-canvas flex flex-col fx-grid relative">
      {/* HUD Scanline Overlay */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.03] fx-scanlines-pattern z-[200]" />
      
      {header}
      
      <main className={cn(
        "flex-1 w-full max-w-[1440px] mx-auto p-6 grid grid-cols-1 lg:grid-cols-4 gap-6",
        className
      )}>
        {/* Tactical Operations Panel (3fr) */}
        <div className="lg:col-span-3 h-full">
          {content}
        </div>
        
        {/* Threat Intel Panel (1fr) */}
        <div className="lg:col-span-1 h-full">
          {sidebar}
        </div>
      </main>

      {/* Decorative Border */}
      <div className="fixed top-0 left-0 w-full h-1 bg-gradient-to-r from-cherenkov-accent via-hud-cyan to-hud-mint opacity-30 z-[150]" />
    </div>
  );
}
