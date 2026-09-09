#!specpp 0.1

# Meta

- name: std/windows/win32
- version: 0.1.0
- description: 창·버튼 GUI를 순수 Win32 API로 만드는 데 필요한 최소 부분집합에 대한 실체 명세.
- platform: windows
- kind: native

# Intent

[`std/ui/widgets.md`](../ui/widgets.md)/[`std/ui/textbox.md`](../ui/textbox.md)/
[`std/ui/menu.md`](../ui/menu.md)/[`std/ui/filedialog.md`](../ui/filedialog.md)를
C/C++로 트랜스파일할 때, 별도 프레임워크(Qt, WinForms 등) 없이 Windows에
이미 있는 Win32 API에 직접 바인딩해야 하는 경우를 위한 것이다. 이미
존재하는 실체이므로 새로 구현할 대상이 아니다(`kind: native`, 1.2절).
메서드 이름은 SPP 관례가 아니라 실제 Win32 함수 이름(유니코드 `W` 접미사
버전)을 그대로 쓴다.

# Domain

## Class: HWND

(불투명 핸들이다 — 멤버를 드러내지 않는다. 최상위 창과 버튼·라벨 같은 자식
컨트롤 모두 Win32에서는 이 타입 하나로 다뤄진다.)

## Class: Win32.Window

메서드:
[Static]
- RegisterClassW(className: string, wndProc: (HWND, int, int, int) -> int) -> void
  설명: 이 프로세스 안에서 className이라는 이름의 창 클래스를 등록한다. 이미
  등록되어 있으면 아무 일도 하지 않는다. `wndProc`는 실제로는
  `LRESULT CALLBACK(HWND, UINT, WPARAM, LPARAM)` 시그니처이며, 여기서는
  네 인자를 모두 정수로 근사했다(아래 Constraints 참조).
- CreateWindowExW(className: string, text: string, width: int, height: int, parent: HWND?) -> HWND
  설명: 실제 창을 만든다. parent가 있으면 그 자식 컨트롤(버튼·라벨 등)을
  만드는 것이다 — Win32에서는 컨트롤도 창의 일종이다. 실패하면 null을
  반환한다.
- ShowWindow(hwnd: HWND) -> void
- SetWindowTextW(hwnd: HWND, text: string) -> void
  설명: 최상위 창이면 제목을, 컨트롤이면 표시 텍스트(버튼 라벨 등)를 바꾼다.
- GetWindowTextW(hwnd: HWND) -> string
- EnableWindow(hwnd: HWND, enabled: boolean) -> void
- DefWindowProcW(hwnd: HWND, message: int, wParam: int, lParam: int) -> int
  설명: `wndProc`가 직접 처리하지 않은 메시지를 OS 기본 처리로 넘긴다.
- PostQuitMessage(exitCode: int) -> void
  설명: 메시지 루프에 `WM_QUIT`을 보내 종료를 요청한다.

## Class: Win32.MessageLoop

메서드:
[Static]
- Run() -> int
  설명: `GetMessage`/`TranslateMessage`/`DispatchMessage`로 이루어진 표준
  Win32 메시지 루프를 돈다. `WM_QUIT`을 받으면 그 종료 코드를 반환하고
  끝난다.

## Class: Win32.Control

메서드:
[Static]
- SendMessageW(hwnd: HWND, message: int, wParam: int, lParam: int) -> int
  설명: 컨트롤에 메시지를 보내 상태를 조회·조작하는 범용 통로다. 예를 들어
  여러 줄 `EDIT` 컨트롤([`std/ui/textbox.md`](../ui/textbox.md) 참조)의
  실행 취소는 `EM_UNDO`, 선택 영역 조회·설정은
  `EM_GETSEL`/`EM_SETSEL`, 줄 번호 조회는
  `EM_LINEFROMCHAR`/`EM_LINEINDEX` 메시지로 이루어진다. `message`에는 이런
  실제 Win32 메시지 상수 이름을 그대로 쓴다.

## Class: HMENU

(불투명 핸들이다 — 멤버를 드러내지 않는다.)

## Class: Win32.Menu

메서드:
[Static]
- CreateMenu() -> HMENU
  설명: 메뉴 막대나 팝업(하위) 메뉴로 쓸 빈 메뉴를 만든다.
- AppendMenuW(menu: HMENU, submenu: HMENU?, id: int, text: string) -> void
  설명: menu에 항목을 추가한다. submenu가 있으면 그 팝업 메뉴를 여는
  항목이 되고(id는 무시), 없으면 id로 식별되는 일반 항목이 된다. text가
  `"-"`이면 구분선을 추가한다.
- SetMenu(hwnd: HWND, menu: HMENU) -> void
  설명: menu를 hwnd(최상위 창)의 메뉴 막대로 붙인다.
- CheckMenuItem(menu: HMENU, id: int, checked: boolean) -> void
- EnableMenuItem(menu: HMENU, id: int, enabled: boolean) -> void

## Class: Win32.CommonDialog

메서드:
[Static]
- GetOpenFileNameW(title: string, filters: list<string>) -> string?
- GetSaveFileNameW(title: string, filters: list<string>, suggestedName: string) -> string?
  설명: 표준 파일 열기/저장 대화 상자를 띄운다
  ([`std/ui/filedialog.md`](../ui/filedialog.md) 참조). 사용자가 취소하면
  null을 반환한다.

# Interface

## Library

`RegisterClassW`로 창 클래스를 등록하고, `CreateWindowExW`로 최상위 창과
그 위의 버튼·라벨을 만든 뒤, `ShowWindow`로 보여주고 `MessageLoop.Run()`을
호출합니다. 버튼 클릭은 `wndProc`가 `WM_COMMAND` 메시지를 받아 컨트롤 ID로
구분해서 처리합니다.

# Constraints

- 헤더 `<windows.h>`. `WNDCLASSW`/`MSG` 같은 실제 구조체 초기화, `ATOM` 반환값
  등 세부 사항은 대상 언어(C/C++)의 Win32 관용구를 그대로 따른다 — 이 계약은
  함수 이름과 역할만 대응시킨다.
- `wParam`/`lParam`은 실제로는 포인터 크기 정수(`WPARAM`/`LPARAM`)이지만
  SPP의 타입 표기에 맞춰 `int`로 근사했다 — 실제 코드에서는 원래 타입을
  쓴다.
- [`std/ui/widgets.md`](../ui/widgets.md)의 `Button.onClick` 이벤트와
  [`std/ui/menu.md`](../ui/menu.md)의 `MenuItem.onClick` 이벤트는 둘 다
  `wndProc`에서 `WM_COMMAND`를 가로채 메시지에 담긴 ID로 식별해서 구현한다
  (컨트롤 ID와 메뉴 항목 ID는 같은 정수 공간을 공유한다).
- [`std/ui/textbox.md`](../ui/textbox.md)의 `TextBox`는 클래스 이름
  `"EDIT"`에 `ES_MULTILINE | ES_AUTOVSCROLL | ES_WANTRETURN` 스타일을 준
  컨트롤로 매핑한다. `onTextChanged`는 `wndProc`가 부모 창으로 전달받는
  `EN_CHANGE` 알림(`WM_COMMAND`의 상위 워드)으로 구현한다.
- 문자열은 유니코드(`W` 접미사) API로 통일한다 — ANSI(`A` 접미사) 버전은
  다루지 않는다.

# Examples

## 예제: 창을 만들고 보여준다

호출: `Win32.Window.RegisterClassW("MyWindow", wndProc)`,
`hwnd = Win32.Window.CreateWindowExW("MyWindow", "제목", 320, 200, null)`,
`Win32.Window.ShowWindow(hwnd)`, `Win32.MessageLoop.Run()`

기대 동작: 화면에 "제목"이라는 제목의 320x200 창이 나타나고, 사용자가 닫을
때까지 프로그램이 종료되지 않는다.

# Open Points

- 정확한 레이아웃(x/y 좌표), 폰트·색상 커스터마이즈는 이 버전의 범위 밖이다.
- 액셀러레이터 테이블(`CreateAcceleratorTableW`)로 단축키를 등록하는 대신
  `wndProc`에서 `WM_KEYDOWN`을 직접 처리하는 것도 허용한다 — 이 계약은
  결과(단축키가 동작하는 것)만 요구한다.
- 리본 UI, 사용자 정의 그리기(owner-draw) 컨트롤은 이 버전의 범위 밖이다.
