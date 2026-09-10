#!specpp 0.1

# Meta

- name: std/cloud/azure/rbac
- version: 0.1.0
- description: 리소스 계층의 특정 범위(scope)에 역할 정의를 할당하는 Azure RBAC(Microsoft Entra ID 기반) 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/accesscontrol.md`](../accesscontrol.md) 추상
계약의 Azure 구현이다 — 같은 계약의 [AWS 구현](../aws/iam.md)/[GCP
구현](../gcp/iam.md)도 참고할 수 있다.

**구조적 차이를 먼저 밝힌다.** AWS IAM Role은 "누가 이 역할을 맡을 수
있는가"를 정의하는 신뢰 정책(trust policy)이 명시적인 첫 단계지만,
**Azure RBAC에는 이 단계가 없다** — 대신 관리 그룹 > 구독 > 리소스
그룹 > 리소스로 이어지는 계층의 특정 지점(scope)에서, 미리 정의된
(또는 커스텀) **역할 정의(role definition)**를 사용자·그룹·서비스
principal·**관리 ID(Managed Identity)**에 바로 **할당(assignment)**한다.
워크로드(함수 등)의 신원은 보통 관리 ID를 그 리소스에서 켜는 것으로
시작한다 — AWS IAM Role, GCP 서비스 계정과 같은 자리를 채운다. 실제
존재하는 서비스이므로 새로 설계할 대상이 아니다(`kind: native`,
SPEC.md 1.2절).

# Domain

## Class: AzureRbac.ManagedIdentity

멤버:
- principalId: string
- clientId: string

## Class: AzureRbac.RoleAssignment

멤버:
- id: string
- roleDefinitionId: string — 예: 내장 역할 `"Storage Blob Data
  Reader"`의 ID, 또는 커스텀 역할 정의 ID.
- principalId: string
- scope: string — 리소스 계층 경로(예:
  `"/subscriptions/.../resourceGroups/.../providers/.../storageAccounts/..."`).

## Class: AzureRbac.Client

메서드:
- enableManagedIdentity(resourceId: string) -> AzureRbac.ManagedIdentity
  설명: 함수 앱 등 리소스에 시스템 할당 관리 ID를 켠다.
- createRoleAssignment(scope: string, roleDefinitionId: string, principalId: string) -> AzureRbac.RoleAssignment
  설명: 실제 `AuthorizationManagementClient().role_assignments.create(...)`에
  대응한다.
- deleteRoleAssignment(id: string) -> void

# Interface

## Library

함수 앱을 만든 뒤 `enableManagedIdentity(functionApp.id)`로 신원을
켜고, 그 `principalId`를 필요한 리소스의 scope에
`createRoleAssignment`로 할당합니다 — AWS처럼 "역할을 만들고 정책을
붙이는" 별도 단계가 아니라 "리소스에 신원을 켜고, 그 신원에 권한을
바로 할당하는" 두 단계다.

# Constraints

- 실제 Azure SDK(`azure-mgmt-authorization`의
  `AuthorizationManagementClient`, `azure-mgmt-msi`의 관리 ID API)에
  매핑한다.
- **최소 권한 원칙**: 가능하면 구독/리소스 그룹 전체가 아니라 개별
  리소스 scope에 할당하는 것을 권장한다 — scope가 넓을수록 그 역할이
  적용되는 리소스 범위도 함께 넓어진다.
- 내장 역할(Built-in role, 예: `"Storage Blob Data Reader"`)이
  실제로 필요한 권한과 정확히 일치하지 않으면 커스텀 역할 정의를
  만들어야 한다(이 버전은 내장 역할 사용만 전제한다, 아래 Open
  Points).
- 역할 할당은 전파에 몇 분 걸릴 수 있는 최종 일관성 동작을 보일 수
  있다.

# Examples

## 예제: 관리 ID 켜고 권한 할당

호출 (순서대로):
```
mi = client.enableManagedIdentity(functionApp.id)
client.createRoleAssignment(storageAccount.id, "Storage Blob Data Reader", mi.principalId)
```

기대 동작: 이 함수 앱은 해당 스토리지 계정의 blob을 읽을 수는 있지만,
쓰거나 지울 수는 없다(그 권한이 할당된 역할에 없으므로 기본값인
거부가 적용된다).

# Open Points

- 커스텀 역할 정의 생성, 조건부 역할 할당(ABAC 조건), 사용자 할당
  관리 ID(리소스 여러 개가 공유하는 신원)는 이 버전의 범위 밖이다.
