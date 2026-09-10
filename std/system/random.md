#!specpp 0.1

# Meta

- name: std/system/random
- version: 0.1.0
- description: 난수를 생성하는 수단.

# Intent

무작위 값(정수, 실수, 불리언)이 필요할 때 쓴다. 시드(seed)를 고정하면 같은 순서의
난수를 재현할 수 있다.

# Domain

## Class: Random

생성자:
- Random()
  설명: 예측할 수 없는 시드(예: 현재 시각)로 초기화한다.
- Random(seed: int)
  설명: 주어진 seed로 초기화한다. 같은 seed로 만든 두 Random은 항상 같은 순서의
  값을 반환한다.

메서드:
- nextInt(min: int, max: int) -> int
  설명: min 이상 max 미만의 정수를 무작위로 반환한다.
- nextFloat() -> float
  설명: 0.0 이상 1.0 미만의 실수를 무작위로 반환한다.
- nextBoolean() -> boolean
  설명: true 또는 false를 무작위로 반환한다.

# Interface

## Library

다른 패키지는 `r = Random()` 또는 `r = Random(42)`로 인스턴스를 만든 뒤
`r.nextInt(1, 7)`처럼 씁니다.

# Constraints

- 타겟 언어의 네이티브 난수 생성기(C++ `<random>`, Python `random`, Java
  `java.util.Random`, JavaScript `Math.random` 등)에 매핑한다. 같은 seed에서
  타겟 언어마다 정확히 같은 수열이 나올 것까지는 보장하지 않는다 — "seed가
  같으면 그 언어·구현 안에서는 재현 가능하다"는 것만 보장한다.

# Examples

## 예제: 범위 안의 정수

호출: `Random(1).nextInt(1, 7)`

기대 동작: `1` 이상 `7` 미만의 정수 하나를 반환한다.

# Open Points

- 암호학적으로 안전한 난수(CSPRNG)는 이 패키지의 범위 밖이다 —
  [`std/system/crypto.md`](crypto.md)의 `SecureRandom`을 대신 쓴다.
