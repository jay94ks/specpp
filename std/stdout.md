#!specpp 0.1

# Meta

- name: std/stdout
- version: 0.1.0
- description: 표준 출력(콘솔)에 텍스트를 쓰는 가장 기본적인 수단.

# Intent

프로그램이 사람이 읽을 텍스트를 콘솔(표준 출력)에 내보내야 할 때 쓴다. 모든 타겟
언어·런타임이 이미 표준 출력 개념을 갖고 있으므로, 이 패키지는 **새로 구현할 대상이
아니라 이미 존재하는 실체에 대한 설명**이다 (SPEC.md 1.2절의 실체 명세 패키지).
AI는 이 계약을 그 언어의 네이티브 표준 출력(예: C++의 `std::cout`, Python의
`print`, JavaScript의 `console.log`, Java의 `System.out`)에 바인딩한다.

# Domain

## Interface: Stdout

메서드:
- print(text: string) -> void
  설명: 줄바꿈 없이 text를 표준 출력에 쓴다.
- println(text: string) -> void
  설명: text를 쓰고 그 뒤에 줄바꿈을 추가한다.
- flush() -> void
  설명: 버퍼링된 출력을 즉시 내보낸다. 런타임이 버퍼링을 하지 않는다면 아무 일도
  하지 않아도 된다 (no-op 허용).

## globals

package_like stdout: Stdout — 이 패키지를 참조하는 쪽에서 쓰는 전역 인스턴스.
AI가 타겟 언어의 네이티브 표준 출력에 바인딩한다.

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `stdout` 전역(Domain 참조)을 가져와
`stdout.print(...)`, `stdout.println(...)`처럼 씁니다.

# Constraints

- 이 패키지 자체의 동작을 새로 구현하지 않는다 — 타겟 언어의 네이티브 표준 출력에
  그대로 위임(바인딩)한다.
- 표준 에러(stderr), 파일 리다이렉션, 색상 출력 등은 이 패키지의 범위가 아니다.

# Examples

## 예제: 줄바꿈 있는 출력

호출: `stdout.println("Hello World")`

기대 동작: 표준 출력에 `Hello World`를 쓰고 줄바꿈한다.

## 예제: 줄바꿈 없는 출력

호출 (순서대로): `stdout.print("A")`, `stdout.print("B")`

기대 동작: 표준 출력에 `AB`가 줄바꿈 없이 이어서 출력된다.

# Open Points

- 패키지가 "생성 대상"이 아니라 "실체 명세"임을 나타내는 정식 표기(1.2절에서
  계속 정의 중인 부분)가 정해지면, 이 파일의 Meta/Intent를 그 표기로 맞춘다.
