"""examples/todo-cli.md reference implementation."""
from datetime import datetime, timezone


class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class NotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class Task:
    def __init__(self, id, title, done, createdAt):
        self.id = id
        self.title = title
        self.done = done
        self.createdAt = createdAt

    def markDone(self):
        self.done = True


class TodoApp:
    def __init__(self):
        self._tasks = []

    def add(self, title):
        title = title.strip()
        if not title:
            raise ValidationError("title은 필수입니다")
        new_id = (max((t.id for t in self._tasks), default=0)) + 1
        task = Task(new_id, title, False, datetime.now(timezone.utc))
        self._tasks.append(task)
        return task

    def done(self, task_id):
        task = next((t for t in self._tasks if t.id == task_id), None)
        if task is None:
            raise NotFoundError(f"Task #{task_id}를 찾을 수 없습니다")
        task.markDone()
        return task

    def list(self, all_=False):
        tasks = self._tasks if all_ else [t for t in self._tasks if not t.done]
        return sorted(tasks, key=lambda t: t.id)


def format_add(task):
    return f"✔ 추가됨: {task.title} (#{task.id})"


def format_done(task):
    return f"✔ 완료: {task.title} (#{task.id})"


def format_list_line(task):
    mark = "x" if task.done else " "
    return f"[{mark}] #{task.id} {task.title}"
