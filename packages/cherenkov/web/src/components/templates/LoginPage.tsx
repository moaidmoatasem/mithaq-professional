import { useState, type FormEvent } from 'react';
import { motion } from 'motion/react';
import { CyberButton, Logo } from '../atoms';
import { API_BASE } from '../../lib/api';
import { Lock, User, ShieldAlert, Loader2 } from 'lucide-react';

interface LoginPageProps {
  onLoginSuccess: (token: string) => void;
}

export function LoginPage({ onLoginSuccess }: LoginPageProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Authentication failed');
      }

      const { access_token } = await res.json();
      sessionStorage.setItem('cherenkov_token', access_token);
      onLoginSuccess(access_token);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cherenkov-background flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Ambience */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,242,255,0.05),transparent_70%)]" />
      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-cherenkov-primary/30 to-transparent" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative"
      >
        <div className="bg-cherenkov-surface/60 backdrop-blur-xl border border-cherenkov-primary/20 rounded-2xl p-8 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
          <div className="flex flex-col items-center gap-6 mb-8">
            <Logo className="w-16 h-16" />
            <div className="text-center">
              <h1 className="text-2xl font-bold text-cherenkov-text tracking-tighter uppercase font-mono">
                Sovereign Access
              </h1>
              <p className="text-cherenkov-muted text-xs mt-1 font-mono">
                CHERENKOV // SECURITY OPERATIONS CENTER
              </p>
            </div>
          </div>

          <form onSubmit={handleLogin} className="space-y-5">
            <div className="space-y-1.5">
              <label className="text-[10px] font-mono text-cherenkov-muted uppercase tracking-widest ml-1">
                Operator ID
              </label>
              <div className="relative group">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-cherenkov-muted group-focus-within:text-cherenkov-primary transition-colors" />
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-cherenkov-background/50 border border-cherenkov-primary/20 rounded-lg py-2.5 pl-10 pr-4 text-sm text-cherenkov-text focus:border-cherenkov-primary/50 outline-none transition-all font-mono"
                  placeholder="admin"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-[10px] font-mono text-cherenkov-muted uppercase tracking-widest ml-1">
                Secure Key
              </label>
              <div className="relative group">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-cherenkov-muted group-focus-within:text-cherenkov-primary transition-colors" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-cherenkov-background/50 border border-cherenkov-primary/20 rounded-lg py-2.5 pl-10 pr-4 text-sm text-cherenkov-text focus:border-cherenkov-primary/50 outline-none transition-all font-mono"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {error && (
              <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-2 bg-sev-critical/10 border border-sev-critical/20 p-3 rounded-lg text-sev-critical text-xs font-mono"
              >
                <ShieldAlert className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </motion.div>
            )}

            <CyberButton
              type="submit"
              variant="primary"
              disabled={loading}
              className="w-full h-11 flex items-center justify-center gap-2 mt-4"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>AUTHORIZING...</span>
                </>
              ) : (
                'INITIALIZE SESSION'
              )}
            </CyberButton>
          </form>

          <div className="mt-8 pt-6 border-t border-cherenkov-primary/10 text-center">
            <p className="text-[10px] font-mono text-cherenkov-muted/50 uppercase tracking-tighter">
              MEISSNER AIR-GAP PROTOCOL ENFORCED // NO EXTERNAL EGRESS
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
