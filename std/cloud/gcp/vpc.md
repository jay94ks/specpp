#!specpp 0.1

# Meta

- name: std/cloud/gcp/vpc
- version: 0.1.0
- description: 네트워크 전역에 걸리는 방화벽 규칙 모델을 쓰는 GCP VPC 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/network.md`](../network.md) 추상 계약의 GCP
구현이다 — 같은 계약의 [AWS 구현](../aws/vpc.md)/[Azure
구현](../azure/vnet.md)도 참고할 수 있다.

**구조적 차이를 먼저 밝힌다.** AWS/Azure의 보안 그룹/NSG는 인스턴스나
서브넷에 붙이는 재사용 가능한 규칙 묶음(리소스)이지만, **GCP 방화벽
규칙은 VPC 네트워크 전체에 걸려 있고, 대상 태그나 서비스 계정으로
적용 범위를 좁히는 모델이다** — 그래서 이 파일에는
[`std/cloud/network.md`](../network.md)의 `SecurityGroup`에 정확히
대응하는 독립 리소스가 없다(아래 Domain 참고). 실제 존재하는
서비스이므로 새로 설계할 대상이 아니다(`kind: native`, SPEC.md
1.2절).

# Domain

## Class: GcpVpc.Network

멤버:
- id: string
- name: string

## Class: GcpVpc.Subnet

멤버:
- id: string
- cidrRange: string
- region: string

## Class: GcpVpc.FirewallRule

멤버:
- name: string
- direction: string — `"INGRESS"` 또는 `"EGRESS"`.
- protocol: string
- ports: list<int>
- sourceRangesOrTags: list<string> — CIDR 범위 또는 대상 태그/서비스
  계정.

## Class: GcpVpc.Client

메서드:
- createNetwork(name: string) -> GcpVpc.Network
  설명: 커스텀 모드 VPC를 만든다(서브넷을 수동으로 만들어야 한다).
- createSubnet(networkId: string, cidrRange: string, region: string) -> GcpVpc.Subnet
- createFirewallRule(networkId: string, rule: GcpVpc.FirewallRule) -> GcpVpc.FirewallRule
  설명: 실제 `FirewallsClient().insert(...)`에 대응한다 — 네트워크
  전체에 적용되며, `sourceRangesOrTags`로 범위를 좁힌다.

# Interface

## Library

`net = client.createNetwork("my-vpc")`로 네트워크를 만들고 리전마다
`createSubnet`으로 나눈 뒤, 필요한 트래픽만 여는
`createFirewallRule`을 네트워크에 직접 겁니다(AWS처럼 재사용 가능한
그룹 객체를 만들어 여러 인스턴스에 붙이는 것이 아니다).

# Constraints

- 실제 GCP SDK(`google-cloud-compute`의 `NetworksClient`/
  `SubnetworksClient`/`FirewallsClient`)에 매핑한다.
- 기본적으로 새 VPC 네트워크는 모든 인바운드를 거부한다(자동 생성
  기본 네트워크는 예외적으로 일부 허용 규칙이 딸려 있다 — 실무에서는
  커스텀 모드로 만들고 명시적으로 규칙을 추가하는 것을 권장한다).
- `createFirewallRule`의 우선순위(priority)는 숫자로 지정하며 Azure
  NSG와 비슷하게 낮은 숫자가 먼저 평가된다(이 계약은 기본 우선순위만
  전제한다).

# Examples

## 예제: 특정 포트만 열기

호출: `client.createFirewallRule(net.id, GcpVpc.FirewallRule("allow-https", "INGRESS", "tcp", [443], ["0.0.0.0/0"]))`

기대 동작: 이 네트워크에 속한(대상 태그가 없으면 전체) 인스턴스는
443(HTTPS) 포트로 들어오는 어떤 IP의 연결도 받을 수 있게 된다.

# Open Points

- 서브넷 단위 프록시 전용/NAT 전용 서브넷, 프라이빗 서비스 연결,
  VPC 피어링, 계층형 방화벽 정책(Hierarchical Firewall Policy)은
  다루지 않는다.
