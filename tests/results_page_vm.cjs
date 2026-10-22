// ZER-11 fix-01 (ZR11-01): the real results.js in a Node VM with a minimal DOM, fake fetch and a
// manual refresh timer. No browser, no network. Each case drives the page through its own handlers
// (connect click, run change, refresh tick) and checks what the DOM shows.
//   node tests/results_page_vm.cjs [path/to/results.js]   -> JSON {cases: [{name, ok, detail}]}, exit 1 on a failure
"use strict";
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const SOURCE = fs.readFileSync(process.argv[2] || path.join(__dirname, "../agent-orchestrator/nemesis/static/results.js"), "utf8");
const RUN_A = "run_" + "a".repeat(32);
const RUN_B = "run_" + "b".repeat(32);

class El {
    constructor(tag) { this.tagName = tag; this.children = []; this.own = ""; this.dataset = {}; this.handlers = {}; this.value = ""; this.disabled = false; this.className = ""; }
    get textContent() { return this.own + this.children.map(c => c.textContent).join(""); }
    set textContent(v) { this.own = String(v); this.children = []; }
    get firstChild() { return this.children[0]; }
    appendChild(c) { this.children.push(c); return c; }
    addEventListener(type, fn) { this.handlers[type] = fn; }
    click() {}
}

function view(runId, verdict) {
    const metric = { status: "OK", verdict, N: 1, passed: 1, missing: 0, unobserved: 0, rate: 1, bounds: [1, 1], mean_observed_s: 30, mean_pool: 1 };
    return { run_id: runId, group: "B1", mode: "RULES", provenance: { schema: "zd-measurement-score/1", sha256: { "score.json": "f".repeat(64) }, inputs: {} },
             data_time: { status: "UNKNOWN", reason: "NO_EVENT_MILESTONE" }, kpi: { mttd: metric, mttr_120: metric, mttr_180: metric, reaction: metric,
             recovered_rate: { numerator: 1, N: 1, rate: 1 }, counts: { status: "OK" }, labels: { RECOVERED: 1 } }, uptime: {}, decisions: {},
             usage: { status: "N/A" }, mode_violations: { count: 0 }, leak: {}, run_flags: [], incident_columns: ["run_id"], incidents: [[runId]] };
}

function answer(status, body) { return { ok: status >= 200 && status < 300, status, json: async () => body, headers: { get: () => null }, blob: async () => null }; }

function page() {
    const nodes = new Map();
    const element = id => { if (!nodes.has(id)) nodes.set(id, new El("div")); return nodes.get(id); };
    const routes = [];  // [{match, reply}] consumed in order; reply = () => answer | Promise | throws
    const calls = [];
    const timers = [];
    const ctx = vm.createContext({
        document: { getElementById: element, createElement: tag => new El(tag), body: new El("body") },
        window: { location: { origin: "http://vm" } }, Node: El, URL: { createObjectURL: () => "blob:", revokeObjectURL() {} }, Date, console,
        setInterval: fn => { timers.push(fn); return timers.length; }, clearInterval: id => { if (id) timers[id - 1] = null; },
        fetch: async (url, init) => {
            calls.push({ url, auth: init.headers.Authorization });
            const i = routes.findIndex(r => url.endsWith(r.match));
            if (i < 0) throw new Error("unexpected fetch " + url);
            const [route] = routes.splice(i, 1);
            return route.reply();
        },
    });
    vm.runInContext(SOURCE, ctx);
    const flush = async () => { for (let i = 0; i < 20; i++) await new Promise(r => setImmediate(r)); };
    const p = {
        el: element, calls, routes,
        on: (match, reply) => routes.push({ match, reply }),
        ok: (match, body) => p.on(match, () => answer(200, body)),
        fail: (match, status, detail) => p.on(match, () => answer(status, { detail })),
        offline: match => p.on(match, () => { throw new TypeError("Failed to fetch"); }),
        connect: async token => { element("token").value = token; await element("connect").handlers.click(); await flush(); },
        choose: async runId => { element("run").handlers.change({ target: { value: runId } }); await flush(); },
        tick: async () => { const live = timers.filter(Boolean); live.forEach(fn => fn()); await flush(); return live.length; },
        timers: () => timers.filter(Boolean).length,
        flush,
        state: () => element("state").textContent,
        // KPI table: header row, then one row per KPI; column 2 is the verdict cell.
        shown: () => ({ state: element("state").textContent, kpi: element("kpi").textContent, downloads: element("downloads").children.length,
                        verdicts: element("kpi").children.slice(1).map(tr => tr.children[2].textContent),
                        run: ctx.document.body.dataset.run, banner: element("banner").textContent }),
    };
    return p;
}

async function loaded(token = "key-1") {
    const p = page();
    p.ok("/runs", { runs: [{ run_id: RUN_A, group: "B1", mode: "RULES" }, { run_id: RUN_B, group: "B1", mode: "RULES" }] });
    await p.connect(token);
    p.ok("/runs/" + RUN_A, view(RUN_A, "PASS"));
    await p.choose(RUN_A);
    return p;
}

const cases = [];
const check = (name, fn) => cases.push({ name, fn });
const cleared = s => s.kpi === "" && s.downloads === 0 && s.run === "";
const every = (s, verdict) => s.verdicts.length === 4 && s.verdicts.every(v => v === verdict);
const showsPass = (s, run = RUN_A) => every(s, "PASS") && s.downloads === 3 && s.run === run;

// Fatal answers on refresh after a good view: the cached PASS must disappear (ZR11-01).
for (const [status, detail, state] of [[422, "ARTIFACT_HASH_MISMATCH", "ARTIFACT_ERROR"], [422, "SCHEMA_UNSUPPORTED", "ARTIFACT_ERROR"],
                                       [422, "EXPORT_INCONSISTENT", "ARTIFACT_ERROR"], [401, "UNAUTHORIZED", "NO_ACCESS"],
                                       [404, "RUN_NOT_REGISTERED", "ERROR"], [503, "REGISTRY_INVALID", "ERROR"], [503, "KEY_SEPARATION", "NO_ACCESS"],
                                       [500, "HTTP_500", "ERROR"]]) {
    check(`good_then_${status}_${detail}_clears_view`, async () => {
        const p = await loaded();
        if (!showsPass(p.shown())) return ["precondition", p.shown()];
        p.fail("/runs/" + RUN_A, status, detail);
        await p.tick();
        const s = p.shown();
        const ok = cleared(s) && s.state === state && s.banner.includes(detail);
        // A refused key also ends the session: no timer keeps polling with it.
        return [ok && (state !== "NO_ACCESS" || p.timers() === 0), s, { timers: p.timers() }];
    });
}

check("good_then_unrenderable_answer_clears_view", async () => {
    const p = await loaded();
    p.ok("/runs/" + RUN_A, Object.assign(view(RUN_A, "NOT_PASS"), { incidents: null }));
    await p.tick();
    const s = p.shown();
    return [cleared(s) && s.state === "ERROR", s];
});

check("good_then_mismatched_answer_clears_view", async () => {
    const p = await loaded();
    p.ok("/runs/" + RUN_A, view(RUN_B, "PASS"));
    await p.tick();
    const s = p.shown();
    return [cleared(s) && s.state === "ARTIFACT_ERROR" && s.banner.includes("RUN_MISMATCH"), s];
});

// Control: a transient outage keeps the last good view as STALE, and the next good answer replaces it.
for (const kind of ["503_upstream", "502", "504", "network"]) {
    check(`good_then_${kind}_is_stale_then_good`, async () => {
        const p = await loaded();
        if (kind === "network") p.offline("/runs/" + RUN_A);
        else p.fail("/runs/" + RUN_A, Number(kind.slice(0, 3)), kind === "503_upstream" ? "FIXTURE_UPSTREAM_DOWN" : undefined);
        await p.tick();
        const stale = p.shown();
        p.ok("/runs/" + RUN_A, view(RUN_A, "NOT_PASS"));
        await p.tick();
        const fresh = p.shown();
        return [stale.state === "STALE" && showsPass(stale) && fresh.state === "OK" && every(fresh, "NOT_PASS"), { stale, fresh }];
    });
}

check("after_fatal_a_later_verified_answer_is_shown_fresh", async () => {
    const p = await loaded();
    p.fail("/runs/" + RUN_A, 422, "ARTIFACT_HASH_MISMATCH");
    await p.tick();
    p.ok("/runs/" + RUN_A, view(RUN_A, "NOT_PASS"));
    await p.tick();
    const s = p.shown();
    return [s.state === "OK" && every(s, "NOT_PASS"), s];
});

check("fatal_then_transient_does_not_bring_back_old_view", async () => {
    const p = await loaded();
    p.fail("/runs/" + RUN_A, 404, "RUN_NOT_REGISTERED");
    await p.tick();
    p.fail("/runs/" + RUN_A, 503, "FIXTURE_UPSTREAM_DOWN");
    await p.tick();
    const s = p.shown();
    return [cleared(s) && s.state === "ERROR", s];
});

// Control kept from the first package: A answers late after B was chosen; only B is shown.
check("late_answer_of_previous_run_is_dropped", async () => {
    const p = page();
    p.ok("/runs", { runs: [{ run_id: RUN_A }, { run_id: RUN_B }] });
    await p.connect("key-1");
    let releaseA;
    p.on("/runs/" + RUN_A, () => new Promise(r => { releaseA = () => r(answer(200, view(RUN_A, "PASS"))); }));
    await p.choose(RUN_A);
    p.ok("/runs/" + RUN_B, view(RUN_B, "NOT_PASS"));
    await p.choose(RUN_B);
    releaseA();
    await p.flush();
    const s = p.shown();
    return [s.run === RUN_B && every(s, "NOT_PASS"), s];
});

// Reconnect with another key: the old view goes before the new key reads the registry, and an old
// in-flight refresh cannot paint over the new session.
check("reconnect_drops_old_view_and_old_inflight_answer", async () => {
    const p = await loaded("key-1");
    let releaseOld;
    p.on("/runs/" + RUN_A, () => new Promise(r => { releaseOld = () => r(answer(200, view(RUN_A, "PASS"))); }));
    await p.tick();  // refresh with key-1 now in flight
    let releaseList, duringList;
    p.on("/runs", () => new Promise(r => { duringList = p.shown(); releaseList = () => r(answer(401, { detail: "UNAUTHORIZED" })); }));
    const connecting = p.connect("key-2");
    await p.flush();
    releaseOld();
    await p.flush();
    releaseList();
    await connecting;
    const s = p.shown();
    const timersAfter = p.timers();
    const polled = await p.tick();
    const auths = p.calls.map(c => c.auth);
    return [cleared(duringList) && cleared(s) && s.state === "NO_ACCESS" && timersAfter === 0 && polled === 0 &&
            auths[auths.length - 1] === "Bearer key-2", { duringList, after: s, timersAfter, auths }];
});

check("reconnect_with_valid_key_reloads_selected_run_with_new_key", async () => {
    const p = await loaded("key-1");
    p.ok("/runs", { runs: [{ run_id: RUN_A }] });
    p.ok("/runs/" + RUN_A, view(RUN_A, "NOT_PASS"));
    await p.connect("key-2");
    const s = p.shown();
    const auths = p.calls.slice(-2).map(c => c.auth);
    return [s.state === "OK" && every(s, "NOT_PASS") && p.timers() === 1 && auths.every(a => a === "Bearer key-2"), { s, auths, timers: p.timers() }];
});

(async () => {
    const results = [];
    for (const c of cases) {
        try {
            const [ok, ...detail] = await c.fn();
            results.push({ name: c.name, ok: ok === true, detail });
        } catch (error) {
            results.push({ name: c.name, ok: false, detail: [String(error && error.stack || error)] });
        }
    }
    console.log(JSON.stringify({ source: process.argv[2] || "agent-orchestrator/nemesis/static/results.js", cases: results }, null, 1));
    process.exit(results.every(r => r.ok) ? 0 : 1);
})();
