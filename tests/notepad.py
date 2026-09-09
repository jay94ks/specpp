"""examples/notepad.md 의 # Domain(Notepad.App) 참조 구현. GUI와 무관하다.

confirmDiscardChanges()의 "저장하지 않은 변경 내용을 저장할지" 확인과,
파일이 아직 없을 때의 "다른 이름으로 저장" 흐름은 GUI 계층의 몫이므로
콜백으로 주입받는다 (rps.py의 computerChooser, game2048.py의 rng와 같은
패턴 — 자동 테스트에서 결과를 고정할 수 있게 한다).
"""


class App:
    # spp-source: examples/notepad.md#Domain.Class:Notepad.App
    def __init__(self, confirmCallback=None, saveAsCallback=None):
        self.filePath = None
        self.isDirty = False
        self.wordWrap = True
        self._text = ""
        self._confirmCallback = confirmCallback  # () -> "yes" | "no" | "cancel"
        self._saveAsCallback = saveAsCallback  # () -> bool (저장이 실제로 끝났으면 true)

    def text(self):
        return self._text

    def setText(self, text):
        self._text = text
        self.isDirty = True

    def newDocument(self):
        if not self.confirmDiscardChanges():
            return False
        self._text = ""
        self.filePath = None
        self.isDirty = False
        return True

    def openFile(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self._text = f.read()
        self.filePath = path
        self.isDirty = False

    def save(self):
        if self.filePath is None:
            return False
        with open(self.filePath, "w", encoding="utf-8") as f:
            f.write(self._text)
        self.isDirty = False
        return True

    def saveAs(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._text)
        self.filePath = path
        self.isDirty = False

    def confirmDiscardChanges(self):
        if not self.isDirty:
            return True
        choice = self._confirmCallback() if self._confirmCallback else "no"
        if choice == "cancel":
            return False
        if choice == "no":
            return True
        # choice == "yes"
        if self.filePath is not None:
            return self.save()
        return self._saveAsCallback() if self._saveAsCallback else False


def findNext(text, cursorIndex, query, matchCase):
    """Behavior.찾기: 커서 뒤에서 찾고, 없으면 처음부터 한 바퀴 순환한다.

    반환값: (start, end) 인덱스 튜플, 못 찾으면 None.
    """
    if not query:
        return None
    haystack = text if matchCase else text.lower()
    needle = query if matchCase else query.lower()

    idx = haystack.find(needle, cursorIndex)
    if idx == -1:
        idx = haystack.find(needle, 0)
    if idx == -1:
        return None
    return (idx, idx + len(query))


def replaceAll(text, query, replacement, matchCase):
    """Behavior.바꾸기 (모두 바꾸기): (새 텍스트, 바뀐 개수)를 반환한다."""
    if not query:
        return text, 0
    if matchCase:
        count = text.count(query)
        return text.replace(query, replacement), count

    result = []
    count = 0
    lower_text = text.lower()
    lower_query = query.lower()
    i = 0
    while True:
        idx = lower_text.find(lower_query, i)
        if idx == -1:
            result.append(text[i:])
            break
        result.append(text[i:idx])
        result.append(replacement)
        count += 1
        i = idx + len(query)
    return "".join(result), count
