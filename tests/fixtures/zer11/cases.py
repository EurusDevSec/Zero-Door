"""SYNTHETIC ZER-11 cases built with the locked ZER-10 trace builder (tests/fixtures/zer10/builder.py).

Each case is a raw trace that goes through the real ZER-9 Archive seal/export and the ZER-10 scorer
CLI; the dashboard then reads the CLI's output. Hand-computed expectations are in expected.json and
are derived from the timeline below (contract 10.1 E01), not from the scorer:
effect 101, detect 131, decision 133, action SUCCESS 150, T_rec 191, stop 240, trial 10-300.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/fixtures/zer10"))
from builder import F01, Trace  # noqa: E402

RECOVERS = [(20, 100, True), (101, 188, False), (189, 260, True)]
NEVER = [(20, 100, True), (101, 260, False)]


def base(group, pattern=RECOVERS, syncs=((10, None, 20), (300, None, 20)), f01=F01):
    tr = Trace(group, f01=f01)
    tr.run_started()
    tr.ground_truth()
    tr.trial_started()
    tr.manifest()
    for t, off, unc in syncs:
        tr.sync(t, off, unc)
    tr.probe_run(pattern)
    return tr


def finish(tr, rv=True, stop=240):
    tr.effect()
    if rv:
        tr.recovery_verified(222, 191, 189, 221)
    if stop is not None:
        tr.stop(stop)
    tr.trial_ended()
    return tr


def b1_recovered():
    """RULES: detect 131, RULES decision 133, guard ACCEPT, SUCCESS 150, verified recovery 191."""
    tr = base("B1")
    tr.attack()
    alert = tr.detected(131)
    dec = tr.decision(133, alert, received=131.4)
    tr.guard(133.1, dec)
    tr.action(dec)
    return finish(tr)


def bm_manual():
    """MANUAL: the operator's decision is the action's source (initiator OPERATOR)."""
    tr = base("BM")
    tr.attack()
    alert = tr.detected(131)
    dec = tr.decision(133, alert, received=131.4)
    tr.action(dec)
    return finish(tr)


def bm_autoheal():
    """MANUAL with an automatic RULES decision behind the action: auto-heal in BM (MODE_VIOLATION)."""
    tr = base("BM")
    tr.attack()
    alert = tr.detected(131)
    dec = tr.decision(133, alert, received=131.4, source="decision_rules")
    tr.action(dec)
    return finish(tr)


def b0_controller():
    """K8S_BASELINE: no ZERO DOOR detector, decision or action; the probe still sees the recovery."""
    tr = base("B0")
    tr.attack()
    return finish(tr)


def b0_with_decision():
    """B0 with a ZERO DOOR decision and action: forbidden by contract 7.4 (MODE_VIOLATION)."""
    tr = base("B0")
    tr.attack()
    alert = tr.detected(131)
    dec = tr.decision(133, alert, received=131.4, source="decision_rules")
    tr.action(dec)
    return finish(tr)


def b1_failed_timeout():
    """RULES action FAILED and no recovery while the probe covers T_eff + cap_rec (cap_rec 120 s): TIMEOUT."""
    tr = base("B1", pattern=NEVER, f01=dict(F01, cap_rec_s=120))
    tr.attack()
    alert = tr.detected(131)
    dec = tr.decision(133, alert, received=131.4)
    tr.guard(133.1, dec)
    tr.action(dec, status="FAILED")
    return finish(tr, rv=False)


def b1_clock_unverified():
    """Probe clock without CLOCK_SYNC: cross-clock milestones are refused (MISSING, CLOCK_UNVERIFIED)."""
    tr = base("B1", syncs=())
    tr.attack()
    alert = tr.detected(131)
    dec = tr.decision(133, alert, received=131.4)
    tr.guard(133.1, dec)
    tr.action(dec)
    return finish(tr)


def b1_empty():
    """A trial without any attack: no incident, KPI EMPTY (never PASS, never 0)."""
    tr = base("B1", pattern=[(20, 260, True)])
    tr.trial_ended()
    return tr


CASES = {name: fn for name, fn in globals().items() if callable(fn) and fn.__module__ == __name__
         and name not in {"base", "finish"}}
