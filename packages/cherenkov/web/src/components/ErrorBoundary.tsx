// @ts-nocheck
import { Component } from 'react';
import { CyberButton } from './atoms/CyberButton';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary]', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-cherenkov-background flex items-center justify-center p-6">
          <div className="bg-cherenkov-surface/60 backdrop-blur-xl border border-sev-critical/30 rounded-2xl p-8 max-w-md w-full text-center shadow-[0_0_50px_rgba(255,0,61,0.15)]">
            <div className="flex justify-center mb-6">
              <div className="w-16 h-16 rounded-full bg-sev-critical/10 border border-sev-critical/30 flex items-center justify-center">
                <AlertTriangle size={32} className="text-sev-critical" />
              </div>
            </div>
            <h2 className="text-xl font-bold text-white uppercase tracking-tight font-mono mb-2">
              SYSTEM_FAULT
            </h2>
            <p className="text-cherenkov-muted text-xs font-mono mb-6">
              An unexpected error occurred in the dashboard component.
            </p>
            {this.state.error && (
              <div className="bg-black/40 border border-white/5 p-3 mb-6 text-left font-mono text-[10px] text-sev-critical break-all max-h-[100px] overflow-y-auto">
                {this.state.error.message}
              </div>
            )}
            <CyberButton
              variant="primary"
              onClick={this.handleReset}
              className="w-full flex items-center justify-center gap-2"
            >
              <RefreshCw size={14} />
              REBOOT DASHBOARD
            </CyberButton>
            <p className="text-[10px] font-mono text-cherenkov-muted/50 mt-4 uppercase tracking-wider">
              MEISSNER AIR-GAP PRESERVED
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
