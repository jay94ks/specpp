"""std/system/process.md reference implementation."""
import subprocess


class Process:
    def __init__(self, path, args=None):
        self._path = path
        self._args = args or []
        self._proc = None
        self.exitCode = None

    def start(self):
        self._proc = subprocess.Popen([self._path, *self._args])

    def wait(self):
        self.exitCode = self._proc.wait()
        return self.exitCode

    def kill(self):
        if self._proc and self._proc.poll() is None:
            self._proc.kill()
            self._proc.wait()
        self.exitCode = self._proc.returncode if self._proc else None

    def isRunning(self):
        return self._proc is not None and self._proc.poll() is None
