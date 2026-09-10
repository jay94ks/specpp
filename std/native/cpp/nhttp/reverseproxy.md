#!specpp 0.1

# Meta

- name: std/native/cpp/nhttp/reverseproxy
- version: 0.1.0
- description: 라운드로빈으로 업스트림에 요청을 분배하는 libnhttp 리버스 프록시 확장 실체 명세.
- platform: linux, windows
- kind: native

# Intent

이 서버 뒤에 실제 애플리케이션 서버(들)를 두고, 특정 경로로 들어오는
요청을 그쪽으로 그대로 전달(그리고 응답을 그대로 돌려주는)해야 할 때
쓴다. [jay94ks/libnhttp](https://github.com/jay94ks/libnhttp)의
`reverse_proxy_for` 확장을 옮긴 것이다 —
[`std/net/reverseproxy.md`](../../../net/reverseproxy.md) 추상 계약의
`kind: native` 구현이다. 실제 존재하는 라이브러리이므로
새로 설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: nhttp::server::upstream

멤버:
- address: platform.Endpoint — 이미 해석(resolve)된 IP·포트.
- use_tls: boolean — 기본값 false.
- tls_sni_hostname: string — `use_tls`가 true일 때만 의미가 있다.
- verify_tls_cert: boolean — 기본값 true.

## Function: reverse_proxy_for

[Static]
- reverse_proxy_for(mountPath: string, upstreams: list<upstream>) -> Extension
  설명: `mountPath` 아래로 들어오는 요청을 `upstreams`에 라운드로빈으로
  분배한다. WebSocket 업그레이드 요청도 그대로 전달한다.

# Interface

## Library

```
list<upstream> upstreams = [upstream(resolvedEndpoint)];
upstreams[0].use_tls = true;
upstreams[0].tls_sni_hostname = "backend.internal";
srv.extends(reverse_proxy_for("/api", upstreams));
```

# Constraints

- 실제 라이브러리 헤더
  `#include <nhttp/server/extensions/reverse_proxy.hpp>`에 매핑한다.
- `upstreams`의 각 항목은 이미 DNS로 해석된 `platform::endpoint`여야
  한다 — 호스트명 문자열을 직접 받지 않는다(호스트명을 쓰려면
  [`std/native/cpp/nhttp/server.md`](server.md)가 참조하는
  `platform::resolve`류 API로 먼저 IP를 얻어야 한다, 아래 Open
  Points).
- 업스트림 쪽에 TLS로 접속해야 한다면(`use_tls: true`), 이 라이브러리가
  업스트림과의 연결에 [`std/native/cpp/nhttp/tls.md`](tls.md)의 TLS
  클라이언트 컨텍스트를 쓴다.
- 분배 정책은 라운드로빈 하나뿐이다 — 가중치, 헬스체크 기반 제외,
  최소 연결 등 다른 로드밸런싱 정책은 없다.

# Examples

## 예제: 라운드로빈 분배

전제: `upstreams`에 서버 A, B 두 개가 있다.

호출: `/api`로 요청을 10번 연속 보낸다.

기대 동작: A와 B가 번갈아(또는 순환 순서로) 요청을 나눠 받는다.

# Open Points

- 헬스체크(응답하지 않는 업스트림을 일시적으로 제외하는 것), 재시도
  정책, 요청/응답 헤더 재작성(X-Forwarded-For 등)의 정확한 규칙은
  다루지 않는다.
- 호스트명을 직접 받아 내부적으로 DNS 해석까지 해 주는 편의
  오버로드는 다루지 않는다 — 호출하는 쪽이 미리 해석해서 넘겨야
  한다.
