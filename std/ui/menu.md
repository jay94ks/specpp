#!specpp 0.1

# Meta

- name: std/ui/menu
- version: 0.1.0
- description: 창 위쪽의 메뉴 막대(파일/편집/... )에 대한 추상 계약.

# Intent

메모장처럼 메뉴 막대로 대부분의 기능을 노출하는 프로그램을 위한 것이다.
[`std/ui/widgets.md`](widgets.md)의 `Button`이 화면 안의 버튼이라면, 이
패키지는 창 자체에 붙는 메뉴 막대를 다룬다.

# Domain

## Class: MenuBar

생성자:
- MenuBar()

메서드:
- addMenu(label: string) -> Menu
  설명: label(예: `"파일(&F)"` — `&` 뒤 글자가 단축키가 된다)이라는 최상위
  메뉴를 추가하고 반환한다.
- attachTo(window: Window) -> void
  설명: 이 메뉴 막대를 window에 붙인다.

## Class: Menu

메서드:
- addItem(label: string, shortcut: string?) -> MenuItem
  설명: label(예: `"저장(&S)"`)이라는 메뉴 항목을 추가한다. shortcut은
  `"Ctrl+S"`처럼 표시용 단축키 문자열이다(있으면 항목 오른쪽에 표시되고,
  실제로 그 키 입력에도 반응한다). 없으면 null.
- addSeparator() -> void
  설명: 구분선을 추가한다.

## Class: MenuItem

멤버:
이벤트:
- onClick: () -> void — 이 항목을 선택하면(클릭 또는 단축키) 발생한다.

메서드:
- setChecked(checked: boolean) -> void
  설명: 체크 표시가 있는 토글형 항목(예: "자동 줄 바꿈")으로 만든다.
- setEnabled(enabled: boolean) -> void

# Interface

## Library

`MenuBar()` → `addMenu("파일(&F)")`로 최상위 메뉴를 얻고 →
`addItem("저장(&S)", "Ctrl+S")`로 항목을 추가한 뒤 `onClick`을 연결합니다.
마지막에 `menuBar.attachTo(window)`로 창에 붙입니다.

# Constraints

- 타겟 플랫폼의 네이티브 메뉴(Windows의 Win32 `HMENU`/`CreateMenu`/
  `AppendMenuW` — [`std/windows/win32.md`](../windows/win32.md) 참조,
  Python `tkinter.Menu` 등)에 매핑한다.
- `shortcut` 문자열이 실제로 그 키 입력에 반응하게 만드는 것(액셀러레이터
  테이블 등)은 대상 플랫폼의 관용적인 방식을 따른다.

# Examples

## 예제: 메뉴 항목 클릭

호출: `file = menuBar.addMenu("파일(&F)")`,
`saveItem = file.addItem("저장(&S)", "Ctrl+S")`,
`saveItem.onClick`에 핸들러 등록. 사용자가 메뉴에서 "저장"을 클릭하거나
Ctrl+S를 누른다.

기대 동작: 등록한 핸들러가 실행된다.

# Open Points

- 하위 메뉴(메뉴 안의 메뉴), 아이콘이 붙은 메뉴 항목은 이 버전의 범위 밖이다.
