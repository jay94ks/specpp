#!specpp 0.1

# Meta

- name: std/net/udp
- version: 0.1.0
- description: 연결 없이 데이터그램을 주고받는 UDP 소켓.

# Intent

[`std/net/tcp.md`](tcp.md)의 스트림 연결과 달리, 순서·도달을 보장하지
않는 대신 지연이 적은 통신이 필요할 때(실시간 게임의 입력 동기화 등) 쓴다.

# Domain

## Class: UdpSocket

생성자:
- UdpSocket(localPort: int)
  설명: localPort에서 데이터그램을 주고받을 소켓을 연다. 0이면 시스템이
  빈 포트를 골라준다.

메서드:
- send(data: bytes, remote: IPEndPoint) -> void
  설명: remote로 data를 한 번에 보낸다(도착 순서·도달 자체를 보장하지
  않는다).
- receive(maxBytes: int) -> (bytes, IPEndPoint)?
  설명: 데이터그램 하나를 기다려 받는다. 함께 반환되는
  [`IPEndPoint`](ipendpoint.md)는 보낸 쪽의 주소다. 소켓이 닫히면 null.
- close() -> void

# Interface

## Library

다른 패키지는 `UdpSocket(0)`으로 소켓을 열고, 상대의 `IPEndPoint`로
`send`하거나 `receive`로 들어오는 데이터그램을 기다립니다.

# Constraints

- 타겟 언어의 네이티브 UDP 소켓(C++/C의 BSD 소켓 `SOCK_DGRAM`, Python
  `socket.SOCK_DGRAM`, C#의 `UdpClient` 등)에 매핑한다.
- 데이터그램 하나의 최대 크기, 순서 보장, 재전송은 이 계약이 다루지
  않는다 — 필요하면 호출하는 쪽이 자체 프로토콜(순번 붙이기 등)로
  구현한다.

# Examples

## 예제: 보내고 받는다

호출 (한쪽): `a = UdpSocket(9000)`, `a.send(b"hi", IPEndPoint(IPAddress("127.0.0.1"), 9001))`

호출 (다른 쪽, 동시에): `b = UdpSocket(9001)`, `b.receive(1024)`

기대 동작: `b.receive(1024)`는 `(b"hi", <a의 주소:9000>)`을 반환한다.

# Open Points

- 멀티캐스트/브로드캐스트는 이 버전의 범위 밖이다.
