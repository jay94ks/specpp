#!specpp 0.1

# Meta

- name: std/ui/textbox
- version: 0.1.0
- description: 여러 줄 텍스트를 입력·편집하는 텍스트 상자에 대한 추상 계약.

# Intent

메모장 같은 텍스트 편집기의 본문 영역처럼, 사용자가 직접 타이핑하고 선택하고
잘라내고 붙여넣는 자유 형식 텍스트 편집 위젯이 필요할 때 쓴다. 되돌리기
(undo)·잘라내기/복사/붙여넣기(clipboard)는 이 위젯이 자체적으로 갖는 기본
기능이다 — 새로 구현할 필요 없이 대상 플랫폼의 네이티브 편집 컨트롤이 이미
제공하는 것을 그대로 쓴다.

# Domain

## Class: TextBox implements Widget

생성자:
- TextBox()

멤버:
이벤트:
- onTextChanged: () -> void — 텍스트 내용이 바뀔 때마다(타이핑, 붙여넣기,
  되돌리기 등 원인과 무관하게) 발생한다.
- onCursorMoved: () -> void — 커서 위치나 선택 범위가 바뀌면 발생한다.

메서드:
- text() -> string
- setText(text: string) -> void
  설명: 전체 내용을 text로 바꾼다. 되돌리기 기록은 초기화된다.
- selection() -> string
  설명: 현재 선택된 텍스트. 선택이 없으면 빈 문자열.
- setSelection(start: int, end: int) -> void
  설명: 문자 인덱스 `[start, end)` 구간을 선택 상태로 만들고 그 위치가
  보이도록 스크롤한다.
- replaceSelection(text: string) -> void
  설명: 현재 선택된 범위를 text로 바꾼다 (선택이 없으면 커서 위치에 삽입한다).
  붙여넣기·바꾸기(replace) 기능이 이 메서드로 구현된다.
- cursorLine() -> int
  설명: 커서가 있는 줄 번호 (1부터 시작).
- cursorColumn() -> int
  설명: 커서가 있는 열 번호 (1부터 시작).
- lineStartIndex(line: int) -> int
  설명: line번째 줄이 시작하는 문자 인덱스를 반환한다 — `goToLine` 같은 기능을
  `setSelection`과 조합해 구현할 때 쓴다.
- undo() -> void
- canUndo() -> boolean
- cut() -> void
- copy() -> void
- paste() -> void
- selectAll() -> void
- setWordWrap(enabled: boolean) -> void
  설명: true면 창 너비에 맞춰 줄을 자동으로 접어 보여준다(실제 텍스트에
  줄바꿈 문자를 추가하지는 않는다).

# Interface

## Library

다른 패키지는 `TextBox`를 만들어 창에 배치하고, `onTextChanged`로 "수정됨"
상태를 추적하며, 메뉴의 잘라내기/복사/붙여넣기/되돌리기/모두 선택 항목을
이 위젯의 같은 이름 메서드에 그대로 연결합니다.

# Constraints

- 타겟 플랫폼의 네이티브 여러 줄 편집 컨트롤(Windows의 Win32 `EDIT`/`RichEdit`
  컨트롤 — [`std/windows/win32.md`](../windows/win32.md) 참조, Python
  `tkinter.Text`, 웹이면 `<textarea>` 등)에 매핑한다.
- 되돌리기(undo)는 최소 한 단계 이상 보장한다 — 정확한 단계 수, "다시
  실행(redo)" 지원 여부는 네이티브 컨트롤의 기본 동작을 따른다(이 계약은
  `redo`를 요구하지 않는다).
- 줄바꿈 문자는 `\n` 하나로 다룬다 — 파일로 읽고 쓸 때(예:
  [`std/io/file.md`](../io/file.md)) 플랫폼별 줄바꿈 변환은 그 파일 I/O
  계층의 책임이다.

# Examples

## 예제: 선택 영역을 바꾼다

호출: `box.setText("hello world")`, `box.setSelection(0, 5)`,
`box.replaceSelection("bye")`

기대 동작: `box.text()`는 `"bye world"`가 된다.

# Open Points

- 문법 강조(syntax highlighting), 읽기 전용 모드는 이 버전의 범위 밖이다.
