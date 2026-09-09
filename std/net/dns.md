#!specpp 0.1

# Meta

- name: std/net/dns
- version: 0.1.0
- description: 호스트 이름을 IP 주소로 조회(resolve)하는 수단.

# Intent

`"example.com"`처럼 이름으로 된 호스트에 접속하려면 먼저 IP 주소를 알아내야
한다. 이 조회 과정을 표준화한다.

# Domain

## Class: Dns

메서드:
[Static]
- resolve(hostname: string) -> list<IPAddress>
  설명: hostname에 연결된 IP 주소 목록을 조회해 반환한다. 하나도 찾을 수 없으면
  오류를 낸다.

# Interface

## Library

다른 패키지는 `Dns.resolve("example.com")`처럼 클래스 이름으로 바로 씁니다.

# Constraints

- 타겟 언어의 네이티브 DNS 조회 수단(C++ `getaddrinfo`, Python
  `socket.getaddrinfo`, Java `InetAddress.getAllByName`, C# `Dns.GetHostAddresses`
  등)에 매핑한다.
- [`IPAddress`](ipendpoint.md) 타입을 결과로 쓴다.

# Examples

## 예제: 조회 결과는 비어있지 않다

호출: `Dns.resolve("localhost")`

기대 동작: 최소 하나 이상의 `IPAddress`를 담은 list를 반환한다 (보통
`127.0.0.1`을 포함한다).

# Open Points

- IPv4/IPv6 우선순위, 캐싱 여부는 AI 재량.
