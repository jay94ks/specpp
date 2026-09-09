import os
import tempfile
import unittest

from notepad import App, findNext, replaceAll


class NotepadExamplesTest(unittest.TestCase):
    """examples/notepad.md 의 # Examples 섹션을 그대로 옮긴 테스트."""

    def test_save_on_new_document_falls_back_to_save_as(self):
        app = App()
        app.setText("hello")
        self.assertFalse(app.save())

    def test_save_as_clears_dirty_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "a.txt")
            app = App()
            app.setText("hello")
            app.saveAs(path)
            self.assertEqual(app.filePath, path)
            self.assertFalse(app.isDirty)
            with open(path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "hello")

    def test_confirm_discard_changes_no_prompt_when_clean(self):
        app = App(confirmCallback=lambda: (_ for _ in ()).throw(AssertionError("should not be asked")))
        self.assertTrue(app.confirmDiscardChanges())

    def test_replace_all(self):
        result, count = replaceAll("cat dog cat", "cat", "fish", matchCase=True)
        self.assertEqual(result, "fish dog fish")
        self.assertEqual(count, 2)


class NotepadRequiredTest(unittest.TestCase):
    """Domain의 test_required Notepad.App 블록을 그대로 옮긴 테스트."""

    def test_clean_confirm_never_prompts(self):
        called = []
        app = App(confirmCallback=lambda: called.append(1) or "cancel")
        self.assertTrue(app.confirmDiscardChanges())
        self.assertEqual(called, [])

    def test_save_as_always_leaves_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            for initial_dirty in (True, False):
                app = App()
                app.setText("x")
                app.isDirty = initial_dirty
                app.saveAs(os.path.join(tmp, "b.txt"))
                self.assertFalse(app.isDirty)


class NotepadWorkflowTest(unittest.TestCase):
    """Behavior의 새로 만들기/열기/저장/끝내기 절차를 옮긴 테스트."""

    def test_new_document_with_yes_saves_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "c.txt")
            app = App()
            app.filePath = path
            app.setText("keep me")

            app._confirmCallback = lambda: "yes"
            self.assertTrue(app.newDocument())
            self.assertEqual(app.text(), "")
            self.assertIsNone(app.filePath)
            with open(path, "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), "keep me")

    def test_new_document_with_cancel_keeps_current_document(self):
        app = App(confirmCallback=lambda: "cancel")
        app.setText("don't lose me")
        self.assertFalse(app.newDocument())
        self.assertEqual(app.text(), "don't lose me")

    def test_open_file_loads_content_and_resets_dirty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "d.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("loaded content")
            app = App()
            app.openFile(path)
            self.assertEqual(app.text(), "loaded content")
            self.assertEqual(app.filePath, path)
            self.assertFalse(app.isDirty)

    def test_exit_cancel_keeps_app_running(self):
        app = App(confirmCallback=lambda: "cancel")
        app.setText("work in progress")
        should_exit = app.confirmDiscardChanges()
        self.assertFalse(should_exit)


class NotepadFindReplaceTest(unittest.TestCase):
    def test_find_next_wraps_around(self):
        text = "abc needle def"
        result = findNext(text, cursorIndex=len(text), query="needle", matchCase=True)
        self.assertEqual(result, (4, 10))

    def test_find_next_case_insensitive(self):
        result = findNext("Hello World", 0, "world", matchCase=False)
        self.assertEqual(result, (6, 11))

    def test_find_next_not_found(self):
        self.assertIsNone(findNext("abc", 0, "zzz", matchCase=True))

    def test_replace_all_case_insensitive(self):
        result, count = replaceAll("Cat cat CAT", "cat", "dog", matchCase=False)
        self.assertEqual(result, "dog dog dog")
        self.assertEqual(count, 3)


if __name__ == "__main__":
    unittest.main()
