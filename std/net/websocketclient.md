#!specpp 0.1

# Meta

- name: std/net/websocketclient
- version: 0.1.0
- description: WebSocket 서버에 접속하는 클라이언트에 대한 추상 계약.

# Intent

[`std/net/websocket.md`](websocket.md)가 서버가 접속을 **받는** 쪽이라면,
이 계약은 클라이언트가 서버에 **접속하는** 쪽이다 — 채팅 클라이언트,
실시간 데이터를 구독하는 프로그램, 다른 서비스의 WebSocket API를 호출하는
코드 등에 쓴다.

# Domain

## Class: WebSocketMessage

멤버:
- type: string — `"text"` 또는 `"binary"`.
- data: string

## Class: WebSocketClient.Connection

메서드:
- receive() -> WebSocketMessage?
  설명: 다음 메시지를 기다린다. 연결이 닫히면 null을 반환한다(오류가
  아니다) — [`std/net/websocket.md`](websocket.md)의 `Connection.receive()`와
  같은 규칙이다.
- sendText(text: string) -> void
- sendBinary(data: bytes) -> void
- close(code: int = 1000, reason: string = "") -> void

## Class: WebSocketClient

[Static]
- connect(uri: string) -> WebSocketClient.Connection
  설명: `uri`는 `ws://` 또는 `wss://`(TLS) 스킴이다. 서버가 핸드셰이크를
  거부하면 오류를 낸다.

# Interface

## Library

```
conn = WebSocketClient.connect("wss://example.com/ws");
conn.sendText("hello");
msg = conn.receive();
```

# Constraints

- 대상 언어의 WebSocket 클라이언트 라이브러리(Python `websockets`/
  `websocket-client`, 브라우저 내장 `WebSocket`, Java
  `jakarta.websocket`, C# `ClientWebSocket` 등)에 매핑한다.
- `wss://`는 서버 인증서를 검증한다(기본값) — 자체 서명 인증서를
  써야 하는 개발 환경이 아니라면 검증을 끄지 않는다.
- 연결이 예기치 않게 끊기는 것(네트워크 오류)과, 서버가 정상적으로
  종료 프레임을 보내고 닫은 것을 구분해야 한다면 `close`가 던지는
  오류의 종류로 판단한다(정상 종료는 `receive()`가 null을 반환하는
  것으로 알 수 있다) — 정확한 구분 방법은 구현에 맡긴다.

# Examples

## 예제: 접속하고 메시지 주고받기

호출 (순서대로): `conn = WebSocketClient.connect("ws://localhost:8080/ws")`,
`conn.sendText("hello")`, `msg = conn.receive()`

기대 동작: 서버가 에코 서버라면 `msg.data`가 `"hello"`다.

## 예제: 연결 종료 감지

호출: 서버가 연결을 닫은 뒤 `conn.receive()`

기대 동작: `null`을 반환한다.

# Open Points

- 재연결 정책(지수 백오프 등), 커스텀 헤더/인증 협상, 서브프로토콜
  지정은 이 버전의 범위 밖이다.
