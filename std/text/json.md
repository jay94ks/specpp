#!specpp 0.1

# Meta

- name: std/text/json
- version: 0.1.0
- description: JSON 문자열과 값 사이의 직렬화·역직렬화.

# Intent

파일이나 네트워크로 구조화된 데이터를 주고받을 때 가장 흔히 쓰는 형식인 JSON을
읽고 쓰기 위한 것이다. [`std/net/httpclient`](../net/httpclient.md)의
`HttpResponse.body`나 [`std/io/file`](../io/file.md)로 읽은 텍스트를 실제
값으로 바꿀 때 함께 쓴다.

# Domain

## Class: Json

메서드:
[Static]
- stringify(value: any) -> string
  설명: 값(기본 타입, list, Dictionary, 또는 멤버가 있는 클래스 인스턴스)을 JSON
  문자열로 직렬화한다.
[Static]
- parse(text: string) -> any
  설명: JSON 문자열을 파싱해 값으로 되돌린다. JSON 객체는
  [`Dictionary<string, any>`](../collections/dictionary.md)로, JSON 배열은
  `list<any>`로 표현한다. text가 올바른 JSON이 아니면 오류를 낸다.

# Interface

## Library

다른 패키지는 `Json.stringify(value)`, `Json.parse(text)`처럼 클래스 이름으로
바로 씁니다.

# Constraints

- 타겟 언어의 네이티브 JSON 라이브러리(Python `json`, JavaScript
  `JSON.parse`/`JSON.stringify`, Java `Jackson`/`org.json`, C#
  `System.Text.Json` 등)에 매핑한다.
- 정해진 클래스 타입으로 역직렬화(예: `Json.parse<Task>(text)`처럼 제네릭
  메서드로 바로 특정 클래스 인스턴스를 만드는 것)는 이 버전의 범위 밖이다 —
  `parse`는 항상 원시 구조(Dictionary/list/기본 타입)로만 반환한다.

# Examples

## 예제: 왕복 변환

호출: `Json.parse(Json.stringify(42))`

기대 동작: `42`를 반환한다.

## 예제: 객체 파싱

호출: `Json.parse("{\"a\": 1}").get("a")`

기대 동작: `1`을 반환한다.

# Open Points

- 특정 클래스로의 직접 역직렬화, 필드 이름 매핑 규칙(camelCase ↔ snake_case
  등)은 다음 버전에서 다룬다.
