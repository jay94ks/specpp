#!specpp 0.1

# Meta

- name: std/net/ipendpoint
- version: 0.1.0
- description: IP 주소와, 주소+포트로 이루어진 접속 지점(엔드포인트).

# Intent

네트워크로 어디에 연결할지("이 IP의 이 포트")를 표현해야 할 때 쓴다.
[`tcp`](tcp.md), [`dns`](dns.md)가 이 타입들을 주고받는다.

# Domain

## Class: IPAddress

생성자:
- IPAddress(text: string)
  설명: `"192.168.0.1"`(IPv4) 또는 IPv6 표기 문자열을 파싱한다. 형식이 올바르지
  않으면 오류를 낸다.

메서드:
- toString() -> string

## Class: IPEndPoint

멤버:
- address: IPAddress — 접속 지점의 IP 주소.
- port: int — 접속 지점의 포트 번호.

생성자:
- IPEndPoint(address: IPAddress, port: int)

메서드:
- toString() -> string
  설명: `"192.168.0.1:8080"` 형태의 문자열로 변환한다.

# Interface

## Library

다른 패키지는 `IPEndPoint(IPAddress("192.168.0.1"), 8080)`처럼 만들어
[`TcpClient.connect`](tcp.md)나 [`TcpListener`](tcp.md)에 넘깁니다.

# Constraints

- 타겟 언어의 네이티브 주소 타입(C++ 소켓 API, Python `ipaddress`/튜플, Java
  `InetAddress`/`InetSocketAddress`, C# `IPAddress`/`IPEndPoint` 등)에 매핑한다.

# Examples

## 예제: 문자열로 조립

호출: `IPEndPoint(IPAddress("127.0.0.1"), 8080).toString()`

기대 동작: `"127.0.0.1:8080"`을 반환한다.

# Open Points

- IPv6 표기의 세부 형식(`toString()`에서 대괄호 표기 등)은 AI 재량.
