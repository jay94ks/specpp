#!specpp 0.1

# Meta

- name: std/text/string
- version: 0.1.0
- description: `string` 기본 타입에 대한 표준 조작 함수 모음.

# Intent

3.1절의 `string`은 타입 표기일 뿐 조작 방법을 정의하지 않는다. 자르기, 나누기,
바꾸기, 대소문자 변환처럼 문자열을 다루는 모든 언어가 공통으로 제공하는 연산을
표준화한다. 인스턴스를 만들 필요가 없는 정적 도구 모음이다.

# Domain

## Class: String

메서드:
[Static]
- length(text: string) -> int
[Static]
- toUpper(text: string) -> string
[Static]
- toLower(text: string) -> string
[Static]
- trim(text: string) -> string
  설명: 앞뒤 공백 문자를 제거한다.
[Static]
- split(text: string, separator: string) -> list<string>
  설명: separator를 기준으로 text를 나눈다. separator가 text에 없으면 text
  하나만 담긴 list를 반환한다.
[Static]
- join(items: list<string>, separator: string) -> string
  설명: `split`의 역연산 — items를 separator로 이어붙인다.
[Static]
- replace(text: string, target: string, replacement: string) -> string
  설명: text 안의 target을 모두 replacement로 바꾼다.
[Static]
- contains(text: string, part: string) -> boolean
[Static]
- indexOf(text: string, part: string) -> int
  설명: part가 처음 나타나는 위치(0부터 시작)를 반환한다. 없으면 `-1`.
[Static]
- substring(text: string, start: int, end: int) -> string
  설명: `[start, end)` 구간을 반환한다. 범위를 벗어나면 오류를 낸다.
[Static]
- format(template: string, args: list<string>) -> string
  설명: template 안의 자리표시자(정확한 표기는 타겟 언어의 관용적인 포맷 문자열
  방식을 따른다)를 args로 순서대로 채운다.

# Interface

## Library

다른 패키지는 `String.split(text, ",")`처럼 클래스 이름으로 바로 씁니다.

# Constraints

- 타겟 언어의 네이티브 문자열 메서드/모듈(대부분의 언어는 문자열 자체가 이런
  메서드를 갖고 있다 — 예: Python `str`, JavaScript `String.prototype`, Java
  `String`, C# `string`)에 매핑한다. 굳이 `String.xxx(text)` 형태의 정적 호출로
  생성할 필요는 없다 — 타겟 언어가 `text.xxx()` 형태를 관용적으로 쓴다면 그렇게
  구현해도 된다. 이 계약은 "이런 연산이 존재해야 한다"는 것이지 호출 형태를
  강제하는 것이 아니다.
- 인덱스는 0부터 시작하고, 유니코드 코드 포인트 단위로 다룬다(바이트 단위가
  아니다).

# Examples

## 예제: 나누고 다시 합친다

호출: `String.join(String.split("a,b,c", ","), "-")`

기대 동작: `"a-b-c"`를 반환한다.

## 예제: 없는 부분 문자열

호출: `String.indexOf("hello", "z")`

기대 동작: `-1`을 반환한다.

# Open Points

- 정규식 기반 검색·치환은 [`std/text/regex.md`](regex.md)에서 다룬다.
- 유니코드 정규화(NFC/NFD 등)는 이 버전의 범위 밖이다.
