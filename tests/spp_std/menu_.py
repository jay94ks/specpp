"""std/ui/menu.md reference implementation (tkinter-based)."""
import re
import tkinter as tk


def _stripAccel(label):
    return re.sub(r"\(&.\)", "", label).replace("&", "")


def _shortcutToSequence(shortcut):
    parts = shortcut.split("+")
    keysym = parts[-1]
    mods = parts[:-1]
    tkMods = []
    shift = False
    for m in mods:
        if m == "Ctrl":
            tkMods.append("Control")
        elif m == "Shift":
            tkMods.append("Shift")
            shift = True
        elif m == "Alt":
            tkMods.append("Alt")
    if len(keysym) == 1:
        keysym = keysym.upper() if shift else keysym.lower()
    return "<" + "-".join(tkMods + [keysym]) + ">"


class MenuBar:
    def __init__(self):
        self._menus = []

    def addMenu(self, label):
        menu = Menu(label)
        self._menus.append(menu)
        return menu

    def attachTo(self, window):
        root = window._root
        tkMenuBar = tk.Menu(root)
        for menu in self._menus:
            menu._materialize(tkMenuBar, root)
        root.config(menu=tkMenuBar)


class Menu:
    def __init__(self, label):
        self._label = _stripAccel(label)
        self._entries = []

    def addItem(self, label, shortcut=None):
        item = MenuItem(label, shortcut)
        self._entries.append(item)
        return item

    def addSeparator(self):
        self._entries.append(None)

    def _materialize(self, parentTkMenu, root):
        tkMenu = tk.Menu(parentTkMenu, tearoff=0)
        for entry in self._entries:
            if entry is None:
                tkMenu.add_separator()
            else:
                entry._materialize(tkMenu, root)
        parentTkMenu.add_cascade(label=self._label, menu=tkMenu)


class MenuItem:
    def __init__(self, label, shortcut=None):
        self._label = _stripAccel(label)
        self._shortcut = shortcut
        self.onClick = None
        self._tkMenu = None
        self._index = None

    def _materialize(self, tkMenu, root):
        self._tkMenu = tkMenu
        tkMenu.add_command(label=self._label, accelerator=self._shortcut or "", command=self._handleClick)
        self._index = tkMenu.index("end")
        if self._shortcut:
            def handler(event):
                self._handleClick()
                return "break"

            root.bind_all(_shortcutToSequence(self._shortcut), handler)

    def _handleClick(self):
        if self.onClick:
            self.onClick()

    def setChecked(self, checked):
        if self._tkMenu is not None and self._index is not None:
            mark = "✓ " if checked else "    "
            base = self._label.lstrip("✓ ").lstrip()
            self._tkMenu.entryconfig(self._index, label=mark + base)

    def setEnabled(self, enabled):
        if self._tkMenu is not None and self._index is not None:
            self._tkMenu.entryconfig(self._index, state=tk.NORMAL if enabled else tk.DISABLED)
