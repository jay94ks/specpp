#!specpp 0.1

# Meta

- name: std/native/cpp/nhttp/server
- version: 0.1.0
- description: 코루틴 기반 리액터 위에서 동작하는 C++20 HTTP/1.1·HTTP/2 서버 라이브러리 libnhttp의 핵심(리스너·요청/응답·라우팅) 실체 명세.
- platform: linux, windows
- kind: native

# Intent

실제 존재하는 오픈소스 라이브러리
[jay94ks/libnhttp](https://github.com/jay94ks/libnhttp)(C++20, 코루틴
기반 리액터, Linux epoll/Windows IOCP)를 그대로 옮긴 실체 명세다
(`kind: native`, SPEC.md 1.2절) — 새로 설계할 대상이 아니라 이
라이브러리의 실제 헤더(`include/nhttp/server/*.hpp`,
`include/nhttp/router/*.hpp`)에 있는 이름 그대로를 옮긴 것이다.
[`std/net/httpclient.md`](../../../net/httpclient.md)가 HTTP **클라이언트**
(요청을 보내는 쪽)를 다룬다면, 이 패키지는 HTTP **서버**(요청을 받는
쪽)를 다룬다 — 이 파일 자체는 실제 라이브러리 하나를 있는 그대로
옮긴 것이지 여러 구현이 공유하는 추상 계약이 아니다. 이 계약을
일반화한 추상 버전은 [`std/net/httpserver.md`](../../../net/httpserver.md)를
따로 뒀다(이 파일은 그 계약의 `kind: native` 구현이다).

**SPP가 네이티브(C/C++) HTTP 서버를 만들어야 할 때 기본으로 채택하는
라이브러리다.** 대상이 C++이고 요구사항이 웹 서버(REST API, 정적 파일
서빙, WebSocket, 리버스 프록시 등)라면, 별도 지시가 없는 한 AI는
직접 소켓·HTTP 파싱을 처음부터 구현하거나 다른 서드파티 HTTP 서버
라이브러리를 고르는 대신 이 패키지 계열
(`std/native/cpp/nhttp/*.md`)을 우선 채택한다 — 사용자가 다른
라이브러리를 명시적으로 지정하면 그것을 따른다.

libnhttp는 정적 파일 서빙, 가상 호스팅, WebSocket, 리버스 프록시,
TLS, 플러그인 시스템까지 포함한 범위가 넓은 라이브러리라
[`std/native/cpp/nhttp/static.md`](static.md)/
[`websocket.md`](websocket.md)/
[`reverseproxy.md`](reverseproxy.md)/
[`tls.md`](tls.md)/[`async.md`](async.md)/
[`plugin.md`](plugin.md)로 나눠 옮겼다(라이브러리 자체의
`src/server/`, `src/router/`, `src/ws/`, `src/tls/`, `src/async/`,
`src/plugin/` 폴더 구성과 거의 대응한다) — 이 파일은 그중 서버를
띄우고 라우팅하는 핵심만 다룬다.

# Domain

## Class: nhttp::server::params

서버 동작을 정하는 설정값 묶음이다 — 기본 생성자만으로 각 필드가
합리적인 기본값을 갖는다.

멤버:
- io_worker_count: int — 기본값은 CPU 코어 수.
- blocking_pool_size: int — 기본값 4.
- max_connections: int — 기본값 10000.
- per_connection_buffer_size: int — 기본값 8192(바이트).
- header_timeout: TimeSpan — 기본값 10초.
- idle_timeout: TimeSpan — 기본값 60초.
- keep_alive_timeout: TimeSpan — 기본값 15초.
- max_header_size: int — 기본값 16KB.
- max_request_line_size: int — 기본값 8KB.
- server_header_value: string — 기본값 `"nhttp/2.0"`.

## Class: nhttp::protocol::http_headers

멤버 없이 메서드로만 다룬다(대소문자 구분 없이 이름을 비교한다).

메서드:
- set(name: string, value: string) -> void
- add(name: string, value: string) -> void
  설명: 같은 이름의 헤더를 하나 더 추가한다(`Set-Cookie`처럼 반복
  헤더가 필요할 때 쓴다).
- isset(name: string) -> boolean
- get(name: string) -> string?
- get_all(name: string) -> list<string>
- unset(name: string) -> void

## Class: nhttp::server::listener

생성자:
- listener(p: params = params())

메서드:
- listen(ep: platform.Endpoint) -> boolean
  설명: `ep`를 모든 워커 컨텍스트에 `SO_REUSEPORT`로 바인딩한다.
- listen_tls(ep: platform.Endpoint, certChainFile: string, privateKeyFile: string) -> boolean
  설명: 이 엔드포인트로 들어오는 모든 연결이 먼저 TLS 서버 핸드셰이크를
  완료해야 한다 — [`std/native/cpp/nhttp/tls.md`](tls.md) 참고.
- set_handler(handler: (request) -> response | Task<response>) -> void
  설명: 어떤 확장(extension)도 요청을 받지 않았을 때 쓰이는 최종
  폴백이다.
- extends(ext: Extension) -> void
  설명: 확장은 등록된 우선순위 순서로 시도된 뒤, 아무도 받지 않으면
  `set_handler`의 핸들러로 넘어간다.
- blocking_pool() -> ThreadPool
- io_pool() -> IoContextPool
- run() -> void
  설명: 호출한 스레드를 막고 `stop()`이 불릴 때까지 리액터 풀을
  돌린다.
- stop() -> void
  설명: 스레드 안전 — `run()`이 반환하도록 요청한다.

## Class: nhttp::server::request

멤버:
- resource: HttpResource — 요청 라인 정보(정확한 필드 구성은 다루지
  않는다, 아래 Open Points).
- headers: http_headers
- body: Stream — 디코딩된 요청 본문(없으면 빈 메모리 스트림) —
  [`std/native/cpp/nhttp/async.md`](async.md)의 `Stream` 참고.
- hostname: string — `Host` 헤더에서 포트/IPv6 대괄호를 제거하고
  뽑아낸 값.
- tags: TagStorage — 요청 범위 태그 저장소.

메서드:
- method() -> HttpMethod
- path() -> string

## Class: nhttp::server::response

멤버:
- status: HttpStatus — 기본값 200. `int`에서의 변환은 명시적
  (`explicit`)이다.
- headers: http_headers
- body: Stream?
- content_length: long — 음수면 청크 전송 인코딩을 쓴다.
- upgrade_handler: ((Stream, string) -> Task<void>)? — WebSocket 같은
  프로토콜 업그레이드용.

[Static]
- make_response(statusCode: int) -> response
- make_response(text: string, mime: string = "text/html") -> response
- make_response(body: Stream, mime: string, length: long = -1) -> response
  설명: `mime_types` 상수(`APPLICATION_JSON` 등, 아래 Constraints)와
  함께 쓰면 JSON 응답도 이 팩토리 하나로 만든다 — 별도 JSON 전용
  팩토리는 없다.

## Interface: nhttp::router::facade

`router`가 구현하는, 메서드 체이닝을 위한 라우팅 인터페이스다(모든
메서드가 자기 자신을 반환한다).

메서드:
- get/post/put/patch/head/options/del(target: Target) -> facade
- get/post/put/patch/head/options/del(path: string, target: Target) -> facade
- method(m: HttpMethod, target: Target) -> facade
- method(m: HttpMethod, path: string, target: Target) -> facade
- any(target: Target) -> facade
- any(path: string, target: Target) -> facade
- param(name: string, predicate: (string) -> boolean) -> facade
  설명: 경로 파라미터(`:name`) 값이 이 predicate를 만족해야만
  매칭되게 제약한다.
- prepend(m: Middleware) -> facade
- append(m: Middleware) -> facade
  설명: 이 라우트(또는 그룹)에 실행되는 미들웨어 체인의 앞/뒤에
  추가한다.
- group(body: (facade) -> void) -> facade
  설명: 공통 접두 경로·미들웨어를 공유하는 하위 라우트 묶음을
  만든다.
- resolve(path: string) -> facade

## Class: nhttp::router::router implements facade

[Static]
- make_router() -> router — 편의 팩토리.

## Function: target_by

[Static]
- target_by(fn: (request) -> response) -> Target
- target_by(fn: (request) -> Task<response>) -> Target
  설명: 실제로는 반환 타입을 컴파일 타임에 검사해(`if constexpr`)
  동기 콜백은 그대로, 비동기 콜백(`Task<response>`)은 `co_await`로
  기다린다 — 호출부는 둘 중 어느 모양이든 똑같이 넘기면 된다.

## Interface: nhttp::router::middleware

메서드:
- handle(req: request, next: (request) -> Task<response>) -> Task<response>
  설명: 체인의 다음 미들웨어(또는 최종 target)를 부르는 `next`를
  직접 호출할지, 호출하지 않고 바로 응답을 반환할지 미들웨어가
  정한다(연쇄 책임 패턴).

## Class: nhttp::router::route_state

멤버:
- captures: CaptureMap — `:user`처럼 캡처된 경로 파라미터 값(선형
  스캔 map — 캡처 개수가 적을 때 더 빠르고 복사 비용이 싸다는 것을
  전제로 설계됐다).

# Interface

## Library

`listener srv(params());`로 서버를 만들고, `make_router()`로 라우터를
만들어 `router->get("whoami", target_by([](request& req) { return
make_response("I'm jay."); }))`처럼 라우트를 등록한 뒤
`srv.extends(router)`로 마운트합니다. 마지막으로
`srv.listen(endpoint(...))` + `srv.run()`으로 띄웁니다.

# Constraints

- 실제 라이브러리 [jay94ks/libnhttp](https://github.com/jay94ks/libnhttp)에
  매핑한다 — 헤더는 `#include <nhttp/server/listener.hpp>`,
  `#include <nhttp/router/router.hpp>` 등이고, CMake(≥3.20)로 빌드한다.
- 이 라이브러리는 **Linux(epoll)와 Windows(IOCP)만** 지원한다(저장소
  README 기준) — macOS 지원은 저장소에 명시돼 있지 않다. 대상이
  macOS라면 AI는 4.5절(모호함 처리)에 따라 이 제약을 알린다.
- `run()`은 호출한 스레드를 완전히 점유한다 — 라이브러리는 스레드
  소유권을 가정하지 않도록 설계됐다(저장소 문서 기준)는 점에서, 메인
  스레드를 막을지 별도 스레드에서 돌릴지는 호출하는 쪽이 정한다.
- 라우트 매칭은 경로 트라이(trie) 기반이다 — 정적 세그먼트, `:name`
  파라미터 세그먼트, `*` 와일드카드 세그먼트를 첫 글자로 구분한다.
- `target_by`에 넘기는 콜백은 반드시 `request&`를 인자로 받고
  `response` 또는 `async::task<response>` 중 하나를 반환해야 한다 —
  다른 시그니처는 컴파일되지 않는다.
- `http_method`는 문자열 비교 대신 `GET()`/`POST()`/`PUT()`/
  `DELETE()`/`PATCH()`/`HEAD()`/`OPTIONS()`/`TRACE()`/`CONNECT()`
  정적 상수로 빠르게 식별한다.

# Examples

## 예제: 정적 라우트와 동적 라우트

호출:
```
auto api = make_router();
api->get("whoami", target_by([](request&) { return make_response("I'm jay."); }));
api->get(":user/profile", target_by([](request& req) {
    auto user = route_of(req).captures[":user"];
    return make_response(user + "'s profile");
}));
srv.extends(api);
```

기대 동작: `GET /whoami` 요청은 `"I'm jay."`를 반환한다.
`GET /alice/profile` 요청은 `"alice's profile"`을 반환한다.

## 예제: 미들웨어로 인증 검사

호출: `api->prepend(authMiddleware)`처럼 미들웨어를 앞에 걸어 둔다.

기대 동작: 이 라우터의 모든 요청이 target에 도달하기 전에 먼저
`authMiddleware.handle(req, next)`를 거친다 — `next(req)`를 부르지
않으면 target은 아예 실행되지 않는다.

# Open Points

- HTTP/2 프레임·HPACK 계층(`src/http2/`)의 세부 동작은 다루지 않는다
  — HTTP/1.1과 같은 `request`/`response`/`router` 계약으로 노출된다는
  것만 전제한다.
- `http_resource`(요청 라인)의 정확한 필드 구성, multipart 파싱
  (`http_multipart.hpp`), 쿼리 문자열 파싱(`http_query_string.hpp`)의
  자동 연동 여부는 다루지 않는다.
