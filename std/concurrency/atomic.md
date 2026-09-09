#!specpp 0.1

# Meta

- name: std/concurrency/atomic
- version: 0.1.0
- description: 여러 스레드가 동시에 접근해도 안전한, 값 하나를 감싸는 원자적 래퍼.

# Intent

여러 스레드가 동시에 읽고 쓸 수 있는 값 하나가 필요할 때 쓴다. 일반 변수는 동시에
읽고 쓰면 경쟁 상태(race condition)가 생길 수 있지만, `Atomic<T>`의 모든 연산은
**더 이상 쪼갤 수 없는 단일 연산(원자적, atomic)**으로 실행된다는 것이 보장된다.
이 패키지는 [`collections`](../collections)처럼 순수한 자료구조가 아니라, 동시성
프로그램의 가장 기초가 되는 빌딩 블록이다.

# Domain

## Class: Atomic<T>

생성자:
- Atomic(initial: T)
  설명: initial 값으로 초기화한다.

메서드:
- get() -> T
  설명: 현재 값을 원자적으로 읽는다.
- set(value: T) -> void
  설명: 값을 원자적으로 덮어쓴다.
- exchange(newValue: T) -> T
  설명: 값을 newValue로 원자적으로 교체하고, 교체되기 전의 값을 반환한다.
- compareAndSwap(expected: T, newValue: T) -> boolean
  설명: 현재 값이 expected와 같으면(비교) newValue로 원자적으로 교체하고(교환)
  true를 반환한다. 같지 않으면 아무것도 바꾸지 않고 false를 반환한다. 이 "비교 후
  교환"이 CAS(compare-and-swap)이며, 락 없이 동시성을 다루는 모든 연산의 기반이
  된다.

불변식:
- 위 네 메서드는 모두 원자적이다 — 여러 스레드가 동시에 호출해도, 마치 하나씩
  순서대로 실행된 것과 같은 결과만 나온다(중간 상태가 관측되지 않는다).

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `Atomic<T>`를 타입으로 써서 멤버·전역 변수를
선언합니다 (예: `counter: Atomic<int>`).

# Constraints

- 타겟 언어에 대응하는 네이티브 원자 타입(C++ `std::atomic<T>`, Java
  `AtomicInteger`/`AtomicReference`, Rust `AtomicUsize`, C#
  `System.Threading.Interlocked` 등)이 있으면 그것을 그대로 활용한다. 없으면
  뮤텍스/락 등으로 같은 원자성 보장을 만족하도록 구현한다.
- `T`가 숫자 타입일 때 흔히 필요한 `increment`/`fetchAdd` 같은 연산은 이 계약에
  포함하지 않는다 — 필요하면 `compareAndSwap`으로 직접 구성하거나(예:
  `get()`으로 읽고 `compareAndSwap(old, old+1)`을 성공할 때까지 재시도), 타겟
  언어에 전용 연산이 있으면 그것을 활용해도 된다.

# Examples

## 예제: 경쟁 없이 값을 교체한다

호출 (순서대로): `a.set(1)`, `a.compareAndSwap(1, 2)`

기대 동작: `compareAndSwap`은 현재 값이 `1`이었으므로 `2`로 바꾸고 `true`를
반환한다.

## 예제: 예상값이 다르면 실패한다

호출 (순서대로): `a.set(1)`, `a.compareAndSwap(999, 2)`

기대 동작: 현재 값(`1`)이 예상값(`999`)과 다르므로 아무것도 바꾸지 않고 `false`를
반환한다. `a.get()`은 여전히 `1`이다.

# Open Points

- 메모리 순서(memory ordering) 세부사항(예: acquire/release/sequentially
  consistent)은 이 버전에서 규정하지 않는다 — 타겟 언어의 기본값을 따른다.
