#!specpp 0.1

# Meta

- name: std/native/cpp/nhttp/websocket
- version: 0.1.0
- description: RFC 6455 WebSocket 핸드셰이크와 메시지 송수신을 제공하는 libnhttp 확장 실체 명세.
- platform: linux, windows
- kind: native

# Intent

실시간 양방향 통신(채팅, 실시간 알림 등)이 필요할 때 쓴다.
[jay94ks/libnhttp](https://github.com/jay94ks/libnhttp)의
`websocket_endpoint_for` 확장을 옮긴 것이다 —
[`std/net/websocket.md`](../../../net/websocket.md) 추상 계약의
`kind: native` 구현이다. 실제 존재하는 라이브러리이므로 새로 설계할
대상이 아니다(`kind: native`, SPEC.md
1.2절).

# Domain

## Class: nhttp::ws::message

멤버:
- type: MessageType — `Text` 또는 `Binary`.
- data: string

## Class: nhttp::ws::ws_connection

메서드:
- receive() -> Task<message?>
  설명: 재조립이 끝난 다음 메시지 하나를 반환한다. 연결이 닫히면
  null을 반환한다(오류가 아니다 — 정상 종료 신호다).
- send_text(text: string) -> Task<void>
- send_binary(data: bytes) -> Task<void>
- close(code: int = 1000, reason: string = "") -> Task<void>
  설명: 아직 닫히지 않았다면 종료 프레임을 보내고 연결을 닫힌 것으로
  표시한다.
- is_closed() -> boolean

## Function: websocket_endpoint_for

[Static]
- websocket_endpoint_for(path: string, onConnect: (WsConnection) -> Task<void>) -> Extension
  설명: `path`로 들어오는 WebSocket 업그레이드 요청의 핸드셰이크를
  검증한 뒤, 성공하면 `onConnect`를 호출한다 — `onConnect`가
  반환(또는 예외로 종료)하면 연결은 정리된다. 연결의 전체
  생명주기(메시지 루프 포함)를 `onConnect` 콜백 하나가 책임진다.

# Interface

## Library

```
srv.extends(websocket_endpoint_for("/ws", [](std::shared_ptr<ws_connection> ws) -> task<void> {
    while (auto msg = co_await ws->receive()) {
        co_await ws->send_text(msg->data);  // 에코
    }
}));
```

연결마다 메시지를 반복해서 받는 루프를 콜백 안에 직접 씁니다.

# Constraints

- 실제 라이브러리 헤더
  `#include <nhttp/server/extensions/websocket_endpoint.hpp>`
  (핸드셰이크는 `ws/handshake.hpp`, 연결은 `ws/connection.hpp`)에
  매핑한다.
- RFC 6455 핸드셰이크(`Sec-WebSocket-Key`/`Sec-WebSocket-Accept`,
  SHA-1 기반)를 그대로 구현한다.
- `onConnect` 콜백이 반환하기 전까지 연결이 유지된다 — `receive()`가
  null을 반환했는데도 콜백이 계속 다른 작업을 한다면 연결은 이미
  닫힌 채로 유지 비용만 든다. 콜백은 `receive()`가 null이면 루프를
  끝내는 것이 관례다.
- [`std/native/cpp/nhttp/reverseproxy.md`](reverseproxy.md)를
  통해서도 WebSocket 업그레이드가 업스트림까지 그대로 전달된다(그
  파일 Constraints 참고).

# Examples

## 예제: 에코 서버

호출: 클라이언트가 `/ws`에 연결해 `"hello"`를 보낸다.

기대 동작: 서버가 같은 문자열 `"hello"`를 텍스트 프레임으로
돌려보낸다.

## 예제: 연결 종료 감지

호출: 클라이언트가 연결을 끊는다.

기대 동작: 서버 쪽 `ws.receive()`가 `null`을 반환한다 — 이때
`onConnect` 콜백이 정상적으로 반환하며 연결 정리가 끝난다.

# Open Points

- 압축 확장(permessage-deflate), 서브프로토콜 협상
  (`Sec-WebSocket-Protocol`), ping/pong 하트비트의 명시적 API는
  다루지 않는다.
