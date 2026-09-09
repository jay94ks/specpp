"""std/stdout.md, std/stderr.md, std/stdin.md reference implementation."""
import sys


class Stdout:
    def __init__(self, stream=None):
        self._stream = stream or sys.stdout

    def print(self, text):
        self._stream.write(text)

    def println(self, text):
        self._stream.write(text + "\n")

    def flush(self):
        self._stream.flush()


class Stderr:
    def __init__(self, stream=None):
        self._stream = stream or sys.stderr

    def print(self, text):
        self._stream.write(text)

    def println(self, text):
        self._stream.write(text + "\n")

    def flush(self):
        self._stream.flush()


class Stdin:
    def __init__(self, stream=None):
        self._stream = stream or sys.stdin

    def readLine(self):
        line = self._stream.readline()
        if line == "":
            return None
        return line.rstrip("\n")

    def readAll(self):
        return self._stream.read()

    def readChar(self):
        ch = self._stream.read(1)
        if ch == "":
            return None
        return ch


stdout = Stdout()
stderr = Stderr()
stdin = Stdin()
