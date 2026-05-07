import { Header } from './components/organisms/Header.js';
import { OperationsControl } from './components/organisms/OperationsControl.js';
import { MainLayout } from './components/templates/MainLayout.js';
import { VulnCard } from './components/molecules/VulnCard.js';

document.addEventListener('DOMContentLoaded', () => {
  const root = document.getElementById('app');

  const runSequence = async () => {
    const btn = document.getElementById('btn-execute');
    const logEl = document.getElementById('execution-log');
    const nodesEl = document.getElementById('stat-nodes');
    const payloadsEl = document.getElementById('stat-payloads');
    const capacityMeter = document.getElementById('capacity-meter');
    const vulnContainer = document.getElementById('vuln-container');
    const vulnEmpty = document.getElementById('vuln-empty');

    btn.disabled = true;
    btn.textContent = "EXECUTING...";
    logEl.innerHTML = "";
    vulnContainer.innerHTML = "";
    if (vulnEmpty) vulnEmpty.style.display = 'none';

    const logMsg = (msg) => {
      const entry = document.createElement('div');
      entry.textContent = `[+] ${msg}`;
      logEl.appendChild(entry);
      logEl.scrollTop = logEl.scrollHeight;
    };

    capacityMeter.style.setProperty('--p', '45%');
    logMsg("Initializing MITHAQ Sovereign Scan...");
    await new Promise(r => setTimeout(r, 1000));
    
    nodesEl.textContent = "128";
    logMsg("Nodes mapped in local subnet.");
    capacityMeter.style.setProperty('--p', '85%');
    
    await new Promise(r => setTimeout(r, 800));
    
    vulnContainer.appendChild(VulnCard({
      title: 'SQL Injection Found',
      severity: 'critical',
      score: '9.8'
    }));
    logMsg("CRITICAL ALERT: Vulnerability detected!");
    
    payloadsEl.textContent = "3";
    
    await new Promise(r => setTimeout(r, 1200));
    logMsg("Operation complete.");
    btn.textContent = "RE-ENGAGE";
    btn.disabled = false;
    capacityMeter.style.setProperty('--p', '15%');
  };

  const header = Header();
  const operations = OperationsControl({ onExecute: runSequence });
  
  const sidebar = document.createElement('div');
  sidebar.className = 'cyber-panel';
  sidebar.style.borderTop = '2px solid var(--sev-medium)';
  sidebar.innerHTML = `
    <h3 class="h3" style="margin-bottom: var(--sp-lg);">Threat Intelligence</h3>
    <div class="hud-bracket" style="margin-bottom: var(--sp-lg);">
      <div class="small" style="color: var(--hud-amber); margin-bottom: 4px;">TARGET</div>
      <div class="mono" style="font-size: 14px;">192.168.1.104</div>
    </div>
    <div class="small" style="margin-bottom: 8px;">DISCOVERED VULNERABILITIES</div>
    <div class="vuln-list" id="vuln-container">
      <div style="color: var(--fg3); font-style: italic;" id="vuln-empty">No threats detected.</div>
    </div>
  `;

  const layout = MainLayout({
    header: header,
    content: operations,
    sidebar: sidebar
  });
  
  root.appendChild(layout);
});
