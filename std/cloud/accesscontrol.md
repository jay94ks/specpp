#!specpp 0.1

# Meta

- name: std/cloud/accesscontrol
- version: 0.1.0
- description: 누가(또는 어떤 리소스가) 무엇을 할 수 있는지를 정의하는 클라우드 접근 제어(IAM)에 대한 추상 계약.

# Intent

이 저장소의 다른 `std/cloud/*.md` 계약들을 실제로 호출할 수 있는지는
전부 이 계약의 실제 구현이 결정한다 — 각 파일의 Constraints에서
반복해 온 "접근 키는 코드에 심지 않는다"는 원칙이 실제로 무엇을
뜻하는지 이 계약이 정의한다.

**다른 `std/cloud/*.md`와의 결정적인 차이.** 대부분의 클라우드 계약은
애플리케이션 코드가 실행 중에 계속 호출하는 런타임 API지만, 접근
제어는 보통 배포 준비(인프라 구성) 단계에서 한 번 설정해 두고
애플리케이션 코드는 그 설정의 존재를 몰라도 되는 API다 — 실제로는
Terraform/CloudFormation/ARM/Bicep 같은 인프라 도구나 배포 스크립트가
이 API를 쓴다.

**이 계약도 근사다.** AWS/GCP는 "역할(Role)에 정책을 붙이고, 리소스가
그 역할을 맡는다"는 모델이 비슷하지만, Azure RBAC는 "역할 정의를
리소스 계층의 특정 범위(scope)에서 특정 principal에게 할당한다"는
구조적으로 다른 모델을 쓴다 — 아래 Constraints에서 이 차이를
명시한다.

# Domain

## Class: AccessControl.PolicyStatement

멤버:
- effect: string — `"Allow"` 또는 `"Deny"`.
- actions: list<string> — 예: `["storage:GetObject"]`.
- resources: list<string> — 리소스 식별자 목록. `"*"`는 모든
  리소스를 뜻한다.

## Class: AccessControl.Role

멤버:
- roleName: string
- id: string
- trustPolicy: list<AccessControl.PolicyStatement> — **누가** 이
  역할을 맡을 수 있는지.

## Class: AccessControl.Client

메서드:
- createRole(roleName: string, trustPolicy: list<AccessControl.PolicyStatement>) -> AccessControl.Role
- putRolePolicy(roleName: string, policyName: string, statements: list<AccessControl.PolicyStatement>) -> void
  설명: 이 역할이 **무엇을** 할 수 있는지(권한 정책)를 붙인다.
- deleteRole(roleName: string) -> void

# Interface

## Library

[`std/cloud/function.md`](function.md) 함수를 배포하기 전에, 그 함수가
실제로 필요한 리소스에만 접근하도록 `createRole(...)` +
`putRolePolicy(...)`로 실행 역할을 먼저 만들어 둡니다.

# Constraints

- 실제 구현은 [`std/cloud/aws/iam.md`](aws/iam.md)(AWS IAM),
  [`std/cloud/gcp/iam.md`](gcp/iam.md)(GCP Cloud IAM),
  [`std/cloud/azure/rbac.md`](azure/rbac.md)(Azure RBAC) 중 타겟에
  맞는 것을 고른다.
- **Azure는 구조적으로 가장 다르다.** AWS/GCP는 역할(또는 서비스
  계정)에 정책을 직접 붙이는 모델이지만, Azure RBAC는 관리 그룹 >
  구독 > 리소스 그룹 > 리소스로 이어지는 계층의 특정 지점(scope)에서,
  미리 정의된(또는 커스텀) **역할 정의**를 사용자/그룹/워크로드
  아이덴티티(관리 ID)에 **할당(assignment)**하는 방식이다 — "이
  워크로드가 이 역할을 맡는다"는 신뢰 정책(trust policy) 단계가
  AWS처럼 명시적이지 않다. 정확한 매핑은
  [`std/cloud/azure/rbac.md`](azure/rbac.md)의 Constraints를 참고한다.
- **최소 권한 원칙(least privilege)**: `actions`/`resources`에
  `"*"`를 쓰면 당장은 편하지만 실제로 필요한 것보다 넓은 권한을
  허용하게 된다.
- 권한 변경은 즉시 반영되지 않을 수 있다 — 세 제공자 모두 변경 사항이
  전 리전/전역으로 퍼지는 데 시간이 걸릴 수 있는 최종 일관성 동작을
  보일 수 있다.

# Examples

## 예제: 역할 만들고 정책 붙이기

호출 (순서대로):
```
role = client.createRole("resize-image-role", [functionTrustStatement])
client.putRolePolicy("resize-image-role", "storage-read-only", [
  AccessControl.PolicyStatement("Allow", ["storage:GetObject"], ["my-bucket/*"])
])
```

기대 동작: 이 역할을 실행 역할로 쓰는 함수는 `my-bucket`의 객체를
읽을 수는 있지만, 쓰거나 지울 수는 없다.

# Open Points

- 사용자·그룹, 관리형(미리 만들어진) 정책 연결, 권한 경계, 다중 계정
  간 역할 위임은 이 버전의 범위 밖이다.
- 정책 조건(예: 특정 IP에서만 허용)은 다루지 않는다.
