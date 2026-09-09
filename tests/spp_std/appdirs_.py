"""std/linux/appdirs.md, std/macos/appdirs.md reference implementation.

경로 조립은 실제 타겟이 어떤 OS든 개념적으로 '/'로 구분되는 XDG/macOS 관례를
따르므로, 호스트 OS와 무관하게 검증할 수 있도록 posixpath를 명시적으로 쓴다.
실제 언어별 트랜스파일 결과는 타겟 OS의 네이티브 경로 조립 방식을 쓰면 된다.
"""
import os
import posixpath


class LinuxAppDirectories:
    def _base(self, env_var, default_relative):
        value = os.environ.get(env_var)
        if value:
            return value
        home = os.environ.get("HOME", "~")
        return posixpath.join(home, default_relative)

    def _ensure(self, path, app_name):
        full = posixpath.join(path, app_name)
        os.makedirs(full, exist_ok=True)
        return full

    def configHome(self, app_name):
        return self._ensure(self._base("XDG_CONFIG_HOME", ".config"), app_name)

    def cacheHome(self, app_name):
        return self._ensure(self._base("XDG_CACHE_HOME", ".cache"), app_name)

    def dataHome(self, app_name):
        return self._ensure(self._base("XDG_DATA_HOME", ".local/share"), app_name)


class MacAppDirectories:
    def _ensure(self, path):
        os.makedirs(path, exist_ok=True)
        return path

    def configHome(self, app_name):
        home = os.environ.get("HOME", "~")
        return self._ensure(posixpath.join(home, "Library", "Application Support", app_name))

    def cacheHome(self, app_name):
        home = os.environ.get("HOME", "~")
        return self._ensure(posixpath.join(home, "Library", "Caches", app_name))

    def dataHome(self, app_name):
        return self.configHome(app_name)
