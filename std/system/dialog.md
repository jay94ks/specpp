#!specpp 0.1

# Meta

- name: std/system/dialog
- version: 0.1.0
- description: 사용자에게 알리거나 확인을 받는 네이티브 대화 상자에 대한 추상 계약.

# Intent

"확인 버튼 하나짜리 알림"과 "확인/취소 확인창"은 거의 모든 데스크톱 OS가
제공하지만 구현 방식은 저마다 다르다. 이 인터페이스는 그 모양만 추상적으로
정의하고, 실제 구현은 OS별 패키지([`std/windows/messagebox.md`](../windows/messagebox.md),
[`std/linux/dialog.md`](../linux/dialog.md),
[`std/macos/dialog.md`](../macos/dialog.md))에 맡긴다.

# Domain

## Interface: Dialog

메서드:
- show(text: string, title: string) -> void
  설명: "확인" 버튼 하나만 있는 대화 상자를 띄운다. 사용자가 닫을 때까지
  블로킹한다.
- confirm(text: string, title: string) -> boolean
  설명: "확인"/"취소" 대화 상자를 띄운다. 확인이면 true, 취소(또는 그냥 닫음)면
  false.

# Interface

## Library

프로그램은 실행되는 OS에 맞는 구현을 고르거나, 1.1절의 제약 조건 참조로
`package_like Dialog`를 요구해 AI가 대상 OS에 맞는 구현을 자동으로 고르게 할
수 있습니다.

# Constraints

- GUI가 없는 실행 환경(콘솔 전용 서버, SSH 세션 등)에서는 어떤 구현도 대화
  상자를 띄울 수 없다. AI는 4.5절에 따라 이 제약을 알리고, 필요하면
  [`stdout`](../stdout.md)/[`stdin`](../stdin.md) 기반의 콘솔 프롬프트로
  대체할지 확인한다. (각 OS별 구현은 이 제약이 구체적으로 어떤 모습인지만
  Constraints에 추가로 적는다.)

# Open Points

- 없음.
