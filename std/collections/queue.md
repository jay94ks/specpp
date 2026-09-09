#!specpp 0.1

# Meta

- name: std/collections/queue
- version: 0.1.0
- description: 먼저 들어간 것이 먼저 나오는(FIFO) 자료구조.

# Intent

처리할 항목들을 들어온 순서대로 하나씩 꺼내 처리해야 할 때 쓴다.

# Domain

## Class: Queue<T> implements Collection<T>

생성자:
- Queue()
  설명: 빈 큐를 만든다.
- Queue(items: list<T>)
  설명: items를 순서대로 넣은 큐를 만든다 (items[0]이 맨 앞).

메서드:
[Static]
- of(items: list<T>) -> Queue<T>
  설명: `Queue(items)`와 같다.
- enqueue(item: T) -> void
  설명: item을 큐의 뒤에 추가한다.
- dequeue() -> T?
  설명: 큐의 맨 앞 항목을 꺼내 제거하고 반환한다. 비어있으면 null을 반환한다.
- peek() -> T?
  설명: 큐의 맨 앞 항목을 제거 없이 반환한다. 비어있으면 null을 반환한다.
- size() -> int
  설명: 담긴 항목 개수를 반환한다.

불변식:
- dequeue()가 반환하는 순서는 항상 enqueue()로 넣은 순서와 같다 (FIFO).

[`Collection<T>`](collection.md)를 구현하므로 `isEmpty()`는 따로 적지 않아도
기본 구현을 그대로 물려받습니다.

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `Queue<T>`를 타입으로 써서 멤버·변수를
선언합니다.

# Constraints

- 타겟 언어에 대응하는 네이티브 큐 구조(C++ `std::queue`, Python
  `collections.deque`, Java `ArrayDeque` 등)가 있으면 그것을 그대로 활용한다.
  없으면 이 계약을 만족하도록 새로 구현한다.

# Examples

## 예제: 넣은 순서대로 나온다

호출 (순서대로): `q.enqueue("a")`, `q.enqueue("b")`, `q.dequeue()`, `q.dequeue()`

기대 동작: 두 번의 `dequeue()`는 각각 `"a"`, `"b"` 순으로 반환한다.

## 예제: 빈 큐에서 꺼내면 null

호출: `q.dequeue()` (아무것도 넣지 않은 상태)

기대 동작: `null`을 반환한다.

# Open Points

- 최대 용량 제한, 동시성(여러 스레드에서 동시 접근) 처리는 이 버전에서 고려하지
  않는다.
