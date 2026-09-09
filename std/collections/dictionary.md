#!specpp 0.1

# Meta

- name: std/collections/dictionary
- version: 0.1.0
- description: 키(key)로 값(value)을 찾아보는 연관 배열.

# Intent

`map<K, V>`(3.1절 primitive 타입)에 대한 구체적인 조작 수단이 필요할 때 쓴다.
이름·아이디 같은 키로 값을 빠르게 찾아야 하는 모든 상황에 쓰인다.

# Domain

## Class: Dictionary<K, V>

생성자:
- Dictionary()
  설명: 빈 딕셔너리를 만든다.

메서드:
[Static]
- of(entries: map<K, V>) -> Dictionary<K, V>
  설명: entries로 초기화된 Dictionary를 만든다.
- set(key: K, value: V) -> void
  설명: key에 value를 저장한다. 이미 key가 있으면 값을 덮어쓴다.
- get(key: K) -> V?
  설명: key에 대응하는 값을 반환한다. 없으면 null을 반환한다.
- has(key: K) -> boolean
  설명: key가 있는지 확인한다.
- remove(key: K) -> void
  설명: key와 그 값을 제거한다. 없으면 아무 일도 하지 않는다.
- keys() -> list<K>
  설명: 담긴 모든 키를 list로 반환한다. 순서는 보장하지 않는다.
- values() -> list<V>
  설명: 담긴 모든 값을 list로 반환한다. 순서는 보장하지 않는다.
- size() -> int
  설명: 담긴 키-값 쌍의 개수를 반환한다.
- isEmpty() -> boolean
  설명: 비어있는지 확인한다.

불변식:
- 같은 키는 동시에 최대 하나의 값만 가진다.

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `Dictionary<K, V>`를 타입으로 써서 멤버·변수를
선언합니다.

# Constraints

- 타겟 언어에 대응하는 네이티브 연관 배열(C++ `std::unordered_map`, Python
  `dict`, JavaScript `Map`, Java `HashMap` 등)이 있으면 그것을 그대로 활용한다.
  없으면 이 계약을 만족하도록 새로 구현한다.

# Examples

## 예제: 저장하고 조회한다

호출 (순서대로): `d.set("a", 1)`, `d.get("a")`, `d.get("b")`

기대 동작: 첫 번째 `get`은 `1`을, 두 번째 `get`은 `null`을 반환한다.

# Open Points

- 반복 순서, 초기 용량 힌트 등 성능 관련 세부사항은 AI 재량.
