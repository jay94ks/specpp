#!specpp 0.1

# Meta

- name: std/collections/stack
- version: 0.1.0
- description: 나중에 들어간 것이 먼저 나오는(LIFO) 자료구조.

# Intent

가장 최근에 넣은 항목부터 꺼내 처리해야 할 때(되돌리기, 괄호 짝 맞추기, 재귀를
반복문으로 흉내낼 때 등) 쓴다.

# Domain

## Class: Stack<T> implements Collection<T>

생성자:
- Stack()
  설명: 빈 스택을 만든다.
- Stack(items: list<T>)
  설명: items를 순서대로 push한 스택을 만든다 (items의 마지막 원소가 맨 위).

메서드:
[Static]
- of(items: list<T>) -> Stack<T>
  설명: `Stack(items)`와 같다.
- push(item: T) -> void
  설명: item을 스택의 맨 위에 추가한다.
- pop() -> T?
  설명: 스택의 맨 위 항목을 꺼내 제거하고 반환한다. 비어있으면 null을 반환한다.
- peek() -> T?
  설명: 스택의 맨 위 항목을 제거 없이 반환한다. 비어있으면 null을 반환한다.
- size() -> int
  설명: 담긴 항목 개수를 반환한다.

불변식:
- pop()이 반환하는 순서는 항상 push()로 넣은 순서의 역순이다 (LIFO).

[`Collection<T>`](collection.md)를 구현하므로 `isEmpty()`는 따로 적지 않아도
기본 구현을 그대로 물려받습니다.

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `Stack<T>`를 타입으로 써서 멤버·변수를
선언합니다.

# Constraints

- 타겟 언어에 대응하는 네이티브 스택 구조(C++ `std::stack`, Python의 `list`를
  스택으로 쓰는 관용구, Java `Deque` 등)가 있으면 그것을 그대로 활용한다. 없으면
  이 계약을 만족하도록 새로 구현한다.

# Examples

## 예제: 넣은 순서의 역순으로 나온다

호출 (순서대로): `s.push("a")`, `s.push("b")`, `s.pop()`, `s.pop()`

기대 동작: 두 번의 `pop()`은 각각 `"b"`, `"a"` 순으로 반환한다.

## 예제: 빈 스택에서 꺼내면 null

호출: `s.pop()` (아무것도 넣지 않은 상태)

기대 동작: `null`을 반환한다.

# Open Points

- 최대 용량 제한, 동시성 처리는 이 버전에서 고려하지 않는다.
