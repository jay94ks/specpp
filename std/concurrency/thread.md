#!specpp 0.1

# Meta

- name: std/concurrency/thread
- version: 0.1.0
- description: 하나의 프로세스 안에서 독립적으로 실행되는 흐름(스레드).

# Intent

한 프로그램 안에서 여러 작업을 동시에(병렬 또는 동시성 있게) 실행해야 할 때
쓴다. [`atomic`](atomic.md), [`concurrency/queue`](queue.md),
[`concurrency/stack`](stack.md)은 여러 스레드가 안전하게 공유할 자료구조를
제공하고, 이 패키지는 그 스레드 자체를 만들고 다루는 수단을 제공한다.

# Domain

## Interface: Thread

멤버:
- id: int — 스레드를 식별하는 고유 번호 (읽기 전용).

메서드:
- start() -> void
  설명: 생성 시 전달된 함수(3.4절의 함수 타입 `() -> void`)를 별도의 실행 흐름에서
  실행하기 시작한다. 이미 시작된 스레드에 다시 호출하면 예외를 낸다.
- join() -> void
  설명: 이 스레드의 실행이 끝날 때까지 호출한 쪽을 블로킹(대기)한다.
- isAlive() -> boolean
  설명: 스레드가 아직 실행 중인지 확인한다.

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 실행할 함수를 넘겨 `Thread`를 만듭니다 (예:
`t = Thread(() -> { ... })`), 그 뒤 `t.start()`로 실행을 시작합니다.

# Constraints

- 타겟 언어의 네이티브 스레드(C++ `std::thread`, Java `Thread`, Python
  `threading.Thread`, Rust `std::thread` 등)에 매핑한다.
- C++의 `std::thread`처럼 **생성과 동시에 실행이 시작되는** 네이티브 스레드
  타입에 매핑할 때는, 이 계약의 "생성자는 준비만 하고 `start()`가 실행을
  시작한다"는 순서를 지키기 위해 실제 네이티브 스레드 객체 생성을 `start()`
  호출 시점까지 미룬다(예: 함수만 멤버로 들고 있다가 `start()` 안에서
  `std::thread`를 만든다).
- 스레드 사이에 상태를 공유할 때는 일반 변수 대신 [`Atomic<T>`](atomic.md)나
  이 저장소의 CAS 기반 컬렉션([`queue`](queue.md), [`stack`](stack.md))을
  쓰는 것을 전제로 한다 — 이 패키지 자체는 동기화 수단을 제공하지 않는다.

# Examples

## 예제: 스레드가 끝날 때까지 기다린다

호출: `t = Thread(fn)`, `t.start()`, `t.join()`

기대 동작: `join()`이 반환한 시점에는 `fn`의 실행이 끝나 있고, `t.isAlive()`는
`false`이다.

# Open Points

- 생성자 표기(예: `Thread(fn)`)와 정적 메서드(예: `Thread.sleep(ms)`) 문법은
  SPEC.md에 아직 정식으로 정의되어 있지 않다 — 정해지면 이 파일도 맞춘다.
- 스레드 우선순위, 데몬/백그라운드 여부, 취소(cancel) 기능은 이 버전의 범위 밖이다.
