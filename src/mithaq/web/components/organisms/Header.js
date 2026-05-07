import { CyberBadge } from '../atoms/CyberBadge.js';
import { PulseDot } from '../atoms/PulseDot.js';

export function Header() {
  const header = document.createElement('header');
  header.innerHTML = `
    <div class="brand-mark fx-glitch" data-text="MITHAQ: LIVE EXECUTION">MITHAQ: LIVE EXECUTION</div>
    <div style="display: flex; gap: 16px; align-items: center;" id="header-status">
    </div>
  `;
  
  const statusContainer = header.querySelector('#header-status');
  statusContainer.appendChild(CyberBadge({ text: 'SIYAADA SYNCED', type: 'safe' }));
  statusContainer.appendChild(PulseDot({ color: 'green' }));
  
  return header;
}
