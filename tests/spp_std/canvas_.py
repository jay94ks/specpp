"""std/ui/canvas.md reference implementation (tkinter-based)."""
import tkinter as tk


class Canvas:
    def __init__(self, tk_canvas):
        self._c = tk_canvas

    def clear(self, color):
        self._c.delete("all")
        w = int(self._c["width"])
        h = int(self._c["height"])
        self._c.create_rectangle(0, 0, w, h, fill=color, outline="")

    def fillRect(self, x, y, width, height, color):
        self._c.create_rectangle(x, y, x + width, y + height, fill=color, outline="")

    def drawText(self, x, y, text, color, fontSize):
        self._c.create_text(x, y, text=text, fill=color, font=("Arial", fontSize, "bold"), anchor="nw")


class CanvasWindow:
    _KEYSYMS = {"Up", "Down", "Left", "Right"}

    def __init__(self, title, width, height):
        self._root = tk.Tk()
        self._root.title(title)
        self._root.geometry(f"{width}x{height}")
        self._root.withdraw()  # 테스트/헤드리스 실행 중 화면에 실제로 뜨지 않게 한다.

        tk_canvas = tk.Canvas(self._root, width=width, height=height, highlightthickness=0)
        tk_canvas.pack()
        self._canvas = Canvas(tk_canvas)

        self.onKeyDown = None
        self.onRender = None
        self._root.bind("<KeyPress>", self._handleKey)

    def _handleKey(self, event):
        if event.keysym in self._KEYSYMS and self.onKeyDown:
            self.onKeyDown(event.keysym)

    def requestRedraw(self):
        if self.onRender:
            self.onRender(self._canvas)

    def show(self):
        self._root.deiconify()
        self.requestRedraw()
        self._root.update()

    def run(self):
        self.show()
        self._root.focus_force()
        self._root.mainloop()

    def close(self):
        self._root.destroy()
