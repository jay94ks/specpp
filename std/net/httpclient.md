#!specpp 0.1

# Meta

- name: std/net/httpclient
- version: 0.1.0
- description: HTTP 요청을 보내고 응답을 받는 수단.

# Intent

웹 API를 호출하는 것처럼, HTTP로 요청을 보내고 응답(상태 코드·헤더·본문)을
받아야 할 때 쓴다. [`tcp`](tcp.md)가 더 저수준의 연결이라면, 이 패키지는 HTTP
프로토콜 자체를 다룬다.

# Domain

## Class: HttpRequest

멤버:
- method: string — `"GET"`, `"POST"` 등.
- uri: Uri — 요청 대상.
- headers: Dictionary<string, string> — 기본값은 빈 딕셔너리.
- body: bytes? — 본문. 없으면 null.

생성자:
- HttpRequest(method: string, uri: Uri)

## Class: HttpResponse

멤버:
- statusCode: int — 예: `200`, `404`.
- headers: Dictionary<string, string>
- body: bytes

## Class: HttpClient

메서드:
- send(request: HttpRequest) -> HttpResponse
  설명: request를 보내고 응답을 반환한다. 연결 실패 등 네트워크 오류는 오류로
  알린다 (statusCode로 감추지 않는다 — statusCode는 서버가 응답했을 때만 의미가
  있다).
- get(uri: Uri) -> HttpResponse
  설명: `send(HttpRequest("GET", uri))`와 같다.
- post(uri: Uri, body: bytes) -> HttpResponse
  설명: body를 담아 POST 요청을 보내는 편의 메서드다.

# Interface

## Library

다른 패키지는 `c = HttpClient()`를 만들고 `c.get(uri)` 또는 직접 만든
`HttpRequest`를 `c.send(request)`로 보냅니다.

# Constraints

- 타겟 언어의 네이티브 HTTP 클라이언트(C++ 라이브러리, Python
  `urllib.request`/`requests`, Java `HttpClient`, C# `HttpClient`, JavaScript
  `fetch`, 또는 interceptor 등 더 풍부한 기능이 필요하면
  [`std/js/axios.md`](../js/axios.md))에 매핑한다.
- 리다이렉트(3xx)를 자동으로 따라갈지는 타겟 언어의 기본 동작을 따른다.

# Examples

## 예제: GET 요청

호출: `HttpClient().get(Uri("https://example.com/"))`

기대 동작: 서버가 정상 응답하면 `statusCode`가 `200`대인 `HttpResponse`를
반환한다.

# Open Points

- 타임아웃, 재시도, 쿠키·세션 관리, 스트리밍 본문은 이 버전의 범위 밖이다.
