#!specpp 0.1

# Meta

- name: std/system/process
- version: 0.1.0
- description: 외부 실행 파일을 별도의 OS 프로세스로 실행하고 다루는 수단.

# Intent

프로그램이 자기 자신과 별개인 다른 프로그램(외부 실행 파일)을 실행하고, 그 종료를
기다리거나 강제 종료해야 할 때 쓴다. [`concurrency/thread`](../concurrency/thread.md)가
같은 프로세스 안의 실행 흐름을 다룬다면, 이 패키지는 OS 수준에서 완전히 분리된
별도의 프로세스를 다룬다.

# Domain

## Interface: Process

멤버:
- exitCode: int? — 프로세스가 종료된 뒤의 종료 코드. 아직 실행 중이면 null.

메서드:
- start() -> void
  설명: 생성 시 지정된 실행 파일과 인자 목록으로 자식 프로세스를 실제로 시작한다.
- wait() -> int
  설명: 프로세스가 끝날 때까지 블로킹(대기)하고, 종료 코드를 반환한다.
- kill() -> void
  설명: 프로세스를 강제 종료한다. 이미 끝난 프로세스에 호출하면 아무 일도 하지
  않는다.
- isRunning() -> boolean
  설명: 프로세스가 아직 실행 중인지 확인한다.

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 실행 파일 경로와 인자 목록으로 `Process`를
만듭니다 (예: `p = Process("ls", ["-la"])`), 그 뒤 `p.start()`로 실행을
시작합니다.

# Constraints

- 타겟 언어의 네이티브 프로세스 실행 수단(C++의 플랫폼별 API, Python
  `subprocess`, Java `ProcessBuilder`, Node.js `child_process` 등)에 매핑한다.
- 자식 프로세스의 표준 입출력을 부모와 어떻게 연결할지(상속, 파이프로 캡처 등)는
  이 버전에서 규정하지 않는다 (아래 Open Points 참조).

# Examples

## 예제: 실행하고 종료 코드를 확인한다

호출: `p = Process("ls", ["-la"])`, `p.start()`, `code = p.wait()`

기대 동작: `ls -la`가 실행되고, 정상 종료하면 `code`는 `0`이다.

## 예제: 강제 종료

호출: `p = Process("sleep", ["100"])`, `p.start()`, `p.kill()`

기대 동작: `p.isRunning()`은 곧 `false`가 되고, `p.exitCode`는 정상 종료 코드가
아닌 값(강제 종료를 나타내는 값)을 갖는다.

# Open Points

- 생성자 표기(예: `Process(path, args)`) 문법은 SPEC.md에 아직 정식으로 정의되어
  있지 않다 — 정해지면 이 파일도 맞춘다.
- 자식 프로세스의 stdin/stdout/stderr를 [`std/stdin`](../stdin.md)·
  [`std/stdout`](../stdout.md)·[`std/stderr`](../stderr.md)와 같은 인터페이스로
  파이프 연결하는 방법은 다음 버전에서 다룬다.
- 환경 변수, 작업 디렉터리 지정은 이 버전의 범위 밖이다.
