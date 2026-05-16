import { cn } from '@/src/lib/utils';

interface GlitchTextProps {
  text: string;
  className?: string;
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'span';
}

export function GlitchText({ text, className, as: Component = 'span' }: GlitchTextProps) {
  return (
    <Component 
      className={cn("fx-glitch relative inline-block", className)}
      data-text={text}
    >
      {text}
    </Component>
  );
}
