// Configuration URLs (relative to window.location)
const API_BASE = window.location.origin;

// State management
let lastLogTimestamp = "";
let isAttackInProgress = false;
let consecutiveErrors = 0;

// Toggle Collapsible Sidebar
function toggleSidebar() {
    const sidebar = document.getElementById("dashboard-sidebar");
    if (!sidebar) return;
    sidebar.classList.toggle("collapsed");
}

// Activate nav item (highlight active)
function activateNavItem(btn) {
    document.querySelectorAll('.sidebar-nav-item').forEach(el => el.classList.remove('active'));
    btn.classList.add('active');
}

// Toggle Collapsible Right Chat Panel
function toggleRightChat() {
    const drawer = document.getElementById("agent-chat-drawer");
    const triggerBtn = document.getElementById("chat-drawer-trigger");
    if (!drawer) return;

    drawer.classList.toggle("collapsed");

    if (drawer.classList.contains("collapsed")) {
        if (triggerBtn) triggerBtn.style.display = "flex";
    } else {
        if (triggerBtn) triggerBtn.style.display = "none";
        setTimeout(() => {
            const chatBox = document.getElementById("agent-chat-box");
            if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
        }, 100);
    }
}

// Format helper
function formatTimestamp(isoString) {
    if (!isoString) return "";
    let cleanStr = isoString.trim().replace(" ", "T");
    if (!cleanStr.endsWith("Z") && !cleanStr.includes("+") && cleanStr.length >= 19) {
        cleanStr += "Z";
    }
    const date = new Date(cleanStr);
    if (isNaN(date.getTime())) {
        return isoString;
    }
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function showConnectionWarning() {
    let warningEl = document.getElementById("connection-lost-banner");
    if (!warningEl) {
        warningEl = document.createElement("div");
        warningEl.id = "connection-lost-banner";
        warningEl.className = "bg-red-50 border-b border-red-200 text-red-700 font-bold font-mono text-center py-2 px-4 text-xs tracking-wider animate-pulse transition-all duration-300 z-50 relative flex items-center justify-center gap-2";
        warningEl.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-red-500"></i> PORT-FORWARD CONNECTION LOST! Please run Start-Demo.ps1 in your terminal to restore dashboard communication.`;
        document.body.insertBefore(warningEl, document.body.firstChild);
    }
}

function hideConnectionWarning() {
    const warningEl = document.getElementById("connection-lost-banner");
    if (warningEl) {
        warningEl.remove();
    }
}

// Render Skeleton cards during load
function renderSkeleton() {
    const container = document.getElementById("services-container");
    if (container && (container.innerHTML.trim() === "" || container.querySelector(".shimmer"))) {
        container.innerHTML = `
            <div class="shimmer" style="height:72px;"></div>
            <div class="shimmer" style="height:72px;"></div>
            <div class="shimmer" style="height:72px;"></div>
            <div class="shimmer" style="height:72px;"></div>
        `;
    }
}

// Fetch System Replicas & CPU Metrics
async function updateMetrics() {
    renderSkeleton();
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        if (!response.ok) throw new Error("Status API returned error");
        
        const data = await response.json();
        renderServices(data.services);
        updateWorkflowGraph(data.services);
        consecutiveErrors = 0;
        hideConnectionWarning();
    } catch (error) {
        console.error("Failed to update metrics:", error);
        consecutiveErrors++;
        if (consecutiveErrors >= 2) {
            showConnectionWarning();
        }
    }
}

// Fetch Combined Logs
async function updateLogs() {
    try {
        const response = await fetch(`${API_BASE}/api/logs`);
        if (!response.ok) throw new Error("Logs API returned error");
        
        const data = await response.json();
        renderLogs(data.logs);
        consecutiveErrors = 0;
        hideConnectionWarning();
    } catch (error) {
        console.error("Failed to update logs:", error);
        consecutiveErrors++;
        if (consecutiveErrors >= 2) {
            showConnectionWarning();
        }
    }
}

// Fetch Agent Reasoning Chat
async function updateAgentChat() {
    try {
        const response = await fetch(`${API_BASE}/api/chat`);
        if (!response.ok) throw new Error("Chat API returned error");
        
        const data = await response.json();
        renderAgentChat(data.chat);
    } catch (error) {
        console.error("Failed to update agent chat:", error);
    }
}

// Render Microservices in Grid
function renderServices(services) {
    const container = document.getElementById("services-container");
    if (!container) return;
    container.innerHTML = "";
    
    let activeStressPod = false;

    Object.entries(services).forEach(([name, status]) => {
        const replicas = status.replicas;
        const cpu = status.cpu;
        
        const cpuLimit = 0.2;
        const cpuPercent = Math.min((cpu / cpuLimit) * 100, 300);
        
        let valClass = "sc-metric-val green";
        let cardStyle = "";
        
        if (cpu > 0.05) {
            valClass = "sc-metric-val red";
            cardStyle = "border-color: var(--clr-danger-border); background: var(--clr-danger-bg);";
            activeStressPod = true;
        } else if (replicas > 1) {
            valClass = "sc-metric-val";
            cardStyle = "border-color: #c5def9; background: #f0f7ff;";
        }

        const barColor = cpu > 0.05 ? 'var(--clr-danger)' : replicas > 1 ? 'var(--clr-brand-primary)' : 'var(--clr-success)';

        const card = document.createElement("div");
        card.className = "service-card";
        card.style.cssText = cardStyle;
        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="sc-name">${name}</span>
                <span class="sc-pods">${replicas} Pod${replicas !== 1 ? 's' : ''}</span>
            </div>
            <div class="sc-metrics">
                <div class="sc-metric-row">
                    <span class="sc-metric-key">CPU Usage</span>
                    <span class="${valClass}">${cpu.toFixed(3)} (${cpuPercent.toFixed(0)}%)</span>
                </div>
            </div>
            <div style="width:100%; height:4px; background:var(--clr-border-divider); border-radius:2px; overflow:hidden; margin-top:2px;">
                <div style="width:${Math.min(cpuPercent, 100)}%; height:100%; background:${barColor}; border-radius:2px; transition:width 1s;"></div>
            </div>
        `;
        container.appendChild(card);
    });

    isAttackInProgress = activeStressPod;
}

// Pretty formatting helper for JSON strings inside log console (Light Theme version)
function formatLogJson(msg) {
    const braceIndex = msg.indexOf("{");
    if (braceIndex === -1) return msg;

    const prefix = msg.substring(0, braceIndex);
    let jsonStr = msg.substring(braceIndex);

    try {
        let validJsonStr = jsonStr
            .replace(/'/g, '"')
            .replace(/None/g, 'null')
            .replace(/True/g, 'true')
            .replace(/False/g, 'false');
            
        const obj = JSON.parse(validJsonStr);
        const prettyJson = JSON.stringify(obj, null, 2);
        
        return `${prefix}<pre class="bg-zinc-50 border border-zinc-200 p-2.5 rounded-lg text-[10px] text-indigo-700 my-2 font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed shadow-inner max-w-full block">${prettyJson}</pre>`;
    } catch (e) {
        return msg;
    }
}

// Render Log List in Console Window
function renderLogs(logs) {
    const consoleLogs = document.getElementById("console-logs");
    if (!consoleLogs) return;
    consoleLogs.innerHTML = "";
    
    if (logs.length === 0) {
        consoleLogs.innerHTML = `<div class="log-line"><span class="log-badge badge-system">SYS</span><span class="log-msg" style="color:#79c0ff;">Listening for agent logs... Trigger an attack to start.</span></div>`;
        return;
    }

    logs.forEach(log => {
        const timeStr = formatTimestamp(log.timestamp);
        let rawMsg = log.message;
        let sender = "SYS";
        let badgeClass = "badge-system";
        let cleanMsg = rawMsg;

        if (rawMsg.includes("[HEPHAESTUS]")) {
            sender = "DEFENDER";
            badgeClass = "badge-defender";
            cleanMsg = rawMsg.replace("[HEPHAESTUS]", "").trim();
        } else if (rawMsg.includes("nemesis-agent")) {
            sender = "ATTACKER";
            badgeClass = "badge-attacker";
            cleanMsg = rawMsg.replace(/nemesis-agent\s*-\s*\[INFO\]\s*-\s*/g, "").replace(/nemesis-agent\s*-\s*\[WARNING\]\s*-\s*/g, "").trim();
        } else if (rawMsg.includes("[GAIA]")) {
            sender = "OBSERVER";
            badgeClass = "badge-observer";
            cleanMsg = rawMsg.replace("[GAIA]", "").trim();
        }

        const line = document.createElement("div");
        line.className = "log-line";
        line.innerHTML = `
            <span class="log-ts">${timeStr}</span>
            <span class="log-badge ${badgeClass}">${sender}</span>
            <span class="log-msg">${cleanMsg}</span>
        `;
        consoleLogs.appendChild(line);
    });
}

// Update Visual Topology Nodes
function updateWorkflowGraph(services) {
    const nodeNemesis = document.getElementById("node-nemesis");
    const nodeLLM = document.getElementById("node-llm");
    const nodeKafka = document.getElementById("node-kafka");
    const nodeWorker = document.getElementById("node-worker");
    const nodeTarget = document.getElementById("node-target");
    const nodeGaia = document.getElementById("node-gaia");
    const nodeHephaestus = document.getElementById("node-hephaestus");

    if (!nodeNemesis) return;

    // Reset all node classes
    [nodeNemesis, nodeLLM, nodeKafka, nodeWorker, nodeGaia, nodeHephaestus].forEach(n => {
        if (n) n.className = n.classList.contains('topo-node-sub') ? 'topo-node-sub' : 'topo-node';
    });
    if (nodeTarget) nodeTarget.className = 'topo-node node-healthy';

    if (isAttackInProgress) {
        if (nodeTarget) { nodeTarget.classList.remove('node-healthy'); nodeTarget.classList.add('node-danger'); }
        if (nodeGaia) nodeGaia.classList.add('node-warning');
        if (nodeHephaestus) nodeHephaestus.classList.add('node-active');
        if (nodeKafka) nodeKafka.classList.add('node-active');
        if (nodeNemesis) nodeNemesis.classList.add('node-active');
    }
}

// Clear local display logs
function clearDashboardLogs() {
    const el = document.getElementById("console-logs");
    if (el) el.innerHTML = `<div class="log-line"><span class="log-badge badge-system">SYS</span><span class="log-msg" style="color:#79c0ff;">Console cleared locally.</span></div>`;
}

// Trigger AI Planning Attack
async function triggerAIAttack() {
    const btn = document.getElementById("btn-ai-attack");
    if (!btn) return;
    const oldText = btn.innerHTML;
    
    const nodeNemesis = document.getElementById("node-nemesis");
    const nodeLLM = document.getElementById("node-llm");
    if (nodeNemesis) nodeNemesis.classList.add('node-active');
    if (nodeLLM) nodeLLM.classList.add('node-active');

    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner" style="animation:spin 1s linear infinite;"></i> Planning Strategy...`;

    try {
        const response = await fetch(`${API_BASE}/attack/llm-plan`, { method: "POST" });
        if (!response.ok) throw new Error("AI Attack trigger failed");
        
        updateLogs();
        updateAgentChat();
    } catch (error) {
        console.error("AI Attack failed:", error);
        alert("Failure triggering AI Attack. Check server configurations and LLM API limits.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = oldText;
    }
}

// Trigger Manual Attack Script
async function triggerManualAttack() {
    const btn = document.getElementById("btn-manual-attack");
    if (!btn) return;
    const service = document.getElementById("select-service").value;
    const type = document.getElementById("select-attack-type").value;
    const intensity = document.getElementById("select-intensity").value;
    
    const oldText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner" style="animation:spin 1s linear infinite;"></i> Injecting...`;

    const nodeNemesis = document.getElementById("node-nemesis");
    const nodeWorker = document.getElementById("node-worker");
    if (nodeNemesis) nodeNemesis.classList.add('node-active');
    if (nodeWorker) nodeWorker.classList.add('node-active');

    let concurrency = 4;
    if (intensity === "HIGH") {
        concurrency = 80;
    } else if (intensity === "MEDIUM") {
        concurrency = 25;
    } else {
        concurrency = 5;
    }

    try {
        const response = await fetch(`${API_BASE}/attack/trigger`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                attackType: type,
                targetService: service,
                intensity: intensity,
                durationSec: 90,
                concurrency: concurrency
            })
        });
        
        if (!response.ok) throw new Error("Manual attack failed");
        updateLogs();
        updateAgentChat();
    } catch (error) {
        console.error("Manual attack failed:", error);
        alert("Failed to inject manual attack script.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = oldText;
    }
}

// Reset System State
async function resetSystem() {
    const btn = document.getElementById("btn-reset");
    if (!btn) return;
    const oldText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin"></i> Resetting...`;

    try {
        const response = await fetch(`${API_BASE}/api/reset`, { method: "POST" });
        if (!response.ok) throw new Error("Reset API returned error");
        
        isAttackInProgress = false;
        await updateMetrics();
        await updateLogs();
        await updateAgentChat();
    } catch (error) {
        console.error("Failed to reset system:", error);
        alert("Failed to reset system state.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = oldText;
    }
}

// // Render Agent Chat Bubbles
function renderAgentChat(chatList) {
    const chatBox = document.getElementById("agent-chat-box");
    const insightsPreview = document.getElementById("agent-insights-preview");
    if (!chatBox) return;
    
    if (chatList.length === 0) {
        chatBox.innerHTML = `
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:40px 16px; color:var(--clr-text-disabled); text-align:center; gap:10px;">
                <i class="fa-solid fa-comments" style="font-size:28px; color:#ddd;"></i>
                <span style="font-size:11px; line-height:1.6;">No active conversations.<br>Trigger an attack to start AI reasoning.</span>
            </div>
        `;
        if (insightsPreview) {
            insightsPreview.innerHTML = `<div class="shimmer" style="height:48px;"></div><div class="shimmer" style="height:60px;"></div>`;
        }
        return;
    }

    const isAtBottom = chatBox.scrollHeight - chatBox.clientHeight <= chatBox.scrollTop + 60;
    chatBox.innerHTML = "";

    chatList.forEach(chat => {
        const timeStr = formatTimestamp(chat.timestamp);
        const agent = chat.agent;
        const msg = chat.message;
        const reasoning = chat.reasoning;

        let avatarClass = "avatar-system";
        let avatarIcon = "fa-solid fa-robot";
        let agentLabel = "SYSTEM";
        let bubbleClass = "bubble-system";
        let reasonClass = "reasoning-system";

        if (agent === "NEMESIS") {
            avatarClass = "avatar-attacker";
            avatarIcon = "fa-solid fa-brain";
            agentLabel = "NEMESIS (ATTACKER)";
            bubbleClass = "bubble-attacker";
            reasonClass = "reasoning-attacker";
        } else if (agent === "HEPHAESTUS") {
            avatarClass = "avatar-defender";
            avatarIcon = "fa-solid fa-shield-halved";
            agentLabel = "HEPHAESTUS (DEFENDER)";
            bubbleClass = "bubble-defender";
            reasonClass = "reasoning-defender";
        } else if (agent === "GAIA") {
            avatarClass = "avatar-observer";
            avatarIcon = "fa-solid fa-eye";
            agentLabel = "GAIA (OBSERVER)";
            bubbleClass = "bubble-observer";
            reasonClass = "reasoning-observer";
        }

        const msgDiv = document.createElement("div");
        msgDiv.className = "chat-entry";
        msgDiv.innerHTML = `
            <div class="chat-avatar ${avatarClass}"><i class="${avatarIcon}"></i></div>
            <div class="chat-bubble-wrap">
                <div class="chat-meta">
                    <span class="chat-agent-name">${agentLabel}</span>
                    <span class="chat-time">${timeStr}</span>
                </div>
                <div class="chat-bubble ${bubbleClass}">
                    <div style="font-weight:700; margin-bottom:6px;">${msg}</div>
                    ${reasoning ? `<div class="chat-reasoning ${reasonClass}">
                        <div class="reasoning-label"><i class="fa-solid fa-lightbulb"></i> Reasoning &amp; Logic</div>
                        ${reasoning}
                    </div>` : ''}
                </div>
            </div>
        `;
        chatBox.appendChild(msgDiv);
    });

    // Also update insights preview panel
    if (insightsPreview && chatList.length > 0) {
        insightsPreview.innerHTML = "";
        const last3 = chatList.slice(-3).reverse();
        last3.forEach(chat => {
            const agent = chat.agent;
            let dotColor = '#6b46c1';
            if (agent === 'NEMESIS') dotColor = '#c00';
            else if (agent === 'HEPHAESTUS') dotColor = '#037f0c';
            else if (agent === 'GAIA') dotColor = '#8d6605';
            const p = document.createElement('div');
            p.style.cssText = `padding:6px 8px; border-radius:4px; border:1px solid var(--clr-border-divider); background:var(--clr-bg-layout); font-size:11px; line-height:1.5; color:var(--clr-text-body);`;
            p.innerHTML = `<div style="font-size:9px; font-family:monospace; font-weight:700; color:${dotColor}; text-transform:uppercase; margin-bottom:3px;">${agent}</div>${chat.message}`;
            insightsPreview.appendChild(p);
        });
    }

    if (isAtBottom) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

// Clear Agent Chat History
async function clearAgentChat() {
    if (!confirm("Bạn có muốn xóa sạch toàn bộ lịch sử trò chuyện của các tác tử không?")) return;
    try {
        const response = await fetch(`${API_BASE}/api/chat/clear`, { method: "POST" });
        if (!response.ok) throw new Error("Clear chat API failed");
        
        updateAgentChat();
    } catch (error) {
        console.error("Failed to clear chat:", error);
    }
}

// Polling setup
setInterval(updateMetrics, 5000);
setInterval(updateLogs, 5000);
setInterval(updateAgentChat, 5000);

// Initial Load
updateMetrics();
updateLogs();
updateAgentChat();
