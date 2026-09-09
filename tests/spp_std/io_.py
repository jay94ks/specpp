"""std/io/{file,directory}.md reference implementation."""
import os
import shutil


class Path:
    @staticmethod
    def combine(parts):
        return os.path.join(*parts)

    @staticmethod
    def fileName(path):
        return os.path.basename(path)

    @staticmethod
    def extension(path):
        _, ext = os.path.splitext(path)
        return ext[1:] if ext else None

    @staticmethod
    def directoryName(path):
        return os.path.dirname(path)


class File:
    @staticmethod
    def exists(path):
        return os.path.isfile(path)

    @staticmethod
    def readAllText(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def writeAllText(path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def appendText(path, content):
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def delete(path):
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def readAllBytes(path):
        with open(path, "rb") as f:
            return f.read()

    @staticmethod
    def writeAllBytes(path, content):
        with open(path, "wb") as f:
            f.write(content)


class Directory:
    @staticmethod
    def exists(path):
        return os.path.isdir(path)

    @staticmethod
    def create(path):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def delete(path, recursive):
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)

    @staticmethod
    def listFiles(path):
        return [os.path.join(path, name) for name in os.listdir(path)]
