import React from 'react';
import { cn } from '@/src/lib/utils';
import { motion } from 'motion/react';

interface CyberButtonProps {
  id?: string;
  text?: string;
  variant?: 'primary' | 'ghost' | 'danger';
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  disabled?: boolean;
  className?: string;
  loading?: boolean;
  type?: 'button' | 'submit' | 'reset';
  children?: React.ReactNode;
}

export function CyberButton({ 
  id, 
  text, 
  variant = 'primary', 
  onClick, 
  disabled = false, 
  className,
  loading = false,
  type = 'button',
  children
}: CyberButtonProps) {
  const variants = {
    primary: 'bg-gradient-to-br from-[#00ff88] to-[#00cc66] text-[#001b0d] hover:shadow-[0_0_15px_rgba(0,255,136,0.4)]',
    ghost: 'bg-transparent border border-[#00ff88]/50 text-[#00ff88] hover:bg-[#00ff88]/5',
    danger: 'bg-gradient-to-br from-[#ff4444] to-[#cc2222] text-white hover:shadow-[0_0_15px_rgba(255,68,68,0.4)]',
  };

  return (
    <motion.button
      id={id}
      type={type}
      whileHover={!disabled && !loading ? { translateY: -1 } : {}}
      whileTap={!disabled && !loading ? { scale: 0.98 } : {}}
      onClick={!disabled && !loading ? onClick : undefined}
      disabled={disabled || loading}
      className={cn(
        'relative px-5 py-2 font-mono text-[11px] font-bold uppercase transition-all duration-300 outline-none group tracking-widest flex items-center justify-center min-h-[36px]',
        loading && 'cursor-wait opacity-80',
        disabled && 'opacity-60 cursor-not-allowed grayscale-[0.5]',
        variants[variant],
        className
      )}
      style={{
        clipPath: 'polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px))'
      }}
    >
      <span className="relative z-10 flex items-center justify-center">
        {loading ? 'EXECUTING...' : (children || text)}
      </span>
      
      {/* HUD Accent Dots */}
      <div className="absolute top-1 left-1 w-0.5 h-0.5 bg-black/20" />
      <div className="absolute bottom-1 right-1 w-0.5 h-0.5 bg-black/20" />
    </motion.button>
  );
}
