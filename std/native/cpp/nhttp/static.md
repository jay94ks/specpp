#!specpp 0.1

# Meta

- name: std/native/cpp/nhttp/static
- version: 0.1.0
- description: 조건부 GET·바이트 Range를 지원하는 정적 파일 서빙과 가상 호스팅을 제공하는 libnhttp 서버 확장 실체 명세.
- platform: linux, windows
- kind: native

# Intent

[jay94ks/libnhttp](https://github.com/jay94ks/libnhttp)의 `overlay_of`
(정적 파일)와 `vhost_for`(가상 호스팅) 확장을 옮긴 것이다 —
[`std/native/cpp/nhttp/server.md`](server.md)의 `listener.extends(...)`로
마운트하는 `Extension` 중 두 가지다. `overlay_of` 부분은
[`std/net/staticfiles.md`](../../../net/staticfiles.md) 추상 계약의
`kind: native` 구현이다(`vhost_for`에 대응하는 추상 계약은 아직 이
저장소에 없다, 아래 Open Points). 실제 존재하는 라이브러리이므로
새로 설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Function: overlay_of

[Static]
- overlay_of(baseDir: string, indexFile: string, pool: ThreadPool) -> Extension
  설명: `baseDir` 아래 파일들을 서빙한다. 디렉터리 요청이면
  `indexFile`을 대신 서빙한다. 조건부 GET(`If-None-Match`/
  `If-Modified-Since`)과 바이트 Range 요청(`Range: bytes=...`)을
  완전히 지원한다(`static_content.hpp`의 공유 엔진 기반) — 블로킹
  파일 I/O는 `pool`(보통 `listener.blocking_pool()`)에서 실행돼
  리액터 스레드를 막지 않는다.

## Function: vhost_for

[Static]
- vhost_for(exactHostname: string) -> VHost
- vhost_for(pattern: Regex) -> VHost
- vhost_for(predicate: (string) -> boolean) -> VHost
  설명: `Host` 헤더 값을 기준으로 이 가상 호스트에 속하는 요청만
  받아들인다. 세 오버로드 중 어느 것으로 만들든 반환된 `VHost`는 그
  자체가 `Extension`이자 `Facade`(라우팅 가능)라서
  `vhost.extends(otherExtension)`, `vhost.get(...)` 모두 가능하다.

# Interface

## Library

`srv.extends(overlay_of(".", "index.html", srv.blocking_pool()));`처럼
정적 파일 서빙을 마운트합니다. 여러 도메인을 한 서버에서 서빙해야
하면 `auto www = vhost_for("www.example.com"); www->extends(overlay_of(...));
srv.extends(www);`처럼 가상 호스트 안에 다시 확장을 겁니다.

# Constraints

- 실제 라이브러리 헤더
  `#include <nhttp/server/extensions/overlay.hpp>`,
  `#include <nhttp/server/extensions/vhost.hpp>`에 매핑한다.
- [`std/native/cpp/nhttp/server.md`](server.md)의 `listener.extends`와
  마찬가지로 확장은 등록된 우선순위 순서로 시도된다 — `overlay_of`를
  라우터보다 먼저(또는 다른 우선순위로) 걸었는지에 따라 정적 파일과
  API 경로가 겹칠 때 결과가 달라질 수 있다.
- 정규식/predicate 기반 `vhost_for`는 여러 실제 호스트명을 하나의
  `VHost`로 묶을 수 있다 — 어떤 요청이 어떤 vhost에 속하는지는 연결
  단위 태그(`http_vhost_tag`)에 스택으로 기록되는 내부 구현 세부사항
  이며, 일반적으로는 신경 쓸 필요가 없다.

# Examples

## 예제: 정적 파일 + Range 요청

전제: `base_dir`에 10MB짜리 `video.mp4`가 있고,
`srv.extends(overlay_of(base_dir, "index.html", srv.blocking_pool()))`로
마운트했다.

호출: `GET /video.mp4` with header `Range: bytes=0-1023`

기대 동작: 상태 코드 `206 Partial Content`와 함께 처음 1024바이트만
반환한다.

## 예제: 가상 호스트 분기

전제: `vhost_for("a.example.com")`와 `vhost_for("b.example.com")`에
서로 다른 정적 파일 확장을 걸어 뒀다.

호출: `Host: a.example.com`으로 `GET /`

기대 동작: a용 디렉터리의 `index.html`을 반환한다 — b용 확장은
시도되지 않는다.

# Open Points

- `single_file.hpp`(디렉터리가 아니라 파일 하나만 서빙하는 변형)와
  `vpath.hpp`(가상 경로 접두어 매핑)는 다루지 않는다.
- MIME 타입 추론 규칙(확장자 → `http_mime_type`)의 전체 매핑 표는
  다루지 않는다.
- `vhost_for`(가상 호스팅)에 대응하는 추상 계약은 이 저장소에 아직
  없다 — 필요해지면 `std/net/vhost.md` 같은 별도 계약으로 분리한다.
