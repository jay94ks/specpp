#!specpp 0.1

# Meta

- name: std/net/reverseproxy
- version: 0.1.0
- description: 특정 경로로 들어오는 요청을 업스트림 서버로 전달하는 리버스 프록시에 대한 추상 계약.

# Intent

이 서버 뒤에 실제 애플리케이션 서버(들)를 두고, 특정 경로로 들어오는
요청을 그대로 전달(응답도 그대로 돌려주는)해야 할 때 쓴다.
[`std/net/httpserver.md`](httpserver.md)의 `Server.mount`로 붙이는
`HttpServer.Extension` 중 하나다.
[`std/native/cpp/nhttp/reverseproxy.md`](../native/cpp/nhttp/reverseproxy.md)의
`reverse_proxy_for`를 일반화한 것이다.

# Domain

## Class: ReverseProxy.Upstream

멤버:
- endpoint: platform.Endpoint — 이미 해석된 IP·포트.
- useTls: boolean — 기본값 false.
- tlsServerName: string? — `useTls`가 true일 때만 의미가 있다.

## Function: reverse_proxy

[Static]
- reverse_proxy(mountPath: string, upstreams: list<ReverseProxy.Upstream>) -> HttpServer.Extension
  설명: `mountPath` 아래 요청을 `upstreams`에 분배한다. WebSocket
  업그레이드 요청도 그대로 전달한다.

# Interface

## Library

```
server.mount(reverse_proxy("/api", [ReverseProxy.Upstream(resolvedEndpoint)]));
```

# Constraints

- 대상 언어의 관용적 리버스 프록시 미들웨어(Node.js
  `http-proxy-middleware`, ASP.NET Core YARP 등)에 매핑한다.
  C/C++이면
  [`std/native/cpp/nhttp/reverseproxy.md`](../native/cpp/nhttp/reverseproxy.md)를
  쓴다.
- 기본 분배 정책은 라운드로빈이다 — 그 이상의 로드밸런싱(가중치,
  헬스체크 등)은 구현이 추가로 제공할 수 있다(이 버전은 요구하지
  않는다).
- `upstreams`는 이미 DNS로 해석된 엔드포인트를 받는다 — 호스트명
  문자열 해석은 이 계약의 책임이 아니다.

# Examples

## 예제: 라운드로빈 분배

전제: `upstreams`에 서버 A, B 두 개가 있다.

호출: `/api`로 요청을 10번 연속 보낸다.

기대 동작: A와 B가 번갈아(또는 순환 순서로) 요청을 나눠 받는다.

# Open Points

- 헬스체크, 재시도 정책, 요청/응답 헤더 재작성(`X-Forwarded-For` 등)의
  정확한 규칙은 다루지 않는다.
