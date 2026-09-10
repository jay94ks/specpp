#!specpp 0.1

# Meta

- name: std/native/cpp/nhttp/async
- version: 0.1.0
- description: task<T> 코루틴과 io_context 리액터로 이루어진 libnhttp의 비동기 실행 계층 실체 명세.
- platform: linux, windows
- kind: native

# Intent

[`std/native/cpp/nhttp/server.md`](server.md)의 라우트 핸들러·미들웨어,
[`std/native/cpp/nhttp/websocket.md`](websocket.md)의 연결 콜백이 전부
이 계층 위에서 실행된다 — 이 실행 모델을 이해해야 콜백 안에서 왜
`co_await`를 써야 하는지, 블로킹 호출을 직접 넣으면 왜 안 되는지 알
수 있다. [jay94ks/libnhttp](https://github.com/jay94ks/libnhttp)의
`async::task`/`async::io_context`/`async::thread_pool`을 옮긴 것이다.
실제 존재하는 라이브러리이므로 새로 설계할 대상이 아니다
(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: nhttp::async::task&lt;T&gt;

**지연 시작(lazily-started), 단일 소유(single-owner), 단일 대기
(single-await)** 코루틴 작업 타입이다 — `co_await`되기 전까지 본문이
실행되지 않고, 복사할 수 없으며(이동만 가능), 한 번만 기다릴 수
있다.

메서드:
- (co_await로 기다리면) 완료 시 `T` 값을 얻는다. 코루틴 안에서
  예외가 났다면 `co_await` 지점에서 다시 던져진다.

## Class: nhttp::async::io_context

"reactor 하나 + 재개 대기열 + 타이머 힙"으로 이루어진 이벤트 루프다.
**`run()`은 반드시 한 스레드에서만 호출해야 한다.**

메서드:
- run() -> void
- stop() -> void
  설명: 스레드 안전 — 다른 스레드에서 불러도 된다.
- post(handle: CoroutineHandle) -> void
  설명: 스레드 안전 — 이 컨텍스트의 스레드에서 코루틴을 재개하도록
  예약한다.
- sleep_for(duration: TimeSpan) -> Task&lt;void&gt;
- schedule() -> Task&lt;void&gt;
  설명: 현재 코루틴을 이 `io_context`가 도는 스레드로 옮긴다.

## Class: nhttp::async::thread_pool

블로킹 작업(파일 I/O, DNS 조회 등)을 리액터 스레드 밖에서 실행하기
위한 스레드 풀이다 — [`std/native/cpp/nhttp/static.md`](static.md)의
`overlay_of`가 이걸 받아 쓴다.

## Interface: nhttp::io::stream

모든 I/O가 비동기(코루틴)로 이뤄진다는 것을 나타내는 공통
인터페이스다 — `request.body`/`response.body`가 이 타입이다.

메서드:
- read(buf: bytes, n: int) -> Task&lt;int&gt;
- read_all() -> Task&lt;string&gt;
- write(buf: bytes, n: int) -> Task&lt;int&gt;
- flush() -> Task&lt;void&gt;
- close() -> Task&lt;void&gt;
- seek(offset: long, origin: SeekOrigin) -> Task&lt;long&gt;

# Interface

## Library

라우트 핸들러가 블로킹 작업 없이 순수 계산만 한다면 그냥
`response(request&)`로 동기 함수를 씁니다. 파일을 읽거나, DB를
호출하거나, 다른 `task<T>`를 기다려야 한다면
`async::task<response>(request&)` 시그니처로 쓰고 그 안에서
`co_await`합니다 — [`std/native/cpp/nhttp/server.md`](server.md)의
`target_by`가 둘 다 받아 줍니다.

# Constraints

- 실제 라이브러리 헤더 `#include <nhttp/async/task.hpp>`,
  `#include <nhttp/async/io_context.hpp>`,
  `#include <nhttp/async/thread_pool.hpp>`,
  `#include <nhttp/io/stream.hpp>`에 매핑한다.
- **`task<T>`는 지연 시작이다** — 변수에 담아만 두고 `co_await`하지
  않으면 코루틴 본문이 아예 실행되지 않는다(일반적인 "즉시 실행 후
  나중에 결과만 기다리는" future/promise 모델과 다르다).
- 라우트 핸들러 안에서 표준 라이브러리의 블로킹 호출(동기 파일 읽기,
  `sleep` 등)을 직접 쓰면 그 `io_context`를 도는 스레드 전체가 멈춘다
  — 반드시 `thread_pool`에 위임하거나 이 라이브러리가 제공하는
  비동기 스트림/타이머를 써야 한다.
- `io_context`의 `run()`은 한 스레드 전용이다 — 여러 스레드에서
  동시에 처리량을 늘리려면
  [`std/native/cpp/nhttp/server.md`](server.md)의 `io_context_pool`처럼
  `io_context`를 여러 개(보통 CPU 코어 수만큼) 만들어 각각 다른
  스레드에서 돌린다.

# Examples

## 예제: 지연 시작 확인

호출: `auto t = doSomething();` (아직 `co_await`하지 않음)

기대 동작: `doSomething` 함수 본문은 아직 한 줄도 실행되지 않았다 —
`co_await t;`를 만나야 비로소 실행이 시작된다.

# Open Points

- `detached_task`(fire-and-forget 변형)의 예외 처리 규칙,
  `io_context_pool`의 작업 분배 정책(라운드로빈인지 등)은 다루지
  않는다.
- `mpmc_queue`(내부 스케줄링 큐) 같은 세부 구현 자료구조는 다루지
  않는다.
