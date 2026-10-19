"""Single-owner append/fsync raw archive; seals and exports are hash checked.

Layout under one plane's root:
  run_<id>/<plane>.jsonl     accepted ingest records; the seal fixes their hash
  run_<id>/rejections.jsonl  quarantine of authenticated input for this run before seal
  run_<id>/manifest.json     seal manifest, written once
  run_<id>/late.jsonl        input for this run after seal (LATE_INGEST or rejection); never
                             added to the sealed raw or its hash
  rejections.jsonl           archive scope: UNSCOPED or unauthenticated input, never attributed
  broker-rejections.jsonl    legacy archive-scope file; read and exported, no new writes
Archives sealed before archive_format 2 (live-11) have no late file or stream counts and
are read and re-sealed unchanged.

Failure is sticky: after a write that raised (bytes may be partly on disk), or a source read that
failed (unreadable, incomplete, edited or unsafe evidence: ArchiveFailure), this process
acknowledges, appends, seals and exports nothing more. Only a restart clears it, and opening the
archive re-verifies every line and refuses an incomplete or edited one; that case needs an
operator, who keeps the bytes. Nothing here truncates or repairs evidence. An export destination
error fails that export only.
"""
import contextlib
import errno
import hashlib
import json
import math
import os
import stat
import threading
import itertools
from pathlib import Path

from .contract import canonical, new_id, now, valid_id, validate

FORMAT = 2
GLOBAL_FILES = ("rejections.jsonl", "broker-rejections.jsonl")
# Live-11 envelopes nest 4 levels. The contract validator and the audit walk values recursively,
# so deeper input is INVALID before any recursive step and is kept as bytes, never parsed back.
MAX_DEPTH = 32


class ArchiveFailure(ValueError):
    """Corrupt or unsafe evidence. Never acknowledged as a handled rejection."""


class Rejected(ValueError):
    """Input durably quarantined under `classification`; acknowledging it is safe."""
    def __init__(self, classification, sealed=False):
        super().__init__(("RUN_SEALED:" if sealed else "") + classification)
        self.classification, self.sealed = classification, sealed


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fsync_dir(path):
    # Windows cannot open a directory for fsync; that power-loss limit is declared in the runbook.
    if os.name == "nt":
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextlib.contextmanager
def reading():
    """Archive (source) side reads: an OSError is unreadable evidence, never 'absent' or 'empty'.

    Export destination errors are deliberately not wrapped: they fail that export only.
    """
    try:
        yield
    except OSError as error:
        raise ArchiveFailure("archive unreadable: " + type(error).__name__) from error


def entry(path):
    """lstat of an archive path, or None when it does not exist. Path.exists() hides some errors
    (all of them from Python 3.13), which would turn an unreadable sealed run into an open one."""
    try:
        return os.lstat(path)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise ArchiveFailure("archive unreadable: " + type(error).__name__) from error


def _finite(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("non-finite number")
    return value


def _constant(_name):
    raise ValueError("non-finite number")


def too_deep(value, limit=MAX_DEPTH):
    """Iterative container depth check, safe for any nesting the JSON decoder accepted."""
    stack = [(value, 1)]
    while stack:
        item, level = stack.pop()
        if isinstance(item, dict):
            children = item.values()
        elif isinstance(item, (list, tuple)):
            children = item
        else:
            continue
        if level > limit:
            return True
        stack.extend((child, level + 1) for child in children)
    return False


def render(event):
    """Bytes for a rejected in-process object that came without original bytes. Never raises."""
    encoders = (("canonical", canonical), ("python-repr", lambda v: repr(v).encode("utf-8", "backslashreplace")))
    for kind, encode in encoders:
        try:
            return encode(event), kind
        except (TypeError, ValueError, RecursionError):
            pass
    return b"", "unrepresentable"


def decode(raw):
    """Strict UTF-8 JSON object, no NaN/Infinity. Returns (event, None) or (None, classification)."""
    try:
        value = json.loads(raw.decode("utf-8"), parse_float=_finite, parse_constant=_constant)
    except (AttributeError, UnicodeDecodeError, ValueError, RecursionError):
        return None, "INVALID"
    if not isinstance(value, dict):
        return None, "INVALID"
    return value, None


def check_record(record, legacy=False):
    """Each quarantine/raw line carries its own hash; editing a line must be detectable.

    `legacy` admits the pre-format-2 broker-rejections lines, which only had raw_hex.
    """
    if "envelope" in record:
        if record.get("envelope_sha256") != sha(canonical(record["envelope"])):
            raise ArchiveFailure("archive hash mismatch")
    elif legacy and "raw_sha256" not in record and "raw_hex" in record:
        return
    elif record.get("raw_sha256") != sha(bytes.fromhex(record.get("raw_hex", ""))):
        raise ArchiveFailure("archive hash mismatch")


class Archive:
    def __init__(self, root, plane):
        if plane not in {"H", "O", "S"}:
            raise ValueError("invalid plane")
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.plane = plane
        self.lock = threading.RLock()
        self.failure = None
        self.owner = open(self.root / ".owner", "a+b")
        try:
            self.owner.seek(0)
            if os.name == "nt":
                import msvcrt
                if self.owner.read(1) == b"":
                    self.owner.write(b"0")
                    self.owner.flush()
                self.owner.seek(0)
                msvcrt.locking(self.owner.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.owner.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.ids, self.late_ids, self.contexts = {}, {}, {}
            for name in GLOBAL_FILES:
                for record in self.iter_file(self.root / name):
                    check_record(record, legacy=name == "broker-rejections.jsonl")
            for directory in self.root.glob("run_*"):
                if not directory.is_dir() or directory.is_symlink():
                    continue
                path = directory / (plane + ".jsonl")
                sealed = directory / "manifest.json"
                if entry(sealed) is not None:
                    saved = json.loads(sealed.read_bytes())
                    if file_sha(path) != saved["sha256"]:
                        raise ArchiveFailure("sealed archive changed")
                    rejected = saved.get("rejections")
                    if rejected and file_sha(directory / "rejections.jsonl") != rejected["sha256"]:
                        raise ArchiveFailure("sealed rejections changed")
                for record in self.iter_file(path):
                    check_record(record)
                    event = record["envelope"]
                    digest = record["envelope_sha256"]
                    if event["event_id"] in self.ids and self.ids[event["event_id"]] != digest:
                        raise ArchiveFailure("archive event conflict")
                    self.ids[event["event_id"]] = digest
                    self.index(event)
                for record in self.iter_file(directory / "rejections.jsonl"):
                    check_record(record)
                for record in self.iter_file(directory / "late.jsonl"):
                    check_record(record)
                    if record["classification"] == "LATE_INGEST":
                        self.late_ids[record["envelope"]["event_id"]] = record["envelope_sha256"]
        except BaseException:
            self.owner.close()
            raise

    def close(self):
        self.owner.close()

    def usable(self):
        if self.failure:
            raise ArchiveFailure("ARCHIVE_FAILED:" + self.failure)

    def fail(self, error):
        """Make the failure sticky (see module doc) and return the error to raise."""
        with self.lock:
            if self.failure is None:
                if isinstance(error, ArchiveFailure) and isinstance(error.__cause__, OSError):
                    error = error.__cause__  # unreadable source: name the I/O error, as a failed write does
                self.failure = "INTEGRITY" if isinstance(error, ArchiveFailure) else type(error).__name__
        return ArchiveFailure("ARCHIVE_FAILED:" + self.failure)

    def lookup(self, path):
        """entry() for checks made under the lock outside a guarded operation: unreadable stops the archive."""
        try:
            return entry(path)
        except ArchiveFailure as error:
            raise self.fail(error) from error

    def write(self, path, record):
        """Append; any exception may have left partial bytes, so it stops this archive."""
        self.usable()
        try:
            self.append(path, record)
        except Exception as error:
            raise self.fail(error) from error

    def path(self, run):
        if not valid_id(run, "run"):
            raise ValueError("invalid run")
        path = self.root / run
        try:
            with reading():
                found = entry(path)
                # No caller-controlled paths or symlink escapes, including export source.
                if found and stat.S_ISLNK(found.st_mode) or path.resolve().parent != self.root:
                    raise ArchiveFailure("unsafe archive path")
        except ArchiveFailure as error:
            raise self.fail(error) from error
        return path

    def run_dir(self, run):
        directory = self.path(run)
        try:
            if entry(directory) is None:
                directory.mkdir(mode=0o700)
                fsync_dir(self.root)
        except (ArchiveFailure, OSError) as error:
            raise self.fail(error) from error
        return directory

    def sealed(self, run):
        with self.lock:
            return self.lookup(self.path(run) / "manifest.json") is not None

    def index(self, event):
        # Binding reads the first stored context; later differing copies are rejected before storage.
        if event["event_type"] == "RUN_CONTEXT":
            self.contexts.setdefault(event["run_id"], {}).setdefault("run", event)
        elif event["event_type"] == "TRIAL_CONTEXT":
            self.contexts.setdefault(event["run_id"], {}).setdefault("trials", {}).setdefault(event["trial_id"], event)

    def context(self, run, trial=None):
        found = self.contexts.get(run, {})
        return found.get("run") if trial is None else found.get("trials", {}).get(trial)

    @staticmethod
    def iter_file(path):
        """Every archive file read goes through here: absent is empty, unreadable is ArchiveFailure."""
        with reading():
            found = entry(path)
            if found is None:
                return
            if stat.S_ISLNK(found.st_mode):
                raise ArchiveFailure("unsafe archive file")
            with open(path, "rb") as handle:
                for line in handle:
                    # Never silently truncate evidence after an interrupted append.
                    if not line.endswith(b"\n"):
                        raise ArchiveFailure("incomplete raw record; operator recovery required")
                    try:
                        record = json.loads(line)
                    except (ValueError, RecursionError):
                        raise ArchiveFailure("corrupt raw record; operator recovery required") from None
                    if not isinstance(record, dict):
                        raise ArchiveFailure("corrupt raw record; operator recovery required")
                    yield record

    @staticmethod
    def read_file(path):
        return list(Archive.iter_file(path))

    @staticmethod
    def append(path, record):
        found = entry(path)
        if found and stat.S_ISLNK(found.st_mode):
            raise ArchiveFailure("unsafe archive file")
        created = found is None
        with open(path, "ab") as handle:
            handle.write(canonical(record) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        if created:
            fsync_dir(path.parent)

    def reject(self, classification, transport, principal, event=None, raw=None, attributable=True):
        """The single quarantine path. Stores, then raises Rejected; never returns.

        Only authenticated input is attributed to the run it names. Input that cannot be
        canonicalized keeps its original bytes. Nothing here is reachable from the O read API.
        """
        with self.lock:
            self.usable()
            record = {"ingest_id": new_id("ing"), "ts_ingest": now(), "transport": transport,
                      "classification": classification, "principal": principal}
            stored = None
            # Too-deep input is kept only as bytes: a parsed copy would be unsafe to re-walk on open.
            if isinstance(event, dict) and not too_deep(event):
                try:
                    record.update(envelope_sha256=sha(canonical(event)), envelope=event)
                    stored = event
                except (TypeError, ValueError, RecursionError):
                    pass
            if stored is None and isinstance(event, dict) and raw is None:
                raw, record["raw_kind"] = render(event)
            if stored is None:
                raw = raw if isinstance(raw, bytes) else b""
                record.update(raw_sha256=sha(raw), raw_hex=raw.hex())
            run = event.get("run_id") if attributable and isinstance(event, dict) else None
            sealed = False
            if valid_id(run, "run"):
                directory = self.run_dir(run)
                sealed = self.lookup(directory / "manifest.json") is not None
                path = directory / ("late.jsonl" if sealed else "rejections.jsonl")
            else:
                path = self.root / "rejections.jsonl"
            self.write(path, record)
            if sealed and classification == "LATE_INGEST":
                self.late_ids[stored["event_id"]] = record["envelope_sha256"]
        raise Rejected(classification, sealed)

    def ingest(self, event, transport, source):
        """Rejects stay private; valid duplicates retain every ingest receipt before seal."""
        with self.lock:
            self.usable()
            error = ("INVALID" if too_deep(event) else None) or validate(event, self.plane, source)
            if error:
                self.reject(error, transport, source, event=event)
            digest = sha(canonical(event))
            event_id = event["event_id"]
            directory = self.run_dir(event["run_id"])
            known = self.ids.get(event_id)
            if self.lookup(directory / "manifest.json") is not None:
                # An exact copy of sealed raw (Kafka redelivery) or of a stored late record
                # changes nothing; anything else after seal is kept outside the sealed hash.
                if known == digest:
                    return {"status": "SEALED_DUPLICATE", "event_id": event_id}
                late = self.late_ids.get(event_id)
                if late == digest:
                    raise Rejected("LATE_INGEST", sealed=True)
                conflict = (known or late) not in {None, digest}
                self.reject("INTEGRITY_ERROR" if conflict else "LATE_INGEST", transport, source, event=event)
            if known not in {None, digest}:
                self.reject("INTEGRITY_ERROR", transport, source, event=event)
            record = {"ingest_id": new_id("ing"), "ts_ingest": now(), "transport": transport,
                      "envelope_sha256": digest, "envelope": event}
            self.write(directory / (self.plane + ".jsonl"), record)
            self.ids[event_id] = digest
            self.index(event)
            return {"status": "DUPLICATE" if known else "RECORDED", "event_id": event_id,
                    "envelope_sha256": digest}

    def records(self, run, after=0, limit=None):
        with self.lock:
            self.usable()
            path = self.path(run) / (self.plane + ".jsonl")
            try:
                # iter_file turns an open/read error into ArchiveFailure: GET /events answers 503.
                return list(itertools.islice(self.iter_file(path), after, after + limit if limit is not None else None))
            except ArchiveFailure as error:
                raise self.fail(error) from error

    @staticmethod
    def summary(path):
        lines = 0
        for record in Archive.iter_file(path):
            check_record(record, legacy=path.name == "broker-rejections.jsonl")
            lines += 1
        with reading():
            return {"file": path.name, "lines": lines, "bytes": path.stat().st_size, "sha256": file_sha(path)}

    def manifest(self, run):
        path = self.path(run) / (self.plane + ".jsonl")
        sequences, counts = {}, {}
        count, first, last, versions = 0, None, None, set()
        for record in self.iter_file(path):
            count += 1
            first = min(first, record["ts_ingest"]) if first else record["ts_ingest"]
            last = max(last, record["ts_ingest"]) if last else record["ts_ingest"]
            event = record["envelope"]
            versions.add(event["schema_version"])
            key = event["source_instance"] + "/" + event["stream"]
            seq = sequences.setdefault(key, {"first": event["seq"], "last": event["seq"]})
            seq["first"] = min(seq["first"], event["seq"])
            seq["last"] = max(seq["last"], event["seq"])
            counts.setdefault(key, set()).add(event["seq"])
        rejected_path = path.parent / "rejections.jsonl"
        rejected = {"file": rejected_path.name, "lines": sum(1 for _ in self.iter_file(rejected_path)),
                    "sha256": file_sha(rejected_path)} if entry(rejected_path) is not None else None
        # Distinct seq per stream lets SEQ_GAP be seen from the manifest: gap if count < last-first+1.
        return {"run_id": run, "plane": self.plane, "raw_file": path.name, "lines": count, "rejections": rejected,
                "sha256": file_sha(path), "bytes": path.stat().st_size, "sequences": sequences,
                "first_ingest": first, "last_ingest": last, "schema_versions": sorted(versions),
                "archive_format": FORMAT, "stream_seq_counts": {k: len(v) for k, v in counts.items()}}

    def seal(self, run):
        with self.lock:
            self.usable()
            directory = self.path(run)
            found = self.lookup(directory)
            if found is None or not stat.S_ISDIR(found.st_mode):
                raise ValueError("UNKNOWN_RUN")
            try:
                return self._seal(run, directory)
            except (ArchiveFailure, OSError, ValueError, KeyError, TypeError) as error:
                # Everything after the run check reads or writes evidence: unreadable is a failure.
                raise self.fail(error) from error

    def _seal(self, run, directory):
        raw = directory / (self.plane + ".jsonl")
        if entry(raw) is None:
            # A run holding only rejections still seals, with an explicit empty raw file.
            with open(raw, "xb") as handle:
                os.fsync(handle.fileno())
            fsync_dir(directory)
        result = self.manifest(run)
        path = directory / "manifest.json"
        if entry(path) is not None:
            saved = json.loads(path.read_bytes())
            # Older seals lack newer fields; compare exactly the fields they recorded.
            if {key: result.get(key) for key in saved} != saved:
                raise ArchiveFailure("sealed archive changed")
            return saved
        with open(path, "xb") as handle:
            handle.write(canonical(result) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        fsync_dir(directory)
        return result

    def export(self, run, destination):
        """Evaluator-only CLI operation, deliberately absent from the O HTTP API.

        Holds the archive lock so the snapshot is consistent with concurrent appends, copies into a
        NEW directory, rechecks every copied file and describes it in export.json. An export is
        complete only if this call returned. Source reads raise ArchiveFailure and stop the archive;
        anything on the destination side raises OSError and fails this export only.
        """
        with self.lock:
            try:
                return self._export(run, destination)
            except ArchiveFailure as error:
                raise self.fail(error) from error

    def _export(self, run, destination):
        manifest = self.seal(run)
        source = self.path(run)
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=False)
        files = {}

        def copy(path, name):
            if path.suffix == ".jsonl":
                before = self.summary(path)
            else:
                with reading():
                    before = {"file": path.name, "bytes": path.stat().st_size, "sha256": file_sha(path)}
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            with reading():
                handle = open(path, "rb")
            with handle, open(target, "xb") as out:
                while True:
                    with reading():
                        chunk = handle.read(1024 * 1024)
                    if not chunk:
                        break
                    digest.update(chunk)
                    out.write(chunk)
            if digest.hexdigest() != before["sha256"]:
                raise ArchiveFailure("archive changed during export")
            if file_sha(target) != before["sha256"]:
                raise OSError(errno.EIO, "export copy differs from the archive", str(target))
            files[name] = dict(before, file=name)
            return before

        raw = copy(source / manifest["raw_file"], manifest["raw_file"])
        copy(source / "manifest.json", "manifest.json")
        if raw["sha256"] != manifest["sha256"]:
            raise ArchiveFailure("export hash mismatch")
        if manifest["rejections"]:
            if copy(source / "rejections.jsonl", "rejections.jsonl")["sha256"] != manifest["rejections"]["sha256"]:
                raise ArchiveFailure("export rejections hash mismatch")
        late = copy(source / "late.jsonl", "late.jsonl") if entry(source / "late.jsonl") is not None else None
        scoped = {name: copy(self.root / name, "archive-scope/" + name)
                  for name in GLOBAL_FILES if entry(self.root / name) is not None}
        described = {"export_format": "zd-export/2", "run_id": run, "plane": self.plane, "exported_at": now(),
                     "seal": manifest, "files": files,
                     "late": dict(late, note="arrived after seal; outside the sealed hash") if late else None,
                     "archive_scope_quarantine": {"scope": "ARCHIVE_GLOBAL_NOT_ATTRIBUTED_TO_RUN",
                                                  "files": scoped}}
        with open(destination / "export.json", "xb") as handle:
            handle.write(canonical(described) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        for path in destination.rglob("*"):
            if path.is_file():
                path.chmod(0o444)
        return manifest
