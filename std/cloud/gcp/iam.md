#!specpp 0.1

# Meta

- name: std/cloud/gcp/iam
- version: 0.1.0
- description: 리소스에 역할 바인딩을 직접 붙이는 GCP Cloud IAM 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/accesscontrol.md`](../accesscontrol.md) 추상
계약의 GCP 구현이다 — 같은 계약의 [AWS 구현](../aws/iam.md)/[Azure
구현](../azure/rbac.md)도 참고할 수 있다. 실제 존재하는 서비스이므로
새로 설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: GcpIam.Binding

멤버:
- role: string — 예: `"roles/storage.objectViewer"`.
- members: list<string> — 예:
  `["serviceAccount:fn@my-project.iam.gserviceaccount.com"]`.

## Class: GcpIam.ServiceAccount

워크로드(함수, VM 등)가 실제로 API를 호출할 때 쓰는 신원이다 — AWS
IAM 역할, Azure의 관리 ID(Managed Identity)와 같은 역할을 한다.

멤버:
- email: string
- uniqueId: string

## Class: GcpIam.Client

메서드:
- createServiceAccount(name: string) -> GcpIam.ServiceAccount
- getIamPolicy(resourceId: string) -> list<GcpIam.Binding>
  설명: 실제 `resource.getIamPolicy()`에 대응한다.
- setIamPolicy(resourceId: string, bindings: list<GcpIam.Binding>) -> void
  설명: 정책 전체를 교체한다(실제로는 리소스 버전 충돌을 막기 위한
  ETag 기반 낙관적 잠금이 있다 — 이 계약은 단순화했다, 아래 Open
  Points).
- addBinding(resourceId: string, role: string, member: string) -> void
  설명: 기존 정책에 바인딩 하나를 추가한다(읽기-수정-쓰기를 대신해
  주는 편의 메서드).

# Interface

## Library

함수를 만들기 전에 `createServiceAccount`로 워크로드 신원을 만들고,
그 신원의 `email`을 `member`(`"serviceAccount:" + email`)로 삼아
필요한 리소스에 `addBinding`으로 최소 권한만 부여합니다.

# Constraints

- 실제 API(`resourcemanager_v3`, 각 리소스 타입의
  `setIamPolicy`/`getIamPolicy` 메서드)에 매핑한다.
- **정책이 역할(Role)이 아니라 리소스에 직접 붙는다** — AWS처럼
  "역할을 만들고 그 역할에 정책을 붙인 뒤 리소스가 그 역할을 맡는"
  것이 아니라, "리소스(버킷, 프로젝트 등) 자체에 `role: members`
  바인딩 목록을 설정"하는 모델이다 —
  [`std/cloud/accesscontrol.md`](../accesscontrol.md)의
  `putRolePolicy`는 이 파일에서 `addBinding`으로 근사했다.
- 서비스 계정은 사람이 아니라 워크로드를 위한 신원이다 — AWS IAM
  Role/Azure 관리 ID와 개념적으로 같은 자리를 채운다.
- 정책 변경은 전파에 몇 분 걸릴 수 있는 최종 일관성 동작을 보일 수
  있다.

# Examples

## 예제: 서비스 계정 만들고 권한 부여

호출 (순서대로):
```
sa = client.createServiceAccount("resize-image-fn")
client.addBinding("my-bucket", "roles/storage.objectViewer", "serviceAccount:" + sa.email)
```

기대 동작: 이 서비스 계정을 쓰는 함수는 `my-bucket`의 객체를 읽을 수
있게 된다.

# Open Points

- 조직/폴더/프로젝트 계층의 정책 상속, 조건부 바인딩(IAM
  Conditions), ETag 기반 낙관적 동시성 제어는 다루지 않는다.
