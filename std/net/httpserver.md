#!specpp 0.1

# Meta

- name: std/net/httpserver
- version: 0.1.0
- description: 요청을 받아 라우팅하고 응답하는 HTTP 서버에 대한 추상 계약.

# Intent

REST API나 웹 페이지처럼, HTTP 요청을 받아 처리하고 응답을 돌려주는
프로그램을 만들 때 쓴다. [`std/net/httpclient.md`](httpclient.md)가
요청을 **보내는** 쪽이라면, 이 패키지는 요청을 **받는** 쪽이다.

[`std/native/cpp/nhttp/server.md`](../native/cpp/nhttp/server.md)
(C/C++ 타겟에서 SPP가 기본으로 채택하는 실제 라이브러리, `kind:
native`)의 실제 API에서 라이브러리 고유의 세부사항(C++ 코루틴 반환
타입, `del()`처럼 언어 예약어 때문에 붙은 이름 등)을 걷어내고
일반화한 것이다 — 정적 파일 서빙([`std/net/staticfiles.md`](staticfiles.md)),
WebSocket([`std/net/websocket.md`](websocket.md)), 리버스 프록시
([`std/net/reverseproxy.md`](reverseproxy.md))는 nhttp 라이브러리
자신의 모듈 구성과 대응해 각각 별도 계약으로 분리했다.

# Domain

## Class: HttpServer.Request

멤버:
- method: string — `"GET"`, `"POST"` 등.
- path: string — 쿼리 문자열을 뺀 경로.
- query: Dictionary<string, string> — 쿼리 문자열을 파싱한 값.
- routeParams: Dictionary<string, string> — 라우트의 `:name` 세그먼트로
  캡처된 값.
- headers: Dictionary<string, string>
- body: bytes

## Class: HttpServer.Response

[Static]
- status(code: int) -> HttpServer.Response
- text(code: int, body: string, mime: string = "text/html") -> HttpServer.Response
- json(code: int, value: any) -> HttpServer.Response
  설명: `value`를 JSON으로 직렬화해 `application/json`으로 담는다.

멤버:
- status: int
- headers: Dictionary<string, string>
- body: bytes

## Interface: HttpServer.Middleware

메서드:
- handle(req: HttpServer.Request, next: (HttpServer.Request) -> HttpServer.Response) -> HttpServer.Response
  설명: `next`를 부를지 말지, 부르기 전/후에 무엇을 할지는 구현이
  정한다(연쇄 책임 패턴) — 인증, 로깅, CORS 헤더 추가 등에 쓴다.

## Interface: HttpServer.Extension

서버가 내장 라우터로 넘기기 전에 먼저 시도해 볼 수 있는, 라우터 밖의
요청 처리기다 — 정적 파일, WebSocket, 리버스 프록시가 전부 이 모양으로
표현된다.

메서드:
- tryHandle(req: HttpServer.Request) -> HttpServer.Response?
  설명: 이 요청을 처리하면 응답을, 처리하지 않으면 null을 반환한다 —
  null이면 서버가 다음 확장(또는 최종적으로 라우터)을 시도한다.

## Interface: HttpServer.Router

메서드:
- get(path: string, handler: Handler) -> HttpServer.Router
- post(path: string, handler: Handler) -> HttpServer.Router
- put(path: string, handler: Handler) -> HttpServer.Router
- patch(path: string, handler: Handler) -> HttpServer.Router
- delete(path: string, handler: Handler) -> HttpServer.Router
- head(path: string, handler: Handler) -> HttpServer.Router
- options(path: string, handler: Handler) -> HttpServer.Router
  설명: `Handler`는 `(HttpServer.Request) -> HttpServer.Response`다
  (동기든 비동기든 대상 언어의 관용적인 함수/콜러블이면 된다).
- use(middleware: HttpServer.Middleware) -> HttpServer.Router
  설명: 등록한 순서대로 실행되는 미들웨어 체인에 추가한다.
- group(prefix: string, body: (HttpServer.Router) -> void) -> HttpServer.Router
  설명: `prefix`를 공유하는 하위 라우트 묶음을 만든다 — `body` 안에서
  등록한 라우트는 모두 `prefix`가 앞에 붙는다.

## Class: HttpServer.Options

멤버:
- maxConnections: int?
- requestTimeout: TimeSpan?

## Class: HttpServer.Server implements HttpServer.Router

생성자:
- Server(options: HttpServer.Options = HttpServer.Options())

메서드:
- mount(extension: HttpServer.Extension) -> void
  설명: 확장은 등록한 순서(우선순위)대로 시도된 뒤, 아무도 처리하지
  않으면 내장 라우터로 넘어간다.
- listen(host: string, port: int) -> void
- listenSecure(host: string, port: int, certChainFile: string, privateKeyFile: string) -> void
  설명: TLS로 서빙한다 — 인증서를 실제로 어떻게 로드하는지는 구현마다
  다르다(예:
  [`std/native/cpp/nhttp/tls.md`](../native/cpp/nhttp/tls.md)).
- run() -> void
  설명: 호출한 스레드(또는 프로세스)를 막고 서버를 돌린다.
- stop() -> void

# Interface

## Library

`server = HttpServer.Server()`를 만들고
`server.get("/whoami", handler)`처럼 라우트를 등록한 뒤, 필요하면
`server.mount(static_files("./public", "index.html"))`처럼 확장을
붙입니다. 마지막으로 `server.listen("0.0.0.0", 8080)` + `server.run()`으로
띄웁니다.

# Constraints

- 대상 언어의 관용적인 웹 서버 프레임워크(Python Flask/FastAPI,
  Node.js Express, Java Spring, C# ASP.NET Core, Go `net/http`, Rust
  actix-web/axum 등)에 매핑한다.
- **C/C++을 타겟한다면** SPP가 기본으로 채택하는 실제 라이브러리
  [`std/native/cpp/nhttp/server.md`](../native/cpp/nhttp/server.md)를
  쓴다(그 파일 Intent 참고) — 이 계약의 `Server`는 nhttp의
  `listener` + `router`(`extends`로 연결하는) 두 객체를 하나로 합쳐
  단순화한 것이고, `Handler`가 동기 함수를 반환할 수도 코루틴
  (`async::task<response>`)을 반환할 수도 있다는 점은 nhttp의
  `target_by`가 두 시그니처를 모두 받아주는 것과 같다.
- `use`(등록 순서 하나로만 실행)는 nhttp의 `prepend`/`append`(앞/뒤
  구분) 같은 더 세밀한 제어를 단순화한 것이다 — 구현이 더 세밀한
  제어를 추가로 제공해도 된다.
- 요청 본문(body)을 다 읽지 않고 핸들러가 끝나면, 구현에 따라 연결을
  재사용(keep-alive)하지 못할 수 있다.

# Examples

## 예제: 정적 라우트와 동적 라우트

호출:
```
server.get("/whoami", (req) -> HttpServer.Response.text(200, "I'm jay."));
server.get("/:user/profile", (req) -> HttpServer.Response.text(200, req.routeParams[":user"] + "'s profile"));
```

기대 동작: `GET /whoami`는 `"I'm jay."`를 반환한다. `GET /alice/profile`은
`"alice's profile"`을 반환한다.

## 예제: 미들웨어로 인증

호출: `server.use(authMiddleware)`를 먼저 등록한 뒤 라우트를
등록한다.

기대 동작: 모든 요청이 라우트 핸들러에 도달하기 전에
`authMiddleware.handle(req, next)`를 거친다 — `next(req)`를 부르지
않으면 핸들러는 아예 실행되지 않는다.

# Open Points

- HTTP/2, 압축(gzip 등), 쿠키/세션 관리는 이 버전의 범위 밖이다.
- 요청 본문 스트리밍(전체를 메모리에 올리지 않고 부분적으로 읽는
  것)은 다루지 않는다 — `body: bytes`로 전체를 전제한다.
