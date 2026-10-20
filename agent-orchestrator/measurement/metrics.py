"""Aggregates over scored incidents: ZER-32 KPI/D-01, uptime D-05/RV-01 and ZER-8 M1-M12.

Every value carries numerator, denominator/cohort, coverage and exclusions. A metric without
evidence is MISSING or N/A with a reason, never 0. Means over observed values are descriptive only
and never replace a rate over all eligible incidents.
"""
import math

from .clock import duration, parse

RECOVERED = {"RECOVERED", "RECOVERED_AFTER_STOP", "RECOVERED_BEFORE_DETECT", "RECOVERED_UNDETECTED"}
MISSING_LABELS = {"MISSING", "MISSING_PROBE", "UNKNOWN_EFFECT"}


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def ratio(k, n):
    return None if not n else round(k / n, 6)


def base_counts(incidents):
    counts = {"requested": len(incidents), "CONFIRMED": 0, "CONFIRMED_NO_EFFECT": 0, "UNKNOWN_EFFECT": 0}
    for r in incidents:
        # Only a verified NO_EFFECT leaves N; a NO_EFFECT record on a MISSING incident stays as unknown.
        if r["label"] == "CONFIRMED_NO_EFFECT":
            counts["CONFIRMED_NO_EFFECT"] += 1
        elif r["effect"] == "CONFIRMED":
            counts["CONFIRMED"] += 1
        else:
            counts["UNKNOWN_EFFECT"] += 1
    eligible = [r for r in incidents if r["label"] != "CONFIRMED_NO_EFFECT"]
    counts["N"] = len(eligible)
    counts["status"] = "EMPTY" if not incidents else "NO_ELIGIBLE" if not eligible else "OK"
    return counts, eligible


def threshold_metric(eligible, counts, value_of, threshold_s, missing_of, unobserved_of, mean_pool=None):
    """D-01: rate < threshold over N, missing-data bounds, descriptive mean and the verdict."""
    n = counts["N"]
    if counts["status"] != "OK":
        return {"status": counts["status"], "verdict": counts["status"], "N": n, "threshold_s": threshold_s}
    values = [value_of(r) for r in eligible]
    if all(v == "N/A" for v in values):
        return {"status": "N/A", "verdict": "N/A", "N": n, "threshold_s": threshold_s, "reason": "no detector/decider in this group"}
    passed = sum(1 for r, v in zip(eligible, values) if number(v) and v < threshold_s and (mean_pool is None or mean_pool(r)))
    missing = sum(1 for r in eligible if missing_of(r))
    unobserved = sum(1 for r in eligible if not missing_of(r) and unobserved_of(r))
    pool = [v for r, v in zip(eligible, values) if number(v) and (mean_pool is None or mean_pool(r))]
    mean = round(sum(pool) / len(pool), 3) if pool else None
    if missing:
        verdict = "UNKNOWN"
    elif unobserved:
        verdict = "NOT_PASS"
    else:
        verdict = "PASS" if mean is not None and mean < threshold_s else "FAIL"
    return {"status": "OK", "threshold_s": threshold_s, "N": n, "passed": passed, "missing": missing,
            "unobserved": unobserved, "rate": ratio(passed, n), "bounds": [ratio(passed, n), ratio(passed + missing, n)],
            "mean_observed_s": mean, "mean_pool": len(pool), "verdict": verdict,
            "note": "mean is descriptive; verdict per ZER-32 D-01; '<' is strict"}


def kpi(incidents, f01, cohort=None):
    counts, eligible = base_counts(incidents)
    labels = {}
    for r in incidents:
        labels[r["label"]] = labels.get(r["label"], 0) + 1
    out = {"counts": counts, "labels": labels,
           "resolution": {"delta_s": f01 and f01["delta_s"], "k": f01 and f01["k"],
                          "note": "MTTR resolution is bounded by delta and K (ZER-32 3.4)"}}
    out["mttd"] = threshold_metric(eligible, counts, lambda r: r["mttd"], 60, lambda r: r["mttd"] == "MISSING",
                                   lambda r: r["mttd"] == "MISSED")
    for theta in (120, 180):
        out[f"mttr_{theta}"] = threshold_metric(
            eligible, counts, lambda r: r["mttr"] if r["label"] == "RECOVERED" else None, theta,
            lambda r: r["label"] in MISSING_LABELS, lambda r: r["label"] != "RECOVERED",
            mean_pool=lambda r: r["label"] == "RECOVERED")
    out["reaction"] = threshold_metric(eligible, counts, lambda r: r["reaction"], 60,
                                       lambda r: r["reaction"] == "MISSING",
                                       lambda r: r["reaction"] in ("NO_SUCCESS", "NO_DETECT"))
    if counts["status"] == "OK":
        n = counts["N"]
        recovered = sum(1 for r in eligible if r["label"] in RECOVERED)
        failed = sum(1 for r in eligible if r["label"] == "TIMEOUT")
        unknown = sum(1 for r in eligible if r["label"] in MISSING_LABELS)
        out["recovered_rate"] = {"numerator": recovered, "N": n, "rate": ratio(recovered, n),
                                 "by_label": {k: v for k, v in labels.items() if k in RECOVERED}}
        # Reported side by side: a mean over recovered incidents never replaces these rates.
        out["failure_rate"] = {"numerator": failed, "N": n, "rate": ratio(failed, n), "labels": ["TIMEOUT"]}
        out["unknown_rate"] = {"numerator": unknown, "N": n, "rate": ratio(unknown, n), "labels": sorted(MISSING_LABELS)}
        out["recovered_distribution"] = {
            "total_s": sorted(r["total"] for r in eligible if r["label"] in RECOVERED and number(r.get("total"))),
            "mttr_s_recovered_only": sorted(r["mttr"] for r in eligible if r["label"] == "RECOVERED" and number(r.get("mttr")))}
    else:
        out["recovered_rate"] = {"status": counts["status"], "N": counts["N"]}
    trials = {}
    for r in incidents:
        trials.setdefault(r["trial_id"], {}).setdefault(r["label"], 0)
        trials[r["trial_id"]][r["label"]] += 1
    out["labels_by_trial"] = trials
    out["r_t"] = r_of_t(eligible, counts, f01)
    if cohort is not None and not cohort["complete"]:
        # Requested turns may be missing from N (unattributable request evidence): no verdict can stand.
        counts["cohort"] = "INCOMPLETE"
        for name in ("mttd", "mttr_120", "mttr_180", "reaction"):
            out[name] = dict(out[name], verdict="UNKNOWN", verdict_reason="COHORT_INCOMPLETE")
        out["cohort_problems"] = cohort["problems"]
    return out


def r_of_t(eligible, counts, f01):
    """M8: R_lower(t)/R_upper(t) from TotalRecovery (from effect; not the MTTR KPI)."""
    if counts["status"] != "OK" or not f01:
        return {"status": counts["status"] if counts["status"] != "OK" else "PARAMS_INVALID"}
    points = {}
    for t in (120, 180, f01["cap_rec_s"]):
        low = sum(1 for r in eligible if number(r.get("total")) and r["total"] <= t)
        # Unknown: no valid TotalRecovery and no evidence of non-recovery up to t.
        unknown = sum(1 for r in eligible if not number(r.get("total")) and r["label"] not in ("TIMEOUT",) and r["label"] not in RECOVERED)
        points[str(t)] = {"lower": ratio(low, counts["N"]), "upper": ratio(low + unknown, counts["N"])}
    cap = points[str(f01["cap_rec_s"])]
    if cap["upper"] < 0.5:
        median = "> cap_rec"
    elif cap["lower"] < 0.5:
        median = "UNKNOWN"
    else:
        median = "<= cap_rec (needs the curve for a point value)"
    return {"status": "OK", "N": counts["N"], "points": points, "median": median,
            "note": "120/180 s here are from effect, not the MTTR KPI from detect"}


# --------------------------------------------------------------------------- uptime (ZER-32 3.7)
def norm(intervals):
    out = []
    for a, b in sorted(i for i in intervals if i[1] > i[0]):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def subtract(intervals, cut):
    out = []
    cut = norm(cut)
    for a, b in norm(intervals):
        pieces = [[a, b]]
        for c, d in cut:
            nxt = []
            for x, y in pieces:
                if d <= x or c >= y:
                    nxt.append([x, y])
                    continue
                if c > x:
                    nxt.append([x, c])
                if d < y:
                    nxt.append([d, y])
            pieces = nxt
        out += pieces
    return norm(out)


def length(intervals):
    return sum(b - a for a, b in norm(intervals))


def clip(intervals, lo, hi):
    return norm([[max(a, lo), min(b, hi)] for a, b in intervals])


def flow_intervals(samples, w0, w1, f01):
    """U_f and outages (point/min/max) of one flow on the reference axis, half-open, clipped to W."""
    delta, gap, k = f01["delta_s"] * 1000, f01["gap_s"] * 1000, f01["k"]
    xs = [s for s in samples if w0 <= s["t"] < w1]
    if not xs:
        return {"U": [[w0, w1]], "point": [], "min": [], "max": [], "samples": 0}
    unobserved = [[w0, xs[0]["t"]]]
    for a, b in zip(xs, xs[1:]):
        if b["t"] - a["t"] > gap or b["seq"] != a["seq"] + 1:
            unobserved.append([a["t"] + delta, b["t"]])
    unobserved.append([xs[-1]["t"] + delta, w1])
    point, low, high = [], [], []
    outage, run, last_pass = None, [], None
    for i, s in enumerate(xs):
        joined = i > 0 and s["t"] - xs[i - 1]["t"] <= gap and s["seq"] == xs[i - 1]["seq"] + 1
        if s["ok"]:
            if outage is None:
                last_pass = s["t"]
                continue
            run = run + [s] if run and joined else [s]
            if len(run) >= k:
                close = run[0]["t"]
                point.append([outage["first"], close])
                low.append([outage["first"], outage["last"]])
                high.append([outage["before"], close])
                outage, run, last_pass = None, [], s["t"]
        else:
            run = []
            if outage is None:
                outage = {"first": s["t"], "last": s["t"], "before": last_pass if last_pass is not None else w0}
            outage["last"] = s["t"]
    if outage is not None:
        point.append([outage["first"], w1])
        low.append([outage["first"], outage["last"]])
        high.append([outage["before"], w1])
    return {"U": clip(unobserved, w0, w1), "point": clip(point, w0, w1), "min": clip(low, w0, w1),
            "max": clip(high, w0, w1), "samples": len(xs)}


def uptime(scorer, trial_id, flows):
    """Time-based availability of one trial over the required flows (D-05). Bounds, not a proof."""
    f01 = scorer.f01
    if f01 is None:
        return {"verdict": "UNKNOWN", "reason": "PARAMS_INVALID"}
    if not flows:
        return {"verdict": "UNKNOWN", "reason": "NO_REQUIRED_FLOWS"}
    trial = scorer.trial.get(trial_id)
    if not trial or not trial["start"] or not trial["end"]:
        return {"verdict": "UNKNOWN", "reason": "TRIAL_BOUNDS_MISSING"}
    warm = trial["start"]["payload"].get("warmup_end")
    if warm is None:
        return {"verdict": "UNKNOWN", "reason": "WARMUP_NOT_REACHED"}
    model = trial["clock"]
    w0 = model.at(trial["start"]["clock"]["clock_id"], parse(warm))
    w1 = model.at(trial["end"]["clock"]["clock_id"], parse(trial["end"]["ts_event"]))
    if not (w0.verified and w1.verified) or w1.ms - w0.ms <= 0:
        return {"verdict": "UNKNOWN", "reason": "INVALID_WINDOW"}
    per_flow, U, points, mins, maxs = {}, [], [], [], []
    for flow in flows:
        regs = [r for r in trial["probes"] if isinstance(r, dict) and r.get("flow") == flow]
        if len(regs) != 1:
            per_flow[flow] = {"reason": "PROBE_NOT_REGISTERED" if not regs else "MULTIPLE_PROBES_OPEN"}
            if len(regs) > 1:
                return {"verdict": "UNKNOWN", "reason": "MULTIPLE_PROBES_OPEN", "flows": per_flow}
            U.append([w0.ms, w1.ms])
            continue
        reg = regs[0]
        verified, reasons = model.state(reg["clock_id"])
        if not verified:
            return {"verdict": "UNKNOWN", "reason": "CLOCK_UNVERIFIED", "clock_reasons": reasons}
        samples = []
        for e in scorer.of("PROBE_SAMPLE", trial_id):
            p = e["payload"]
            if (p["flow"], p["probe_id"], p["probe_version"], e["clock"]["clock_id"]) == (flow, reg["probe_id"], reg["probe_version"], reg["clock_id"]):
                samples.append({"t": model.at(reg["clock_id"], parse(p["t_start"])).ms, "ok": p["pass"], "seq": p["sequence"]})
        samples.sort(key=lambda s: (s["t"], s["seq"]))
        f = flow_intervals(samples, w0.ms, w1.ms, f01)
        per_flow[flow] = {"samples": f["samples"], "unobserved_s": round(length(f["U"]) / 1000, 3),
                          "outages": len(f["point"])}
        U += f["U"]
        points += subtract(f["point"], f["U"])
        mins += subtract(f["min"], f["U"])
        maxs += f["max"]
    width = w1.ms - w0.ms
    d_point, d_min, d_lower = length(points), length(mins), length(maxs + U)
    a_lower, a_upper, a_point = 1 - d_lower / width, 1 - d_min / width, 1 - d_point / width
    verdict = "PASS" if a_lower >= 0.999 else "FAIL" if a_upper < 0.999 else "UNKNOWN"
    return {"verdict": verdict, "W_s": round(width / 1000, 3), "U_s": round(length(U) / 1000, 3),
            "D_point_s": round(d_point / 1000, 3), "D_min_s": round(d_min / 1000, 3), "D_lower_s": round(d_lower / 1000, 3),
            "A_lower": round(a_lower, 6), "A_point": round(a_point, 6), "A_upper": round(a_upper, 6),
            "delta_s": f01["delta_s"], "gap_s": f01["gap_s"], "k": f01["k"], "flows": per_flow,
            "assumption": "up between passing samples spaced <= gap; outages shorter than the spacing can be missed"}


# --------------------------------------------------------------------------- decisions (ZER-8 5.3-5.5)
GT_CONSTRAINTS = "zd-gt-constraints/0"  # offline proposal; the action enum/params are OPEN in ZER-50


def constraint_problem(action, rule):
    """Why one zd-gt-constraints/0 entry cannot be used, or None. Types/ranges are checked before any comparison."""
    if not isinstance(rule, dict):
        return "not an object"
    if action == "SCALE_UP":
        value = rule.get("max_replicas")
        return None if type(value) is int and value >= 1 else "max_replicas must be an integer >= 1"
    if action == "BLOCK_IP":
        low, high = rule.get("ttl_s_min"), rule.get("ttl_s_max")
        if not (number(low) and number(high) and 0 <= low <= high):
            return "ttl_s_min/ttl_s_max must be numbers with 0 <= min <= max"
        return None
    if action == "ROLLBACK":
        return None  # judged against the request's known_good_revision
    return "action not supported by " + GT_CONSTRAINTS


def gt_view(inc):
    """The incident's locked ground truth as (gt, problems): every field the metrics read is type-checked once.

    A malformed field never crashes the scorer and is never replaced by a default: the outcome that
    needs it is UNKNOWN_GT / UNKNOWN_COHORT with the problem as its reason (ZER-8 5.4).
    """
    gt = inc["gt"]
    if inc["gt_conflict"]:
        return None, {"gt": "more than one GROUND_TRUTH_LOCKED for the variant"}
    if gt is None:
        return None, {"gt": "no GROUND_TRUTH_LOCKED for the variant"}
    if not isinstance(gt, dict):
        return None, {"gt": "not an object"}
    problems = {}
    if type(gt.get("decision_required")) is not bool:
        problems["decision_required"] = "not a boolean"
    if not (isinstance(gt.get("case_class"), str) and gt["case_class"]):
        problems["case_class"] = "not a non-empty string"
    allowed = gt.get("acceptable_actions")
    if not (isinstance(allowed, list) and all(isinstance(a, str) for a in allowed)):
        problems["acceptable_actions"] = "not a list of strings"
    constraints = gt.get("constraints")
    if constraints is not None and not isinstance(constraints, dict):
        problems["constraints"] = "not an object"
    elif constraints:
        for action, rule in constraints.items():
            problem = constraint_problem(action, rule)
            if problem:
                problems["constraints." + str(action)] = problem
    return gt, problems


def strings(value):
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def assess(decision, inc):
    """(outcome, reason) of one pre-guard decision against the locked ground truth (ZER-8 5.3/5.4)."""
    gt, problems = gt_view(inc)
    if gt is None:
        return "UNKNOWN_GT", problems["gt"]
    if "acceptable_actions" in problems:
        return "UNKNOWN_GT", "acceptable_actions: " + problems["acceptable_actions"]
    allowed = gt["acceptable_actions"]
    p = decision["payload"]
    kind = p["response_kind"]
    if kind in ("NO_ACTION", "ABSTAIN"):
        return (f"{kind}_VALID" if kind in allowed else f"{kind}_INVALID"), None
    if kind == "SCHEMA_INVALID":
        return "SCHEMA_INVALID", None
    if kind in ("TIMEOUT", "REFUSAL"):
        return "NO_RESPONSE", None
    proposal = p.get("proposal")
    params = proposal.get("params") if isinstance(proposal, dict) else None
    if not isinstance(proposal, dict) or not isinstance(params, dict):
        return "SCHEMA_INVALID", "proposal/params not an object"
    action = proposal.get("action_type")
    if not isinstance(action, str) or action not in allowed:
        return "INCORRECT", None
    for key in ("constraints", "constraints." + action):
        if key in problems:
            return "UNKNOWN_GT", f"{key}: {problems[key]}"
    rules = (gt.get("constraints") or {}).get(action)
    req = inc["req"]["payload"]
    if inc.get("targets_unknown") and action in ("SCALE_UP", "ROLLBACK"):
        return "UNKNOWN_GT", "request targets unknown (request invalid or late)"
    if action == "SCALE_UP":
        if rules is None:
            return "UNKNOWN_GT", "no SCALE_UP constraint"
        if "service" not in params or "replicas" not in params:
            return "INCORRECT", "proposal lacks service/replicas"
        ok = isinstance(params["service"], str) and params["service"] in inc["targets"] and \
            type(params["replicas"]) is int and 0 < params["replicas"] <= rules["max_replicas"]
    elif action == "BLOCK_IP":
        if rules is None:
            return "UNKNOWN_GT", "no BLOCK_IP constraint"
        if not strings(req.get("s_att")):
            return "UNKNOWN_GT", "request s_att missing or malformed"
        sources, ttl = params.get("sources"), params.get("ttl_s")
        ok = strings(sources) and bool(sources) and set(sources) <= set(req["s_att"]) and number(ttl) \
            and rules["ttl_s_min"] <= ttl <= rules["ttl_s_max"]
    elif action == "ROLLBACK":
        if not isinstance(req.get("known_good_revision"), str):
            return "UNKNOWN_GT", "request known_good_revision missing or malformed"
        ok = isinstance(params.get("service"), str) and params["service"] in inc["targets"] and \
            params.get("revision") == req["known_good_revision"]
    else:
        return "UNKNOWN_GT", "action not supported by " + GT_CONSTRAINTS
    return ("CORRECT" if ok else "INCORRECT"), None


def judge(decision, inc):
    return assess(decision, inc)[0]


GOOD = {"CORRECT", "NO_ACTION_VALID", "ABSTAIN_VALID"}
UNKNOWN_OUTCOMES = {"UNKNOWN_GT", "MISSING_ORDER", "UNKNOWN_COHORT", "DECISION_CONFLICT"}


def first_decision(scorer, inc, result):
    """Earliest PROPOSAL after T_det from the group's decider (or its fallback); ZER-8 5.3.

    Order needs comparable clocks: an unverified decision clock, an unknown T_det or two proposals at
    the same earliest instant give MISSING_ORDER, never a choice by ingest order.
    """
    group = scorer.group
    allowed = {"B1": {"decision_rules"}, "B2": {"decision_llm", "decision_rules"},
               "B3": {"decision_single_llm", "decision_rules"}, "BM": {"operator_console"}}.get(group, set())
    det = inc.get("t_det")
    pool = []
    for d in inc["decisions"]:
        if d["payload"]["stage"] != "PROPOSAL" or d["source_component"] not in allowed:
            continue
        t = scorer.stamp_of(d)
        if t is None or (det is not None and not t.comparable(det)):
            return None, "MISSING_ORDER"
        if det is not None and t.ms < det.ms:
            continue
        pool.append((t, d))
    if pool and result.get("t_det_status") == "CLOCK_UNVERIFIED":
        return None, "MISSING_ORDER"
    if any(not pool[0][0].comparable(t) for t, _ in pool):
        return None, "MISSING_ORDER"
    pool.sort(key=lambda x: x[0].ms)
    if len(pool) > 1 and pool[0][0].ms == pool[1][0].ms and pool[0][1]["decision_id"] != pool[1][1]["decision_id"]:
        return None, "MISSING_ORDER"
    if pool and ("DECISION", pool[0][1]["decision_id"]) in inc.get("conflicted", set()):
        return None, "DECISION_CONFLICT"
    return (pool[0][1], None) if pool else (None, None)


def decision_metrics(scorer, results):
    group = scorer.group
    if group == "B0":
        na = {"status": "N/A", "reason": "B0 has no ZERO DOOR decision"}
        return {"M1": na, "M1c": na, "M3": na, "M4": na, "M10": na}
    rows, by_class = [], {}
    for r in results:
        inc = scorer.inc[r["incident_id"]]
        gt, problems = gt_view(inc)
        cohort = None if gt is None or "decision_required" in problems else gt["decision_required"]
        case_class = None if gt is None or "case_class" in problems else gt["case_class"]
        decision, problem = first_decision(scorer, inc, r)
        reason = None
        if r["label"] == "CONFIRMED_NO_EFFECT":
            outcome = "OUT_NO_EFFECT"
        elif cohort is None:
            outcome, reason = "UNKNOWN_COHORT", problems.get("gt") or problems.get("decision_required")
        elif problem:
            outcome = problem
        elif r.get("t_det_status") == "CLOCK_UNVERIFIED":
            outcome, reason = "MISSING_ORDER", "T_det on an unverified clock"
        elif r["milestones"]["t_det"] is None:
            outcome = "NO_TRIGGER"
        elif decision is None:
            outcome = "NO_RESPONSE"
        elif decision["payload"]["fallback"]:
            outcome = "FALLBACK_RULES"
        elif decision["payload"]["response_kind"] in ("TIMEOUT", "SCHEMA_INVALID", "REFUSAL") and any(
                d["payload"]["fallback"] and d["payload"]["fallback_of"] == decision["decision_id"] for d in inc["decisions"]):
            # The first attempt failed and RULES decided instead: never credited to the LLM (ZER-8 5.4).
            outcome = "FALLBACK_RULES"
        else:
            outcome, reason = assess(decision, inc)
        latency = None
        if decision is not None and inc.get("t_det") is not None:
            d = duration(inc["t_det"], scorer.stamp_of(decision))
            latency = None if d is None else round(d[0] / 1000, 3)
        rows.append({"incident_id": r["incident_id"], "class": case_class, "decision_required": cohort,
                     "outcome": outcome, "reason": reason, "decision_id": decision and decision["decision_id"],
                     "decision_latency_s": latency})
    cohort_rows = [x for x in rows if x["decision_required"] is True or x["outcome"] == "UNKNOWN_COHORT"]

    def rate(selected):
        n = len([x for x in selected if x["outcome"] != "OUT_NO_EFFECT"])
        if not selected:
            return {"status": "EMPTY"}
        if n == 0:
            return {"status": "NO_ELIGIBLE"}
        good = sum(1 for x in selected if x["outcome"] in GOOD)
        unknown = sum(1 for x in selected if x["outcome"] in UNKNOWN_OUTCOMES)
        return {"status": "OK", "numerator": good, "N": n, "unknown": unknown,
                "bounds": [ratio(good, n), ratio(good + unknown, n)],
                "outcomes": {o: sum(1 for x in selected if x["outcome"] == o) for o in sorted({x["outcome"] for x in selected})}}
    for x in cohort_rows:
        by_class.setdefault(x["class"] or "UNKNOWN", []).append(x)
    classes = {c: rate(v) for c, v in sorted(by_class.items())}
    main = [classes.get(c) for c in ("C1", "C2", "C3", "C4")]
    if any(m is None or m["status"] != "OK" for m in main):
        macro = {"status": "UNDETERMINED", "reason": "a C1-C4 class is empty, no-eligible or absent"}
    else:
        macro = {"status": "OK", "bounds": [round(sum(m["bounds"][0] for m in main) / 4, 6), round(sum(m["bounds"][1] for m in main) / 4, 6)],
                 "weights": "1/4 each C1-C4; C5 reported separately"}
    triggered = [x for x in cohort_rows if x["outcome"] not in ("NO_TRIGGER", "OUT_NO_EFFECT", "UNKNOWN_COHORT")]
    known = [x for x in triggered if x["outcome"] not in UNKNOWN_OUTCOMES]
    m1c = {"numerator": sum(1 for x in known if x["outcome"] in GOOD), "N": len(known),
           "rate": ratio(sum(1 for x in known if x["outcome"] in GOOD), len(known)),
           "coverage_trigger": ratio(len(triggered), len([x for x in cohort_rows if x["outcome"] != "OUT_NO_EFFECT"])),
           "coverage_scorable": ratio(len(known), len([x for x in cohort_rows if x["outcome"] != "OUT_NO_EFFECT"]))}
    # M3: every proposal that reached the guard, judged on its own. Contract 3.2 allows 0..1 verdict per
    # decision_id; more than one distinct verdict (or decision) is a conflict, reported unknown.
    guard = {"accept_correct": 0, "accept_incorrect": 0, "accept_unknown": 0, "true_block": 0, "false_block": 0,
             "unknown_block": 0, "conflicting_verdicts": 0, "proposals_without_verdict": 0}
    for inc in scorer.inc.values():
        verdicts, proposals = {}, {}
        for v in inc.get("guards", []):
            verdicts.setdefault(v["decision_id"], []).append(v["payload"]["verdict"])
        for d in inc["decisions"]:
            if d["payload"]["stage"] == "PROPOSAL" and d["payload"]["response_kind"] == "ACTION":
                proposals.setdefault(d["decision_id"], d)
        conflicted = inc.get("conflicted", set())
        for decision_id, d in sorted(proposals.items()):
            if decision_id not in verdicts:
                guard["proposals_without_verdict"] += 1
                continue
            if ("GUARD_VERDICT", decision_id) in conflicted or ("DECISION", decision_id) in conflicted:
                guard["conflicting_verdicts"] += 1
                continue
            judged = judge(d, inc)
            accepted = verdicts[decision_id][0] == "ACCEPT"
            key = ("accept_" + {"CORRECT": "correct", "INCORRECT": "incorrect"}.get(judged, "unknown")) if accepted else \
                {"CORRECT": "false_block", "INCORRECT": "true_block"}.get(judged, "unknown_block")
            guard[key] += 1
    reached = sum(v for k, v in guard.items() if k != "proposals_without_verdict")
    unscorable = guard["accept_unknown"] + guard["unknown_block"] + guard["conflicting_verdicts"]
    m3 = {"status": "N/A", "reason": "BM has no automatic guard"} if group == "BM" else \
        dict(guard, N=reached, coverage_scorable=ratio(reached - unscorable, reached))
    if group in ("B2", "B3"):
        # Trigger = an observed T_det on an eligible incident, never the cohort label; unknown order is reported.
        labels = {r["incident_id"]: r["label"] for r in results}
        status = {r["incident_id"]: r.get("t_det_status") for r in results}
        eligible = [x for x in rows if labels[x["incident_id"]] != "CONFIRMED_NO_EFFECT"]
        trig = [x for x in eligible if status[x["incident_id"]] == "OBSERVED"]
        fb = [x for x in trig if any(d["payload"]["fallback"] for d in scorer.inc[x["incident_id"]]["decisions"])]
        m4 = {"numerator": len(fb), "N": len(trig), "rate": ratio(len(fb), len(trig)),
              "trigger_unknown": sum(1 for x in eligible if status[x["incident_id"]] == "CLOCK_UNVERIFIED"),
              "recovery_of_fallback": {l: sum(1 for x in fb if labels[x["incident_id"]] == l) for l in sorted({labels[x["incident_id"]] for x in fb})}}
    else:
        m4 = {"status": "N/A", "reason": "fallback exists only in B2/B3"}
    # Executed actions and false actions (an executed action whose proposal was judged INCORRECT).
    actions = {"executed": 0, "terminal": {"SUCCESS": 0, "FAILED": 0, "PARTIAL": 0, "TIMEOUT": 0, "MISSING": 0, "CONFLICT": 0},
               "false_action": 0, "unknown_correctness": 0}
    for inc in scorer.inc.values():
        by_decision = {}
        for d in inc["decisions"]:
            by_decision.setdefault(d["decision_id"], d)
        conflicted = inc.get("conflicted", set())
        for attempt in inc["actions"].values():
            for hs in attempt.get("HEAL_STARTED", []):
                actions["executed"] += 1
                done = attempt.get("ACTION_COMPLETED", [])
                actions["terminal"]["MISSING" if not done else "CONFLICT" if len(done) > 1 else done[0]["payload"]["status"]] += 1
                d = by_decision.get(hs["decision_id"])
                verdict = judge(d, inc) if d and ("DECISION", hs["decision_id"]) not in conflicted else "UNKNOWN_GT"
                if verdict == "INCORRECT":
                    actions["false_action"] += 1
                elif verdict not in GOOD:
                    actions["unknown_correctness"] += 1
    actions["coverage_scorable"] = ratio(actions["executed"] - actions["unknown_correctness"], actions["executed"])
    lat = [x["decision_latency_s"] for x in rows if number(x["decision_latency_s"])]
    m10 = {"values": len(lat), "N_with_decision": sum(1 for x in rows if x["decision_id"]),
           "N_incidents": len(rows), "mean_s": round(sum(lat) / len(lat), 3) if lat else None,
           "no_response": sum(1 for x in rows if x["outcome"] == "NO_RESPONSE"),
           "missing_order": sum(1 for x in rows if x["outcome"] == "MISSING_ORDER"),
           "clock_missing": sum(1 for x in rows if x["decision_id"] and x["decision_latency_s"] is None)}
    return {"rows": rows, "M1": {"pooled_check": rate(cohort_rows), "by_class": classes, "macro_C1_C4": macro},
            "M1c": m1c, "M3": m3, "M4": m4, "M10": m10, "actions": actions, "gt_constraints": GT_CONSTRAINTS}


def funnel(results, decisions):
    outcomes = {x["incident_id"]: x["outcome"] for x in decisions.get("rows", [])}
    return {"requested": len(results),
            "CONFIRMED": sum(1 for r in results if r["effect"] == "CONFIRMED" and r["label"] != "CONFIRMED_NO_EFFECT"),
            "CONFIRMED_NO_EFFECT": sum(1 for r in results if r["label"] == "CONFIRMED_NO_EFFECT"),
            "UNKNOWN_EFFECT": sum(1 for r in results if r["effect"] == "UNKNOWN_EFFECT"),
            "triggered": sum(1 for r in results if r["milestones"]["t_det"] is not None),
            "trigger_unknown": sum(1 for r in results if r.get("t_det_status") == "CLOCK_UNVERIFIED"),
            "valid_response": sum(1 for r in results if outcomes.get(r["incident_id"]) not in (None, "NO_TRIGGER", "NO_RESPONSE", "SCHEMA_INVALID", "UNKNOWN_COHORT", "OUT_NO_EFFECT", "MISSING_ORDER", "DECISION_CONFLICT")),
            "action_success": sum(1 for r in results if r.get("terminal", {}).get("SUCCESS")),
            "recovered": sum(1 for r in results if r["label"] in RECOVERED)}


# --------------------------------------------------------------------------- usage / cost (M11)
LLM_SOURCES = {"decision_llm", "decision_single_llm"}


def unusable(scorer, typ):
    """Envelopes of `typ` kept out of the scored raw (invalid, quarantined, late), once per event_id."""
    out = {}
    for _, event in [(k, e) for k, e in scorer.invalid if isinstance(e, dict)] + scorer.unscored:
        if event.get("event_type") == typ and isinstance(event.get("event_id"), str):
            out.setdefault(event["event_id"], event)
    return list(out.values())


def usage(scorer):
    """Every LLM_CALL counted once by call_id (retries are separate calls); never 0 or COMPLETE for missing.

    Coverage starts from the decisions that needed a model: each LLM decision must have at least one
    valid call record. A missing, invalid, quarantined or conflicting record makes call/usage/cost
    coverage MISSING for the run and the trial/incident/actor it belongs to; sums are then lower bounds.
    """
    calls, conflicts, extra = {}, set(), []
    for event in scorer.of("LLM_CALL"):
        cid = event["call_id"]
        if cid in calls and calls[cid]["event_id"] != event["event_id"]:
            conflicts.add(cid)
            extra.append(event)  # kept to mark the groups it names; never counted as a second call
            continue
        calls[cid] = event
    decisions = [d for d in scorer.of("DECISION") if d["source_component"] in LLM_SOURCES]
    bad_calls = unusable(scorer, "LLM_CALL")
    bad_decisions = [d for d in unusable(scorer, "DECISION") if d.get("source_component") in LLM_SOURCES]
    if scorer.group in ("B0", "B1", "BM") and not calls and not decisions and not bad_calls and not bad_decisions:
        return {"status": "N/A", "reason": f"group {scorer.group} makes no LLM calls"}
    incident_of, call_incidents = {}, {}
    for inc in scorer.inc.values():
        for c in inc["calls"]:
            call_incidents[c["event_id"]] = inc["id"]
        for d in inc["decisions"]:
            incident_of["decision:" + d["decision_id"]] = inc["id"]
    with_call = {c["decision_id"] for c in calls.values()}
    uncovered = [d for d in decisions if d["decision_id"] not in with_call]
    groups = {}

    def bucket(keys):
        for key in keys:
            yield groups.setdefault(key[0], {}).setdefault(str(key[1]), {
                "calls": 0, "retries": 0, "retries_unknown": 0, "input_tokens": 0, "output_tokens": 0, "usage_missing": 0,
                "usd": 0.0, "cost_missing": 0, "price_refs": set(), "invalid_call_records": 0, "decisions_without_call": 0,
                "conflicting_call_records": 0})

    def call_keys(event):
        return [("run", scorer.h.run_id), ("actor", event["source_component"]), ("model", event["payload"]["model"]),
                ("trial", event.get("trial_id")), ("incident", call_incidents.get(event["event_id"], "UNLINKED"))]
    # Every record of a conflicting call_id marks the groups it names (FX01-N1): the call is counted once,
    # but which record is true is unknown, so none of those groups has COMPLETE call coverage.
    for event in [calls[cid] for cid in sorted(conflicts)] + extra:
        for g in bucket(call_keys(event)):
            g["conflicting_call_records"] += 1
    for cid, event in calls.items():
        p = event["payload"]
        for g in bucket(call_keys(event)):
            g["calls"] += 1
            if cid in conflicts:
                g["retries_unknown"] += 1
            else:
                g["retries"] += 1 if p["attempt_no"] > 1 else 0
            if cid in conflicts or p["usage"]["status"] != "COMPLETE":
                g["usage_missing"] += 1
            else:
                g["input_tokens"] += p["usage"]["input_tokens"]
                g["output_tokens"] += p["usage"]["output_tokens"]
            if cid in conflicts or p["cost"]["status"] != "COMPLETE":
                g["cost_missing"] += 1
            else:
                g["usd"] += p["cost"]["usd"]
                g["price_refs"].add(p["cost"]["price_ref"])
    # Unusable records are not counted as provider calls; they only mark the groups they name as incomplete.
    for event in bad_calls:
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        keys = [("run", scorer.h.run_id), ("actor", event.get("source_component")), ("model", payload.get("model")),
                ("trial", event.get("trial_id")),
                ("incident", call_incidents.get(event.get("event_id")) or incident_of.get("decision:" + str(event.get("decision_id")), "UNLINKED"))]
        for g in bucket(keys):
            g["invalid_call_records"] += 1
    for d in uncovered + bad_decisions:
        keys = [("run", scorer.h.run_id), ("actor", d.get("source_component")), ("trial", d.get("trial_id")),
                ("incident", incident_of.get("decision:" + str(d.get("decision_id")), "UNLINKED"))]
        for g in bucket(keys):
            g["decisions_without_call"] += 1
    for level in groups.values():
        for g in level.values():
            g["price_refs"] = sorted(g["price_refs"])
            g["usd"] = round(g["usd"], 6)
            incomplete = g["invalid_call_records"] or g["decisions_without_call"] or g["conflicting_call_records"]
            g["call_coverage_status"] = "MISSING" if incomplete else "COMPLETE"
            g["usage_status"] = "MISSING" if incomplete or g["usage_missing"] else "COMPLETE"
            g["cost_status"] = "MISSING" if incomplete or g["cost_missing"] else "COMPLETE"
            if g["usage_status"] == "MISSING" or g["cost_status"] == "MISSING":
                g["note"] = "sums are lower bounds: some calls or their usage/cost are not known"
    reasons = []
    if uncovered:
        reasons.append(f"{len(uncovered)} LLM decision(s) without a valid LLM_CALL record")
    if bad_decisions:
        reasons.append(f"{len(bad_decisions)} invalid/quarantined LLM decision record(s)")
    if bad_calls:
        reasons.append(f"{len(bad_calls)} invalid/quarantined LLM_CALL record(s)")
    if conflicts:
        reasons.append(f"{len(conflicts)} call_id(s) with conflicting records")
    run = groups.get("run", {}).get(str(scorer.h.run_id), {})
    return {"status": "MISSING" if reasons else "OK", "reasons": reasons, "calls": len(calls),
            "calls_lower_bound": bool(reasons), "raw_call_records": len(scorer.of("LLM_CALL")) + len(bad_calls),
            "call_coverage_status": "MISSING" if reasons else "COMPLETE",
            "usage_status": run.get("usage_status", "MISSING" if reasons else "COMPLETE"),
            "cost_status": run.get("cost_status", "MISSING" if reasons else "COMPLETE"),
            "call_id_conflicts": sorted(conflicts), "llm_decisions": len(decisions),
            "decisions_without_call": sorted(d["decision_id"] for d in uncovered), "by": groups,
            "rule": "one LLM_CALL per call_id, retries included; coverage from LLM decisions; missing stays MISSING"}


# --------------------------------------------------------------------------- benign (M5/M6)
def episode_key(event):
    """ZER-8 5.5 de-dup key: (detector signature, or rule when no signature; target service)."""
    p = event["payload"]
    rule = p.get("signature") if isinstance(p.get("signature"), str) and p["signature"] else p.get("rule_id")
    return str(rule), str((event.get("target") or {}).get("service"))


def benign(scorer, options):
    """M5 slots/episodes and M6 actions on declared C0 windows (ZER-8 5.5).

    Slots: an alert proves a hit; a slot without alert is a no-hit only where detector coverage is
    declared, else unknown. Episodes per hour need the whole alert stream (declared coverage of all of
    W and no unplaceable/invalid alert): otherwise only the observed count, verdict UNKNOWN. M6 counts
    ZERO DOOR actions from HEAL_STARTED in W; a missing terminal or harm evidence is reported, never 0.
    """
    cfg = options.get("benign")
    if not cfg or not cfg.get("trial_ids"):
        return {"status": "MISSING", "reason": "C0 designation not provided (H schedule); FPR never defaults to 0"}
    slot_s, episode_gap_s = cfg.get("slot_s"), cfg.get("episode_gap_s")
    if not (number(slot_s) and slot_s > 0 and number(episode_gap_s) and episode_gap_s >= 0):
        return {"status": "MISSING", "reason": "w_b/g_b not provided (OPEN, ZER-53)"}
    detector_off = scorer.group == "B0" and not scorer.of("DETECTED")
    out = {}
    for trial_id in cfg["trial_ids"]:
        trial = scorer.trial.get(trial_id)
        if not trial or not trial["start"] or not trial["end"] or trial["start"]["payload"].get("warmup_end") is None:
            out[trial_id] = {"status": "INVALID_WINDOW"}
            continue
        model = trial["clock"]
        a = model.at(trial["start"]["clock"]["clock_id"], parse(trial["start"]["payload"]["warmup_end"]))
        b = model.at(trial["end"]["clock"]["clock_id"], parse(trial["end"]["ts_event"]))
        if not a.comparable(b) or b.ms <= a.ms:
            out[trial_id] = {"status": "INVALID_WINDOW"}
            continue
        w0, w1 = a.ms, b.ms
        row = {"W_s": round((w1 - w0) / 1000, 3)}
        if detector_off:
            row["M5"] = {"status": "N/A", "reason": "B0 without detector: no run of the detector is not zero false alarms"}
        else:
            row.update(m5(scorer, trial_id, model, a, w0, w1, slot_s, episode_gap_s, cfg))
        row.update(m6(scorer, trial_id, model, a, w0, w1, cfg))
        out[trial_id] = row
    return {"status": "OK", "trials": out, "slot_s": slot_s, "episode_gap_s": episode_gap_s, "provenance": cfg.get("provenance", "UNSTATED")}


def placed_ms(model, window_start, event):
    """Event time on the window's axis, or None when its clock cannot be compared with the window."""
    t = model.at(event["clock"]["clock_id"], parse(event["ts_event"]))
    return t.ms if t.comparable(window_start) else None


def m5(scorer, trial_id, model, start, w0, w1, slot_s, episode_gap_s, cfg):
    slots = math.ceil((w1 - w0) / (slot_s * 1000))
    coverage = [[parse(x), parse(y)] for x, y in cfg.get("detector_coverage", {}).get(trial_id, [])]
    uncovered = length(subtract([[w0, w1]], coverage))
    inside, unplaced = [], 0
    for event in scorer.of("DETECTED", trial_id):
        t = placed_ms(model, start, event)
        if t is None:
            unplaced += 1
        elif w0 <= t < w1:
            inside.append((t, episode_key(event)))
    invalid = sum(1 for e in unusable(scorer, "DETECTED") if e.get("trial_id") == trial_id)
    hit = {int((t - w0) // (slot_s * 1000)) for t, _ in inside}
    unknown = 0
    for i in range(slots):
        if i in hit:
            continue
        lo, hi = w0 + i * slot_s * 1000, min(w0 + (i + 1) * slot_s * 1000, w1)
        # An alert that cannot be placed (clock) or used (invalid) may be in any slot without a hit.
        if unplaced or invalid or length(subtract([[lo, hi]], coverage)) > 0:
            unknown += 1
    keyed = {}
    for t, key in sorted(inside):
        keyed.setdefault(key, []).append(t)
    episodes = 0
    for times in keyed.values():
        episodes += 1 + sum(1 for x, y in zip(times, times[1:]) if y - x > episode_gap_s * 1000)
    stream_complete = uncovered == 0 and not unplaced and not invalid
    slot_verdict = "OK" if unknown == 0 else "UNKNOWN"
    episode_verdict = "OK" if stream_complete else "UNKNOWN"
    return {"N_slot": slots, "last_slot_s": round(((w1 - w0) - (slots - 1) * slot_s * 1000) / 1000, 3),
            "hit": len(hit), "unknown": unknown, "bounds": [ratio(len(hit), slots), ratio(len(hit) + unknown, slots)],
            "detector_uncovered_s": round(uncovered / 1000, 3), "alerts_unplaced": unplaced, "alerts_invalid": invalid,
            "episode_keys": len(keyed), "episodes_observed": episodes,
            "episodes_per_hour": round(episodes / ((w1 - w0) / 3.6e6), 6) if stream_complete else None,
            "slot_verdict": slot_verdict, "episode_verdict": episode_verdict,
            "verdict": "OK" if slot_verdict == episode_verdict == "OK" else "UNKNOWN",
            "note": "slot rate is not a time rate; never divided by attack counts; observed episodes are not a lower bound"}


def m6(scorer, trial_id, model, start, w0, w1, cfg):
    if scorer.group == "B0":
        return {"M6": {"status": "N/A", "reason": "B0 has no ZERO DOOR action (controller scaling is reported separately)"}}
    starts, unplaced = {}, 0
    for event in scorer.of("HEAL_STARTED", trial_id):
        t = placed_ms(model, start, event)
        if t is None:
            unplaced += 1
        elif w0 <= t < w1:
            starts.setdefault(event["action_id"], []).append(t)
    terminals = {}
    for event in scorer.of("ACTION_COMPLETED", trial_id):
        terminals.setdefault(event["action_id"], []).append(event["payload"]["status"])
    terminal = {"SUCCESS": 0, "FAILED": 0, "PARTIAL": 0, "TIMEOUT": 0, "MISSING": 0, "CONFLICT": 0}
    for action_id in starts:
        found = terminals.get(action_id, [])
        terminal["MISSING" if not found else "CONFLICT" if len(found) > 1 else found[0]] += 1
    invalid = sum(1 for typ in ("HEAL_STARTED", "API_ACCEPTED", "ACTION_COMPLETED")
                  for e in unusable(scorer, typ) if e.get("trial_id") == trial_id)
    log_complete = bool(cfg.get("action_log_complete")) and not unplaced and not invalid
    return {"M6_actions_executed": len(starts), "M6_actions_observed": len(starts), "M6_actions_unplaced": unplaced,
            "M6_invalid_action_records": invalid, "M6_terminal": terminal,
            "M6_terminal_status": "COMPLETE" if not terminal["MISSING"] and not terminal["CONFLICT"] else "MISSING",
            "M6_harm": {"status": "UNKNOWN" if starts else "N/A",
                        "reason": "no benign-impact evidence is joined to actions in the exports" if starts else "no action in W"},
            "M6_action_log_coverage": bool(cfg.get("action_log_complete")),
            "M6_verdict": "OK" if log_complete else "UNKNOWN"}


def containment(scorer, results):
    """M12: CONTAINMENT_VERIFIED on C2/C5 incidents; never inferred from availability."""
    rows = []
    for r in results:
        inc = scorer.inc[r["incident_id"]]
        gt, problems = gt_view(inc)
        cls = None if gt is None or "case_class" in problems else gt["case_class"]
        if cls in ("C2", "C5") and r["label"] != "CONFIRMED_NO_EFFECT":
            rows.append({"incident_id": r["incident_id"], "class": cls, "verified": bool(inc["containment"])})
    if not rows:
        return {"status": "EMPTY", "reason": "no C2/C5 incident with ground truth in this run"}
    k = sum(1 for x in rows if x["verified"])
    return {"status": "OK", "numerator": k, "N": len(rows), "rate": ratio(k, len(rows)),
            "benign_success_rate": {"status": "MISSING", "reason": "benign client request log not in the exports"}}


def run_metrics(scorer, scored, options):
    results = scored["incidents"]
    decisions = decision_metrics(scorer, results)
    flows = options.get("required_flows") or []
    return {
        "kpi": kpi(results, scorer.f01, scored.get("cohort")),
        # A trial known only from its context or incidents (no usable TRIAL_STARTED) stays listed as UNKNOWN.
        "uptime": {trial: uptime(scorer, trial, flows) for trial in sorted(t for t in
            set(scorer.trial) | {e["trial_id"] for e in scorer.of("TRIAL_CONTEXT")} | {i["trial"] for i in scorer.inc.values()}
            if isinstance(t, str))},
        "decisions": decisions,
        "M2_funnel": funnel(results, decisions),
        "M5_M6_benign": benign(scorer, options),
        "M11_usage": usage(scorer),
        "M12_containment": containment(scorer, results),
        "cpu_P179": {"status": "MISSING", "reason": "no container CPU usage/limit series in the H/O exports (ZER-38/44)"},
        "request_success_rate": {"status": "MISSING", "reason": "benign client request log not in the exports"},
    }
