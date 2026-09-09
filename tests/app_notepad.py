"""examples/notepad.md 의 # Interface > ## GUI 참조 구현 (tkinter 기반).

Windows/네이티브 대상일 때는 std/windows/win32.md의 EDIT/메뉴/공용
대화상자로 구현하는 것이 Constraints에서 우선이지만, 여기서는
std/ui/{textbox,menu,filedialog}.md 계약을 만족하는 다른 구현(tkinter)으로
Python에서 검증한다. 찾기/바꾸기/이동 대화 상자는 std/ui/widgets.md 기반의
작은 별도 창으로 구현한다(Constraints 참조).
"""
import os
import tkinter as tk
from tkinter import messagebox

from notepad import App, findNext, replaceAll
from spp_std.filedialog_ import FileDialog
from spp_std.menu_ import MenuBar
from spp_std.textbox_ import TextBox
from spp_std.ui_ import Label, Window

FILTERS = ["텍스트 문서 (*.txt)", "모든 파일 (*.*)"]


class NotepadApp:
    # spp-source: examples/notepad.md#Interface.GUI
    def __init__(self):
        self.app = App(confirmCallback=self._askDiscard, saveAsCallback=self._doSaveAs)
        self._lastFindQuery = ""
        self._lastMatchCase = False

        self.window = Window("제목 없음 - 메모장", 700, 500)

        self.statusLabel = Label("줄 1, 열 1")
        self.window.addChild(self.statusLabel, side="bottom")

        self.textBox = TextBox()
        self.window.addChild(self.textBox, fill=True)
        self.textBox.onTextChanged = self._onTextChanged
        self.textBox.onCursorMoved = self._updateStatusBar

        self._buildMenu()
        self._updateTitle()
        self._updateStatusBar()
        self.window._root.protocol("WM_DELETE_WINDOW", self._onExit)

    # ---- 상태 동기화 ----

    def _syncAppText(self):
        self.app._text = self.textBox.text()

    def _updateTitle(self):
        name = os.path.basename(self.app.filePath) if self.app.filePath else "제목 없음"
        self.window._root.title(f"{name} - 메모장")

    def _updateStatusBar(self):
        if self.app.wordWrap:
            self.statusLabel.setText("")
        else:
            self.statusLabel.setText(f"줄 {self.textBox.cursorLine()}, 열 {self.textBox.cursorColumn()}")

    def _onTextChanged(self):
        self.app.isDirty = True

    def _askDiscard(self):
        result = messagebox.askyesnocancel("메모장", "변경 내용을 저장하시겠습니까?")
        if result is None:
            return "cancel"
        return "yes" if result else "no"

    def _doSaveAs(self):
        return self._saveAs()

    # ---- Behavior.새로 만들기 ----
    def newDocument(self):
        self._syncAppText()
        if not self.app.newDocument():
            return
        self.textBox.setText("")
        self._updateTitle()

    # ---- Behavior.파일 열기 ----
    def openFile(self):
        self._syncAppText()
        if not self.app.confirmDiscardChanges():
            return
        path = FileDialog.showOpen("열기", FILTERS)
        if path is None:
            return
        try:
            self.app.openFile(path)
        except OSError as e:
            messagebox.showerror("메모장", f"파일을 열 수 없습니다.\n{e}")
            return
        self.textBox.setText(self.app.text())
        self._updateTitle()

    # ---- Behavior.저장 ----
    def save(self):
        self._syncAppText()
        if not self.app.save():
            self.saveAs()
        else:
            self._updateTitle()

    # ---- Behavior.다른 이름으로 저장 ----
    def saveAs(self):
        self._saveAs()

    def _saveAs(self):
        self._syncAppText()
        default = os.path.basename(self.app.filePath) if self.app.filePath else "제목 없음.txt"
        path = FileDialog.showSave("다른 이름으로 저장", FILTERS, default)
        if path is None:
            return False
        self.app.saveAs(path)
        self._updateTitle()
        return True

    # ---- Behavior.끝내기 ----
    def _onExit(self):
        self._syncAppText()
        if self.app.confirmDiscardChanges():
            self.window.close()

    # ---- Behavior.자동 줄 바꿈 토글 ----
    def _toggleWordWrap(self, item):
        self.app.wordWrap = not self.app.wordWrap
        self.textBox.setWordWrap(self.app.wordWrap)
        item.setChecked(self.app.wordWrap)
        self._updateStatusBar()

    def _showAbout(self):
        messagebox.showinfo("메모장 정보", "메모장 (examples/notepad.md 참조 구현)")

    # ---- Behavior.찾기/다음 찾기 ----
    def _doFind(self, query, matchCase):
        if not query:
            return
        self._syncAppText()
        cursorIndex = len(self.textBox.widget.get("1.0", "insert"))
        result = findNext(self.app.text(), cursorIndex, query, matchCase)
        if result is None:
            messagebox.showinfo("메모장", "찾을 수 없습니다.")
            return
        start, end = result
        self.textBox.setSelection(start, end)

    def _findNextShortcut(self):
        if self._lastFindQuery:
            self._doFind(self._lastFindQuery, self._lastMatchCase)
        else:
            self._findDialog()

    def _findDialog(self):
        dialog = tk.Toplevel(self.window._root)
        dialog.title("찾기")
        tk.Label(dialog, text="찾을 내용:").grid(row=0, column=0, padx=5, pady=5)
        entry = tk.Entry(dialog, width=30)
        entry.insert(0, self._lastFindQuery)
        entry.grid(row=0, column=1, padx=5, pady=5)
        matchCaseVar = tk.BooleanVar(value=self._lastMatchCase)
        tk.Checkbutton(dialog, text="대/소문자 구분", variable=matchCaseVar).grid(row=1, column=0, columnspan=2)

        def onFindNext():
            self._lastFindQuery = entry.get()
            self._lastMatchCase = matchCaseVar.get()
            self._doFind(self._lastFindQuery, self._lastMatchCase)

        tk.Button(dialog, text="다음 찾기", command=onFindNext).grid(row=0, column=2, padx=5)
        entry.focus_set()

    # ---- Behavior.바꾸기 (모두 바꾸기) ----
    def _performReplaceAll(self, query, replacement, matchCase):
        self._syncAppText()
        newText, count = replaceAll(self.app.text(), query, replacement, matchCase)
        self.app.setText(newText)
        self.textBox.setText(newText)
        messagebox.showinfo("메모장", f"{count}개 항목을 바꿨습니다.")
        return count

    def _replaceDialog(self):
        dialog = tk.Toplevel(self.window._root)
        dialog.title("바꾸기")
        tk.Label(dialog, text="찾을 내용:").grid(row=0, column=0, padx=5, pady=5)
        findEntry = tk.Entry(dialog, width=30)
        findEntry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(dialog, text="바꿀 내용:").grid(row=1, column=0, padx=5, pady=5)
        replaceEntry = tk.Entry(dialog, width=30)
        replaceEntry.grid(row=1, column=1, padx=5, pady=5)
        matchCaseVar = tk.BooleanVar(value=False)
        tk.Checkbutton(dialog, text="대/소문자 구분", variable=matchCaseVar).grid(row=2, column=0, columnspan=2)

        def onFindNext():
            self._doFind(findEntry.get(), matchCaseVar.get())

        def onReplace():
            sel = self.textBox.selection()
            query, matchCase = findEntry.get(), matchCaseVar.get()
            matches = sel == query if matchCase else sel.lower() == query.lower()
            if sel and matches:
                self.textBox.replaceSelection(replaceEntry.get())
                self.app.isDirty = True
            self._doFind(query, matchCase)

        def onReplaceAll():
            self._performReplaceAll(findEntry.get(), replaceEntry.get(), matchCaseVar.get())

        tk.Button(dialog, text="다음 찾기", command=onFindNext).grid(row=0, column=2, padx=5)
        tk.Button(dialog, text="바꾸기", command=onReplace).grid(row=1, column=2, padx=5)
        tk.Button(dialog, text="모두 바꾸기", command=onReplaceAll).grid(row=2, column=2, padx=5)
        findEntry.focus_set()

    # ---- Behavior.이동 ----
    def _goToDialog(self):
        dialog = tk.Toplevel(self.window._root)
        dialog.title("이동")
        tk.Label(dialog, text="줄 번호:").grid(row=0, column=0, padx=5, pady=5)
        entry = tk.Entry(dialog, width=10)
        entry.grid(row=0, column=1, padx=5, pady=5)

        def onGo():
            try:
                line = int(entry.get())
            except ValueError:
                return
            lineCount = int(self.textBox.widget.index("end-1c").split(".")[0])
            line = max(1, min(line, lineCount))
            idx = self.textBox.lineStartIndex(line)
            self.textBox.setSelection(idx, idx)
            dialog.destroy()

        tk.Button(dialog, text="이동", command=onGo).grid(row=0, column=2, padx=5)
        entry.focus_set()

    # ---- 메뉴 구성 (# Interface > ## GUI 의 표) ----
    def _buildMenu(self):
        menuBar = MenuBar()

        fileMenu = menuBar.addMenu("파일(&F)")
        fileMenu.addItem("새로 만들기(&N)", "Ctrl+N").onClick = self.newDocument
        fileMenu.addItem("열기(&O)...", "Ctrl+O").onClick = self.openFile
        fileMenu.addItem("저장(&S)", "Ctrl+S").onClick = self.save
        fileMenu.addItem("다른 이름으로 저장(&A)...", "Ctrl+Shift+S").onClick = self.saveAs
        fileMenu.addSeparator()
        fileMenu.addItem("끝내기(&X)").onClick = self._onExit

        editMenu = menuBar.addMenu("편집(&E)")
        editMenu.addItem("실행 취소(&U)").onClick = self.textBox.undo
        editMenu.addSeparator()
        editMenu.addItem("잘라내기(&T)").onClick = self.textBox.cut
        editMenu.addItem("복사(&C)").onClick = self.textBox.copy
        editMenu.addItem("붙여넣기(&P)").onClick = self.textBox.paste
        editMenu.addSeparator()
        editMenu.addItem("찾기(&F)...", "Ctrl+F").onClick = self._findDialog
        editMenu.addItem("다음 찾기(&N)", "F3").onClick = self._findNextShortcut
        editMenu.addItem("바꾸기(&R)...", "Ctrl+H").onClick = self._replaceDialog
        editMenu.addItem("이동(&G)...", "Ctrl+G").onClick = self._goToDialog
        editMenu.addSeparator()
        editMenu.addItem("모두 선택(&A)", "Ctrl+A").onClick = self.textBox.selectAll

        formatMenu = menuBar.addMenu("서식(&O)")
        wrapItem = formatMenu.addItem("자동 줄 바꿈(&W)")
        wrapItem.onClick = lambda: self._toggleWordWrap(wrapItem)
        self.wordWrapItem = wrapItem

        helpMenu = menuBar.addMenu("도움말(&H)")
        helpMenu.addItem("메모장 정보(&A)").onClick = self._showAbout

        menuBar.attachTo(self.window)
        wrapItem.setChecked(self.app.wordWrap)
