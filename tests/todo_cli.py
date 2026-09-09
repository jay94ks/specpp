"""examples/todo-cli.md reference implementation.

ValidationError/NotFoundError는 std/system/exception.md의 Exception을
상속한다. 예외를 던지는 곳마다 specRef를 채워 넣는데, 이는 스펙 작성자가 적은
것이 아니라 AI가 트랜스파일 시점에 "지금 어떤 Feature를 번역 중인지" 알고
자동으로 주입한 것이다(SPEC.md 4.7절). 각 메서드 위의 spp-source 주석도 같은
절차로 자동 삽입된다.
"""
from datetime import datetime, timezone

from spp_std.system_ import Exception_


class ValidationError(Exception_):
    pass


class NotFoundError(Exception_):
    pass


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

    # spp-source: examples/todo-cli.md#Behavior.할 일 추가
    def add(self, title):
        title = title.strip()
        if not title:
            raise ValidationError(
                "title은 필수입니다",
                specRef="examples/todo-cli.md#Behavior.할 일 추가",
            )
        new_id = (max((t.id for t in self._tasks), default=0)) + 1
        task = Task(new_id, title, False, datetime.now(timezone.utc))
        self._tasks.append(task)
        return task

    # spp-source: examples/todo-cli.md#Behavior.할 일 완료 처리
    def done(self, task_id):
        task = next((t for t in self._tasks if t.id == task_id), None)
        if task is None:
            raise NotFoundError(
                f"Task #{task_id}를 찾을 수 없습니다",
                specRef="examples/todo-cli.md#Behavior.할 일 완료 처리",
            )
        task.markDone()
        return task

    # spp-source: examples/todo-cli.md#Behavior.할 일 목록 조회
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
