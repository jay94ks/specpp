#!specpp 0.1

# Meta

- name: std/system/timespan
- version: 0.1.0
- description: 두 시각 사이의 기간(duration)을 표현.

# Intent

"3일", "90초"처럼 시각이 아니라 **길이**를 나타내야 할 때 쓴다. `datetime`
(SPEC.md 3.1절의 primitive 타입)이 특정 시점을 가리킨다면, `TimeSpan`은 그 사이의
간격을 가리킨다.

# Domain

## Class: TimeSpan

메서드:
[Static]
- fromSeconds(value: float) -> TimeSpan
[Static]
- fromMinutes(value: float) -> TimeSpan
[Static]
- fromHours(value: float) -> TimeSpan
[Static]
- fromDays(value: float) -> TimeSpan
- totalSeconds() -> float
  설명: 이 기간 전체를 초 단위 실수로 환산해 반환한다.
- add(other: TimeSpan) -> TimeSpan
  설명: 두 기간을 더한 새 TimeSpan을 반환한다 (원본은 바뀌지 않는다).
- compareTo(other: TimeSpan) -> int
  설명: 이 기간이 other보다 짧으면 음수, 길면 양수, 같으면 0을 반환한다.

# Interface

## Library

다른 패키지는 `TimeSpan.fromMinutes(5)`처럼 정적 메서드로 만듭니다.

# Constraints

- 타겟 언어의 네이티브 기간 타입(C++ `std::chrono::duration`, Python
  `datetime.timedelta`, Java `Duration`, JavaScript는 보통 밀리초 정수 등)에
  매핑한다.

# Examples

## 예제: 초 단위 환산

호출: `TimeSpan.fromMinutes(2).totalSeconds()`

기대 동작: `120`을 반환한다.

# Open Points

- 음수 기간 허용 여부는 AI 재량.
