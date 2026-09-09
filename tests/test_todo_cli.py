import unittest
from todo_cli import TodoApp, ValidationError, NotFoundError, format_add, format_done, format_list_line


class TodoCliExamplesTest(unittest.TestCase):
    """examples/todo-cli.md 의 # Examples 섹션을 그대로 옮긴 테스트."""

    def test_add_to_empty_list(self):
        app = TodoApp()
        task = app.add("우유 사기")
        self.assertEqual(format_add(task), "✔ 추가됨: 우유 사기 (#1)")

    def test_second_add_increments_id(self):
        app = TodoApp()
        app.add("우유 사기")
        task = app.add("청소하기")
        self.assertEqual(format_add(task), "✔ 추가됨: 청소하기 (#2)")

    def test_blank_title_fails(self):
        app = TodoApp()
        with self.assertRaises(ValidationError) as ctx:
            app.add("   ")
        self.assertEqual(ctx.exception.message, "title은 필수입니다")

    def test_done_task_excluded_from_default_list(self):
        app = TodoApp()
        app.add("우유 사기")
        app.done(1)
        self.assertEqual(app.list(all_=False), [])

    def test_all_flag_includes_done(self):
        app = TodoApp()
        app.add("우유 사기")
        app.done(1)
        lines = [format_list_line(t) for t in app.list(all_=True)]
        self.assertEqual(lines, ["[x] #1 우유 사기"])

    def test_done_missing_id_fails(self):
        app = TodoApp()
        with self.assertRaises(NotFoundError) as ctx:
            app.done(999)
        self.assertEqual(ctx.exception.message, "Task #999를 찾을 수 없습니다")


class TodoTaskRequiredTest(unittest.TestCase):
    """Domain의 test_required Todo.Task 블록을 그대로 옮긴 테스트."""

    def test_blank_title_rejected(self):
        app = TodoApp()
        with self.assertRaises(ValidationError):
            app.add("   ")

    def test_mark_done_twice_is_idempotent(self):
        app = TodoApp()
        app.add("우유 사기")
        app.done(1)
        app.done(1)  # 두 번째 호출도 예외 없이 통과해야 한다
        task = app.list(all_=True)[0]
        self.assertTrue(task.done)


if __name__ == "__main__":
    unittest.main()
