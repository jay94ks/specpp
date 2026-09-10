#!specpp 0.1

# Meta

- name: std/cloud/aws/iam
- version: 0.1.0
- description: 누가(또는 어떤 리소스가) 무엇을 할 수 있는지를 정의하는 접근 제어(AWS IAM) 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/accesscontrol.md`](../accesscontrol.md) 추상 계약의 AWS 구현이다 — 같은 계약의 [GCP 구현](../gcp/iam.md)/[Azure 구현](../azure/rbac.md)도 참고할 수 있다.

이 저장소의 다른 `std/cloud/*.md`(S3, DynamoDB, Lambda 등)를 실제로
호출할 수 있는지는 전부 IAM이 결정한다 — 지금까지 각 파일의
Constraints에서 반복해 온 "접근 키는 코드에 심지 않고 IAM 역할에서
읽는다"는 원칙이 실제로 무엇을 뜻하는지 이 패키지가 정의한다.

**다른 `std/cloud/*.md`와의 결정적인 차이.** S3나 SQS는 애플리케이션
코드가 실행 중에 계속 호출하는 런타임 API지만, IAM은 보통 배포
준비(인프라 구성) 단계에서 한 번 설정해 두고 애플리케이션 코드는 그
설정의 존재를 몰라도 되는 API다 — 실제로는 애플리케이션 코드 안에
이 패키지를 직접 호출하는 줄이 거의 없고, Terraform/CloudFormation/
CDK 같은 인프라 도구나 배포 스크립트가 이 API를 쓴다. 그럼에도 실제
API로 존재하는 것이므로 `kind: native`로 옮긴다(SPEC.md 1.2절) —
배포 자동화 스크립트를 SPP로 작성할 때 이 패키지를 참조한다.

# Domain

## Class: Iam.PolicyStatement

IAM 정책 문서 하나를 이루는 단위 규칙이다(실제 JSON 정책 문서의
`Statement` 배열 원소 하나에 대응).

멤버:
- effect: string — `"Allow"` 또는 `"Deny"`.
- actions: list<string> — 예: `["s3:GetObject", "s3:PutObject"]`.
- resources: list<string> — ARN 목록(예:
  `"arn:aws:s3:::my-bucket/*"`). `"*"`는 모든 리소스를 뜻한다.

## Class: Iam.Role

멤버:
- roleName: string
- arn: string
- trustPolicy: list<Iam.PolicyStatement> — **누가** 이 역할을 맡을 수
  있는지(예: Lambda 서비스 자체, 다른 AWS 계정 등).

## Class: Iam.Client

메서드:
- createRole(roleName: string, trustPolicy: list<Iam.PolicyStatement>) -> Iam.Role
  설명: 실제 `CreateRole`에 대응한다.
- putRolePolicy(roleName: string, policyName: string, statements: list<Iam.PolicyStatement>) -> void
  설명: 이 역할이 **무엇을** 할 수 있는지(권한 정책)를 붙인다(실제
  `PutRolePolicy`/`AttachRolePolicy`에 대응 — 이 계약은 역할에 직접
  박아 넣는 인라인 정책 쪽으로 단순화했다).
- deleteRole(roleName: string) -> void

# Interface

## Library

[`std/cloud/aws/lambda.md`](lambda.md) 함수를 배포하기 전에, 그 함수가
실제로 필요한 리소스에만 접근하도록 `createRole(...)` +
`putRolePolicy(...)`로 실행 역할을 먼저 만들어 둡니다.

# Constraints

- 실제 AWS SDK(`boto3.client("iam")`, JS SDK v3의 `IAMClient` 등)에
  매핑한다.
- **최소 권한 원칙(least privilege)**: `actions`/`resources`에
  `"*"`를 쓰면 당장은 편하지만 실제로 필요한 것보다 넓은 권한을
  허용하게 된다 — 이 저장소의 다른 `std/cloud/*.md`를 참조하는
  역할은, 정확히 그 파일이 실제로 부르는 API(예:
  [`std/cloud/aws/s3.md`](s3.md)의 `getObject`라면 `"s3:GetObject"`)만
  허용하는 것을 권장한다.
- `effect: "Deny"`는 같은 정책 안의 `"Allow"`보다 항상 우선한다(실제
  IAM 평가 규칙) — 명시적 거부는 어떤 허용으로도 뒤집을 수 없다.
- 정책은 즉시 반영되지 않을 수 있다 — 실제 IAM은 변경 사항이 전
  리전으로 퍼지는 데 최대 몇 분이 걸릴 수 있는 최종 일관성 서비스다.

# Examples

## 예제: 역할 만들고 정책 붙이기

호출 (순서대로):
```
role = iam.createRole("resize-image-role", [lambdaTrustStatement])
iam.putRolePolicy("resize-image-role", "s3-read-only", [
  Iam.PolicyStatement("Allow", ["s3:GetObject"], ["arn:aws:s3:::my-bucket/*"])
])
```

기대 동작: 이 역할을 실행 역할로 쓰는 Lambda 함수는 `my-bucket`의
객체를 읽을 수는 있지만(GetObject), 쓰거나 지울 수는 없다(그 액션은
허용 목록에 없으므로 기본값인 거부가 적용된다).

# Open Points

- 사용자(IAM User)·그룹, 관리형 정책(AWS가 미리 만들어 둔 정책) 연결,
  권한 경계(permission boundary), 다중 계정 간 역할 위임(AssumeRole
  체인)은 이 버전의 범위 밖이다.
- 정책 조건(condition, 예: 특정 IP에서만 허용)은 다루지 않는다.
