"""std/windows/{registry,messagebox}.md reference implementation.

Windows 전용(platform: windows) — winreg/ctypes는 Windows에서만 동작한다.
"""
import winreg
import ctypes

_HIVES = {
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
    "HKEY_USERS": winreg.HKEY_USERS,
    "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
}


class RegistryKey:
    HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
    HKEY_LOCAL_MACHINE = "HKEY_LOCAL_MACHINE"
    HKEY_CLASSES_ROOT = "HKEY_CLASSES_ROOT"
    HKEY_USERS = "HKEY_USERS"
    HKEY_CURRENT_CONFIG = "HKEY_CURRENT_CONFIG"

    def __init__(self, hive, subKeyPath, _handle=None):
        self._hive = hive
        self._subKeyPath = subKeyPath
        if _handle is not None:
            self._handle = _handle
        else:
            self._handle = winreg.OpenKey(_HIVES[hive], subKeyPath, 0, winreg.KEY_ALL_ACCESS)

    @staticmethod
    def create(hive, subKeyPath):
        handle = winreg.CreateKey(_HIVES[hive], subKeyPath)
        return RegistryKey(hive, subKeyPath, _handle=handle)

    def getValue(self, name):
        try:
            value, _ = winreg.QueryValueEx(self._handle, name)
            return value
        except FileNotFoundError:
            return None

    def setValue(self, name, value):
        winreg.SetValueEx(self._handle, name, 0, winreg.REG_SZ, value)

    def deleteValue(self, name):
        try:
            winreg.DeleteValue(self._handle, name)
        except FileNotFoundError:
            pass

    def deleteSubKey(self, subKeyPath):
        winreg.DeleteKey(self._handle, subKeyPath)

    def close(self):
        winreg.CloseKey(self._handle)


class MessageBox:
    MB_OKCANCEL = 0x1
    IDOK = 1

    @staticmethod
    def show(text, title):
        ctypes.windll.user32.MessageBoxW(0, text, title, 0)

    @staticmethod
    def confirm(text, title):
        result = ctypes.windll.user32.MessageBoxW(0, text, title, MessageBox.MB_OKCANCEL)
        return result == MessageBox.IDOK
