#!specpp 0.1

# Meta

- name: std/cloud/vpc
- version: 0.1.0
- description: 클라우드 리소스를 격리된 가상 네트워크로 나누고 트래픽을 걸러내는 네트워크 격리(AWS VPC/보안 그룹) 실체 명세.
- kind: native

# Intent

여러 리소스(서버, 데이터베이스 등)를 하나의 계정 안에서 서로 격리된
네트워크 구역으로 나누고, 어떤 트래픽이 어떤 리소스에 들어오고 나갈
수 있는지 규칙으로 제한하고 싶을 때 쓴다. [`std/cloud/iam.md`](iam.md)가
"누가 어떤 API를 부를 수 있는가"를 다룬다면, 이 패키지는 "어떤
네트워크 트래픽이 어떤 리소스에 도달할 수 있는가"를 다룬다 — 서로
다른 계층의 접근 제어다.

`std/cloud/iam.md`와 마찬가지로, 이 API는 보통 애플리케이션 코드가
실행 중에 호출하는 것이 아니라 인프라를 준비하는 단계에서 한 번
구성해 두는 것이다(아래 Constraints) — 그럼에도 실제 API로 존재하므로
`kind: native`로 옮긴다(SPEC.md 1.2절).

# Domain

## Class: Vpc.Network

멤버:
- vpcId: string
- cidrBlock: string — 예: `"10.0.0.0/16"`.

## Class: Vpc.Subnet

멤버:
- subnetId: string
- cidrBlock: string — vpc의 `cidrBlock` 범위 안이어야 한다.
- availabilityZone: string

## Class: Vpc.SecurityGroup

"이 리소스로 들어오고 나갈 수 있는 트래픽"을 정의하는 방화벽 규칙
묶음이다.

메서드:
- authorizeIngress(protocol: string, fromPort: int, toPort: int, cidrOrSourceGroup: string) -> void
  설명: 실제 `AuthorizeSecurityGroupIngress`에 대응한다 — 들어오는
  트래픽을 허용하는 규칙을 추가한다.
- authorizeEgress(protocol: string, fromPort: int, toPort: int, cidrOrSourceGroup: string) -> void
  설명: 나가는 트래픽을 허용하는 규칙을 추가한다.
- revokeIngress(protocol: string, fromPort: int, toPort: int, cidrOrSourceGroup: string) -> void

## Class: Vpc.Client

메서드:
- createVpc(cidrBlock: string) -> Vpc.Network
- createSubnet(vpcId: string, cidrBlock: string, availabilityZone: string) -> Vpc.Subnet
- createSecurityGroup(vpcId: string, name: string, description: string) -> Vpc.SecurityGroup

# Interface

## Library

`vpc = client.createVpc("10.0.0.0/16")`로 네트워크를 만들고, 가용
영역마다 `createSubnet`으로 나눈 뒤, 리소스마다 필요한 트래픽만 여는
`SecurityGroup`을 만들어 연결합니다.

# Constraints

- 실제 AWS SDK(`boto3.client("ec2")`의 VPC 관련 메서드들, JS SDK v3의
  `EC2Client` 등 — VPC는 실제로 EC2 API의 일부다)에 매핑한다.
- **보안 그룹은 상태 저장(stateful)이다** — 들어오는 연결을 허용하면
  그 연결에 대한 응답 트래픽은 별도로 `authorizeEgress`를 걸지 않아도
  자동으로 허용된다(방화벽 규칙마다 따로 열어야 하는 네트워크 ACL과
  다른 지점 — 네트워크 ACL은 이 버전에서 다루지 않는다, 아래 Open
  Points).
- 기본적으로 새 보안 그룹은 모든 인바운드를 거부하고 모든 아웃바운드는
  허용한다 — 실제로 필요한 포트만 `authorizeIngress`로 명시적으로
  여는 것이 [`std/cloud/iam.md`](iam.md)와 같은 최소 권한 원칙이다.
- `cidrOrSourceGroup`에 `"0.0.0.0/0"`(모든 IP)을 쓰면 인터넷 전체에
  여는 것이다 — 정말 공개 서비스(예: 80/443 포트의 공개 웹 서버)가
  아니라면 특정 CIDR이나 다른 보안 그룹 ID로 좁히는 것을 권장한다.

# Examples

## 예제: 특정 포트만 열기

호출: `sg.authorizeIngress("tcp", 443, 443, "0.0.0.0/0")`

기대 동작: 이 보안 그룹이 붙은 리소스는 443(HTTPS) 포트로 들어오는
어떤 IP의 연결도 받을 수 있게 된다 — 다른 포트(예: 22/SSH)는 별도로
열지 않는 한 여전히 막혀 있다.

# Open Points

- 네트워크 ACL(서브넷 단위의 상태 비저장 규칙), 라우팅 테이블,
  인터넷 게이트웨이/NAT 게이트웨이, VPC 피어링은 이 버전의 범위
  밖이다.
- [`std/cloud/lambda.md`](lambda.md) 함수나 다른 관리형 서비스를 이
  VPC 안에 배치하는 것(콜드 스타트에 영향을 준다)은 다루지 않는다.
