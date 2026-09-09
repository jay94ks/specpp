#!specpp 0.1

# Meta

- name: std/net/uri
- version: 0.1.0
- description: URI 문자열을 구성 요소로 분해해 다루는 수단.

# Intent

`"https://example.com:8443/path?query=1"`처럼 URI/URL 형태의 문자열을 scheme,
host, port, path, query로 나눠 다뤄야 할 때 쓴다.

# Domain

## Class: Uri

생성자:
- Uri(text: string)
  설명: text를 파싱한다. 형식이 올바르지 않으면 오류를 낸다.

메서드:
- scheme() -> string
  설명: `"https"`처럼 프로토콜 부분을 반환한다.
- host() -> string
- port() -> int
  설명: 명시적 포트가 없으면 scheme에 맞는 기본 포트(예: http=80, https=443)를
  반환한다.
- path() -> string
- query() -> string?
  설명: `?` 뒤의 쿼리 문자열. 없으면 null.
- toString() -> string
  설명: 다시 전체 URI 문자열로 조립해 반환한다.

# Interface

## Library

다른 패키지는 `Uri(text)`로 만들고 각 접근 메서드로 구성 요소를 읽습니다.

# Constraints

- 타겟 언어의 네이티브 URI 파서(C++ 라이브러리, Python `urllib.parse`, Java
  `java.net.URI`, JavaScript `URL` 등)에 매핑한다.

# Examples

## 예제: 구성 요소 분해

호출: `Uri("https://example.com:8443/a/b?x=1").host()`

기대 동작: `"example.com"`을 반환한다.

# Open Points

- 상대 URI, 퍼센트 인코딩·디코딩 세부사항은 이 버전의 범위 밖이다.
