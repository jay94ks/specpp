#!specpp 0.1

# Meta

- name: std/concurrency/queue
- version: 0.1.0
- description: 여러 스레드가 동시에 접근해도 안전한 FIFO 큐(CAS 기반).

# Intent

[`std/collections/queue.md`](../collections/queue.md)와 같은 FIFO 동작이
필요하지만, 여러 스레드가 동시에 `enqueue`/`dequeue`를 호출해도 안전해야 할 때
쓴다.

# Domain

## Class: ConcurrentQueue<T> implements Collection<T>

생성자:
- ConcurrentQueue()
  설명: 빈 큐를 만든다.

메서드:
- enqueue(item: T) -> void
  설명: item을 큐의 뒤에 추가한다. 여러 스레드가 동시에 호출해도 안전하다.
- dequeue() -> T?
  설명: 큐의 맨 앞 항목을 꺼내 제거하고 반환한다. 비어있으면 null을 반환한다.
  여러 스레드가 동시에 호출해도 안전하다.
- size() -> int
  설명: 담긴 항목 개수를 반환한다. 동시 접근 중에는 호출 시점에 따라 근사값일 수
  있다 (`isEmpty()`도 [`Collection<T>`](../collections/collection.md)의 기본
  구현을 통해 마찬가지로 근사값이다).

불변식:
- 여러 스레드가 동시에 enqueue/dequeue를 호출해도, 각 원소는 정확히 한 번만
  dequeue된다 (경쟁 상태로 원소가 사라지거나 중복 반환되지 않는다).
- 단일 스레드에서 보면 dequeue()가 반환하는 순서는 항상 enqueue()로 넣은 순서와
  같다 (FIFO).

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `ConcurrentQueue<T>`를 타입으로 써서 멤버·
변수를 선언합니다.

# Constraints

- 락(lock)이 아니라 [`Atomic<T>`](atomic.md)의 `compareAndSwap`을 이용한
  무잠금(lock-free) 알고리즘으로 구현하는 것을 우선한다.
- 타겟 언어에 성숙한 lock-free 큐 구현(예: Java `ConcurrentLinkedQueue`, C++
  라이브러리의 lock-free queue)이 있으면 그것을 그대로 활용해도 된다 — 반드시
  CAS 알고리즘을 직접 새로 구현해야 하는 것은 아니다. 다만 동시성 안전성 보장
  (위 불변식)은 반드시 지켜야 한다.

# Examples

## 예제: 단일 스레드에서는 넣은 순서대로 나온다

호출 (순서대로): `q.enqueue("a")`, `q.enqueue("b")`, `q.dequeue()`, `q.dequeue()`

기대 동작: 두 번의 `dequeue()`는 각각 `"a"`, `"b"` 순으로 반환한다.

## 예제: 동시에 접근해도 원소를 잃어버리지 않는다

호출: 스레드 A와 스레드 B가 동시에 각각 `q.enqueue("a")`, `q.enqueue("b")`를
한 번씩 호출한다.

기대 동작: 이후 `q.size()`는 정확히 `2`이다 (호출 순서와 무관하게 두 원소 모두
살아남는다).

# Open Points

- 대기(블로킹) 방식으로 빈 큐에서 dequeue를 기다리는 기능은 이 버전의 범위 밖이다
  — dequeue()는 항상 즉시(non-blocking) 반환한다.
