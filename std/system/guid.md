#!specpp 0.1

# Meta

- name: std/system/guid
- version: 0.1.0
- description: 전역적으로 유일한(사실상 충돌하지 않는) 식별자.

# Intent

여러 프로세스·기기에 걸쳐서도 사실상 겹치지 않는 고유 식별자가 필요할 때 쓴다.
(패키지 안에서만 고유하면 되는 값은 그냥 `uuid` 타입이나 3.4절의 `id: int` 순번
방식으로 충분하다 — 이 패키지는 그보다 강한 전역 유일성이 필요할 때 쓴다.)

# Domain

## Class: Guid

메서드:
[Static]
- newGuid() -> Guid
  설명: 새로운, 사실상 다른 모든 Guid와 겹치지 않는 값을 만들어 반환한다.
[Static]
- parse(text: string) -> Guid
  설명: 표준 문자열 표현(예: `"550e8400-e29b-41d4-a716-446655440000"`)을
  Guid로 해석한다. 형식이 올바르지 않으면 오류를 낸다.
- toString() -> string
  설명: 표준 문자열 표현으로 변환한다.
- equals(other: Guid) -> boolean
  설명: 같은 값을 나타내는지 비교한다.

# Interface

## Library

다른 패키지는 `Guid.newGuid()`로 새 값을 만들고, `uuid` 타입 자리에 필요하면
이 클래스를 씁니다.

# Constraints

- 타겟 언어의 네이티브 GUID/UUID 구현(C++ 플랫폼 API 또는 라이브러리, Python
  `uuid.uuid4()`, Java `java.util.UUID`, JavaScript `crypto.randomUUID()` 등)에
  매핑한다. 버전(v4 등)은 AI 재량으로 정하되, 무작위성 기반으로 사실상 충돌하지
  않아야 한다는 요구는 반드시 지킨다.

# Examples

## 예제: 왕복 변환

호출: `Guid.parse(g.toString())`

기대 동작: 원래의 `g`와 `equals()`로 같다고 판정된다.

# Open Points

- 특정 버전(v4, v7 등)을 강제할지는 다음 버전에서 다룬다.
