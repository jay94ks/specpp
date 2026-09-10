#!specpp 0.1

# Meta

- name: std/collections/priorityqueue
- version: 0.1.0
- description: 우선순위가 가장 높은 항목을 항상 먼저 꺼내는 큐.

# Intent

작업 스케줄링, 최단 경로 탐색(다익스트라)처럼 "다음에 처리할 것"이
삽입 순서가 아니라 우선순위로 정해질 때 쓴다.
[`std/collections/queue.md`](queue.md)(FIFO)와 이름은 비슷하지만 순서
규칙이 다르다 — 헷갈리지 않도록 주의한다.

# Domain

## Class: PriorityQueue<T> implements Collection<T>

생성자:
- PriorityQueue(comparator: (T, T) -> int)
  설명: `comparator(a, b)`가 음수면 `a`가 더 높은 우선순위(먼저
  나옴)다 — 표준 정렬 comparator 관례와 같다.

메서드:
- enqueue(item: T) -> void
- dequeue() -> T?
  설명: 가장 높은 우선순위 항목을 꺼내 반환한다. 비어 있으면 null을
  반환한다 — [`std/collections/queue.md`](queue.md)/
  [`stack.md`](stack.md)와 같은 규칙이다.
- peek() -> T?
  설명: 꺼내지 않고 다음에 나올 항목만 확인한다. 비어 있으면 null을
  반환한다.

# Interface

## Library

`pq = PriorityQueue((a, b) -> a.priority - b.priority)`처럼 comparator를
정해 만든 뒤 `enqueue`/`dequeue`를 씁니다.

# Constraints

- 실제로는 힙(heap) 자료구조로 구현되는 것이 일반적이다(대상 언어의
  C++ `std::priority_queue`, Python `heapq`, Java `PriorityQueue`,
  C# `PriorityQueue` 등) — `enqueue`/`dequeue` 모두 `O(log n)`을
  기대할 수 있다.
- 같은 우선순위를 가진 항목들 사이의 순서는 보장하지 않는다(안정
  정렬이 아니다) — 필요하면 comparator에 삽입 순서를 2차 기준으로
  직접 포함시킨다.

# Examples

## 예제: 최소값이 먼저 나온다

호출 (순서대로): `pq = PriorityQueue((a, b) -> a - b)`, `pq.enqueue(5)`,
`pq.enqueue(1)`, `pq.enqueue(3)`, `pq.dequeue()`

기대 동작: 마지막 호출은 `1`을 반환한다.

## 예제: 빈 큐에서 꺼내면 null

호출: `pq.dequeue()` (아무것도 넣지 않은 상태)

기대 동작: `null`을 반환한다.

# Open Points

- 우선순위 변경(decrease-key)은 이 버전의 범위 밖이다 — 필요하면 새
  항목을 다시 넣고 오래된 항목을 무시하는 지연 삭제(lazy deletion)
  패턴을 쓴다.
