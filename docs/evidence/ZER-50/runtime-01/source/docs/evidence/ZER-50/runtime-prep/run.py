"""ZER-50 single-use acceptance supervisor. Default/import perform no runtime work."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

PREP = Path(__file__).resolve().parent
ROOT = PREP.parents[3]
OUT = PREP.parent / "runtime-01"
HEAD = "39d1bb7b5d2ec86a9cd2cdfdaf057529da7d4598"


def native_python():
    # A venv python.exe can be a Windows redirector that spawns before stdin.
    # Launch the physical image directly so every descendant inherits the Job.
    if os.name != "nt":
        return sys.executable
    from ctypes import wintypes as w
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.GetCurrentProcess.restype = w.HANDLE
    api.QueryFullProcessImageNameW.argtypes = [w.HANDLE, w.DWORD, w.LPWSTR, ctypes.POINTER(w.DWORD)]
    size = w.DWORD(32768); image = ctypes.create_unicode_buffer(size.value)
    if not api.QueryFullProcessImageNameW(api.GetCurrentProcess(), 0, image, ctypes.byref(size)):
        raise OSError("NATIVE_PYTHON_IDENTITY")
    return image.value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    temp = path.with_suffix(path.suffix + ".writing")
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf8")
    temp.replace(path)


def verify_sources(root=ROOT, prep=PREP):
    lock = json.loads((prep / "source-manifest.json").read_bytes())
    if not lock.get("sha256"):
        raise ValueError("EMPTY_MANIFEST")
    for relative, digest in lock["sha256"].items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path) != digest:
            raise ValueError("SOURCE_DRIFT:" + relative)
    return lock


def admit(path):
    auth = json.loads(Path(path).read_bytes())
    if (auth.get("approved") is not True or auth.get("issue") != "ZER-50"
            or auth.get("attempt") != "runtime-01"
            or auth.get("proposal_sha256") != sha(PREP / "proposal.md")
            or auth.get("source_manifest_sha256") != sha(PREP / "source-manifest.json")
            or type(auth.get("expires_epoch")) not in (int, float)
            or not time.time() < auth["expires_epoch"] <= time.time() + 86400):
        raise ValueError("FRESH_EXACT_OWNER_APPROVAL_REQUIRED")
    verify_sources()
    return auth


class Tree:
    """Gate child on stdin until attached to a kill-on-close Windows Job.

    The worker's kubectl/docker children inherit the Job. POSIX uses a new
    process group. No process-name matching or unrelated process termination.
    """
    def __init__(self, child):
        self.child, self.job = child, None
        if os.name == "nt":
            from ctypes import wintypes as w
            class IO(ctypes.Structure):
                _fields_ = [(n, ctypes.c_ulonglong) for n in
                    ("readOps", "writeOps", "otherOps", "readBytes", "writeBytes", "otherBytes")]
            class BASIC(ctypes.Structure):
                _fields_ = [("processTime", ctypes.c_longlong), ("jobTime", ctypes.c_longlong),
                    ("flags", w.DWORD), ("minWs", ctypes.c_size_t), ("maxWs", ctypes.c_size_t),
                    ("active", w.DWORD), ("affinity", ctypes.c_size_t),
                    ("priority", w.DWORD), ("scheduling", w.DWORD)]
            class EXTENDED(ctypes.Structure):
                _fields_ = [("basic", BASIC), ("io", IO), ("processMemory", ctypes.c_size_t),
                    ("jobMemory", ctypes.c_size_t), ("peakProcess", ctypes.c_size_t), ("peakJob", ctypes.c_size_t)]
            self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
            self.kernel.CreateJobObjectW.restype = w.HANDLE
            self.kernel.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
            self.kernel.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
            self.kernel.CloseHandle.argtypes = [w.HANDLE]
            self.kernel.TerminateJobObject.argtypes = [w.HANDLE, w.UINT]
            self.kernel.QueryInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.c_void_p]
            self.job = self.kernel.CreateJobObjectW(None, None)
            info = EXTENDED(); info.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if (not self.job or not self.kernel.SetInformationJobObject(self.job, 9, ctypes.byref(info), ctypes.sizeof(info))
                    or not self.kernel.AssignProcessToJobObject(self.job, w.HANDLE(int(child._handle)))):
                self.close()
                raise OSError("OWNED_JOB_ADMISSION_FAILED")

    def close(self):
        if self.job:
            try:
                self.kernel.TerminateJobObject(self.job, 1)
                # Basic accounting has four LARGE_INTEGER values followed by
                # four DWORDs; ActiveProcesses is DWORD index 2 (byte offset40).
                accounting = ctypes.create_string_buffer(48)
                end = time.monotonic() + 5
                while True:
                    if not self.kernel.QueryInformationJobObject(self.job, 1, accounting, 48, None):
                        raise OSError("OWNED_JOB_EXIT_UNKNOWN")
                    if int.from_bytes(accounting.raw[40:44], "little") == 0:
                        break
                    if time.monotonic() >= end:
                        raise OSError("OWNED_JOB_TREE_NOT_EXITED")
                    time.sleep(.02)
            finally:
                self.kernel.CloseHandle(self.job); self.job = None
        elif os.name != "nt":
            try:
                os.killpg(self.child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def run_child(command, env, log, *, timeout):
    child = tree = None
    timed_out = False
    command = list(command)
    if os.path.normcase(command[0]) == os.path.normcase(sys.executable):
        command[0] = native_python()
    try:
        with log.open("xb") as stream:
            child = subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.PIPE,
                stdout=stream, stderr=stream, start_new_session=os.name != "nt",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            tree = Tree(child)
            child.stdin.write(b"GO\n"); child.stdin.flush(); child.stdin.close()
            try:
                child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
    finally:
        try:
            if tree is not None:
                tree.close()
        finally:
            if child is not None:
                if child.poll() is None:
                    child.kill()
                child.wait(timeout=5)
                if os.name == "nt":
                    child._handle.Close()
                if child.stdin and not child.stdin.closed:
                    child.stdin.close()
    return {"pid": child.pid, "exit_code": child.returncode,
            "timed_out": timed_out, "process_reaped": child.poll() is not None,
            "owned_tree_closed": True}


def execute(authorization):
    auth = admit(authorization)
    OUT.mkdir()  # Consumes this attempt even when preflight/model/cleanup fails.
    save(OUT / "authorization.json", auth)
    save(OUT / "started.json", {"at": time.time(), "head": HEAD,
        "work_seconds": 600, "cleanup_seconds": 300, "restart_allowed": False})
    lock = verify_sources()
    for relative in lock["sha256"]:
        target = OUT / "source" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    save(OUT / "source-manifest.json", lock)
    (OUT / "proposal.md").write_bytes((PREP / "proposal.md").read_bytes())
    # Key is inherited from an explicitly approved Doppler invocation, never written.
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=os.pathsep.join((str(ROOT / "agent-orchestrator"),
                   str(Path(sys.prefix) / ("Lib/site-packages" if os.name == "nt" else "lib/python%d.%d/site-packages" % sys.version_info[:2])))),
               MSYS_NO_PATHCONV="1")
    worker = {"status": "UNKNOWN"}
    cleanup = {"status": "UNKNOWN"}
    failure = None
    started = time.monotonic()
    try:
        worker = run_child([sys.executable, "-B", str(PREP / "lab.py"), "--work"],
                           env, OUT / "worker.log", timeout=600)
    except BaseException as error:
        failure = type(error).__name__
    finally:
        # Cleanup runs in a fresh owned process after the work tree is closed.
        # It receives no provider key, and never starts a new model/fixture test.
        env.pop("OPENAI_API_KEY", None)
        try:
            cleanup = run_child([sys.executable, "-B", str(PREP / "lab.py"), "--cleanup"],
                                env, OUT / "cleanup.log", timeout=285)
        except BaseException as error:
            failure = failure or "CLEANUP_" + type(error).__name__
    work = json.loads((OUT / "work-result.json").read_bytes()) if (OUT / "work-result.json").exists() else {}
    clean = json.loads((OUT / "cleanup.json").read_bytes()) if (OUT / "cleanup.json").exists() else {}
    passed = (not failure and worker.get("exit_code") == 0 and not worker.get("timed_out")
        and cleanup.get("exit_code") == 0 and not cleanup.get("timed_out")
        and work.get("status") == "OBSERVED_PENDING_REVIEW" and clean.get("verdict") == "CLEAN")
    result = {"status": "RECONCILE_REQUIRED" if passed else "NOT_MET_OR_UNKNOWN", "failure": failure,
        "worker": worker, "cleanup_process": cleanup, "elapsed_seconds": time.monotonic() - started,
        "provider_calls": work.get("provider_calls", "UNKNOWN"), "cleanup": clean.get("verdict", "UNKNOWN"),
        "issue_done": False, "benchmark_eligible": False, "recovery_verified": False}
    save(OUT / "acceptance.json", result)
    print(json.dumps(result))
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--authorization")
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({"status": "PLAN_ONLY", "provider_calls": 0, "lab_operations": 0}))
        return 0
    if not args.authorization:
        parser.error("fresh exact owner authorization required")
    return execute(args.authorization)


if __name__ == "__main__":
    raise SystemExit(main())
