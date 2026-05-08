export function CyberButton({ id, text, className = "", onClick, disabled = false }) {
  const btn = document.createElement('button');
  btn.id = id;
  btn.className = `cyber-btn ${className}`;
  btn.textContent = text;
  btn.disabled = disabled;
  if (onClick) btn.onclick = onClick;
  return btn;
}
