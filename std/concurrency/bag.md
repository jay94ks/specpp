#!specpp 0.1

# Meta

- name: std/concurrency/bag
- version: 0.1.0
- description: 순서 없이 중복을 허용하는, 여러 스레드가 동시에 접근해도 안전한 모음.

# Intent

여러 스레드가 각자 만든 결과를 순서에 상관없이 한 곳에 모아야 할 때 쓴다.
[`set`](../collections/set.md)과 달리 중복을 허용하고, [`queue`](queue.md)나
[`stack`](stack.md)과 달리 꺼내는 순서를 보장하지 않는 대신, 그만큼 더 가볍고
빠르게 동시 추가를 처리하도록 구현될 수 있다.

# Domain

## Class: ConcurrentBag<T>

생성자:
- ConcurrentBag()
  설명: 빈 bag을 만든다.

메서드:
- add(item: T) -> void
  설명: item을 추가한다. 여러 스레드가 동시에 호출해도 안전하다.
- tryTake() -> T?
  설명: 담긴 항목 중 하나를 골라 꺼내 제거하고 반환한다. 어떤 항목이 나올지
  순서는 보장하지 않는다. 비어있으면 null을 반환한다. 여러 스레드가 동시에
  호출해도 각 항목은 정확히 한 번만 반환된다.
- size() -> int
  설명: 담긴 항목 개수를 반환한다. 동시 접근 중에는 근사값일 수 있다.
- isEmpty() -> boolean

불변식:
- 여러 스레드가 동시에 add/tryTake를 호출해도, 각 항목은 정확히 한 번만
  tryTake된다.
- 순서는 보장하지 않는다 — FIFO도 LIFO도 아니다.

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `ConcurrentBag<T>`를 타입으로 써서 멤버·변수를
선언합니다.

# Constraints

- 타겟 언어에 성숙한 동시성 bag/풀 구현(C# `ConcurrentBag<T>` 등)이 있으면 그대로
  활용한다. 없으면 [`ConcurrentQueue<T>`](queue.md)나 [`ConcurrentStack<T>`](stack.md)
  중 구현하기 쉬운 쪽으로 대체 구현해도 된다 — 순서 무보장이라는 계약만 지키면 된다.

# Examples

## 예제: 넣은 개수만큼 꺼낼 수 있다

호출: `b.add("a")`, `b.add("b")`, `b.add("c")`

기대 동작: 이후 `tryTake()`를 세 번 호출하면 `"a"`, `"b"`, `"c"`가 (순서 무관하게)
한 번씩 나오고, 네 번째 호출은 `null`을 반환한다.

# Open Points

- 없음.
