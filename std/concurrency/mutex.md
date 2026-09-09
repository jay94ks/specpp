#!specpp 0.1

# Meta

- name: std/concurrency/mutex
- version: 0.1.0
- description: 한 번에 하나의 스레드만 들어갈 수 있는 임계 구역(critical section)을 만드는 잠금.

# Intent

[`atomic`](atomic.md)이나 CAS 기반 컬렉션으로 표현하기엔 너무 복잡한 로직 —
여러 멤버 변수를 한꺼번에 일관되게 바꿔야 하는 경우 — 을 여러 스레드로부터
보호해야 할 때 쓴다.

# Domain

## Class: Mutex

생성자:
- Mutex()

메서드:
- lock() -> void
  설명: 잠금을 얻을 때까지 블로킹(대기)한다. 이미 다른 스레드가 잠그고 있으면
  풀릴 때까지 기다린다.
- unlock() -> void
  설명: 잠금을 푼다. 이 스레드가 잠그지 않은 Mutex를 풀려고 하면 오류를 낸다.
- tryLock() -> boolean
  설명: 즉시 잠금을 시도한다. 이미 다른 스레드가 잠그고 있으면 기다리지 않고
  바로 false를 반환한다. 성공하면 true를 반환하고, 이 경우 반드시 나중에
  `unlock()`을 호출해야 한다.

불변식:
- 동시에 `lock()`(또는 성공한 `tryLock()`)을 가진 스레드는 최대 하나뿐이다.

# Interface

## Library

다른 패키지는 `m = Mutex()`를 멤버·전역으로 두고, 임계 구역 앞뒤로
`m.lock()`/`m.unlock()`을 짝지어 씁니다. (대상 언어에 `with`/`using`처럼 스코프
종료 시 자동으로 풀어주는 관용구가 있으면 그것을 활용해도 된다 — 예외가 나도
반드시 풀리도록 하는 것을 권장한다.)

# Constraints

- 타겟 언어의 네이티브 뮤텍스(C++ `std::mutex`, Python
  `threading.Lock`, Java `synchronized`/`ReentrantLock`, C#
  `lock`/`Monitor` 등)에 매핑한다.
- 재진입(같은 스레드가 이미 잠근 Mutex를 다시 잠그는 것) 허용 여부는 타겟
  언어의 기본 동작을 따른다 — 이 계약은 규정하지 않는다.

# Examples

## 예제: 배타적 접근

호출: 스레드 A가 `m.lock()`을 잡고 있는 동안 스레드 B가 `m.tryLock()`을
호출한다.

기대 동작: B의 `tryLock()`은 즉시 `false`를 반환한다 (기다리지 않는다). A가
`unlock()`하면 그 뒤의 `tryLock()`은 `true`를 반환할 수 있다.

# Open Points

- 재진입 허용 여부, 데드락 감지는 이 버전의 범위 밖이다.
