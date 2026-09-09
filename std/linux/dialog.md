#!specpp 0.1

# Meta

- name: std/linux/dialog
- version: 0.1.0
- description: Linux 데스크톱에서 네이티브 대화 상자를 띄우는 수단.
- platform: linux -> fallback: std/macos/dialog.md or std/windows/messagebox.md

# Intent

Linux 데스크톱 환경에서 실행되는 GUI 프로그램이 사용자에게 간단한 알림을
보이거나 확인을 받아야 할 때 쓴다. [`std/system/dialog.md`](../system/dialog.md)의
`Dialog` 계약을 구현한다. Windows의 `MessageBox`처럼 모든 배포판에 공통으로
보장되는 단일 네이티브 API는 없으므로, 데스크톱에 흔히 설치되어 있는 외부
도구(`zenity`, `kdialog`)를 호출하는 방식으로 구현한다.

# Domain

## Class: LinuxDialog implements Dialog

메서드:
- show(text: string, title: string) -> void
- confirm(text: string, title: string) -> boolean

# Interface

## Library

다른 패키지는 `LinuxDialog().confirm(text, title)`처럼 씁니다. 여러 OS를
대상으로 코드를 쓸 때는 [`Dialog`](../system/dialog.md) 타입으로 선언해두고
실행 환경에 맞는 구현을 주입하는 것을 권장합니다.

# Constraints

- `zenity --question`/`zenity --info`, 없으면 `kdialog --yesno`/`kdialog
  --msgbox` 순서로 시도한다(3.9절 extern의 `or` 목록과 같은 "왼쪽부터 순서대로
  시도" 원칙). 둘 다 없으면 오류를 낸다 — 이 경우 호출하는 쪽이 4.5절에 따라
  대체 수단(예: 콘솔 프롬프트)을 마련해야 한다.
- 데스크톱 세션이 없는 환경(SSH로 접속한 서버 등)에서는 애초에 쓸 수 없다.

# Examples

## 예제: 확인 대화 상자

호출: `LinuxDialog().confirm("정말 삭제하시겠습니까?", "확인")`

기대 동작: 사용자가 "예"를 고르면 `true`, "아니오"를 고르거나 닫으면 `false`를
반환한다.

# Open Points

- GNOME/KDE 외의 데스크톱 환경(예: Wayland 전용 컴포지터)에서 `zenity`/
  `kdialog`가 모두 없을 때의 대체 수단은 다음 버전에서 다룬다.
