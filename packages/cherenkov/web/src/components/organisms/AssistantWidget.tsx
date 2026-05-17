import { useState, useRef, useEffect, type KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { CyberButton } from '../atoms';
import { MessageSquare, X, Send, Bot, User, Loader2 } from 'lucide-react';
import { cn } from '@/src/lib/utils';
import { API_BASE } from '@/src/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function AssistantWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'CHERENKOV AI online. How can I assist your security operation?',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 300);
  }, [isOpen]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const token = sessionStorage.getItem('cherenkov_token');
      const res = await fetch(`${API_BASE}/assistant/advice`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          findings: [], // In a real scenario, we'd pass current findings
          context: { query: text },
        }),
      });

      if (!res.ok) throw new Error('Assistant API error');
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.advice || 'No advice received.' },
      ]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setError(msg);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `⚠ ${msg}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[1000] flex flex-col items-end gap-4">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            className="w-[400px] h-[600px] max-h-[80vh] bg-cherenkov-surface/95 backdrop-blur-md border border-cherenkov-primary/30 rounded-xl overflow-hidden shadow-[0_0_60px_rgba(0,0,0,0.6)] flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-cherenkov-surface border-b border-cherenkov-primary/20 shrink-0">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-cherenkov-primary animate-pulse shadow-[0_0_8px_theme(colors.cherenkov.primary)]" />
                <h3 className="text-sm font-semibold text-cherenkov-text tracking-wide font-mono uppercase">
                  AI Security Assistant
                </h3>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 rounded-md text-cherenkov-muted hover:text-cherenkov-text hover:bg-white/5 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Zero-Egress Banner */}
            <div className="px-3 py-2 bg-hud-cyan/10 border-b border-hud-cyan/20 text-[10px] text-hud-cyan font-mono">
              🛡 MEISSNER AIR-GAP PROTECTED // LOCAL OLLAMA ACTIVE
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-cherenkov-primary/20">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={cn(
                    'flex gap-2.5',
                    msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                  )}
                >
                  <div
                    className={cn(
                      'w-7 h-7 rounded-full flex items-center justify-center shrink-0 border',
                      msg.role === 'assistant'
                        ? 'bg-cherenkov-primary/10 border-cherenkov-primary/30 text-cherenkov-primary'
                        : 'bg-cherenkov-accent/10 border-cherenkov-accent/30 text-cherenkov-accent'
                    )}
                  >
                    {msg.role === 'assistant' ? (
                      <Bot className="w-3.5 h-3.5" />
                    ) : (
                      <User className="w-3.5 h-3.5" />
                    )}
                  </div>
                  <div
                    className={cn(
                      'max-w-[80%] px-3 py-2 rounded-lg text-xs leading-relaxed whitespace-pre-wrap',
                      msg.role === 'assistant'
                        ? 'bg-cherenkov-background/80 border border-cherenkov-primary/10 text-cherenkov-text'
                        : 'bg-cherenkov-accent/10 border border-cherenkov-accent/20 text-cherenkov-text'
                    )}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex gap-2.5">
                  <div className="w-7 h-7 rounded-full flex items-center justify-center border bg-cherenkov-primary/10 border-cherenkov-primary/30 text-cherenkov-primary">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                  <div className="bg-cherenkov-background/80 border border-cherenkov-primary/10 px-3 py-2 rounded-lg flex items-center gap-1.5">
                    <Loader2 className="w-3 h-3 text-cherenkov-primary animate-spin" />
                    <span className="text-xs text-cherenkov-muted font-mono">Analysing...</span>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="shrink-0 px-3 py-3 border-t border-cherenkov-primary/20 bg-cherenkov-surface">
              <div className="flex gap-2 items-center bg-cherenkov-background/50 border border-cherenkov-primary/20 rounded-lg px-3 py-1.5">
                <input
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about vulnerabilities, findings..."
                  className="flex-1 bg-transparent text-xs text-cherenkov-text placeholder:text-cherenkov-muted outline-none font-mono"
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || loading}
                  className="text-cherenkov-primary hover:text-cherenkov-primary/80 disabled:opacity-30 transition-colors shrink-0"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
              <p className="text-[9px] text-cherenkov-muted/50 font-mono mt-1.5 text-center">
                Powered by Local Ollama · Zero-Egress Mode
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* FAB */}
      <CyberButton
        onClick={() => setIsOpen(!isOpen)}
        variant="primary"
        className="w-14 h-14 !p-0 !rounded-full flex items-center justify-center shadow-[0_0_20px_theme(colors.cherenkov.primary/0.4)] hover:shadow-[0_0_35px_theme(colors.cherenkov.primary/0.7)]"
      >
        <AnimatePresence mode="wait">
          <motion.span
            key={isOpen ? 'close' : 'open'}
            initial={{ rotate: -90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: 90, opacity: 0 }}
            transition={{ duration: 0.15 }}
          >
            {isOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
          </motion.span>
        </AnimatePresence>
      </CyberButton>
    </div>
  );
}
