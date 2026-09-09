#!specpp 0.1

# Meta

- name: std/concurrency/stack
- version: 0.1.0
- description: 여러 스레드가 동시에 접근해도 안전한 LIFO 스택(CAS 기반).

# Intent

[`std/collections/stack.md`](../collections/stack.md)와 같은 LIFO 동작이
필요하지만, 여러 스레드가 동시에 `push`/`pop`을 호출해도 안전해야 할 때 쓴다.

# Domain

## Class: ConcurrentStack<T> implements Collection<T>

생성자:
- ConcurrentStack()
  설명: 빈 스택을 만든다.

메서드:
- push(item: T) -> void
  설명: item을 스택의 맨 위에 추가한다. 여러 스레드가 동시에 호출해도 안전하다.
- pop() -> T?
  설명: 스택의 맨 위 항목을 꺼내 제거하고 반환한다. 비어있으면 null을 반환한다.
  여러 스레드가 동시에 호출해도 안전하다.
- size() -> int
  설명: 담긴 항목 개수를 반환한다. 동시 접근 중에는 근사값일 수 있다 (`isEmpty()`도
  [`Collection<T>`](../collections/collection.md)의 기본 구현을 통해 마찬가지로
  근사값이다).

불변식:
- 여러 스레드가 동시에 push/pop을 호출해도, 각 원소는 정확히 한 번만 pop된다
  (경쟁 상태로 원소가 사라지거나 중복 반환되지 않는다).
- 단일 스레드에서 보면 pop()이 반환하는 순서는 항상 push()로 넣은 순서의 역순이다
  (LIFO).

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `ConcurrentStack<T>`를 타입으로 써서 멤버·
변수를 선언합니다.

# Constraints

- 락(lock)이 아니라 [`Atomic<T>`](atomic.md)의 `compareAndSwap`을 이용한
  무잠금(lock-free) 알고리즘 — 전형적으로 맨 위 노드를 가리키는 `Atomic<Node?>`에
  CAS로 push/pop하는 방식(Treiber stack) — 으로 구현하는 것을 우선한다.
- 타겟 언어에 성숙한 lock-free 스택 구현이 있으면 그것을 그대로 활용해도 된다 —
  다만 동시성 안전성 보장(위 불변식)은 반드시 지켜야 한다.

# Examples

## 예제: 단일 스레드에서는 넣은 순서의 역순으로 나온다

호출 (순서대로): `s.push("a")`, `s.push("b")`, `s.pop()`, `s.pop()`

기대 동작: 두 번의 `pop()`은 각각 `"b"`, `"a"` 순으로 반환한다.

## 예제: 동시에 접근해도 원소를 잃어버리지 않는다

호출: 스레드 A와 스레드 B가 동시에 각각 `s.push("a")`, `s.push("b")`를 한 번씩
호출한다.

기대 동작: 이후 `s.size()`는 정확히 `2`이다 (호출 순서와 무관하게 두 원소 모두
살아남는다).

# Open Points

- ABA 문제 방지(예: 태그가 붙은 포인터, 세대 번호 등)를 어떻게 구현할지는 타겟
  언어와 사용 가능한 원자 연산에 따라 AI가 결정한다.
