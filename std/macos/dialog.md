#!specpp 0.1

# Meta

- name: std/macos/dialog
- version: 0.1.0
- description: macOS에서 네이티브 대화 상자를 띄우는 수단.
- platform: macos -> fallback: std/linux/dialog.md or std/windows/messagebox.md

# Intent

macOS에서 실행되는 프로그램이 사용자에게 간단한 알림을 보이거나 확인을 받아야
할 때 쓴다. [`std/system/dialog.md`](../system/dialog.md)의 `Dialog` 계약을
구현한다.

# Domain

## Class: MacDialog implements Dialog

메서드:
- show(text: string, title: string) -> void
- confirm(text: string, title: string) -> boolean

# Interface

## Library

다른 패키지는 `MacDialog().confirm(text, title)`처럼 씁니다.

# Constraints

- AppleScript의 `display dialog` 명령을 `osascript`로 실행하는 방식(예:
  `osascript -e 'display dialog "..." buttons {"Cancel","OK"} default button
  "OK"'`)에 매핑한다. GUI 애플리케이션 번들 안에서 실행되는 경우
  `NSAlert`(AppKit) 같은 네이티브 API를 직접 써도 된다 — 이 계약은 결과
  동작만 규정한다.
- "취소" 버튼을 누르면 `osascript`가 0이 아닌 종료 코드를 반환한다 — 이 경우를
  `confirm() == false`로 처리한다(예외로 취급하지 않는다).

# Examples

## 예제: 확인 대화 상자

호출: `MacDialog().confirm("정말 삭제하시겠습니까?", "확인")`

기대 동작: 사용자가 "OK"를 누르면 `true`, "Cancel"을 누르거나 닫으면 `false`를
반환한다.

# Open Points

- 없음.
