#!specpp 0.1

# Meta

- name: std/native/cpp/nhttp/tls
- version: 0.1.0
- description: OpenSSL 기반 TLS 서버/클라이언트 컨텍스트를 제공하는 libnhttp TLS 계층 실체 명세.
- platform: linux, windows
- kind: native

# Intent

HTTPS로 서버를 노출하거나([`std/native/cpp/nhttp/server.md`](server.md)의
`listener.listen_tls`), [`std/native/cpp/nhttp/reverseproxy.md`](reverseproxy.md)로
TLS를 쓰는 업스트림에 접속할 때 필요한 하위 계층이다.
[jay94ks/libnhttp](https://github.com/jay94ks/libnhttp)의
`tls_context`를 옮긴 것이다. 실제 존재하는 라이브러리이므로 새로
설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: nhttp::tls::tls_context

불변(읽기 전용) 객체로, 여러 스레드가 동시에 공유해도 안전하다.
복사·이동할 수 없다.

[Static]
- create_server(certChainFile: string, privateKeyFile: string) -> tls_context?
  설명: 인증서 체인과 개인 키 파일로 서버용 컨텍스트를 만든다.
  실패하면 null을 반환한다(예외를 던지지 않는다).
- create_client(verifyPeer: boolean = true) -> tls_context?
  설명: 클라이언트(리버스 프록시가 업스트림에 접속할 때 등)용
  컨텍스트를 만든다.

메서드:
- native() -> OpaqueHandle
  설명: 실제로는 `SSL_CTX*`(OpenSSL 네이티브 핸들)를 반환한다 — 이
  라이브러리가 감싸지 않은 세부 기능이 필요할 때만 쓴다.

# Interface

## Library

`listener.listen_tls(ep, "cert.pem", "key.pem")`처럼 `listener`가
내부적으로 `tls_context::create_server`를 호출해 준다 — 대부분의
경우 이 클래스를 직접 다룰 필요는 없다.

# Constraints

- 실제 라이브러리 헤더 `#include <nhttp/tls/context.hpp>`에 매핑하고,
  내부적으로 OpenSSL(`libssl`/`libcrypto`)에 링크한다.
- TLS 1.2 이상만 허용한다(그보다 낮은 버전은 협상되지 않는다).
- `create_server`/`create_client` 둘 다 **예외가 아니라 null 반환으로
  실패를 알린다** — 이 저장소의 다른 많은 계약이 "오류를 낸다"고
  표현하는 것과 다른 지점이니, 호출부는 반드시 null 체크를 해야
  한다.
- `create_client(verifyPeer: false)`는 인증서 검증을 끄는 것이므로
  개발/테스트 용도로만 쓰고, 자체 서명 인증서를 쓰는 내부망
  업스트림이 아니라면 프로덕션에서는 피한다.

# Examples

## 예제: 인증서 로드 실패

호출: `tls_context.create_server("없는파일.pem", "없는키.pem")`

기대 동작: `null`을 반환한다 — 예외를 던지지 않는다.

# Open Points

- 클라이언트 인증서(mTLS), 인증서 자동 갱신, SNI 기반 다중 인증서
  서빙(도메인마다 다른 인증서)은 다루지 않는다.
