"""Probe clock, CLOCK_SYNC measurement and the scorer's clock normalization (contract 4.1-4.3).

Timestamps are epoch milliseconds internally and `YYYY-MM-DDTHH:MM:SS.mmmZ` (floor) on the wire.
Milliseconds are the storage unit, not the accuracy: every clock reports its real resolution.
"""
import bisect
import json
import math
import re
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

STAMP = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def stamp(ms):
    """Floor to the millisecond, as the contract requires; never rounds up."""
    whole = math.floor(ms)
    return (EPOCH + timedelta(milliseconds=whole)).strftime("%Y-%m-%dT%H:%M:%S.") + f"{whole % 1000:03d}Z"


def parse(text):
    """Strict contract timestamp -> integer epoch ms. Anything else raises ValueError."""
    if not isinstance(text, str) or not STAMP.fullmatch(text):
        raise ValueError("invalid timestamp")
    value = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    return (value - EPOCH) // timedelta(milliseconds=1)


def observed_step_ms(read, limit=2000):
    """Smallest positive step seen while spinning on `read` (seconds): coarse clocks show 15.6 ms on Windows."""
    steps, last = [], read()
    for _ in range(limit):
        value = read()
        if value != last:
            steps.append(value - last)
            last = value
            if len(steps) >= 5:
                break
    return min(steps) * 1000 if steps else None


class ProbeClock:
    """UTC readings for t_start plus a monotonic counter for elapsed time and deadlines.

    HOST_SHARED probes read the wall clock (the contract treats the host kernel clock as the
    reference). OFF_HOST/UNKNOWN probes anchor the wall clock once and advance it monotonically, so a
    wall step mid-trial cannot reorder samples; CLOCK_SYNC measures that same clock.
    """
    def __init__(self, clock_id, clock_source, wall=time.time, counter=time.perf_counter_ns):
        self.clock_id, self.clock_source = clock_id, clock_source
        self.wall, self.counter = wall, counter
        self.anchor_ms, self.anchor_ns = wall() * 1000, counter()
        info = time.get_clock_info("time" if clock_source == "HOST_SHARED" else "perf_counter").resolution * 1000
        seen = observed_step_ms(wall) if clock_source == "HOST_SHARED" else None
        # One millisecond is the floor of the wire format itself.
        self.resolution_ms = round(max(1.0, info, seen or 0.0), 3)

    def now_ms(self):
        if self.clock_source == "HOST_SHARED":
            return self.wall() * 1000
        return self.anchor_ms + (self.counter() - self.anchor_ns) / 1e6

    def envelope(self):
        return {"clock_id": self.clock_id, "clock_source": self.clock_source, "resolution_ms": self.resolution_ms}


class HttpReference:
    """Reference clock endpoint answering {"clock_id", "utc_ms", "resolution_ms"} (proposal; not in the lab yet)."""
    def __init__(self, url, timeout_s=2.0):
        if urlsplit(url).scheme not in {"http", "https"}:
            raise ValueError("reference clock URL must be http(s)")
        self.url, self.timeout_s = url, timeout_s

    def read(self):
        request = Request(self.url, headers={"Accept": "application/json"})
        # The scheme is restricted to http(s) in __init__ (Bandit B310).
        with urlopen(request, timeout=self.timeout_s) as response:  # nosec B310
            value = json.loads(response.read(4096))
        if not all(k in value for k in ("clock_id", "utc_ms", "resolution_ms")) or \
                not all(type(value[k]) in (int, float) and math.isfinite(value[k]) for k in ("utc_ms", "resolution_ms")):
            raise ValueError("reference answer is not a clock reading")
        return value


def cristian(clock, reference, method="cristian-http/0"):
    """One offset measurement: offset = midpoint(local send, local receive) - reference reading.

    uncertainty = half the round trip + both resolutions. The method is OPEN (ZER-38/F-01); it is
    recorded with every CLOCK_SYNC so a later protocol can reject it.
    """
    t1 = clock.now_ms()
    answer = reference.read()
    t4 = clock.now_ms()
    offset = (t1 + t4) / 2 - answer["utc_ms"]
    return {"clock_id": clock.clock_id, "reference_clock_id": answer["clock_id"],
            "offset_ms": round(offset, 3),
            "uncertainty_ms": round((t4 - t1) / 2 + answer["resolution_ms"] + clock.resolution_ms, 3),
            "method": method, "measured_at": stamp(answer["utc_ms"])}


class ClockModel:
    """Scorer-side normalization of one trial's clocks onto the reference clock (contract 4.3).

    A clock is verified for a trial when it has CLOCK_SYNC at or before TRIAL_STARTED and at or after
    TRIAL_ENDED, every measurement has an uncertainty, and its resolution is known. HOST_SHARED clocks
    are the reference (offset 0). Nothing is inferred: unverified clocks keep local readings and every
    comparison across them is refused.
    """
    def __init__(self, reference_clock_id, trial_start, trial_end):
        self.reference = reference_clock_id
        self.trial_start, self.trial_end = trial_start, trial_end
        self.meta, self.syncs = {}, {}

    def see(self, clock):
        """Record a clock from an event envelope; conflicting descriptions make it unusable."""
        known = self.meta.get(clock["clock_id"])
        if known is None:
            self.meta[clock["clock_id"]] = dict(clock)
        elif known.get("clock_source") != clock.get("clock_source") or known.get("resolution_ms") != clock.get("resolution_ms"):
            known["conflict"] = True

    def sync(self, payload):
        self.syncs.setdefault(payload["clock_id"], []).append(payload)

    def state(self, clock_id):
        """(verified, reasons). Reasons explain CLOCK_UNVERIFIED; empty when verified."""
        meta = self.meta.get(clock_id)
        if meta is None:
            return False, ["UNKNOWN_CLOCK"]
        if meta.get("conflict"):
            return False, ["CLOCK_DESCRIPTION_CONFLICT"]
        if meta.get("clock_source") == "HOST_SHARED" or clock_id == self.reference:
            return True, []
        reasons = []
        syncs = self.syncs.get(clock_id, [])
        if meta.get("resolution_ms") is None:
            reasons.append("RESOLUTION_UNKNOWN")
        if any(s["reference_clock_id"] != self.reference for s in syncs):
            reasons.append("SYNC_WRONG_REFERENCE")
        if any(s.get("uncertainty_ms") is None for s in syncs):
            reasons.append("SYNC_UNCERTAINTY_MISSING")
        times = [parse(s["measured_at"]) for s in syncs]
        if self.trial_start is None or not any(t <= self.trial_start for t in times):
            reasons.append("NO_SYNC_AT_TRIAL_START")
        if self.trial_end is None or not any(t >= self.trial_end for t in times):
            reasons.append("NO_SYNC_AT_TRIAL_END")
        return not reasons, reasons

    def error_ms(self, clock_id):
        meta = self.meta.get(clock_id, {})
        resolution = meta.get("resolution_ms")
        if meta.get("clock_source") == "HOST_SHARED" or clock_id == self.reference:
            return resolution
        unc = [s["uncertainty_ms"] for s in self.syncs.get(clock_id, [])]
        if resolution is None or not unc or any(u is None for u in unc):
            return None
        return max(unc) + resolution

    def offset(self, clock_id, local_ms):
        """Linear interpolation on the clock's own axis (measured_at + offset); nearest outside."""
        points = sorted((parse(s["measured_at"]) + s["offset_ms"], s["offset_ms"]) for s in self.syncs[clock_id])
        axes = [p[0] for p in points]
        i = bisect.bisect_left(axes, local_ms)
        if i == 0:
            return points[0][1]
        if i == len(points):
            return points[-1][1]
        (a, oa), (b, ob) = points[i - 1], points[i]
        return oa if b == a else oa + (ob - oa) * (local_ms - a) / (b - a)

    def at(self, clock_id, local_ms):
        """Milestone object: value on the reference axis when verified, else the local reading."""
        verified, _ = self.state(clock_id)
        resolution = self.meta.get(clock_id, {}).get("resolution_ms")
        if not verified:
            return Instant(local_ms, clock_id, False, None, resolution)
        if self.meta[clock_id].get("clock_source") == "HOST_SHARED" or clock_id == self.reference:
            return Instant(local_ms, clock_id, True, self.error_ms(clock_id), resolution)
        return Instant(local_ms - self.offset(clock_id, local_ms), clock_id, True, self.error_ms(clock_id), resolution)

    def to_local(self, clock_id, reference_ms):
        """Inverse of `at` for a verified clock (fixed point; offsets change slowly)."""
        local = reference_ms
        for _ in range(8):
            local = reference_ms + self.offset(clock_id, local)
        return local


class Instant:
    """A milestone: `ms` on the reference axis if verified, else the local reading of `clock_id`."""
    __slots__ = ("ms", "clock_id", "verified", "error_ms", "resolution_ms")

    def __init__(self, ms, clock_id, verified, error_ms, resolution_ms=None):
        self.ms, self.clock_id, self.verified, self.error_ms = ms, clock_id, verified, error_ms
        self.resolution_ms = resolution_ms

    def comparable(self, other):
        return self.clock_id == other.clock_id or (self.verified and other.verified)

    def __repr__(self):
        return f"Instant({stamp(self.ms)}, {self.clock_id}, verified={self.verified})"


def duration(a, b):
    """b - a in ms with its uncertainty, or None when the two clocks cannot be compared.

    Same clock: offsets cancel; uncertainty is 2 x resolution. Across clocks: sum of both errors.
    """
    if a is None or b is None or not a.comparable(b):
        return None
    if a.clock_id == b.clock_id:
        res = a.resolution_ms
        return b.ms - a.ms, (None if res is None else res * 2)
    if a.error_ms is None or b.error_ms is None:
        return b.ms - a.ms, None
    return b.ms - a.ms, a.error_ms + b.error_ms
