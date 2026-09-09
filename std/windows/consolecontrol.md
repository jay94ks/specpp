#!specpp 0.1

# Meta

- name: std/windows/consolecontrol
- version: 0.1.0
- description: Windows 콘솔 제어 이벤트(Ctrl+C 등)를 받아 처리하는 수단.
- platform: windows -> fallback: std/posix/signal.md (Linux/macOS에서는 SIGINT/SIGTERM으로 대응)

# Intent

Windows는 [`std/posix/signal.md`](../posix/signal.md)의 POSIX 시그널 모델을
쓰지 않고, 콘솔 제어 이벤트(`CTRL_C_EVENT`, `CTRL_CLOSE_EVENT` 등)라는 별도
메커니즘을 쓴다. 이 패키지는 Windows 콘솔 프로그램이 Ctrl+C나 콘솔 창 닫힘에
반응해 정리 작업을 해야 할 때 쓴다. `std/posix/signal.md`가 다루는 것과 목적은
같지만(사용자가 프로그램을 중단시키려 할 때 정리할 기회를 준다), 그 메커니즘은
Windows 전용이다.

# Domain

## Class: ConsoleControl

메서드:
[Static]
- onCtrlEvent(handler: () -> boolean) -> void
  설명: Ctrl+C, Ctrl+Break, 콘솔 창 닫힘 등의 이벤트가 발생하면 handler를
  호출하도록 등록한다. handler가 true를 반환하면 이벤트를 처리한 것으로 보고
  기본 동작(즉시 종료)을 막는다. false를 반환하면 기본 동작이 이어진다.

# Interface

## Library

다른 패키지는 `ConsoleControl.onCtrlEvent(() -> { ...정리 작업...; return
true; })`처럼 프로그램 시작 시 등록해 둡니다. 여러 OS를 대상으로 하는 코드는
[`std/posix/signal.md`](../posix/signal.md)의 `SIGINT` 핸들러와 이 등록을
함께 두어 각 OS에서 알맞은 쪽이 동작하게 합니다.

# Constraints

- Win32 `SetConsoleCtrlHandler` API(또는 C#의 `Console.CancelKeyPress`, 다른
  언어의 대응 래퍼)에 매핑한다.

# Examples

## 예제: Ctrl+C 가로채기

호출: `ConsoleControl.onCtrlEvent(() -> { stdout.println("정리 중..."); return
true; })` 등록 후 사용자가 Ctrl+C를 누른다.

기대 동작: 프로그램이 즉시 종료되지 않고 `"정리 중..."`을 출력한다.

# Open Points

- 서비스로 실행 중일 때의 제어 이벤트(`CTRL_SHUTDOWN_EVENT` 등)는 이 버전의
  범위 밖이다.
