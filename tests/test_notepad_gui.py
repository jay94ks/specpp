import os
import tempfile
import unittest
from unittest import mock

from app_notepad import NotepadApp


class NotepadGuiWiringTest(unittest.TestCase):
    """# Interface > ## GUI: 메뉴 항목/텍스트 상자 배선이 Behavior를 실제로 실행하는지 확인.

    실제 창은 띄우지 않는다(Window가 생성 즉시 withdraw한다). 파일 대화 상자는
    실제 사용자 입력이 필요하므로 spp_std.filedialog_.FileDialog를 모킹한다.
    """

    def setUp(self):
        self.notepad = NotepadApp()

    def tearDown(self):
        self.notepad.window.close()

    def _typeText(self, text):
        """setText()는 '불러오기'로 취급되어 dirty를 세우지 않는다 — 실제
        타이핑을 흉내내려면 위젯에 직접 insert하고 <<Modified>> 이벤트가
        전달되도록 update()로 이벤트 큐를 흘려보낸다."""
        self.notepad.textBox.widget.insert("1.0", text)
        self.notepad.window._root.update()

    def test_typing_marks_dirty_and_menu_wiring_saves(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "a.txt")
            self._typeText("hello notepad")
            self.assertTrue(self.notepad.app.isDirty)

            with mock.patch("app_notepad.FileDialog") as mockDialog:
                mockDialog.showSave.return_value = path
                self.notepad.save()  # filePath가 없으니 다른 이름으로 저장으로 넘어가야 한다

            self.assertEqual(self.notepad.app.filePath, path)
            self.assertFalse(self.notepad.app.isDirty)
            with open(path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "hello notepad")
            self.assertIn(os.path.basename(path), self.notepad.window._root.title())

    def test_open_file_loads_into_textbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "b.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("loaded from disk")

            with mock.patch("app_notepad.FileDialog") as mockDialog:
                mockDialog.showOpen.return_value = path
                self.notepad.openFile()

            self.assertEqual(self.notepad.textBox.text(), "loaded from disk")
            self.assertFalse(self.notepad.app.isDirty)

    def test_open_dialog_cancelled_leaves_document_untouched(self):
        self.notepad.textBox.setText("keep me")
        with mock.patch("app_notepad.FileDialog") as mockDialog:
            mockDialog.showOpen.return_value = None
            self.notepad.openFile()
        self.assertEqual(self.notepad.textBox.text(), "keep me")

    def test_word_wrap_toggle_updates_status_bar_visibility(self):
        self.assertTrue(self.notepad.app.wordWrap)
        self.notepad.textBox.setText("line one\nline two")

        self.notepad._toggleWordWrap(self.notepad.wordWrapItem)

        self.assertFalse(self.notepad.app.wordWrap)
        self.assertTrue(self.notepad.statusLabel.text().startswith("줄"))

        self.notepad._toggleWordWrap(self.notepad.wordWrapItem)
        self.assertEqual(self.notepad.statusLabel.text(), "")

    def test_find_selects_match(self):
        self.notepad.textBox.setText("the quick brown fox")
        self.notepad._doFind("brown", matchCase=True)
        self.assertEqual(self.notepad.textBox.selection(), "brown")

    def test_replace_all_updates_textbox_and_app(self):
        self.notepad.textBox.setText("cat dog cat")
        with mock.patch("app_notepad.messagebox"):
            self.notepad._performReplaceAll("cat", "fish", matchCase=True)
        self.assertEqual(self.notepad.textBox.text(), "fish dog fish")

    def test_new_document_prompts_and_clears_on_yes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "c.txt")
            self.notepad.app.filePath = path
            self._typeText("will be saved then cleared")

            with mock.patch("app_notepad.messagebox") as mockBox:
                mockBox.askyesnocancel.return_value = True  # "예"
                self.notepad.newDocument()

            self.assertEqual(self.notepad.textBox.text(), "")
            self.assertIsNone(self.notepad.app.filePath)
            with open(path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "will be saved then cleared")


if __name__ == "__main__":
    unittest.main()
