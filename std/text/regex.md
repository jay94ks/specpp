#!specpp 0.1

# Meta

- name: std/text/regex
- version: 0.1.0
- description: 정규 표현식으로 문자열을 검사·검색·치환하는 수단.

# Intent

`String`(3.4절 [`string.md`](string.md))의 `contains`/`indexOf`로는 표현할 수
없는, 패턴 기반의 문자열 검사·검색·치환이 필요할 때 쓴다.

# Domain

## Class: Regex

생성자:
- Regex(pattern: string)
  설명: pattern을 정규 표현식으로 컴파일한다. pattern이 올바르지 않으면 오류를
  낸다. 문법은 PCRE(Perl 호환 정규식)에 준한다.

메서드:
- test(text: string) -> boolean
  설명: text 안에 이 패턴과 일치하는 부분이 있는지 확인한다.
- match(text: string) -> string?
  설명: text 안에서 이 패턴과 처음 일치하는 부분 문자열을 반환한다. 없으면
  null.
- matchAll(text: string) -> list<string>
  설명: text 안에서 이 패턴과 일치하는 모든 부분을 순서대로 반환한다.
- replace(text: string, replacement: string) -> string
  설명: text 안에서 이 패턴과 일치하는 첫 부분을 replacement로 바꾼다.
- replaceAll(text: string, replacement: string) -> string
  설명: 일치하는 모든 부분을 replacement로 바꾼다.

# Interface

## Library

다른 패키지는 `r = Regex("[0-9]+")`로 컴파일한 뒤 `r.test(text)`처럼 씁니다.

# Constraints

- 타겟 언어의 네이티브 정규식 엔진(C++ `<regex>`, Python `re`, Java
  `java.util.regex`, JavaScript `RegExp`, C# `System.Text.RegularExpressions`
  등)에 매핑한다. 문법 차이(예: 후방탐색 지원 여부)는 타겟 언어의 한계를
  따른다 — 이 계약이 모든 PCRE 기능의 이식을 보장하지는 않는다.

# Examples

## 예제: 존재 확인

호출: `Regex("[0-9]+").test("room 42")`

기대 동작: `true`를 반환한다.

## 예제: 모두 치환

호출: `Regex("[0-9]+").replaceAll("a1b22c333", "#")`

기대 동작: `"a#b#c#"`를 반환한다.

# Open Points

- 캡처 그룹 추출(`match`가 그룹별 결과를 담은 구조를 반환하는 기능)은 다음
  버전에서 다룬다 — 이 버전의 `match`/`matchAll`은 일치한 전체 문자열만
  반환한다.
