// ZER-11 results page: read-only view of registered scorer artifacts (S plane).
//
// - Every value comes from /api/results (score.json passed through); nothing is computed here
//   except the update delay (display time - latest scored event milestone) and readable formatting.
// - null/absent is shown as "no data" with its status; it is never turned into 0 or 100%.
// - Untrusted strings are set with textContent only.
// - Only GET requests. The key stays in memory for this tab; it is not stored.
// - Switching runs or keys discards late answers of the previous run or key.
// - A refresh that fails in transit or upstream (no response, 502/503/504 other than the store's
//   own configuration reasons) keeps the last good view marked STALE with the time it was fetched.
//   Any other failure (integrity/schema 422, access 401/403, run no longer registered 404, registry
//   or key configuration, a mismatched answer) means the shown run can no longer be verified: the
//   cached view, its KPI and its downloads are cleared and the error is shown instead.
"use strict";

const API = window.location.origin + "/api/results";
const REFRESH_MS = 15000;
const S = { token: "", runs: [], selected: "", session: 0, generation: 0, view: null, viewAt: null, timer: null };
// 503 reasons of measurement_view/authorize_reader that are configuration or registry state, not a
// transient outage: the run cannot be verified, so they are fatal like a 4xx.
const FATAL_503 = new Set(["RESULTS_NOT_CONFIGURED", "RESULTS_ROOT_INVALID", "REGISTRY_MISSING", "REGISTRY_INVALID", "KEY_SEPARATION"]);

function $(id) { return document.getElementById(id); }

function node(tag, text, className) {
    const n = document.createElement(tag);
    if (className) n.className = className;
    if (text !== undefined && text !== null) n.textContent = String(text);
    return n;
}

function show(value, unit) {
    if (value === null || value === undefined || value === "") return node("span", "no data", "na");
    if (typeof value === "number") return node("span", unit ? `${value} ${unit}` : String(value));
    if (Array.isArray(value)) {
        if (value.some(v => v !== null && typeof v === "object")) return node("span", `${value.length} mục`, "mono");
        return node("span", value.length ? value.join(", ") : "[]");
    }
    if (typeof value === "object") return node("span", JSON.stringify(value), "mono");
    return node("span", String(value));
}

function setState(state, detail) {
    $("state").textContent = state;
    $("state").dataset.state = state;
    $("state-detail").textContent = detail || "";
}

function banner(text) { $("banner").textContent = text || ""; }

async function get(path) {
    let response;
    try {
        response = await fetch(API + path, { method: "GET", headers: { Authorization: "Bearer " + S.token }, cache: "no-store" });
    } catch (e) {
        throw Object.assign(new Error("NETWORK_ERROR"), { transport: true });  // no HTTP answer at all
    }
    let body = null;
    try { body = await response.json(); } catch (e) { body = null; }
    if (!response.ok) {
        const reason = body && typeof body.detail === "string" ? body.detail : `HTTP_${response.status}`;
        const error = new Error(reason);
        error.status = response.status;
        throw error;
    }
    return body;
}

function clearView() {
    for (const id of ["provenance", "kpi", "rates", "counts", "uptime", "modes", "incidents", "downloads"]) $(id).textContent = "";
    $("download-note").textContent = "";
}

function dropView() {
    S.view = null;
    S.viewAt = null;
    clearView();
    document.body.dataset.run = "";
}

// Transient: no HTTP answer at all (network, aborted) or a gateway/upstream outage. Anything else,
// including a bad answer (status 0) or a view that cannot be rendered, is fatal.
function transient(error) {
    if (error.transport === true) return true;
    return [502, 503, 504].includes(error.status) && !FATAL_503.has(error.message);
}

function fatalState(error) {
    if (error.status === 401 || error.status === 403 || error.message === "KEY_SEPARATION") return "NO_ACCESS";
    if (error.status === 422 || error.status === 0) return "ARTIFACT_ERROR";
    return "ERROR";
}

function addKV(list, key, value, unit) {
    list.appendChild(node("dt", key));
    const dd = node("dd");
    dd.appendChild(value instanceof Node ? value : show(value, unit));
    list.appendChild(dd);
}

function table(target, columns, rows) {
    const head = node("tr");
    columns.forEach(c => head.appendChild(node("th", c)));
    target.appendChild(head);
    rows.forEach(cells => {
        const tr = node("tr");
        cells.forEach(cell => {
            const td = node("td");
            td.appendChild(cell instanceof Node ? cell : show(cell));
            tr.appendChild(td);
        });
        target.appendChild(tr);
    });
}

function verdict(value) {
    const span = node("span", value === undefined || value === null ? "no data" : value);
    span.className = value === undefined || value === null ? "na" : "verdict-" + value;
    return span;
}

function percent(rate) {
    if (typeof rate !== "number") return show(rate);
    return node("span", `${rate} (${(rate * 100).toFixed(1)}%)`);
}

function renderProvenance(v, displayedAt) {
    const list = $("provenance");
    const p = v.provenance || {};
    addKV(list, "run_id", v.run_id);
    addKV(list, "Nhóm / chế độ", `${v.group} / ${v.mode}`);
    addKV(list, "Schema / scorer", `${p.schema} / ${p.scorer_version}`);
    addKV(list, "score.json SHA-256", p.sha256 && p.sha256["score.json"]);
    addKV(list, "incidents.csv SHA-256", p.sha256 && p.sha256["incidents.csv"]);
    addKV(list, "usage.csv SHA-256", p.sha256 && p.sha256["usage.csv"]);
    addKV(list, "options SHA-256", p.options_sha256);
    addKV(list, "Export H / O (export.json SHA-256)", `${(p.inputs || {}).h_export_json_sha256 || "—"} / ${(p.inputs || {}).o_export_json_sha256 || "—"}`);
    addKV(list, "Đăng ký lúc", p.registered_at);
    addKV(list, "Scorer ghi artifact lúc", `${p.generated_at} (${p.generated_at_meaning})`);
    const d = v.data_time || {};
    if (d.status === "OK") {
        addKV(list, "Mốc event mới nhất đã chấm", `${new Date(d.latest_ms).toISOString()} (${d.milestone}, ${d.clock_id})`);
        const delay = (displayedAt - d.latest_ms) / 1000;
        addKV(list, "Độ trễ cập nhật", `${delay.toFixed(1)} s (thời điểm hiển thị − mốc event; đồng hồ trình duyệt)`);
    } else {
        addKV(list, "Mốc event mới nhất đã chấm", node("span", `UNKNOWN (${d.reason})`, "na"));
        addKV(list, "Độ trễ cập nhật", node("span", "UNKNOWN: không có mốc event đã xác minh", "na"));
    }
    addKV(list, "Hiển thị lúc", new Date(displayedAt).toISOString());
    addKV(list, "Server trả lúc", v.served_at);
}

function renderKpi(v) {
    const k = v.kpi || {};
    const rows = [["MTTD < 60 s", "mttd"], ["MTTR < 120 s", "mttr_120"], ["MTTR < 180 s", "mttr_180"], ["Reaction < 60 s", "reaction"]].map(([label, key]) => {
        const m = k[key] || {};
        return [label, show(m.status), verdict(m.verdict), show(m.N), show(m.passed), show(m.missing), show(m.unobserved),
                percent(m.rate), show(m.bounds), show(m.mean_observed_s, "s"), show(m.mean_pool), node("span", m.verdict_reason || m.reason || "")];
    });
    table($("kpi"), ["KPI", "status", "verdict", "N", "passed", "missing", "unobserved", "rate", "bounds", "mean (mô tả)", "mean pool", "ghi chú"], rows);
    const rates = [["Phục hồi xác minh", "recovered_rate"], ["Thất bại (TIMEOUT)", "failure_rate"], ["Chưa xác định", "unknown_rate"]].map(([label, key]) => {
        const m = k[key];
        if (!m) return [label, node("span", "no data", "na"), "", "", ""];
        return [label, show(m.status || "OK"), show(m.numerator), show(m.N), percent(m.rate)];
    });
    table($("rates"), ["Tỷ lệ", "status", "tử số", "N", "rate"], rates);
    const c = k.counts || {};
    const counts = $("counts");
    addKV(counts, "Trạng thái cohort", c.status);
    addKV(counts, "Requested / CONFIRMED / NO_EFFECT / UNKNOWN_EFFECT / N", [c.requested, c.CONFIRMED, c.CONFIRMED_NO_EFFECT, c.UNKNOWN_EFFECT, c.N].map(x => x === undefined || x === null ? "—" : x).join(" / "));
    if (c.cohort) addKV(counts, "Cohort", c.cohort);
    addKV(counts, "Nhãn", k.labels && Object.keys(k.labels).length ? Object.entries(k.labels).map(([a, b]) => `${a}=${b}`).join(", ") : node("span", "không có incident", "na"));
    addKV(counts, "Độ phân giải", k.resolution);
    addKV(counts, "R(t)", k.r_t);
}

function renderUptime(v) {
    const entries = Object.entries(v.uptime || {});
    if (!entries.length) { $("uptime").appendChild(node("tr", "Không có trial", "na")); return; }
    table($("uptime"), ["trial_id", "verdict", "W (s)", "U (s)", "lý do"], entries.map(([trial, u]) => [trial, verdict(u.verdict), show(u.W_s), show(u.U_s), show(u.reason)]));
}

function renderModes(v) {
    const list = $("modes");
    addKV(list, "Chế độ (nguồn: group của run trong score.json)", `${v.mode} (${v.group})`);
    if (v.group === "B2" || v.group === "B3") addKV(list, "Producer AI", node("span", "Chưa có producer LLM thật trong R1: chỉ hiện quyết định có trong raw đã chấm", "na"));
    const mv = v.mode_violations || {};
    addKV(list, "MODE_VIOLATION", `${mv.count} ${mv.count ? JSON.stringify(mv.by_trial) : ""}`);
    Object.entries(v.decisions || {}).forEach(([name, m]) => addKV(list, "Quyết định " + name,
        m && !Array.isArray(m) && typeof m === "object" && m.status ? `${m.status}${m.reason ? " — " + m.reason : ""}` : m));
    const u = v.usage || {};
    addKV(list, "Usage (M11)", `${u.status}${u.reason ? " — " + u.reason : ""}`);
    addKV(list, "Funnel (M2)", v.funnel);
    addKV(list, "Containment (M12)", v.containment && v.containment.status);
    addKV(list, "Benign (M5/M6)", v.benign && v.benign.status);
    addKV(list, "CPU P179", v.cpu_P179 && v.cpu_P179.status);
    addKV(list, "Request success", v.request_success_rate && v.request_success_rate.status);
    Object.entries(v.leak || {}).forEach(([trial, l]) => addKV(list, "Leak " + trial, `${l.result}${l.unknown.length ? " (" + l.unknown.join(", ") + ")" : ""}`));
    addKV(list, "Cờ run", v.run_flags);
}

function renderIncidents(v) {
    if (!v.incidents.length) { $("incidents").appendChild(node("tr", "Không có incident trong run này", "na")); return; }
    // In the CSV an empty list column means "none"; an empty value column means no value (null).
    const lists = new Set(["flags", "missing_reasons"]);
    table($("incidents"), v.incident_columns, v.incidents.map(row => row.map((cell, i) =>
        cell !== "" ? node("span", cell, "mono") : lists.has(v.incident_columns[i]) ? node("span", "none", "na") : show(null))));
}

function renderDownloads(v) {
    const box = $("downloads");
    ["score.json", "incidents.csv", "usage.csv"].forEach(name => {
        const b = node("button", "Tải " + name);
        b.type = "button";
        b.addEventListener("click", () => download(v.run_id, name));
        box.appendChild(b);
    });
}

async function download(runId, name) {
    const session = S.session;
    try {
        const response = await fetch(`${API}/runs/${encodeURIComponent(runId)}/files/${encodeURIComponent(name)}`,
            { method: "GET", headers: { Authorization: "Bearer " + S.token }, cache: "no-store" });
        if (!response.ok) throw new Error(`HTTP_${response.status}`);
        const blob = await response.blob();
        if (session !== S.session || !S.view || S.view.run_id !== runId) return;
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `${runId}-${name}`;
        a.click();
        URL.revokeObjectURL(a.href);
        $("download-note").textContent = `${name}: SHA-256 ${response.headers.get("X-ZD-SHA256")}`;
    } catch (error) {
        if (session !== S.session) return;
        $("download-note").textContent = `${name}: tải lỗi (${error.message})`;
    }
}

function render(v) {
    clearView();
    const displayedAt = Date.now();
    renderProvenance(v, displayedAt);
    renderKpi(v);
    renderUptime(v);
    renderModes(v);
    renderIncidents(v);
    renderDownloads(v);
    document.body.dataset.run = v.run_id;
}

async function loadRun(runId, refresh) {
    const generation = refresh ? S.generation : ++S.generation;
    if (!refresh) {
        S.selected = runId;
        S.view = null;
        clearView();
        banner("");
        document.body.dataset.run = "";
    }
    if (!runId) { setState(S.runs.length ? "OK" : "NO_RUNS", S.runs.length ? "Chọn một run" : "Chưa có run nào được đăng ký"); return; }
    if (!refresh) setState("LOADING", runId);
    try {
        const view = await get("/runs/" + encodeURIComponent(runId));
        // A late answer for a run that is no longer selected is dropped, never mixed in.
        if (generation !== S.generation || runId !== S.selected) return;
        if (!view || view.run_id !== runId) throw Object.assign(new Error("RUN_MISMATCH"), { status: 0 });
        render(view);  // only a view that rendered completely becomes the last good one
        S.view = view;
        S.viewAt = Date.now();
        banner("");
        setState("OK", `run ${runId} · lấy lúc ${new Date(S.viewAt).toISOString()}`);
    } catch (error) {
        if (generation !== S.generation || runId !== S.selected) return;
        if (S.view && refresh && transient(error)) {
            setState("STALE", `lần tải gần nhất lỗi (${error.message}); số liệu đang hiện là của lần thành công lúc ${new Date(S.viewAt).toISOString()}`);
            return;
        }
        dropView();
        const state = fatalState(error);
        setState(state, error.message);
        if (state === "NO_ACCESS") {
            endSession();
            banner(`Khóa không còn được chấp nhận (${error.message}): đã xóa số liệu, cần kết nối lại.`);
        } else if (state === "ARTIFACT_ERROR") {
            banner(`Artifact không hợp lệ (${error.message}): không hiện số liệu.`);
        } else if (transient(error)) {
            banner(`Không tải được run (${error.message}).`);
        } else {
            banner(`Run không còn xác minh được (${error.message}): không hiện số liệu.`);
        }
    }
}

// Forget everything read with the current key: in-flight answers, the cached view, the run list and
// the refresh timer. Used before a (re)connect and when the key stops being accepted.
function endSession() {
    S.session++;
    S.generation++;
    clearInterval(S.timer);
    S.timer = null;
    S.runs = [];
    S.selected = "";
    dropView();
    const select = $("run");
    select.textContent = "";
    select.disabled = true;
}

async function loadRuns() {
    const session = S.session;
    let body;
    try {
        body = await get("/runs");
    } catch (error) {
        if (session !== S.session) return false;
        endSession();
        setState(error.status === 401 || error.status === 403 ? "NO_ACCESS" : "ERROR", error.message);
        banner(error.status === 401 || error.status === 403 ? "Khóa không hợp lệ." : `Không đọc được danh sách run (${error.message}).`);
        return false;
    }
    // A list answered for an earlier key or connect is dropped.
    if (session !== S.session) return false;
    S.runs = body && Array.isArray(body.runs) ? body.runs : [];
    const select = $("run");
    select.textContent = "";
    select.appendChild(node("option", S.runs.length ? "— chọn run —" : "— không có run —"));
    select.firstChild.value = "";
    S.runs.forEach(r => {
        const o = node("option", `${r.run_id} · ${r.group}/${r.mode} · đăng ký ${r.registered_at}`);
        o.value = r.run_id;
        select.appendChild(o);
    });
    select.disabled = !S.runs.length;
    if (!S.runs.some(r => r.run_id === S.selected)) S.selected = "";
    select.value = S.selected;
    return true;
}

$("connect").addEventListener("click", async () => {
    // The previous key's view and answers are invalid before the new key reads the registry.
    const selected = S.selected;
    endSession();
    banner("");
    setState("LOADING", "đọc danh sách run");
    S.token = $("token").value;
    $("token").value = "";
    S.selected = selected;
    const session = S.session;
    if (!(await loadRuns())) return;
    await loadRun(S.selected || "", false);
    if (session !== S.session) return;  // a newer connect or a refused key owns the page now
    S.timer = setInterval(() => { if (S.selected) loadRun(S.selected, true); }, REFRESH_MS);
});
$("run").addEventListener("change", event => loadRun(event.target.value, false));
