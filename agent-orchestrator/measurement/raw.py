"""Read sealed H/O exports (event_pipeline Archive.export) and verify them before any scoring.

An export is accepted only if export.json, the seal, every copied file and every line hash agree.
Any mismatch raises RawError and nothing is scored. Raw bytes are never modified. Quarantined,
late and archive-scope records are surfaced as evidence, never silently merged into raw.
"""
import hashlib
import json
from pathlib import Path

from event_pipeline.contract import canonical

EXPORT_FORMAT = "zd-export/2"


class RawError(ValueError):
    """The export cannot be trusted as raw evidence."""


def file_sha(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lines(path):
    with open(path, "rb") as handle:
        for number, line in enumerate(handle, 1):
            if not line.endswith(b"\n"):
                raise RawError(f"{path.name}:{number} truncated record")
            try:
                record = json.loads(line)
            except ValueError:
                raise RawError(f"{path.name}:{number} corrupt record") from None
            if not isinstance(record, dict):
                raise RawError(f"{path.name}:{number} corrupt record")
            yield number, record


def line_hash_ok(record):
    if "envelope" in record:
        return record.get("envelope_sha256") == hashlib.sha256(canonical(record["envelope"])).hexdigest()
    if "raw_hex" in record:
        try:
            raw = bytes.fromhex(record["raw_hex"])
        except (TypeError, ValueError):
            return False
        return "raw_sha256" not in record or record["raw_sha256"] == hashlib.sha256(raw).hexdigest()
    return False


class Export:
    """One verified plane export: raw records, quarantine, late and archive-scope records."""
    def __init__(self, directory, plane):
        self.dir = Path(directory)
        meta_path = self.dir / "export.json"
        if not meta_path.is_file():
            raise RawError(f"{plane}: export.json missing (not a sealed export)")
        self.meta_sha256 = file_sha(meta_path)
        try:
            meta = json.loads(meta_path.read_bytes())
        except ValueError:
            raise RawError(f"{plane}: export.json corrupt") from None
        if meta.get("export_format") != EXPORT_FORMAT or meta.get("plane") != plane:
            raise RawError(f"{plane}: unsupported export or wrong plane")
        self.plane, self.run_id, self.meta = plane, meta.get("run_id"), meta
        seal = meta.get("seal") or {}
        files = meta.get("files") or {}
        for name, info in files.items():
            self.check_file(name, info)
        try:
            manifest = json.loads((self.dir / "manifest.json").read_bytes())
        except (OSError, ValueError):
            raise RawError(f"{plane}: manifest.json unreadable") from None
        if manifest != seal or seal.get("run_id") != self.run_id or seal.get("plane") != plane:
            raise RawError(f"{plane}: seal differs from export.json")
        raw_name = seal.get("raw_file")
        if raw_name not in files or files[raw_name].get("sha256") != seal.get("sha256"):
            raise RawError(f"{plane}: raw hash differs from the seal")
        self.records = self.read(raw_name, expect_lines=seal.get("lines"), envelope_only=True)
        rejected = seal.get("rejections")
        self.rejections = []
        if rejected:
            if files.get("rejections.jsonl", {}).get("sha256") != rejected.get("sha256"):
                raise RawError(f"{plane}: rejections hash differs from the seal")
            self.rejections = self.read("rejections.jsonl", expect_lines=rejected.get("lines"))
        self.late = self.read("late.jsonl") if meta.get("late") else []
        if meta.get("late") and files.get("late.jsonl", {}).get("sha256") != meta["late"].get("sha256"):
            raise RawError(f"{plane}: late file hash differs")
        scope = (meta.get("archive_scope_quarantine") or {}).get("files") or {}
        self.archive_scope = []
        for name, info in scope.items():
            self.check_file("archive-scope/" + name, info)
            self.archive_scope += self.read("archive-scope/" + name, legacy=name == "broker-rejections.jsonl")
        for record in self.records:
            if record["envelope"].get("run_id") != self.run_id:
                raise RawError(f"{plane}: raw record of another run")

    def check_file(self, name, info):
        path = self.dir / name
        if not path.is_file() or path.is_symlink():
            raise RawError(f"{self.plane}: {name} missing")
        if file_sha(path) != info.get("sha256") or path.stat().st_size != info.get("bytes"):
            raise RawError(f"{self.plane}: {name} hash/size mismatch")

    def read(self, name, expect_lines=None, envelope_only=False, legacy=False):
        out = []
        for number, record in lines(self.dir / name):
            if envelope_only and "envelope" not in record:
                raise RawError(f"{self.plane}: {name}:{number} raw record without envelope")
            if not line_hash_ok(record) and not (legacy and "raw_hex" in record):
                raise RawError(f"{self.plane}: {name}:{number} line hash mismatch")
            out.append(record)
        if expect_lines is not None and len(out) != expect_lines:
            raise RawError(f"{self.plane}: {name} line count differs from the seal")
        return out


def load(h_dir, o_dir):
    """Both planes of one run, verified. The O export may be absent only for B0 (caller decides)."""
    h = Export(h_dir, "H")
    o = Export(o_dir, "O") if o_dir else None
    if o is not None and o.run_id != h.run_id:
        raise RawError("H and O exports belong to different runs")
    return h, o
