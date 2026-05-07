document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("cmd-input");
  const outputHistory = document.getElementById("output-history");
  const terminalContainer = document.getElementById("terminal-container");

  // Keep focus on input
  document.addEventListener("click", () => input.focus());

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const command = input.value.trim();
      if (command) {
        processCommand(command);
      }
      input.value = "";
    }
  });

  function appendLine(text, isCommand = false, cssClass = "") {
    const line = document.createElement("div");
    line.className = "terminal-line " + cssClass;
    
    if (isCommand) {
      line.innerHTML = `<span class="prompt-symbol">mithaq@core:~$</span><span class="fg1">${text}</span>`;
    } else {
      line.innerHTML = `<span>${text}</span>`;
    }

    outputHistory.appendChild(line);
    terminalContainer.scrollTop = terminalContainer.scrollHeight;
    return line;
  }

  async function processCommand(cmd) {
    appendLine(cmd, true);

    const args = cmd.split(" ");
    const base = args[0].toLowerCase();

    if (base === "help") {
      appendLine("AVAILABLE COMMANDS:", false, "neon-soft");
      appendLine("&nbsp;&nbsp;help&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Show this manual");
      appendLine("&nbsp;&nbsp;scan &lt;url&gt;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Execute deep topological scan");
      appendLine("&nbsp;&nbsp;clear&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Wipe terminal history");
      appendLine("&nbsp;&nbsp;status&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Check system integrity");
    } else if (base === "clear") {
      outputHistory.innerHTML = "";
    } else if (base === "status") {
      appendLine("SYSTEM STATUS: <span class='neon'>OPTIMAL</span>");
      appendLine("DEFENSE LAYER: <span class='neon'>ACTIVE</span>");
      appendLine("NETWORK NODE:&nbsp;&nbsp;<span class='neon-soft'>AIR-GAPPED</span>");
    } else if (base === "scan" || base === "mithaq") {
      let target = args[1];
      if (base === "mithaq" && args[1] === "scan") {
        target = args[2];
      }

      if (!target) {
        appendLine("ERROR: Missing target. Usage: scan &lt;url&gt;", false, "neon-red");
        return;
      }

      input.disabled = true;
      await runScanSequence(target);
      input.disabled = false;
      input.focus();
    } else {
      appendLine(`bash: ${cmd}: command not found`, false, "neon-red");
    }
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async function runScanSequence(target) {
    appendLine(`Initiating AL-BURHAN scan sequence for target: <span class='neon'>${target}</span>`);
    await sleep(800);
    
    const scanContainer = document.createElement("div");
    scanContainer.className = "scan-module";
    outputHistory.appendChild(scanContainer);

    const logToScan = async (msg, delay = 500, style = "fg2") => {
      await sleep(delay);
      const entry = document.createElement("div");
      entry.className = style + " type-on";
      entry.style.borderRight = "none";
      entry.style.animation = "none";
      entry.innerHTML = `> ${msg}`;
      scanContainer.appendChild(entry);
      terminalContainer.scrollTop = terminalContainer.scrollHeight;
    };

    await logToScan("Bypassing edge relays...", 600);
    await logToScan("Mapping topological nodes...", 800);
    await logToScan("[+] Open port detected: 443 (HTTPS)", 400, "neon-soft");
    await logToScan("[+] Open port detected: 22 (SSH)", 200, "neon-soft");
    await logToScan("Executing heuristic payload delivery...", 1200);
    
    await sleep(1000);
    const vulnCard = document.createElement("div");
    vulnCard.className = "cyber-vuln critical";
    vulnCard.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 4px;">CRITICAL VULNERABILITY DETECTED</div>
      <div>Target: ${target}</div>
      <div>Vector: CVE-2024-X491 (RCE via Protocol Buffer Overflow)</div>
      <div class="badge critical" style="margin-top: 8px;">Severity: 9.8</div>
    `;
    scanContainer.appendChild(vulnCard);
    terminalContainer.scrollTop = terminalContainer.scrollHeight;

    await logToScan("Scan complete. Logs securely archived via Siyaada protocol.", 1000, "neon");
  }
});
