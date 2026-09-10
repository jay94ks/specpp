#!specpp 0.1

# Meta

- name: std/native/cpp/nhttp/plugin
- version: 0.1.0
- description: 서버 생명주기와 요청 범위에 훅을 거는 libnhttp 플러그인 시스템 실체 명세.
- platform: linux, windows
- kind: native

# Intent

로깅, 인증, 메트릭 수집처럼 여러 라우트에 걸쳐 반복되는 관심사
([`std/native/cpp/nhttp/server.md`](server.md)의 미들웨어와 비슷하지만,
미들웨어는 라우터 안에서만 걸리는 반면 플러그인은 서버 시작/종료
시점까지 훅을 건다는 점이 다르다)를 한 곳에 모을 때 쓴다.
[jay94ks/libnhttp](https://github.com/jay94ks/libnhttp)의 `plugin`/
`plugin_manager`를 옮긴 것이다. 실제 존재하는 라이브러리이므로 새로
설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Interface: nhttp::plugin::plugin

모든 훅은 기본 구현이 빈 본문이다 — 필요한 것만 오버라이드한다.

메서드:
- on_init(srv: Listener, ctx: IoContext) -> Task<void>
  설명: 서버 시작 시 한 번 실행된다.
- on_deinit(srv: Listener, ctx: IoContext) -> Task<void>
  설명: 서버 종료 시 한 번 실행된다.
- on_begin(req: request) -> Task<void>
  설명: 이 플러그인이 적용된 경로의 요청을 처리하기 **전**에
  실행된다.
- on_end(req: request) -> Task<void>
  설명: 요청 처리 **후**에 실행된다 — 처리 중 예외가 났어도 항상
  호출된다.

## Class: nhttp::plugin::plugin_manager

메서드:
- register(p: Plugin) -> void
- init_all(srv: Listener) -> Task<void>
  설명: 등록된 모든 플러그인의 `on_init`을 순서대로 부른다.
- deinit_all(srv: Listener) -> Task<void>

# Interface

## Library

`plugin_manager plugins; plugins.register(make_shared<RequestCounter>());`처럼
등록해 두고, `srv.run()` 앞뒤로 `plugins.init_all(srv)`/
`plugins.deinit_all(srv)`를 부릅니다.

# Constraints

- 실제 라이브러리 헤더 `#include <nhttp/plugin/plugin.hpp>`,
  `#include <nhttp/plugin/plugin_manager.hpp>`에 매핑한다.
- `on_end`는 **예외가 발생해도 항상 호출된다**(`finally`류 보장) —
  리소스 정리·메트릭 기록처럼 반드시 실행돼야 하는 로직은 `on_end`에
  둔다.
- 플러그인이 실제로 어떤 요청 범위에 적용되는지(전체 서버인지, 특정
  라우트 그룹인지)는 `plugin_scope.hpp`가 정하는 세부사항이다(아래
  Open Points) — 이 계약은 훅 시그니처 자체만 다룬다.

# Examples

## 예제: 요청 카운터

호출: 플러그인의 `on_begin`마다 카운터를 1 증가시키고, 별도 라우트
`GET /counted`에서 그 값을 반환하도록 구현한다.

기대 동작: 요청을 5번 보낸 뒤 `GET /counted`를 호출하면 6(자기 자신
포함) 이상의 값을 반환한다.

# Open Points

- `plugin_scope.hpp`(플러그인이 적용되는 요청 범위를 좁히는 방법)의
  정확한 API는 다루지 않는다.
- 플러그인 간 실행 순서 보장, 플러그인 사이의 상태 공유 방법은
  다루지 않는다.
