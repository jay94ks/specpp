#!specpp 0.1

# Meta

- name: std/cloud/gcp/secretmanager
- version: 0.1.0
- description: 버전이 명시적으로 쌓이는 GCP Secret Manager 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/secrets.md`](../secrets.md) 추상 계약의 GCP
구현이다 — 같은 계약의 [AWS
구현](../aws/secretsmanager.md)/[Azure 구현](../azure/keyvault.md)도
참고할 수 있다. 실제 존재하는 서비스이므로 새로 설계할 대상이
아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: SecretManager.Client

메서드:
- getSecretValue(secretId: string, version: string?) -> string
  설명: 실제 `access_secret_version(name=...)`에 대응한다. `version`을
  생략하면 실제 API의 별칭 `"latest"`를 쓴다.
- createSecret(name: string, value: string) -> void
  설명: 실제로는 `create_secret` 호출 뒤 `add_secret_version`을
  이어 부르는 두 단계다 — 이 계약은 하나로 묶었다.
- putSecretValue(secretId: string, value: string) -> void
  설명: `add_secret_version`에 대응한다 — 기존 값을 덮어쓰는 것이
  아니라 **새 버전을 추가**한다. 이전 버전은 명시적으로
  비활성화(disable)하거나 파기(destroy)하기 전까지 남아 있다.

# Interface

## Library

`client.getSecretValue("prod-db-password")`로 최신 버전 값을 가져와
캐싱합니다.

# Constraints

- 실제 클라이언트 라이브러리 `google-cloud-secret-manager`(Python
  `google.cloud.secretmanager`)에 매핑한다.
- 버전은 불변(immutable)이고 명시적으로 참조된다(또는 `"latest"`) —
  [`std/cloud/aws/secretsmanager.md`](../aws/secretsmanager.md)의
  "값을 교체"라는 표현보다는 "새 버전을 추가"라는 표현이 더 정확하다.
- 권한은 GCP IAM 역할 `roles/secretmanager.secretAccessor` 등으로
  제어한다 — [`std/cloud/gcp/iam.md`](iam.md) 참조.
- **시크릿 값은 절대 로그로 남기면 안 된다**
  ([`std/cloud/secrets.md`](../secrets.md)와 동일한 원칙).

# Examples

## 예제: 저장하고 읽기

호출 (순서대로): `client.createSecret("test-key", "s3cr3t")`,
`client.getSecretValue("test-key")`

기대 동작: 두 번째 호출은 `"s3cr3t"`를 반환한다.

# Open Points

- 자동 회전 훅의 정확한 계약(Secret Manager는 Pub/Sub 알림을 통해
  회전을 트리거한다 — AWS Lambda 직접 호출 모델과 다르다)은 다루지
  않는다.
- 버전 비활성화/파기 API는 다루지 않는다.
