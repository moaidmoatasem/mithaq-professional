document.addEventListener("DOMContentLoaded", () => {
  const btnExecute = document.getElementById('btn-execute');
  const log = document.getElementById('execution-log');
  const capacityMeter = document.getElementById('capacity-meter');
  const statNodes = document.getElementById('stat-nodes');
  const statPayloads = document.getElementById('stat-payloads');
  const vulnContainer = document.getElementById('vuln-container');
  const vulnEmpty = document.getElementById('vuln-empty');

  let isExecuting = false;

  const sleep = ms => new Promise(r => setTimeout(r, ms));

  function logMsg(msg, isAlert = false) {
    const entry = document.createElement("div");
    entry.style.marginBottom = "4px";
    if (isAlert) {
      entry.innerHTML = `<span style="color: var(--sev-critical)">[!] ${msg}</span>`;
    } else {
      entry.innerHTML = `[+] ${msg}`;
    }
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
  }

  function addVuln(title, sevClass, score) {
    if (vulnEmpty) vulnEmpty.style.display = 'none';
    
    const card = document.createElement('div');
    card.className = `cyber-vuln ${sevClass}`;
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: start;">
        <div style="font-weight: bold; font-size: 14px;">${title}</div>
        <div class="badge ${sevClass}">${score}</div>
      </div>
    `;
    vulnContainer.appendChild(card);
  }

  btnExecute.addEventListener('click', async () => {
    if (isExecuting) return;
    isExecuting = true;
    
    btnExecute.disabled = true;
    btnExecute.textContent = "EXECUTING...";
    log.innerHTML = "";
    vulnContainer.innerHTML = "";
    statNodes.textContent = "0";
    statPayloads.textContent = "0";
    capacityMeter.style.setProperty('--p', '40%');

    logMsg("Initializing Operation: CHERENKOV-ECHO");
    await sleep(1000);
    
    capacityMeter.style.setProperty('--p', '75%');
    logMsg("Allocating swarm agents to target matrix...");
    await sleep(1200);

    // Nodes Loop
    for(let i=1; i<=5; i++) {
      statNodes.textContent = (i * 24).toString();
      logMsg(`Discovered topology node cluster 0x0${i}...`);
      await sleep(600);
    }

    capacityMeter.style.setProperty('--p', '95%');
    logMsg("Analyzing exposed services...");
    await sleep(800);
    
    addVuln("Exposed RDP Port", "medium", "5.4");
    logMsg("Found open port: 3389", true);
    await sleep(1000);

    logMsg("Executing payload heuristics...");
    statPayloads.textContent = "12";
    await sleep(1500);

    addVuln("Unauthenticated RCE", "critical", "9.8");
    logMsg("CRITICAL: Unauthenticated Remote Code Execution identified.", true);
    statPayloads.textContent = "47";
    await sleep(1200);

    capacityMeter.style.setProperty('--p', '20%');
    logMsg("Consolidating telemetry. Ablation sync active.");
    await sleep(800);

    logMsg("Operation complete.");
    btnExecute.textContent = "RE-ENGAGE";
    btnExecute.disabled = false;
    isExecuting = false;
  });
});
