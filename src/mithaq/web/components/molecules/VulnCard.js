import { CyberBadge } from '../atoms/CyberBadge.js';

export function VulnCard({ title, severity, score, description, scanner, cve }) {
  const card = document.createElement('div');
  card.className = `cyber-vuln ${severity} reveal-up`;
  
  const header = document.createElement('div');
  header.style.display = 'flex';
  header.style.justifyContent = 'space-between';
  header.style.alignItems = 'start';
  
  const titleEl = document.createElement('div');
  titleEl.style.fontWeight = 'bold';
  titleEl.style.fontSize = '14px';
  titleEl.textContent = title;
  
  const badge = CyberBadge({ text: score, type: severity });
  
  header.appendChild(titleEl);
  header.appendChild(badge);
  card.appendChild(header);
  
  // Expandable details (Simulating the logic from previous agent work)
  card.style.cursor = 'pointer';
  card.onclick = () => {
    // Toggle details logic could go here
    console.log(`Clicked ${title}`);
  };

  return card;
}
