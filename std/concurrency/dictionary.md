#!specpp 0.1

# Meta

- name: std/concurrency/dictionary
- version: 0.1.0
- description: 여러 스레드가 동시에 접근해도 안전한 키-값 저장소(CAS 기반).

# Intent

[`std/collections/dictionary`](../collections/dictionary.md)와 같은 동작이
필요하지만, 여러 스레드가 동시에 읽고 쓸 수 있어야 할 때 쓴다.

# Domain

## Class: ConcurrentDictionary<K, V>

생성자:
- ConcurrentDictionary()
  설명: 빈 딕셔너리를 만든다.

메서드:
- set(key: K, value: V) -> void
  설명: key에 value를 저장한다. 이미 key가 있으면 값을 덮어쓴다. 여러 스레드가
  동시에 호출해도 안전하다.
- get(key: K) -> V?
  설명: key에 대응하는 값을 반환한다. 없으면 null을 반환한다.
- has(key: K) -> boolean
- remove(key: K) -> void
  설명: key와 그 값을 제거한다. 없으면 아무 일도 하지 않는다.
- getOrAdd(key: K, factory: () -> V) -> V
  설명: key가 이미 있으면 그 값을 반환한다. 없으면 factory()를 호출해 값을 만들고
  key에 저장한 뒤 그 값을 반환한다. 여러 스레드가 같은 key로 동시에 호출하면,
  **그 key에 최종적으로 저장되는 값은 단 하나이고 모든 호출자가 그 값을
  돌려받는다**는 것만 보장한다. `factory` 자체가 몇 번 호출되는지는 구현 방식에
  따라 다르다 — 락 기반 구현이면 보통 한 번만 호출되지만, CAS 기반의 낙관적
  구현이면 여러 스레드가 각자 factory를 호출한 뒤 그 중 하나의 결과만 채택하고
  나머지는 버릴 수 있다. 따라서 factory에 부작용(side effect)이 있으면 안 된다
  — 순수하게 값만 만들어 반환해야 한다.
- size() -> int
  설명: 담긴 키-값 쌍의 개수를 반환한다. 동시 접근 중에는 근사값일 수 있다.
- isEmpty() -> boolean

불변식:
- 같은 키는 동시에 최대 하나의 값만 가진다. 동시에 여러 스레드가 같은 key를
  set()해도 경쟁 상태로 값이 깨지지 않는다(마지막에 완료된 set()의 값으로
  정리된다).

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `ConcurrentDictionary<K, V>`를 타입으로 써서
멤버·변수를 선언합니다.

# Constraints

- 락(lock) 기반이든 [`Atomic<T>`](atomic.md) 기반 CAS든, 동시성 안전성 보장(위
  불변식)만 지키면 구현 방식은 AI 재량이다.
- 타겟 언어에 성숙한 동시성 딕셔너리(Java `ConcurrentHashMap`, C#
  `ConcurrentDictionary` 등)가 있으면 그대로 활용한다.

# Examples

## 예제: 동시에 getOrAdd해도 같은 값으로 수렴한다

호출: 스레드 A와 스레드 B가 동시에 `d.getOrAdd("count", () -> makeValue())`를
호출한다.

기대 동작: A와 B는 항상 같은 값을 돌려받고, 그 뒤 `d.get("count")`도 같은 값을
반환한다. (`makeValue()`가 몇 번 실행되었는지는 구현에 따라 다를 수 있다.)

# Open Points

- 반복(iterate) 중 다른 스레드의 수정에 대한 정확한 가시성 규칙은 타겟 언어의
  기본 보장을 따른다.
- factory가 반드시 정확히 한 번만 호출되어야 하는 "단 한 번 초기화" 용도가
  필요하면, 이 메서드 대신 별도의 잠금(lock)이나 지연 초기화(lazy
  initialization) 패턴을 직접 구성해야 한다 — `getOrAdd`는 그런 보장을 하지
  않는다.
