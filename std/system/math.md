#!specpp 0.1

# Meta

- name: std/system/math
- version: 0.1.0
- description: 기본적인 수학 상수와 함수 모음.

# Intent

제곱근, 거듭제곱, 반올림처럼 자주 쓰는 수학 연산과 상수를, 매번 직접 구현하지
않고 공통된 이름으로 쓰기 위한 것이다. 인스턴스를 만들 필요가 없는, 순전히
정적(static)인 도구 모음이다.

# Domain

## Class: Math

멤버:
[Static]
- PI: float — 원주율 근사값.
[Static]
- E: float — 자연로그의 밑(e) 근사값.

메서드:
[Static]
- abs(x: float) -> float
  설명: x의 절댓값을 반환한다.
[Static]
- sqrt(x: float) -> float
  설명: x의 제곱근을 반환한다. x가 음수면 오류(3.1절 타입 추론 예외가 아니라
  런타임 오류)로 처리한다.
[Static]
- pow(base: float, exponent: float) -> float
  설명: base의 exponent제곱을 반환한다.
[Static]
- min(a: float, b: float) -> float
[Static]
- max(a: float, b: float) -> float
[Static]
- floor(x: float) -> int
  설명: x보다 크지 않은 가장 큰 정수를 반환한다.
[Static]
- ceil(x: float) -> int
  설명: x보다 작지 않은 가장 작은 정수를 반환한다.
[Static]
- round(x: float) -> int
  설명: x를 가장 가까운 정수로 반올림한다. `.5`는 타겟 언어의 관용적인 반올림
  규칙(예: 은행가 반올림 vs 사사오입)을 따른다.

# Interface

## Library

다른 패키지는 인스턴스를 만들지 않고 `Math.sqrt(2)`, `Math.PI`처럼 클래스
이름으로 바로 씁니다.

# Constraints

- 타겟 언어의 네이티브 수학 라이브러리(C++ `<cmath>`, Python `math`, Java
  `Math`, JavaScript `Math` 등)에 그대로 매핑한다.

# Examples

## 예제: 제곱근

호출: `Math.sqrt(16)`

기대 동작: `4`를 반환한다.

## 예제: 최댓값

호출: `Math.max(3, 7)`

기대 동작: `7`을 반환한다.

# Open Points

- 삼각함수(sin/cos/tan), 로그(log) 등 추가 함수는 다음 버전에서 필요에 따라
  추가한다.
