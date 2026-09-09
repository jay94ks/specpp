#!specpp 0.1

# Meta

- name: std/posix/signal
- version: 0.1.0
- description: POSIX 시그널을 받아 처리하거나 다른 프로세스에 보내는 수단.
- platform: linux, macos -> fallback: std/windows/consolecontrol.md (제한된 부분집합만 대응)

# Intent

Linux와 macOS는 둘 다 POSIX를 따르므로 시그널 처리가 동일하다 — 이 패키지
하나가 두 OS 모두에 적용된다(Meta의 `platform: linux, macos`, SPEC.md 3.10절).
`SIGINT`(Ctrl+C), `SIGTERM`(정상 종료 요청)처럼 OS가 프로세스에 보내는 신호를
받아 정리 작업을 하거나, 다른 프로세스에 신호를 보낼 때 쓴다.

# Domain

## Class: Signal

메서드:
[Static]
- onSignal(name: string, handler: () -> void) -> void
  설명: name(`"SIGINT"`, `"SIGTERM"` 등) 시그널을 받았을 때 handler를 호출하도록
  등록한다. 이미 등록된 핸들러가 있으면 덮어쓴다.
[Static]
- ignore(name: string) -> void
  설명: name 시그널을 무시하도록 설정한다(기본 동작을 막는다).
[Static]
- raiseSignal(pid: int, name: string) -> void
  설명: pid 프로세스에 name 시그널을 보낸다. 자기 자신에게 보낼 수도 있다.

# Interface

## Library

다른 패키지는 `Signal.onSignal("SIGINT", () -> { ... 정리 작업 ... })`처럼
프로그램 시작 시 등록해 둡니다.

# Constraints

- 네이티브 시그널 처리(C/C++ `signal`/`sigaction`, Python `signal` 모듈, Java는
  `sun.misc.Signal`류의 비표준 API, Rust `signal-hook` 등)에 매핑한다.
- 시그널 핸들러 안에서는 최소한의 작업만 안전하다는 일반적인 POSIX 제약을
  따른다 — 이 계약 자체가 핸들러 안에서 무엇을 해도 되는지 보장하지는 않는다.

# Examples

## 예제: Ctrl+C 처리

호출: `Signal.onSignal("SIGINT", () -> stdout.println("정리 중..."))` 등록 후
사용자가 Ctrl+C를 누른다.

기대 동작: 프로그램이 즉시 종료되지 않고 `"정리 중..."`을 출력한 뒤 (핸들러가
직접 종료하지 않는 한) 계속 실행된다.

# Open Points

- 실시간 시그널(`SIGRTMIN`..`SIGRTMAX`), 시그널 마스킹(`sigprocmask`)은 이
  버전의 범위 밖이다.
