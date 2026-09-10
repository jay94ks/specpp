#!specpp 0.1

# Meta

- name: std/cloud/azure/vnet
- version: 0.1.0
- description: 우선순위 숫자로 평가 순서를 명시하는 네트워크 보안 그룹(NSG)을 쓰는 Azure Virtual Network 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/network.md`](../network.md) 추상 계약의
Azure 구현이다 — 같은 계약의 [AWS 구현](../aws/vpc.md)/[GCP
구현](../gcp/vpc.md)도 참고할 수 있다. 실제 존재하는 서비스이므로
새로 설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: VNet.Network

멤버:
- id: string
- addressSpace: string — 예: `"10.0.0.0/16"`.

## Class: VNet.Subnet

멤버:
- id: string
- addressPrefix: string

## Class: VNet.NetworkSecurityGroup

AWS의 `SecurityGroup`, GCP의 방화벽 규칙과 같은 역할을 하지만,
**규칙마다 명시적인 우선순위 숫자가 필요하다**는 점이 다르다(아래
Constraints).

메서드:
- addSecurityRule(name: string, direction: string, priority: int, protocol: string, portRange: string, sourceOrDest: string, allow: boolean) -> void
  설명: 실제 `security_rules.begin_create_or_update(...)`에
  대응한다. `priority`(100~4096)가 낮을수록 먼저 평가된다.
  `allow`가 false면 명시적 거부 규칙이다(AWS 보안 그룹에는 없는
  기능 — 아래 Constraints).

## Class: VNet.Client

메서드:
- createVirtualNetwork(addressSpace: string) -> VNet.Network
- createSubnet(vnetId: string, addressPrefix: string) -> VNet.Subnet
- createNetworkSecurityGroup(vnetId: string, name: string) -> VNet.NetworkSecurityGroup

# Interface

## Library

`vnet = client.createVirtualNetwork("10.0.0.0/16")`로 네트워크를
만들고, `createSubnet`으로 나눈 뒤, 서브넷이나 개별 NIC에 붙일
`NetworkSecurityGroup`을 만들어 `addSecurityRule`로 규칙을 우선순위
순서대로 추가합니다.

# Constraints

- 실제 Azure SDK(`azure-mgmt-network`의 `NetworkManagementClient`)에
  매핑한다.
- **NSG는 상태 저장(stateful)이다** — [`std/cloud/aws/vpc.md`](../aws/vpc.md)의
  보안 그룹과 같은 지점이다(들어오는 연결을 허용하면 응답 트래픽은
  자동으로 허용된다).
- **규칙에 명시적 우선순위(100~4096, 낮을수록 우선)가 필요하고,
  명시적 `Deny` 규칙을 둘 수 있다** — AWS 보안 그룹은 우선순위 개념이
  없고(모든 규칙이 순수 허용 목록이다) 명시적 거부도 없다는 점과
  다르다. 이 점에서 NSG는 전통적인 방화벽 규칙 목록(순서가 있는
  ACL)에 더 가깝다.
- **NSG는 서브넷 또는 개별 네트워크 인터페이스(NIC) 둘 중 어디에도
  붙을 수 있다** — AWS 보안 그룹이 인스턴스(ENI)에만 붙는 것과 다른
  지점이다. 둘 다에 붙어 있으면 두 NSG의 규칙이 모두 적용된다.

# Examples

## 예제: 특정 포트만 열기

호출: `nsg.addSecurityRule("allow-https", "Inbound", 100, "Tcp", "443", "0.0.0.0/0", true)`

기대 동작: 이 NSG가 붙은 서브넷/NIC은 443(HTTPS) 포트로 들어오는
어떤 IP의 연결도 받을 수 있게 된다 — 우선순위 100보다 낮은 숫자의
`Deny` 규칙이 먼저 없다면 그대로 적용된다.

# Open Points

- 애플리케이션 보안 그룹(ASG, NSG 규칙에서 IP 대신 논리적 그룹으로
  참조할 수 있는 태그형 리소스), 라우팅 테이블, NAT 게이트웨이, VNet
  피어링은 이 버전의 범위 밖이다.
