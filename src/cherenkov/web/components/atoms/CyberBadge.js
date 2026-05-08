export function CyberBadge({ text, type = "safe", className = "" }) {
  const badge = document.createElement('span');
  badge.className = `badge ${type} ${className}`;
  badge.textContent = text;
  return badge;
}
