#!specpp 0.1

# Meta

- name: std/net/tcp
- version: 0.1.0
- description: TCP로 연결을 맺고 데이터를 주고받는 수단.

# Intent

두 프로그램이 네트워크로 신뢰성 있는(순서 보장, 재전송) 스트림 연결을 맺고
데이터를 주고받아야 할 때 쓴다. `TcpClient`는 연결하는 쪽, `TcpListener`는
연결을 받아들이는 쪽이다.

# Domain

## Class: TcpClient

생성자:
- TcpClient()
  설명: 아직 어디에도 연결되지 않은 클라이언트를 만든다.

메서드:
- connect(endpoint: IPEndPoint) -> void
  설명: endpoint로 연결을 시도한다. 실패하면 오류를 낸다.
- send(data: bytes) -> void
  설명: 연결된 상대에게 data를 보낸다.
- receive(maxBytes: int) -> bytes
  설명: 상대로부터 최대 maxBytes만큼 데이터를 읽어 반환한다. 상대가 연결을
  끊었으면 빈 bytes를 반환한다.
- close() -> void
- isConnected() -> boolean

## Class: TcpListener

생성자:
- TcpListener(port: int)
  설명: port에서 들어오는 연결을 받을 준비를 한다 (아직 듣기 시작하지는 않는다).

메서드:
- start() -> void
  설명: 연결 받기를 시작한다.
- acceptClient() -> TcpClient
  설명: 새 연결이 들어올 때까지 블로킹(대기)하고, 연결된 `TcpClient`를 반환한다.
- stop() -> void

# Interface

## Library

서버 쪽은 `TcpListener(8080)` → `start()` → 반복해서 `acceptClient()`, 클라이언트
쪽은 `TcpClient()` → `connect(endpoint)` → `send`/`receive`를 씁니다.

# Constraints

- 타겟 언어의 네이티브 TCP 소켓(C++ 소켓 API, Python `socket`, Java
  `Socket`/`ServerSocket`, C# `TcpClient`/`TcpListener` 등)에 매핑한다.
- `receive`는 기본적으로 블로킹이다 — 논블로킹·타임아웃은 이 버전의 범위 밖이다.

# Examples

## 예제: 보내고 받는다

호출 (서버): `l = TcpListener(9000)`, `l.start()`, `c = l.acceptClient()`,
`c.receive(1024)`

호출 (클라이언트, 동시에): `t = TcpClient()`, `t.connect(endpoint)`,
`t.send(data)`

기대 동작: 서버의 `receive(1024)`는 클라이언트가 `send(data)`로 보낸 것과 같은
내용을 반환한다.

# Open Points

- 타임아웃, 논블로킹 I/O, TLS/암호화는 이 버전의 범위 밖이다.
