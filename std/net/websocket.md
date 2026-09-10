#!specpp 0.1

# Meta

- name: std/net/websocket
- version: 0.1.0
- description: HTTP 서버에 WebSocket(RFC 6455) 엔드포인트를 추가하는 것에 대한 추상 계약.

# Intent

채팅, 실시간 알림처럼 서버와 클라이언트가 연결을 유지한 채 양방향으로
메시지를 주고받아야 할 때 쓴다.
[`std/net/httpserver.md`](httpserver.md)의 `Server.mount`로 붙이는
`HttpServer.Extension` 중 하나다.
[`std/native/cpp/nhttp/websocket.md`](../native/cpp/nhttp/websocket.md)의
`websocket_endpoint_for`를 일반화한 것이다.

# Domain

## Class: WebSocket.Message

멤버:
- type: string — `"text"` 또는 `"binary"`.
- data: string

## Class: WebSocket.Connection

메서드:
- receive() -> WebSocket.Message?
  설명: 다음 메시지를 기다린다. 연결이 닫히면 null을 반환한다(오류가
  아니다).
- sendText(text: string) -> void
- sendBinary(data: bytes) -> void
- close(code: int = 1000, reason: string = "") -> void

## Function: websocket_endpoint

[Static]
- websocket_endpoint(path: string, onConnect: (WebSocket.Connection) -> void) -> HttpServer.Extension
  설명: `path`로 온 업그레이드 요청의 핸드셰이크를 검증한 뒤
  `onConnect`를 부른다. 연결의 생명주기 전체를 `onConnect`(보통 그
  안의 `receive()` 루프)가 책임진다.

# Interface

## Library

```
server.mount(websocket_endpoint("/ws", (ws) -> {
    while (msg = ws.receive()) {
        ws.sendText(msg.data);  // 에코
    }
}));
```

# Constraints

- 대상 언어의 관용적 WebSocket 라이브러리(Node.js `ws`, Python
  `websockets`, ASP.NET Core `WebSocketMiddleware` 등)에 매핑한다.
  C/C++이면
  [`std/native/cpp/nhttp/websocket.md`](../native/cpp/nhttp/websocket.md)를
  쓴다.
- RFC 6455 핸드셰이크(`Sec-WebSocket-Key`/`Sec-WebSocket-Accept`)를
  구현해야 한다 — HTTP 업그레이드 요청이 아니면 이 엔드포인트는
  적용되지 않는다.
- `onConnect`가 반환하면 연결은 정리된다 — `receive()`가 null을
  반환했는데 콜백이 계속 돈다면 이미 닫힌 연결을 붙들고 있는 것이다.

# Examples

## 예제: 에코 서버

호출: 클라이언트가 `/ws`에 연결해 `"hello"`를 보낸다.

기대 동작: 서버가 같은 문자열을 텍스트 프레임으로 돌려보낸다.

# Open Points

- 서브프로토콜 협상, 압축 확장(permessage-deflate), ping/pong
  하트비트는 이 버전의 범위 밖이다.
