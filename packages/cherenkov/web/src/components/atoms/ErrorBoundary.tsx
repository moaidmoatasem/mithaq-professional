import { Component, ErrorInfo, ReactNode } from 'react';
import { ShieldAlert, RefreshCw, Terminal } from 'lucide-react';
import { CyberButton } from './CyberButton';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-[400px] w-full bg-cherenkov-background border border-sev-critical/30 rounded-xl p-8 flex flex-col justify-between relative overflow-hidden font-mono select-none">
          {/* Top terminal bar */}
          <div className="absolute top-0 left-0 right-0 h-8 bg-black/40 border-b border-white/5 px-4 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2">
              <Terminal size={12} className="text-sev-critical" />
              <span className="text-[10px] text-sev-critical uppercase tracking-widest font-bold">SYSTEM_KERNEL_CRASH</span>
            </div>
            <div className="flex gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-sev-critical/30" />
              <div className="w-2.5 h-2.5 rounded-full bg-sev-high/30" />
              <div className="w-2.5 h-2.5 rounded-full bg-hud-mint/30" />
            </div>
          </div>

          {/* Error Details */}
          <div className="mt-8 flex-1 flex flex-col justify-center gap-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 flex items-center justify-center bg-sev-critical/10 border border-sev-critical/20">
                <ShieldAlert size={24} className="text-sev-critical animate-pulse" />
              </div>
              <div>
                <h3 className="text-lg font-black text-white uppercase tracking-tight">Topology Isolation Fault</h3>
                <p className="text-[10px] text-sev-critical/80 uppercase tracking-widest leading-none mt-1">Component_Execution_Terminated</p>
              </div>
            </div>

            <div className="p-4 bg-black/50 border border-white/5 text-[11px] text-fg2 space-y-2 leading-relaxed">
              <div className="flex justify-between border-b border-white/5 pb-1 mb-2">
                <span className="text-fg3 uppercase">Faulting_Subsystem</span>
                <span className="text-white font-bold">REACT_DOM_VIRTUAL</span>
              </div>
              <div className="text-sev-critical font-bold truncate">
                ERROR: {this.state.error?.message || 'Unknown Exception'}
              </div>
              <div className="text-fg3 text-[10px] uppercase tracking-tighter">
                AUTOMATIC AIR-GAP CONTAINMENT ENGAGED // MEISSNER PROTOCOL SAFE
              </div>
            </div>
          </div>

          {/* Reboot Button */}
          <div className="mt-6 pt-6 border-t border-white/5 flex justify-end">
            <CyberButton
              onClick={this.handleReset}
              variant="primary"
              className="px-6 flex items-center gap-2"
            >
              <RefreshCw size={12} className="animate-spin-slow" />
              <span>REBOOT_TOPOLOGY_COMPONENT</span>
            </CyberButton>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
