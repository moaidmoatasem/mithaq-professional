export function PulseDot({ color = "green", className = "" }) {
  const dot = document.createElement('div');
  dot.className = `pulse-dot ${color === 'red' ? 'red' : ''} ${className}`;
  return dot;
}
