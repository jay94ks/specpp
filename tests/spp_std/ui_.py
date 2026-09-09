"""std/ui/widgets.md reference implementation (tkinter-based)."""
import tkinter as tk


class Widget:
    pass


class Window:
    def __init__(self, title, width, height):
        self._root = tk.Tk()
        self._root.title(title)
        self._root.geometry(f"{width}x{height}")
        self._root.withdraw()  # 테스트/헤드리스 실행 중 화면에 실제로 뜨지 않게 한다.

    def addChild(self, widget):
        widget._materialize(self._root)
        widget._tk.pack()

    def show(self):
        self._root.deiconify()
        self._root.update()

    def run(self):
        """show() 하고, 창이 닫힐 때까지 이벤트 루프를 실제로 돌린다.

        std/ui/widgets.md의 Constraints: "이벤트 루프는 타겟 GUI 툴킷이 이미
        제공하는 기능을 그대로 쓴다" — tkinter의 mainloop()가 그것이다.
        """
        self.show()
        self._root.mainloop()

    def close(self):
        self._root.destroy()


class Button(Widget):
    def __init__(self, label):
        self._label = label
        self.onClick = None
        self._tk = None

    def _materialize(self, parent):
        self._tk = tk.Button(parent, text=self._label, command=self._handle_click)

    def _handle_click(self):
        if self.onClick:
            self.onClick()

    def click(self):
        """테스트 전용: 사용자가 이 버튼을 눌렀다고 가정하고 onClick을 그대로 실행한다."""
        self._handle_click()

    def setLabel(self, text):
        self._label = text
        if self._tk:
            self._tk.config(text=text)

    def setEnabled(self, enabled):
        if self._tk:
            self._tk.config(state=tk.NORMAL if enabled else tk.DISABLED)


class Label(Widget):
    def __init__(self, text):
        self._text = text
        self._tk = None

    def _materialize(self, parent):
        self._tk = tk.Label(parent, text=self._text)

    def setText(self, text):
        self._text = text
        if self._tk:
            self._tk.config(text=text)

    def text(self):
        return self._text
