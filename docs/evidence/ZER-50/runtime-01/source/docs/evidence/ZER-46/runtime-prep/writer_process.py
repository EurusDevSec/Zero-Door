"""Read-only Windows process handle, held across shutdown to defeat PID reuse.
No enumeration, termination or process access until explicitly constructed.
"""
import ctypes
from ctypes import wintypes
import os
import time


def current_image():
    """Physical image of this process, distinct from a Windows venv launcher path."""
    if os.name != 'nt': raise RuntimeError('WRITER_EXIT_PLATFORM_UNSUPPORTED')
    api = ctypes.WinDLL('kernel32', use_last_error=True)
    api.GetCurrentProcess.argtypes = []
    api.GetCurrentProcess.restype = wintypes.HANDLE
    api.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    api.QueryFullProcessImageNameW.restype = wintypes.BOOL
    size = wintypes.DWORD(32768); path = ctypes.create_unicode_buffer(size.value)
    if not api.QueryFullProcessImageNameW(api.GetCurrentProcess(), 0, path, ctypes.byref(size)):
        raise RuntimeError('WRITER_SELF_IMAGE_UNKNOWN')
    return path.value


class WriterProcess:
    def __init__(self, pid, executable, started_at):
        if os.name != 'nt':
            raise RuntimeError('WRITER_EXIT_PLATFORM_UNSUPPORTED')
        self.api = ctypes.WinDLL('kernel32', use_last_error=True)
        self.api.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.api.OpenProcess.restype = wintypes.HANDLE
        self.api.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
        self.api.GetProcessTimes.restype = wintypes.BOOL
        self.api.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
        self.api.QueryFullProcessImageNameW.restype = wintypes.BOOL
        self.api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.api.WaitForSingleObject.restype = wintypes.DWORD
        self.api.CloseHandle.argtypes = [wintypes.HANDLE]
        self.api.CloseHandle.restype = wintypes.BOOL
        self.handle = self.api.OpenProcess(0x100000 | 0x1000, False, pid)
        if not self.handle: raise RuntimeError('WRITER_HANDLE_UNAVAILABLE')
        try:
            created, exited, kernel, user = [wintypes.FILETIME() for _ in range(4)]
            if not self.api.GetProcessTimes(self.handle, ctypes.byref(created), ctypes.byref(exited), ctypes.byref(kernel), ctypes.byref(user)):
                raise RuntimeError('WRITER_CREATION_UNKNOWN')
            ticks = (created.dwHighDateTime << 32) | created.dwLowDateTime
            size = wintypes.DWORD(32768); path = ctypes.create_unicode_buffer(size.value)
            if not self.api.QueryFullProcessImageNameW(self.handle, 0, path, ctypes.byref(size)):
                raise RuntimeError('WRITER_EXECUTABLE_UNKNOWN')
            if os.path.normcase(os.path.realpath(path.value)) != os.path.normcase(os.path.realpath(executable)):
                raise RuntimeError('WRITER_EXECUTABLE_MISMATCH')
            unix_created = ticks / 10000000 - 11644473600
            if unix_created < started_at - 2 or unix_created > time.time() + 2:
                raise RuntimeError('WRITER_CREATION_MISMATCH')
            self.identity = {'pid': pid, 'creation_ticks': ticks, 'executable': path.value,
                             'method': 'WINDOWS_RETAINED_PROCESS_HANDLE'}
        except Exception:
            self.close(); raise

    def wait_exit(self, seconds):
        result = self.api.WaitForSingleObject(self.handle, max(0, int(seconds * 1000)))
        if result == 0: return 'EXITED'
        if result == 258: return 'ALIVE'
        return 'UNKNOWN'

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle); self.handle = None
