#!specpp 0.1

# Meta

- name: std/text/encoding
- version: 0.1.0
- description: 바이트를 텍스트로, 텍스트를 바이트로 안전하게 옮기는 인코딩(Base64/Hex/URL)에 대한 추상 계약.

# Intent

바이너리 데이터를 JSON 문자열이나 URL 안에 넣어야 할 때, 또는
[`std/system/crypto.md`](../system/crypto.md)의 해시·암호화 결과
(`bytes`)를 사람이 읽거나 로그에 남길 수 있는 문자열로 바꿔야 할 때
쓴다.

# Domain

## Class: Base64

[Static]
- encode(data: bytes) -> string
- decode(text: string) -> bytes
  설명: 유효하지 않은 Base64 문자열이면 오류를 낸다.
- encodeUrlSafe(data: bytes) -> string
  설명: URL·파일 경로에 안전한 변형(`+`/`/` 대신 `-`/`_`)이다 — 토큰,
  세션 ID를 URL에 그대로 넣어야 할 때 쓴다.

## Class: Hex

[Static]
- encode(data: bytes) -> string
  설명: 소문자 16진수 문자열을 반환한다(예: `[255]` → `"ff"`).
- decode(text: string) -> bytes
  설명: 대소문자를 모두 허용한다. 길이가 홀수이거나 16진수가 아닌
  문자가 있으면 오류를 낸다.

## Class: UrlEncoding

[Static]
- encode(text: string) -> string
  설명: URL 쿼리 문자열에 안전하게 넣을 수 있게 퍼센트 인코딩한다
  (공백은 `%20` 또는 `+`, 구현이 관용적으로 정한다).
- decode(text: string) -> string

# Interface

## Library

`Base64.encode(hashBytes)`처럼 이진 데이터를 문자열로 바꿔 저장·전송하고,
받은 쪽에서 `Base64.decode(text)`로 되돌립니다.

# Constraints

- 대상 언어의 표준 인코딩 함수(Python `base64`/`urllib.parse`, Java
  `java.util.Base64`/`java.net.URLEncoder`, C#
  `Convert.ToBase64String`/`Uri.EscapeDataString`, JavaScript `btoa`/
  `encodeURIComponent` 등)에 매핑한다.
- `Base64.encode`/`Hex.encode`는 항상 성공한다(입력이 `bytes`이므로
  실패할 이유가 없다) — 반대로 `decode`류는 입력 문자열이 그 인코딩
  형식이 아니면 반드시 오류를 낸다(3.1절 "넘겨짚지 않는다" 원칙과
  같은 태도).

# Examples

## 예제: Base64 왕복

호출 (순서대로): `e = Base64.encode([104, 105])`, `Base64.decode(e)`

기대 동작: 두 번째 호출은 `[104, 105]`를 반환한다.

## 예제: 잘못된 Hex 문자열

호출: `Hex.decode("zz")`

기대 동작: 오류를 낸다 — `z`는 16진수 문자가 아니다.

# Open Points

- Base32, 커스텀 알파벳 인코딩은 이 버전의 범위 밖이다.
