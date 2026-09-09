#!specpp 0.1

# Meta

- name: std/system/convert
- version: 0.1.0
- description: 기본 타입 사이의 변환·파싱.

# Intent

문자열로 들어온 값을 숫자로 바꾸거나, 값을 사람이 읽을 문자열로 바꾸는 것처럼
기본 타입 사이를 오가는 변환을 표준화한다.

# Domain

## Class: Convert

메서드:
[Static]
- toInt(text: string) -> int
  설명: 문자열을 정수로 해석한다. 정수로 해석할 수 없으면 오류를 낸다.
[Static]
- toFloat(text: string) -> float
  설명: 문자열을 실수로 해석한다. 실수로 해석할 수 없으면 오류를 낸다.
[Static]
- toBoolean(text: string) -> boolean
  설명: `"true"`/`"false"`(대소문자 무시)를 불리언으로 해석한다. 그 외 값이면
  오류를 낸다.
[Static]
- toString(value: int | float | boolean) -> string
  설명: 기본 타입 값을 사람이 읽을 수 있는 문자열로 바꾼다.

# Interface

## Library

다른 패키지는 `Convert.toInt(text)`처럼 클래스 이름으로 바로 씁니다.

# Constraints

- 타겟 언어의 네이티브 파싱·포매팅 함수(C++ `std::stoi`/`std::to_string`,
  Python `int()`/`str()`, Java `Integer.parseInt`/`String.valueOf`, JavaScript
  `parseInt`/`String()` 등)에 매핑한다.
- `toInt`/`toFloat`/`toBoolean`은 실패를 조용히 넘기지 않는다 — 해석할 수 없는
  입력은 반드시 오류로 알린다 (3.1절 "넘겨짚지 않는다" 원칙과 같은 태도).

# Examples

## 예제: 문자열을 정수로

호출: `Convert.toInt("42")`

기대 동작: `42`를 반환한다.

## 예제: 해석할 수 없으면 오류

호출: `Convert.toInt("abc")`

기대 동작: 오류가 발생한다 (`42` 같은 값을 억지로 만들어내지 않는다).

# Open Points

- 진법 지정(16진수 파싱 등), 로캘(locale)에 따른 형식 차이는 이 버전의 범위 밖이다.
