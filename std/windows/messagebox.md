#!specpp 0.1

# Meta

- name: std/windows/messagebox
- version: 0.1.0
- description: Windows 네이티브 메시지 박스(대화 상자)를 띄우는 수단.
- platform: windows -> fallback: std/linux/dialog.md or std/macos/dialog.md

# Intent

콘솔 없이 실행되는 Windows 프로그램(GUI 앱)이 사용자에게 간단한 알림을 보이거나
예/아니오 확인을 받아야 할 때 쓴다. Win32의 `MessageBox` API에 대응하는, 이
운영체제에만 있는 개념이므로 패키지 전체가 Windows 전용이다 (Meta의 `platform`
필드, SPEC.md 3.10절). [`std/system/dialog.md`](../system/dialog.md)의
`Dialog` 계약을 구현하며, Linux/macOS에서는 그곳에 나열된 대체 구현을 대신
쓴다.

# Domain

## Class: MessageBox implements Dialog

메서드:
[Static]
- show(text: string, title: string) -> void
[Static]
- confirm(text: string, title: string) -> boolean

(동작 설명은 [`Dialog`](../system/dialog.md)의 기본 구현을 그대로 물려받습니다
— 3.4절 "인터페이스... 시그니처에 절차·설명까지 적어두면 기본 구현이 있는
메서드가 된다" 참조.)

# Interface

## Library

다른 패키지는 `MessageBox.show("저장되었습니다", "알림")`처럼 클래스 이름으로
바로 씁니다.

# Constraints

- Win32 `MessageBox`/`MessageBoxW` API(또는 C#의
  `System.Windows.Forms.MessageBox`, 다른 언어의 대응 래퍼)에 매핑한다.

# Examples

## 예제: 확인 대화 상자

호출: `MessageBox.confirm("정말 삭제하시겠습니까?", "확인")`

기대 동작: 사용자가 "확인"을 누르면 `true`, "취소"를 누르면 `false`를 반환한다.

# Open Points

- 아이콘(경고·오류 등) 지정, 버튼 구성(예/아니오/취소 3버튼) 커스터마이즈는
  다음 버전에서 다룬다.
