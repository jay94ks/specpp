#!specpp 0.1

# Meta

- name: std/ui/widgets
- version: 0.1.0
- description: 창·버튼·라벨로 이루어진 가장 기본적인 GUI 위젯 계약.

# Intent

콘솔이 아니라 창(window)을 띄우고 버튼을 누르는 방식으로 상호작용하는
프로그램을 기술할 때 쓴다. [`std/windows/messagebox.md`](../windows/messagebox.md)류의
`Dialog`가 "한 번 띄우고 닫는 대화 상자"라면, 이 패키지는 버튼을 여러 번
누르며 계속 상호작용하는 일반적인 GUI 화면을 위한 것이다. 레이아웃 세부
규칙(정확히 몇 픽셀에 무엇이 있는지)까지는 규정하지 않는다 — "이런 위젯이
있고, 이렇게 반응한다"는 것만 명세하고 배치는 AI 재량에 맡긴다.

# Domain

## Class: Window

생성자:
- Window(title: string, width: int, height: int)

메서드:
- show() -> void
  설명: 창을 화면에 띄운다.
- close() -> void
  설명: 창을 닫는다.
- addChild(widget: Widget) -> void
  설명: widget을 이 창 위에 배치한다. 배치 위치·순서는 AI가 대상 GUI
  툴킷의 관용적인 방식(레이아웃 매니저 등)으로 정한다.

## Interface: Widget

(공통 마커 인터페이스 — 이 인터페이스를 구현하는 것만이 `Window.addChild`에
들어갈 수 있다는 것을 나타낸다. 요구하는 메서드는 없다.)

## Class: Button implements Widget

생성자:
- Button(label: string)

멤버:
이벤트:
- onClick: () -> void — 사용자가 이 버튼을 클릭하면 발생한다.

메서드:
- setLabel(text: string) -> void
- setEnabled(enabled: boolean) -> void
  설명: false면 클릭할 수 없게(회색으로 비활성화) 만든다.

## Class: Label implements Widget

생성자:
- Label(text: string)

메서드:
- setText(text: string) -> void
- text() -> string

# Interface

## Library

다른 패키지는 `Window`를 만들고, `Button`/`Label`을 만들어
`window.addChild(...)`로 배치한 뒤, `button.onClick`에 핸들러를 등록해
상호작용을 구현합니다.

# Constraints

- 타겟 언어·플랫폼의 관용적인 GUI 툴킷(Python `tkinter`, C++/C# 등에서는
  Qt/WinForms/WPF/GTK, Windows 네이티브는
  [`std/windows/win32.md`](../windows/win32.md), 웹은
  [`std/web/dom.md`](../web/dom.md))에 매핑한다. 콘솔만 있는
  환경(GUI 없음)에서는 [`std/windows/messagebox.md`](../windows/messagebox.md)류와
  마찬가지로 쓸 수 없다 — AI는 4.5절에 따라 이 제약을 알린다.
- `Window.show()`가 호출된 뒤 창이 닫힐 때까지 프로그램이 종료되지 않고
  이벤트(버튼 클릭 등)를 계속 처리하는 것(이벤트 루프)은 타겟 GUI 툴킷이
  이미 제공하는 기능을 그대로 쓴다 — 이 계약이 별도로 정의하지 않는다.

# Examples

## 예제: 버튼을 누르면 라벨이 바뀐다

호출: `label = Label("0")`, `button = Button("+1")`,
`button.onClick`에 `() -> label.setText(...)`(현재 값 + 1) 등록, 창에 둘 다
`addChild`, `window.show()`. 사용자가 버튼을 한 번 클릭한다.

기대 동작: `label.text()`가 `"1"`이 된다.

# Open Points

- 텍스트 입력 상자(TextBox), 이미지(Image), 레이아웃을 세밀하게 제어하는
  방법은 다음 버전에서 다룬다.
