#!specpp 0.1

# Meta

- name: std/system/datetime
- version: 0.1.0
- description: 특정 시점(날짜와 시각)을 표현하고 다루는 수단.

# Intent

3.1절의 `datetime` 타입은 "날짜/시각 값"이라는 표기일 뿐, 그 값을 어떻게 만들고
비교하고 가공하는지는 정의하지 않는다. 이 패키지는 그 조작 방법을 표준화한다.
[`TimeSpan`](timespan.md)과 함께 써서 시각 사이의 간격을 다룬다.

# Domain

## Class: DateTime

생성자:
- DateTime(year: int, month: int, day: int, hour: int, minute: int, second: int)
  설명: 주어진 연-월-일 시:분:초로 특정 시점을 만든다. 존재하지 않는 날짜/시각
  (예: 2월 30일)이면 오류를 낸다.
- DateTime(year: int, month: int, day: int)
  설명: 시:분:초를 `0:0:0`으로 간주한다 (자정).

메서드:
[Static]
- now() -> DateTime
  설명: 현재 지역 시각을 담은 DateTime을 만들어 반환한다.
[Static]
- utcNow() -> DateTime
  설명: 현재 UTC 시각을 담은 DateTime을 만들어 반환한다.
- addDays(days: float) -> DateTime
  설명: days만큼 뒤(음수면 앞)의 시각을 새 DateTime으로 반환한다 (원본은 바뀌지
  않는다).
- add(span: TimeSpan) -> DateTime
  설명: span만큼 뒤의 시각을 새 DateTime으로 반환한다.
- compareTo(other: DateTime) -> int
  설명: 이 시각이 other보다 이르면 음수, 늦으면 양수, 같으면 0을 반환한다.
- toString() -> string
  설명: 사람이 읽을 수 있는 형태의 문자열로 변환한다. 정확한 형식은 타겟 언어의
  관용적인 기본 형식을 따른다.

# Interface

## Library

다른 패키지는 `DateTime.now()`처럼 정적 메서드로 인스턴스를 얻고, 필요하면
`.addDays(1)`처럼 가공합니다.

# Constraints

- 타겟 언어의 네이티브 날짜·시각 타입(C++ `std::chrono::system_clock`, Python
  `datetime.datetime`, Java `java.time.Instant`/`LocalDateTime`, JavaScript
  `Date` 등)에 매핑한다.
- 시간대(timezone) 처리는 `now()`(지역)와 `utcNow()`(UTC)의 구분 정도만 다룬다
  — 임의 시간대 변환은 이 버전의 범위 밖이다.

# Examples

## 예제: 하루 뒤

호출: `DateTime.now().addDays(1).compareTo(DateTime.now())`

기대 동작: 양수를 반환한다 (하루 뒤가 항상 더 늦은 시각이므로).

## 예제: 특정 날짜를 직접 만든다

호출: `DateTime(2024, 1, 1).compareTo(DateTime(2024, 1, 2))`

기대 동작: 음수를 반환한다 (1월 1일이 1월 2일보다 이르므로).

# Open Points

- 특정 형식으로 파싱·포매팅(`parse`, `format(pattern)`)은 다음 버전에서
  [`Convert`](convert.md)와 함께 다룬다.
