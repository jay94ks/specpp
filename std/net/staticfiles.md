#!specpp 0.1

# Meta

- name: std/net/staticfiles
- version: 0.1.0
- description: 디스크의 디렉터리를 조건부 GET·바이트 Range 지원과 함께 HTTP로 서빙하는 것에 대한 추상 계약.

# Intent

빌드된 프론트엔드 산출물이나 업로드된 파일처럼, 디스크에 이미 있는
파일들을 별도 코드 없이 그대로 HTTP로 내려주고 싶을 때 쓴다.
[`std/net/httpserver.md`](httpserver.md)의 `Server.mount`로 붙이는
`HttpServer.Extension` 중 하나다.
[`std/native/cpp/nhttp/static.md`](../native/cpp/nhttp/static.md)의
`overlay_of`를 일반화한 것이다.

# Domain

## Function: static_files

[Static]
- static_files(baseDir: string, indexFile: string = "index.html") -> HttpServer.Extension
  설명: `baseDir` 아래 파일을 경로 그대로 서빙한다. 디렉터리 요청이면
  `indexFile`을 대신 서빙한다.

# Interface

## Library

`server.mount(static_files("./public", "index.html"));`처럼 한 줄로
붙입니다.

# Constraints

- 대상 언어의 관용적 정적 파일 미들웨어(Express의 `express.static`,
  ASP.NET Core의 `UseStaticFiles`, Flask의 `send_from_directory` 등)에
  매핑한다. C/C++이면
  [`std/native/cpp/nhttp/static.md`](../native/cpp/nhttp/static.md)를
  쓴다.
- **조건부 GET**(`If-None-Match`/`If-Modified-Since` →
  `304 Not Modified`)과 **바이트 Range 요청**(`Range: bytes=...` →
  `206 Partial Content`)을 지원해야 한다 — 이 둘을 지원하지 않으면 이
  계약을 만족하지 않는다.
- 블로킹 파일 I/O를 리액터/이벤트 루프 스레드에서 직접 하면 다른
  요청 처리를 막을 수 있다 — 구현은 별도 스레드 풀이나 비동기 파일
  I/O를 쓴다(예:
  [`std/native/cpp/nhttp/async.md`](../native/cpp/nhttp/async.md)의
  `thread_pool`).
- `baseDir` 밖의 경로(`../../etc/passwd` 같은 경로 탈출)에 접근하지
  못하게 막아야 한다.

# Examples

## 예제: Range 요청

전제: `baseDir`에 10MB짜리 `video.mp4`가 있다.

호출: `GET /video.mp4` with header `Range: bytes=0-1023`

기대 동작: `206 Partial Content`와 함께 처음 1024바이트만 반환한다.

## 예제: 경로 탈출 차단

호출: `GET /../../etc/passwd`

기대 동작: 오류(보통 `400`이나 `404`)를 낸다 — `baseDir` 밖의 파일을
반환하지 않는다.

# Open Points

- 디렉터리 목록(인덱스 파일이 없을 때 파일 목록을 보여주는 것),
  gzip 사전 압축 파일(`.gz`) 자동 서빙은 다루지 않는다.
