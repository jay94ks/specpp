#!specpp 0.1

# Meta

- name: std/collections/list
- version: 0.1.0
- description: `list<T>` 기본 타입에 대한 표준 조작 함수 모음.

# Intent

3.1절의 `list<T>`는 타입 표기일 뿐 조작 방법을 정의하지 않는다. 정렬, 변환,
필터링, 접기(reduce)처럼 거의 모든 언어가 목록에 공통으로 제공하는 연산을
표준화한다. [`String`](../text/string.md)과 마찬가지로 인스턴스 없이 쓰는
정적 도구 모음이다.

# Domain

## Class: List

메서드:
[Static]
- map<T, U>(items: list<T>, fn: (T) -> U) -> list<U>
  설명: items의 각 원소에 fn을 적용한 새 list를 반환한다 (원본은 바뀌지 않는다).
[Static]
- filter<T>(items: list<T>, predicate: (T) -> boolean) -> list<T>
  설명: predicate가 true를 반환하는 원소만 남긴 새 list를 반환한다.
[Static]
- reduce<T, R>(items: list<T>, initial: R, fn: (R, T) -> R) -> R
  설명: initial부터 시작해 items를 앞에서부터 fn으로 하나씩 누적한 최종 값을
  반환한다.
[Static]
- sort<T>(items: list<T>, compare: (T, T) -> int) -> list<T>
  설명: compare(a, b)가 음수/0/양수를 반환하는 규칙(a가 b보다 앞/같음/뒤)에 따라
  정렬한 새 list를 반환한다.
[Static]
- indexOf<T>(items: list<T>, item: T) -> int
  설명: item이 처음 나타나는 위치를 반환한다. 없으면 `-1`.
[Static]
- contains<T>(items: list<T>, item: T) -> boolean
[Static]
- slice<T>(items: list<T>, start: int, end: int) -> list<T>
  설명: `[start, end)` 구간의 새 list를 반환한다.
[Static]
- reverse<T>(items: list<T>) -> list<T>
  설명: 순서를 뒤집은 새 list를 반환한다.

# Interface

## Library

다른 패키지는 `List.map(items, fn)`처럼 클래스 이름으로 바로 씁니다.

# Constraints

- 타겟 언어에 목록 자체의 메서드(예: Python 리스트 컴프리헨션·`sorted()`,
  JavaScript `Array.prototype.map`, Java `Stream`, C# LINQ)로 이 연산들을
  표현하는 관용구가 있으면 그것을 그대로 쓴다 — [`String`](../text/string.md)과
  마찬가지로 이 계약은 "이런 연산이 존재해야 한다"는 것이지 호출 형태를 강제하지
  않는다.
- 모든 메서드는 원본 list를 변경하지 않는다(비파괴적) — 결과는 항상 새 list다.

# Examples

## 예제: 필터 후 매핑

호출: `List.map(List.filter([1, 2, 3, 4], (x) -> x % 2 == 0), (x) -> x * 10)`

기대 동작: `[20, 40]`을 반환한다.

## 예제: 합계

호출: `List.reduce([1, 2, 3], 0, (acc, x) -> acc + x)`

기대 동작: `6`을 반환한다.

# Open Points

- 지연 평가(lazy evaluation)/스트림 파이프라인은 이 버전의 범위 밖이다 — 모든
  연산은 즉시(eager) 새 list를 만든다.
