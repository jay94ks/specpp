#!specpp 0.1

# Meta

- name: std/stderr
- version: 0.1.0
- description: 표준 에러(오류·진단 출력)에 텍스트를 쓰는 가장 기본적인 수단.

# Intent

프로그램이 오류·경고·진단 메시지처럼, 정상 출력(stdout)과 구분해서 내보내야 할
텍스트를 쓸 때 사용한다. [`stdout`](stdout.md)과 마찬가지로 **새로 구현할
대상이 아니라 이미 존재하는 실체에 대한 설명**이다 (SPEC.md 1.2절의 실체 명세
패키지). AI는 이 계약을 그 언어의 네이티브 표준 에러(예: C++의 `std::cerr`,
Python의 `sys.stderr`, JavaScript의 `console.error`, Java의 `System.err`)에
바인딩한다.

# Domain

## Interface: Stderr

메서드:
- print(text: string) -> void
  설명: 줄바꿈 없이 text를 표준 에러에 쓴다.
- println(text: string) -> void
  설명: text를 쓰고 그 뒤에 줄바꿈을 추가한다.
- flush() -> void
  설명: 버퍼링된 출력을 즉시 내보낸다. 관례적으로 표준 에러는 즉시 반영되는(버퍼링
  없는) 경우가 많으므로, 그런 런타임에서는 아무 일도 하지 않아도 된다 (no-op 허용).

## globals

package_like stderr: Stderr — 이 패키지를 참조하는 쪽에서 쓰는 전역 인스턴스.
AI가 타겟 언어의 네이티브 표준 에러에 바인딩한다.

# Interface

## Library

이 패키지를 참조하는 다른 패키지는 `stderr` 전역(Domain 참조)을 가져와
`stderr.println(...)`처럼 씁니다.

# Constraints

- 이 패키지 자체의 동작을 새로 구현하지 않는다 — 타겟 언어의 네이티브 표준 에러에
  그대로 위임(바인딩)한다.
- stdout과 별개의 스트림으로 다룬다 — 둘을 하나로 합치지 않는다.

# Examples

## 예제: 오류 메시지 출력

호출: `stderr.println("✘ title은 필수입니다")`

기대 동작: 표준 에러에 `✘ title은 필수입니다`를 쓰고 줄바꿈한다. 표준 출력에는
아무것도 쓰지 않는다.

# Open Points

- 패키지가 "생성 대상"이 아니라 "실체 명세"임을 나타내는 정식 표기(1.2절에서
  계속 정의 중인 부분)가 정해지면, 이 파일의 Meta/Intent를 그 표기로 맞춘다.
