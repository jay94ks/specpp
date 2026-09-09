#!specpp 0.1

# Meta

- name: std/stdin
- version: 0.1.0
- description: 표준 입력(콘솔)에서 텍스트를 읽는 가장 기본적인 수단.

# Intent

프로그램이 사용자나 파이프로부터 텍스트를 입력받아야 할 때 쓴다.
[`stdout`](stdout.md), [`stderr`](stderr.md)과 마찬가지로 **새로 구현할 대상이
아니라 이미 존재하는 실체에 대한 설명**이다 (SPEC.md 1.2절의 실체 명세 패키지).
AI는 이 계약을 그 언어의 네이티브 표준 입력(예: C++의 `std::cin`, Python의
`sys.stdin`/`input()`, JavaScript의 `process.stdin`, Java의 `System.in`)에
바인딩한다.

# Domain

## Interface: Stdin

메서드:
- readLine() -> string?
  설명: 표준 입력에서 한 줄을 읽어 반환한다. 반환값에 줄바꿈 문자는 포함하지
  않는다. 더 읽을 내용이 없으면(EOF) null을 반환한다.
- readAll() -> string
  설명: 표준 입력이 끝날 때까지(EOF) 남은 내용을 전부 읽어 하나의 문자열로
  반환한다. 더 읽을 내용이 없었다면 빈 문자열을 반환한다.
- readChar() -> string?
  설명: 문자 하나를 읽어 반환한다. 더 읽을 내용이 없으면(EOF) null을 반환한다.

## globals

package_like stdin: Stdin — 이 패키지를 참조하는 쪽에서 쓰는 전역 인스턴스. AI가
타겟 언어의 네이티브 표준 입력에 바인딩한다.

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `stdin` 전역(Domain 참조)을 가져와
`stdin.readLine()`처럼 씁니다.

# Constraints

- 이 패키지 자체의 동작을 새로 구현하지 않는다 — 타겟 언어의 네이티브 표준
  입력에 그대로 위임(바인딩)한다.
- 입력 파싱(숫자 변환, 토큰 분리 등)은 이 패키지의 범위가 아니다 — 호출하는 쪽이
  `readLine()`/`readAll()`의 결과를 직접 해석한다.

# Examples

## 예제: 한 줄 읽기

입력 스트림: `우유 사기\n`

호출: `stdin.readLine()`

기대 동작: `"우유 사기"`를 반환한다 (줄바꿈 문자는 포함하지 않는다).

## 예제: 더 읽을 내용이 없을 때

입력 스트림: (이미 끝까지 읽은 상태, EOF)

호출: `stdin.readLine()`

기대 동작: `null`을 반환한다.

# Open Points

- 패키지가 "생성 대상"이 아니라 "실체 명세"임을 나타내는 정식 표기(1.2절에서
  계속 정의 중인 부분)가 정해지면, 이 파일의 Meta/Intent를 그 표기로 맞춘다.
