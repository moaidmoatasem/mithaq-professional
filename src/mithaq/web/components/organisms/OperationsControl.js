import { CyberButton } from '../atoms/CyberButton.js';
import { StatCard } from '../molecules/StatCard.js';

export function OperationsControl({ onExecute }) {
  const container = document.createElement('div');
  container.className = 'cyber-panel';
  
  const header = document.createElement('div');
  header.className = 'panel-header';
  header.innerHTML = '<h2 class="h2 neon-soft">Tactical Operations</h2>';
  
  const executeBtn = CyberButton({
    id: 'btn-execute',
    text: '▶ INITIATE SEQUENCE',
    onClick: onExecute
  });
  
  header.appendChild(executeBtn);
  container.appendChild(header);
  
  const stats = document.createElement('div');
  stats.className = 'stats-grid';
  stats.appendChild(StatCard({ label: 'NODES MAPPED', value: '0', id: 'stat-nodes' }));
  stats.appendChild(StatCard({ label: 'PAYLOADS DELIVERED', value: '0', id: 'stat-payloads' }));
  container.appendChild(stats);
  
  container.innerHTML += `
    <div class="small" style="margin-bottom: 8px;">OPERATION STREAM</div>
    <div class="log-container datastream" id="execution-log">AWAITING COMMAND...</div>
    <div class="small" style="margin-bottom: 8px;">SYSTEM CAPACITY</div>
    <div class="cyber-meter"><i id="capacity-meter" style="--p: 10%;"></i></div>
  `;
  
  // Re-attach button because innerHTML wipes it
  const oldHeader = container.querySelector('.panel-header');
  oldHeader.innerHTML = '<h2 class="h2 neon-soft">Tactical Operations</h2>';
  oldHeader.appendChild(executeBtn);

  return container;
}
