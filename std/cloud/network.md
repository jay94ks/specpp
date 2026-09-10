#!specpp 0.1

# Meta

- name: std/cloud/network
- version: 0.1.0
- description: 클라우드 리소스를 격리된 가상 네트워크로 나누고 트래픽을 걸러내는 네트워크 격리(VPC/가상 네트워크)에 대한 추상 계약.

# Intent

여러 리소스(서버, 데이터베이스 등)를 하나의 계정 안에서 서로 격리된
네트워크 구역으로 나누고, 어떤 트래픽이 어떤 리소스에 들어오고 나갈
수 있는지 규칙으로 제한하고 싶을 때 쓴다.
[`std/cloud/accesscontrol.md`](accesscontrol.md)가 "누가 어떤 API를
부를 수 있는가"를 다룬다면, 이 계약은 "어떤 네트워크 트래픽이 어떤
리소스에 도달할 수 있는가"를 다룬다 — 서로 다른 계층의 접근 제어다.

`std/cloud/accesscontrol.md`와 마찬가지로, 이 API는 보통 애플리케이션
코드가 실행 중에 호출하는 것이 아니라 인프라를 준비하는 단계에서 한 번
구성해 두는 것이다.

# Domain

## Class: Network.Vpc

멤버:
- id: string
- cidrBlock: string — 예: `"10.0.0.0/16"`.

## Class: Network.Subnet

멤버:
- id: string
- cidrBlock: string
- availabilityZone: string

## Class: Network.SecurityGroup

"이 리소스로 들어오고 나갈 수 있는 트래픽"을 정의하는 방화벽 규칙
묶음이다.

메서드:
- authorizeIngress(protocol: string, fromPort: int, toPort: int, cidrOrSourceGroup: string) -> void
- authorizeEgress(protocol: string, fromPort: int, toPort: int, cidrOrSourceGroup: string) -> void
- revokeIngress(protocol: string, fromPort: int, toPort: int, cidrOrSourceGroup: string) -> void

## Class: Network.Client

메서드:
- createVpc(cidrBlock: string) -> Network.Vpc
- createSubnet(vpcId: string, cidrBlock: string, availabilityZone: string) -> Network.Subnet
- createSecurityGroup(vpcId: string, name: string, description: string) -> Network.SecurityGroup

# Interface

## Library

`vpc = client.createVpc("10.0.0.0/16")`로 네트워크를 만들고, 가용
영역마다 `createSubnet`으로 나눈 뒤, 리소스마다 필요한 트래픽만 여는
`SecurityGroup`을 만들어 연결합니다.

# Constraints

- 실제 구현은 [`std/cloud/aws/vpc.md`](aws/vpc.md)(AWS VPC),
  [`std/cloud/gcp/vpc.md`](gcp/vpc.md)(GCP VPC), 또는
  [`std/cloud/azure/vnet.md`](azure/vnet.md)(Azure Virtual Network) 중
  타겟에 맞는 것을 고른다.
- **방화벽 규칙이 적용되는 단위가 제공자마다 다르다.** AWS/Azure는
  "보안 그룹/NSG"라는 재사용 가능한 규칙 묶음을 인스턴스(또는
  서브넷)에 붙이는 모델이지만, GCP는 방화벽 규칙이 VPC 네트워크
  전체에 걸려 있고 대상 태그/서비스 계정으로 범위를 좁히는 모델이다
  — 이 계약의 `SecurityGroup`처럼 명확히 분리된 리소스가 GCP에는
  없다(아래 Open Points). Azure NSG는 우선순위(priority) 숫자로 규칙
  평가 순서를 명시해야 한다는 점도 AWS/GCP와 다르다 — 정확한 차이는
  각 구현 파일 참고.
- **AWS/Azure 보안 그룹·NSG는 상태 저장(stateful)이다** — 들어오는
  연결을 허용하면 응답 트래픽은 자동으로 허용된다.
- 기본적으로 새 보안 경계는 모든 인바운드를 거부하고 모든 아웃바운드는
  허용하는 것이 공통 관례다 — 필요한 포트만 명시적으로 여는 것이
  [`std/cloud/accesscontrol.md`](accesscontrol.md)와 같은 최소 권한
  원칙이다.

# Examples

## 예제: 특정 포트만 열기

호출: `sg.authorizeIngress("tcp", 443, 443, "0.0.0.0/0")`

기대 동작: 이 보안 그룹이 붙은 리소스는 443(HTTPS) 포트로 들어오는
어떤 IP의 연결도 받을 수 있게 된다 — 다른 포트는 여전히 막혀 있다.

# Open Points

- 네트워크 ACL, 라우팅 테이블, 인터넷/NAT 게이트웨이, 네트워크 피어링은
  이 버전의 범위 밖이다.
- GCP의 네트워크 전역 방화벽 규칙 모델은 이 계약의 `SecurityGroup`
  추상과 정확히 1:1로 대응하지 않는다 — 정확한 매핑은
  [`std/cloud/gcp/vpc.md`](gcp/vpc.md)를 참고한다.
