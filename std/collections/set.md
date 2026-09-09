#!specpp 0.1

# Meta

- name: std/collections/set
- version: 0.1.0
- description: 중복 없는 원소들의 모음(집합) 자료구조.

# Intent

같은 값이 두 번 이상 들어가면 안 되는 모음이 필요할 때 쓴다. `list<T>`(3.1절
참조)는 순서 있는 중복 허용 목록이고, 이 패키지는 그와 대비되는 "중복 없는 모음"을
표준화된 형태로 제공한다.

# Domain

## Class: Set<T> implements Collection<T>

생성자:
- Set()
  설명: 빈 집합을 만든다.
- Set(items: list<T>)
  설명: items로 초기화한다. items 안에 중복이 있으면 한 번만 담긴다.

메서드:
[Static]
- of(items: list<T>) -> Set<T>
  설명: `Set(items)`와 같다. 호출부에서 타입을 더 짧게 쓰기 위한 편의 팩토리다.
- add(item: T) -> void
  설명: item을 집합에 추가한다. 이미 있으면 아무 일도 하지 않는다.
- remove(item: T) -> void
  설명: item을 집합에서 제거한다. 없으면 아무 일도 하지 않는다.
- has(item: T) -> boolean
  설명: item이 집합에 있는지 확인한다.
- size() -> int
  설명: 집합에 담긴 원소 개수를 반환한다.
- toList() -> list<T>
  설명: 집합의 원소들을 list로 변환한다. 순서는 보장하지 않는다.

불변식:
- 같은 값의 원소는 동시에 최대 한 번만 존재한다.

[`Collection<T>`](collection.md)를 구현하므로 `isEmpty()`는 따로 적지 않아도
기본 구현(`size() == 0`)을 그대로 물려받습니다.

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `Set<T>`를 타입으로 써서 자신의 멤버·변수를
선언합니다 (예: `members: Set<string>`).

# Constraints

- 타겟 언어에 대응하는 네이티브 집합 구조(C++ `std::unordered_set`, Python `set`,
  JavaScript `Set`, Java `HashSet` 등)가 있으면 그것을 그대로 활용한다. 없으면 이
  계약을 만족하도록 새로 구현한다.
- 원소의 동등성 비교 방식(구조적 동등 vs 참조 동등)은 타겟 언어의 관용적인 방식을
  따른다.

# Examples

## 예제: 중복 추가는 무시된다

호출 (순서대로): `s.add("a")`, `s.add("a")`, `s.size()`

기대 동작: `size()`는 `1`을 반환한다.

## 예제: 있는지 확인

호출 (순서대로): `s.add("a")`, `s.has("a")`, `s.has("b")`

기대 동작: 첫 번째 `has`는 `true`, 두 번째 `has`는 `false`를 반환한다.

# Open Points

- 반복(iterate) 순서, 초기 용량 힌트 등 성능 관련 세부사항은 AI 재량.
