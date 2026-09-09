"""std/ui/textbox.md reference implementation (tkinter-based)."""
import tkinter as tk


class TextBox:
    """std/ui/widgets.md의 Widget과 같은 방식(Window.addChild)으로 배치된다."""

    def __init__(self):
        self._widget = None
        self.onTextChanged = None
        self.onCursorMoved = None

    def _materialize(self, parent):
        self._widget = tk.Text(parent, wrap="word", undo=True)
        self._widget.bind("<<Modified>>", self._onModified)
        self._widget.bind("<KeyRelease>", lambda e: self._fireCursorMoved())
        self._widget.bind("<ButtonRelease>", lambda e: self._fireCursorMoved())
        self._tk = self._widget  # Window.addChild가 widget._tk.pack()을 부른다

    @property
    def widget(self):
        """내부 tk.Text — 포커스 제어 등에 쓴다."""
        return self._widget

    def _onModified(self, event=None):
        if self._widget.edit_modified():
            if self.onTextChanged:
                self.onTextChanged()
            self._widget.edit_modified(False)

    def _fireCursorMoved(self):
        if self.onCursorMoved:
            self.onCursorMoved()

    def text(self):
        return self._widget.get("1.0", "end-1c")

    def setText(self, text):
        self._widget.delete("1.0", "end")
        self._widget.insert("1.0", text)
        self._widget.edit_reset()
        self._widget.edit_modified(False)

    def selection(self):
        try:
            return self._widget.get("sel.first", "sel.last")
        except tk.TclError:
            return ""

    def setSelection(self, start, end):
        self._widget.tag_remove("sel", "1.0", "end")
        self._widget.tag_add("sel", f"1.0+{start}c", f"1.0+{end}c")
        self._widget.mark_set("insert", f"1.0+{end}c")
        self._widget.see(f"1.0+{start}c")

    def replaceSelection(self, text):
        try:
            self._widget.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        self._widget.insert("insert", text)

    def cursorLine(self):
        return int(self._widget.index("insert").split(".")[0])

    def cursorColumn(self):
        return int(self._widget.index("insert").split(".")[1]) + 1

    def lineStartIndex(self, line):
        return len(self._widget.get("1.0", f"{line}.0"))

    def undo(self):
        try:
            self._widget.edit_undo()
        except tk.TclError:
            pass

    def canUndo(self):
        try:
            return bool(int(self._widget.edit("canundo")))
        except tk.TclError:
            return False

    def cut(self):
        self._widget.event_generate("<<Cut>>")

    def copy(self):
        self._widget.event_generate("<<Copy>>")

    def paste(self):
        self._widget.event_generate("<<Paste>>")

    def selectAll(self):
        self._widget.tag_remove("sel", "1.0", "end")
        self._widget.tag_add("sel", "1.0", "end-1c")

    def setWordWrap(self, enabled):
        self._widget.config(wrap="word" if enabled else "none")
