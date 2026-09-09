#!specpp 0.1

# Meta

- name: notepad-clone
- version: 0.1.0
- description: Windows 메모장(Notepad)과 같은 핵심 기능을 갖는 텍스트 편집기.
- target: 미지정 — AI가 상황에 맞게 제안. Windows에서는
  [`std/windows/win32.md`](../std/windows/win32.md)의 네이티브 컨트롤을
  우선한다 (아래 Constraints 참조).

# Intent

Windows 기본 메모장과 같은 방식으로 동작하는 순수 텍스트 편집기가 필요하다:
메뉴로 파일을 열고 저장하고, 자유롭게 타이핑하고, 찾기/바꾸기를 하고, 자동
줄 바꿈을 켜고 끌 수 있어야 한다. 서식 있는 문서(굵게, 색상 등)는 다루지
않는다 — 메모장과 마찬가지로 순수 텍스트만 다룬다.

이 버전은 메모장의 가장 널리 쓰이는 핵심 기능을 그대로 재현하지만, 인쇄/
페이지 설정, 글꼴 선택 대화 상자, 확대/축소, 시간/날짜 삽입, 맞춤법 검사
같은 부가 기능은 범위 밖이다(아래 Open Points 참조) — "완전히 동일"보다는
"핵심 기능이 동일"을 목표로 한다.

# Domain

## Class: Notepad.App

멤버:
- filePath: string? — 현재 편집 중인 파일의 경로. 새로 만든 뒤 아직 한 번도
  저장하지 않았으면 null.
- isDirty: boolean — 마지막으로 열거나 저장한 뒤로 내용이 바뀌었으면 true.
  기본값 false.
- wordWrap: boolean — 자동 줄 바꿈 사용 여부. 기본값 true (메모장의 기본
  설정과 같다).

생성자:
- App()
  설명: 빈 문서로 시작한다 (filePath=null, isDirty=false).

메서드:
- newDocument() -> boolean
  설명: 새 문서를 시작한다. isDirty면 먼저
  `confirmDiscardChanges()`(아래)를 거친다 — 사용자가 취소를 고르면 아무
  것도 하지 않고 false를 반환한다. 진행하면 본문을 비우고 filePath=null,
  isDirty=false로 만들고 true를 반환한다.
- openFile(path: string) -> void
  설명: path의 파일 전체를 읽어 본문에 채운다. filePath=path,
  isDirty=false로 만든다. (호출하는 쪽에서 열기 전에 필요하면
  `confirmDiscardChanges()`를 먼저 부른다 — `Behavior.파일 열기` 참조.)
- save() -> boolean
  설명: filePath가 있으면 그 경로에 본문 전체를 그대로 덮어쓰고
  isDirty=false로 만든 뒤 true를 반환한다. filePath가 없으면(새 문서)
  아무것도 하지 않고 false를 반환한다 — 이 경우 호출하는 쪽이
  `Behavior.다른 이름으로 저장`을 대신 실행해야 한다.
- saveAs(path: string) -> void
  설명: path에 본문 전체를 저장하고, filePath=path, isDirty=false로 만든다.
- confirmDiscardChanges() -> boolean
  설명: isDirty가 아니면 곧바로 true를 반환한다. isDirty면 "저장하지 않은
  변경 내용을 저장하시겠습니까?" 확인을 받는다 — "예"를 고르면
  `Behavior.저장`(filePath가 없으면 `Behavior.다른 이름으로 저장`)을 실행한
  뒤, 그 저장이 실제로 끝났으면 true를 반환한다. "아니오"를 고르면 저장하지
  않고 true를 반환한다(변경 내용을 버려도 좋다는 뜻). "취소"를 고르면
  false를 반환한다(진행하던 동작을 멈춰야 한다는 뜻).

불변식:
- filePath가 null이면 이 문서는 한 번도 저장된 적이 없다.

test_required Notepad.App {
  - isDirty가 false인 상태에서 confirmDiscardChanges()는 사용자에게 묻지
    않고 곧바로 true를 반환한다.
  - saveAs()를 호출하면 그 뒤 isDirty는 항상 false다.
}

# Behavior

## Feature: 새로 만들기

설명: "파일 > 새로 만들기" (Ctrl+N).

절차:
1. `App.newDocument()`를 호출한다. 반환값이 false면(사용자가 확인 단계에서
   취소함) 여기서 멈춘다.
2. 텍스트 상자를 비우고, 창 제목을 "제목 없음 - 메모장"으로 되돌린다.

## Feature: 파일 열기

설명: "파일 > 열기..." (Ctrl+O).

절차:
1. `App.confirmDiscardChanges()`를 호출한다. false면 멈춘다.
2. [`std/ui/filedialog.md`](../std/ui/filedialog.md)의
   `FileDialog.showOpen("열기", ["텍스트 문서 (*.txt)", "모든 파일 (*.*)"])`를
   부른다. 사용자가 취소했으면(null) 멈춘다.
3. 얻은 경로로 `App.openFile(path)`를 호출한다.
4. 텍스트 상자 내용을 새로 읽은 본문으로 바꾸고, 창 제목을 "{파일명} -
   메모장"으로 바꾼다.

예외:
- 읽기에 실패하면(권한 없음 등) 오류 메시지를 알리고 문서 상태는 열기 전
  그대로 둔다.

## Feature: 저장

설명: "파일 > 저장" (Ctrl+S).

절차:
1. `App.save()`를 호출한다.
2. 반환값이 false였으면(아직 저장된 적 없는 새 문서) `Behavior.다른 이름으로
   저장`을 대신 실행한다.

## Feature: 다른 이름으로 저장

설명: "파일 > 다른 이름으로 저장..." (Ctrl+Shift+S).

절차:
1. `FileDialog.showSave("다른 이름으로 저장", ["텍스트 문서 (*.txt)", "모든
   파일 (*.*)"], 현재 파일명 또는 "제목 없음.txt")`를 부른다. 사용자가
   취소했으면(null) 멈춘다.
2. 얻은 경로로 `App.saveAs(path)`를 호출한다.
3. 창 제목을 "{새 파일명} - 메모장"으로 바꾼다.

## Feature: 끝내기

설명: "파일 > 끝내기", 또는 창을 직접 닫으려 할 때.

절차:
1. `App.confirmDiscardChanges()`를 호출한다. true면 프로그램을 종료한다.
   false면 종료를 취소하고 계속 편집 상태로 남는다.

## Feature: 찾기

설명: "편집 > 찾기..." (Ctrl+F). 찾기 대화 상자(찾을 내용 입력란, 대/소문자
구분 체크박스, 다음 찾기 버튼)를 띄운다.

입력:
- query: string
- matchCase: boolean

절차:
1. 텍스트 상자에서 현재 커서 위치 뒤부터 query를 찾는다(matchCase에 따라
   대소문자를 구분하거나 구분하지 않는다).
2. 찾으면 그 부분을 선택 상태로 만들고 보이도록 스크롤한다.
3. 커서 뒤에서 못 찾았으면 문서 처음부터 다시 찾는다(한 바퀴 순환).
4. 그래도 못 찾았으면 "찾을 수 없습니다" 알림을 보여준다.

## Feature: 바꾸기

설명: "편집 > 바꾸기..." (Ctrl+H). 찾을 내용/바꿀 내용 입력란과 "다음 찾기/
바꾸기/모두 바꾸기" 버튼이 있는 대화 상자.

입력:
- query: string
- replacement: string
- matchCase: boolean
- all: boolean — true면 "모두 바꾸기".

절차:
1. all이 false면: 현재 선택된 텍스트가 query와 일치하면 replacement로
   바꾸고, 그 뒤 `Behavior.찾기`와 같은 방식으로 다음 위치를 찾아 선택한다.
   선택된 것이 없거나 일치하지 않으면 바꾸지 않고 다음 위치만 찾는다.
2. all이 true면: 문서 처음부터 끝까지 순서대로 일치하는 모든 부분을
   replacement로 바꾼다. 바뀐 개수를 세어 "N개 항목을 바꿨습니다"로
   알린다.

## Feature: 이동

설명: "편집 > 이동..." (Ctrl+G). 줄 번호 입력란이 있는 대화 상자.

입력:
- line: int

절차:
1. line이 문서의 줄 수보다 크면 마지막 줄로 대신 이동한다.
2. 커서를 그 줄의 시작으로 옮기고 보이도록 스크롤한다.

## Feature: 자동 줄 바꿈 토글

설명: "서식 > 자동 줄 바꿈" (체크형 메뉴 항목).

절차:
1. `App.wordWrap`을 반전시킨다.
2. 텍스트 상자에 그 값을 적용한다.
3. 자동 줄 바꿈이 켜져 있으면 상태 표시줄의 줄/열 표시를 숨기고, 꺼져
   있으면 다시 보여준다 (메모장의 실제 동작과 같다 — 줄 바꿈이 켜져 있으면
   "줄"의 경계가 자동으로 바뀌어서 줄/열 표시가 의미가 없어지기 때문이다).

# Interface

## GUI

[`std/ui/widgets.md`](../std/ui/widgets.md)의 `Window`,
[`std/ui/menu.md`](../std/ui/menu.md), [`std/ui/textbox.md`](../std/ui/textbox.md)
기반. 창 하나에 메뉴 막대, 본문 전체를 채우는 `TextBox` 하나, 맨 아래
상태 표시줄(`Label`, 자동 줄 바꿈이 꺼져 있을 때만 "줄 N, 열 M" 표시)을
둔다.

| 메뉴 | 항목 | 단축키 | 매핑되는 Feature |
|---|---|---|---|
| 파일(&F) | 새로 만들기(&N) | Ctrl+N | 새로 만들기 |
| 파일(&F) | 열기(&O)... | Ctrl+O | 파일 열기 |
| 파일(&F) | 저장(&S) | Ctrl+S | 저장 |
| 파일(&F) | 다른 이름으로 저장(&A)... | Ctrl+Shift+S | 다른 이름으로 저장 |
| 파일(&F) | 끝내기(&X) | — | 끝내기 |
| 편집(&E) | 실행 취소(&U) | Ctrl+Z | `TextBox.undo()`를 그대로 호출 |
| 편집(&E) | 잘라내기(&T) | Ctrl+X | `TextBox.cut()`을 그대로 호출 |
| 편집(&E) | 복사(&C) | Ctrl+C | `TextBox.copy()`를 그대로 호출 |
| 편집(&E) | 붙여넣기(&P) | Ctrl+V | `TextBox.paste()`를 그대로 호출 |
| 편집(&E) | 찾기(&F)... | Ctrl+F | 찾기 |
| 편집(&E) | 다음 찾기(&N) | F3 | 찾기 (마지막 검색어로 반복) |
| 편집(&E) | 바꾸기(&R)... | Ctrl+H | 바꾸기 |
| 편집(&E) | 이동(&G)... | Ctrl+G | 이동 |
| 편집(&E) | 모두 선택(&A) | Ctrl+A | `TextBox.selectAll()`을 그대로 호출 |
| 서식(&O) | 자동 줄 바꿈(&W) | — | 자동 줄 바꿈 토글 (체크형) |
| 도움말(&H) | 메모장 정보(&A) | — | 프로그램 이름/버전을 알리는 대화 상자 |

창 제목은 항상 `"{파일명 또는 '제목 없음'} - 메모장"` 형식이다 (메모장과
동일하게, 수정 여부를 제목에 `*` 등으로 따로 표시하지는 않는다 — 대신
닫거나 새로 만들 때 `confirmDiscardChanges()`로 물어본다).

# Constraints

- Windows에서는 [`std/windows/win32.md`](../std/windows/win32.md)의 네이티브
  `EDIT`(여러 줄) 컨트롤, `HMENU`, 공용 대화 상자(`GetOpenFileNameW`/
  `GetSaveFileNameW`)로 구현하는 것을 우선한다. 다른 플랫폼/언어에서는
  [`std/ui/textbox.md`](../std/ui/textbox.md)/[`std/ui/menu.md`](../std/ui/menu.md)/
  [`std/ui/filedialog.md`](../std/ui/filedialog.md) 계약을 만족하는 다른
  구현(예: Python `tkinter`)으로 대체한다.
- 파일은 UTF-8 텍스트로 읽고 쓴다 — 메모장이 실제로 갖는 인코딩 자동 감지
  (UTF-16, ANSI 코드페이지 등)는 이 버전의 범위 밖이다.
- 찾기/바꾸기/이동 대화 상자는 [`std/ui/widgets.md`](../std/ui/widgets.md)
  기반의 작은 별도 창으로 구현한다.

# Examples

## 예제: 새 문서에서 저장하면 다른 이름으로 저장으로 넘어간다

전제: 새로 만든 `App`(filePath=null)이고, 본문이 비어있지 않다(isDirty를
true로 만들어 둔 상태).

호출: `app.save()`

기대 동작: `false`를 반환한다 — 호출한 쪽이 `Behavior.다른 이름으로 저장`을
이어서 실행해야 한다.

## 예제: 저장하고 나면 dirty가 아니다

전제: `App`의 본문이 바뀌어 `isDirty`가 true다.

호출: `app.saveAs("C:\\temp\\a.txt")`

기대 동작: 파일에 본문이 그대로 저장되고, `app.filePath`는
`"C:\\temp\\a.txt"`, `app.isDirty`는 `false`가 된다.

## 예제: 변경 사항이 없으면 확인 없이 진행된다

전제: 방금 저장해서 `isDirty`가 false인 `App`.

호출: `app.confirmDiscardChanges()`

기대 동작: 사용자에게 아무것도 묻지 않고 곧바로 `true`를 반환한다.

## 예제: 모두 바꾸기

전제: 본문이 `"cat dog cat"`이다.

호출: `Behavior.바꾸기`를 `query="cat"`, `replacement="fish"`, `all=true`로
실행한다.

기대 동작: 본문이 `"fish dog fish"`가 되고, "2개 항목을 바꿨습니다"라고
알린다.

# Open Points

- 인쇄, 페이지 설정, 글꼴 선택 대화 상자는 이 버전의 범위 밖이다.
- 확대/축소, 시간/날짜 삽입(F5), 맞춤법 검사·자동 고침(Windows 11의 최신
  메모장 기능)은 다루지 않는다.
- 여러 문서를 탭으로 동시에 여는 것은 다루지 않는다 — 한 번에 문서 하나만
  편집한다(고전적인 메모장과 동일).
- 정규식 찾기/바꾸기는 지원하지 않는다 — 순수 텍스트 일치만 한다.
