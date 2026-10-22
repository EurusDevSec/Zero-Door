// Configuration URLs (relative to window.location)
const API_BASE = window.location.origin;

// State management
let lastLogTimestamp = "";
let isAttackInProgress = false;
let consecutiveErrors = 0;

// Chart.js State
let telemetryChart = null;
const chartHistoryLimit = 12; // 60 seconds (12 points * 5s)
const chartData = {
    labels: [],
    cpuData: [],
};

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
        warningEl.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-red-500"></i> PORT-FORWARD CONNECTION LOST! Check your tunnel terminal, stop the old session with Ctrl+C, then run bash start-demo.sh from the repository root.`;
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

// Live O telemetry state: last good answer and when it was fetched. A failed poll keeps the last
// good values on screen but marks them stale; it never refreshes their time or shows them as new.
const telemetry = { lastGood: null, lastGoodAt: null, lastError: null };

function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
}

function renderTelemetrySource() {
    let banner = document.getElementById("telemetry-source");
    const container = document.getElementById("services-container");
    if (!container) return;
    if (!banner) {
        banner = el("div", "telemetry-source");
        banner.id = "telemetry-source";
        container.parentNode.insertBefore(banner, container);
    }
    const good = telemetry.lastGood;
    const parts = [];
    if (good) {
        const src = good.source || {};
        parts.push(`Source: ${src.name || "unknown"} (${src.status || "UNKNOWN"})`);
        parts.push(`fetched ${formatTimestamp(src.fetched_at) || "?"}`);
        if (src.errors && src.errors.length) parts.push(`errors: ${src.errors.join(", ")}`);
    } else {
        parts.push("Source: no successful fetch yet");
    }
    if (telemetry.lastError) parts.push(`STALE — last poll failed (${telemetry.lastError})`);
    banner.textContent = parts.join(" · ");
    banner.dataset.state = telemetry.lastError ? "stale" : (good && good.source && good.source.status) || "none";
}

// Fetch System Replicas & CPU Metrics
async function updateMetrics() {
    renderSkeleton();
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        telemetry.lastGood = data;
        telemetry.lastGoodAt = Date.now();
        telemetry.lastError = null;
        renderServices(data.services || {});
        updateWorkflowGraph(data.services || {});

        // Chart only real readings; a service without data adds a gap, not a zero.
        const selectedService = document.getElementById("select-service")?.value || "frontend";
        const serviceStatus = (data.services || {})[selectedService] || {};
        const currentCPU = typeof serviceStatus.cpu === "number" ? serviceStatus.cpu : null;
        const timeLabel = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        chartData.labels.push(timeLabel);
        chartData.cpuData.push(currentCPU);
        if (chartData.labels.length > chartHistoryLimit) {
            chartData.labels.shift();
            chartData.cpuData.shift();
        }
        if (telemetryChart) {
            const values = chartData.cpuData.filter(v => typeof v === "number");
            const maxVal = Math.max(...values, 0.2);
            telemetryChart.options.scales.y.max = maxVal > 0.4 ? maxVal * 1.2 : 0.5;
            telemetryChart.data.datasets[0].label = `${selectedService} CPU (Cores)`;
            telemetryChart.data.datasets[0].borderColor = currentCPU !== null && currentCPU > 0.05 ? '#b50000' : '#6b46c1';
            telemetryChart.update();
        }
        consecutiveErrors = 0;
        hideConnectionWarning();
    } catch (error) {
        console.error("Failed to update metrics:", error);
        telemetry.lastError = error.message || "error";
        consecutiveErrors++;
        if (consecutiveErrors >= 2) {
            showConnectionWarning();
        }
    }
    renderTelemetrySource();
}

// Fetch Combined Logs
async function updateLogs() {
    try {
        const response = await fetch(`${API_BASE}/api/logs`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        renderLogs(data.logs || [], data.sources || {});
        consecutiveErrors = 0;
        hideConnectionWarning();
    } catch (error) {
        console.error("Failed to update logs:", error);
        renderLogsError(error.message || "error");
        consecutiveErrors++;
        if (consecutiveErrors >= 2) {
            showConnectionWarning();
        }
    }
}

// Decision reasoning: unavailable in R1 (no AI decision producer). Nothing is generated here.
async function updateAgentChat() {
    let state = { status: "UNAVAILABLE", reason: "NO_DECISION_PRODUCER_IN_R1" };
    try {
        const response = await fetch(`${API_BASE}/api/chat`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        state = await response.json();
    } catch (error) {
        state = { status: "ERROR", reason: error.message || "error" };
    }
    renderAgentChat(state);
}

// Render Microservices in Grid. Values are text; null is "no data", never 0.
function renderServices(services) {
    const container = document.getElementById("services-container");
    if (!container) return;
    container.textContent = "";
    let activeStressPod = false;

    Object.entries(services).forEach(([name, status]) => {
        const replicas = typeof status.replicas === "number" ? status.replicas : null;
        const cpu = typeof status.cpu === "number" ? status.cpu : null;
        const cpuLimit = 0.2;
        const cpuPercent = cpu === null ? null : Math.min((cpu / cpuLimit) * 100, 300);

        const card = el("div", "service-card");
        if (cpu !== null && cpu > 0.05) {
            card.style.cssText = "border-color: var(--clr-danger-border); background: var(--clr-danger-bg);";
            activeStressPod = true;
        } else if (replicas !== null && replicas > 1) {
            card.style.cssText = "border-color: #c5def9; background: #f0f7ff;";
        }
        const head = el("div");
        head.style.cssText = "display:flex; justify-content:space-between; align-items:center;";
        head.appendChild(el("span", "sc-name", name));
        head.appendChild(el("span", "sc-pods", replicas === null ? "no data" : `${replicas} Pod${replicas !== 1 ? 's' : ''}`));
        card.appendChild(head);

        const metrics = el("div", "sc-metrics");
        const row = el("div", "sc-metric-row");
        row.appendChild(el("span", "sc-metric-key", "CPU Usage"));
        row.appendChild(el("span", cpu === null ? "sc-metric-val nodata" : cpu > 0.05 ? "sc-metric-val red" : "sc-metric-val green",
            cpu === null ? "no data" : `${cpu.toFixed(3)} (${cpuPercent.toFixed(0)}%)`));
        metrics.appendChild(row);
        card.appendChild(metrics);

        const track = el("div");
        track.style.cssText = "width:100%; height:4px; background:var(--clr-border-divider); border-radius:2px; overflow:hidden; margin-top:2px;";
        if (cpu !== null) {
            const bar = el("div");
            const barColor = cpu > 0.05 ? 'var(--clr-danger)' : replicas !== null && replicas > 1 ? 'var(--clr-brand-primary)' : 'var(--clr-success)';
            bar.style.cssText = `width:${Math.min(cpuPercent, 100)}%; height:100%; background:${barColor}; border-radius:2px; transition:width 1s;`;
            track.appendChild(bar);
        }
        card.appendChild(track);
        container.appendChild(card);
    });

    isAttackInProgress = activeStressPod;
}

function logLine(time, badge, badgeClass, message) {
    const line = el("div", "log-line");
    line.appendChild(el("span", "log-ts", time));
    line.appendChild(el("span", `log-badge ${badgeClass}`, badge));
    line.appendChild(el("span", "log-msg", message));
    return line;
}

function renderLogsError(reason) {
    const consoleLogs = document.getElementById("console-logs");
    if (!consoleLogs) return;
    const notice = logLine("", "SYS", "badge-system", `Log poll failed (${reason}); lines below may be stale.`);
    notice.dataset.state = "stale";
    const old = consoleLogs.querySelector('[data-state="stale"]');
    if (old) old.remove();
    consoleLogs.insertBefore(notice, consoleLogs.firstChild);
}

// Render Log List in Console Window. Log text is untrusted: it is set as text, never as HTML.
function renderLogs(logs, sources) {
    const consoleLogs = document.getElementById("console-logs");
    if (!consoleLogs) return;
    consoleLogs.textContent = "";
    const failed = Object.entries(sources || {}).filter(([, state]) => state !== "OK");
    if (failed.length) {
        consoleLogs.appendChild(logLine("", "SYS", "badge-system",
            `Source error: ${failed.map(([name, state]) => `${name}=${state}`).join(", ")} — missing lines are not "no actions".`));
    }
    if (logs.length === 0) {
        consoleLogs.appendChild(logLine("", "SYS", "badge-system", "No log lines received."));
        return;
    }
    logs.forEach(log => {
        const rawMsg = String(log.message || "");
        let sender = "SYS", badgeClass = "badge-system", cleanMsg = rawMsg;
        if (rawMsg.includes("[HEPHAESTUS]")) {
            sender = "DEFENDER"; badgeClass = "badge-defender";
            cleanMsg = rawMsg.replace("[HEPHAESTUS]", "").trim();
        } else if (rawMsg.includes("nemesis-agent")) {
            sender = "ATTACKER"; badgeClass = "badge-attacker";
            cleanMsg = rawMsg.replace(/nemesis-agent\s*-\s*\[(INFO|WARNING|ERROR)\]\s*-\s*/g, "").trim();
        } else if (rawMsg.includes("[GAIA]")) {
            sender = "OBSERVER"; badgeClass = "badge-observer";
            cleanMsg = rawMsg.replace("[GAIA]", "").trim();
        }
        consoleLogs.appendChild(logLine(formatTimestamp(log.timestamp), sender, badgeClass, cleanMsg));
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

// Decision reasoning panel. R1 has no AI decision producer: say so; never write reasoning here.
function renderAgentChat(state) {
    const chatBox = document.getElementById("agent-chat-box");
    const insightsPreview = document.getElementById("agent-insights-preview");
    if (!chatBox) return;
    const message = state.status === "ERROR"
        ? `Reasoning status unavailable (${state.reason}).`
        : "AI decision producer: unavailable in R1. No reasoning is generated or replayed in this console; " +
          "decisions and their sources are read from scored results only.";
    chatBox.textContent = "";
    const box = el("div", "chat-unavailable", message);
    box.dataset.status = state.status || "UNAVAILABLE";
    chatBox.appendChild(box);
    if (insightsPreview) {
        insightsPreview.textContent = "";
        insightsPreview.appendChild(el("div", "chat-unavailable", `AI: ${state.status || "UNAVAILABLE"} (${state.reason || "NO_DECISION_PRODUCER_IN_R1"})`));
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

// Initialize Real-time Line Chart
function initChart() {
    const ctx = document.getElementById('telemetryChart');
    if (!ctx) return;
    
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded yet.');
        return;
    }

    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'CPU Usage (Cores)',
                data: chartData.cpuData,
                borderColor: '#6b46c1',
                backgroundColor: 'rgba(107, 70, 193, 0.1)',
                borderWidth: 2,
                pointRadius: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 0.5,
                    ticks: {
                        font: { size: 9 }
                    }
                },
                x: {
                    ticks: {
                        font: { size: 9 },
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 6
                    }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Polling setup
setInterval(updateMetrics, 5000);
setInterval(updateLogs, 5000);
setInterval(updateAgentChat, 5000);

// Initial Load
initChart();
updateMetrics();
updateLogs();
updateAgentChat();
