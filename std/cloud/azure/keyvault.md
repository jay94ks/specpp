#!specpp 0.1

# Meta

- name: std/cloud/azure/keyvault
- version: 0.1.0
- description: 시크릿뿐 아니라 암호화 키·인증서도 함께 관리하는 Azure Key Vault 실체 명세(이 파일은 시크릿 부분집합만 다룬다).
- kind: native

# Intent

이 패키지는 [`std/cloud/secrets.md`](../secrets.md) 추상 계약의
Azure 구현이다 — 같은 계약의 [AWS
구현](../aws/secretsmanager.md)/[GCP 구현](../gcp/secretmanager.md)도
참고할 수 있다. 실제 존재하는 서비스이므로 새로 설계할 대상이
아니다(`kind: native`, SPEC.md 1.2절).

**범위가 더 넓은 서비스라는 점을 먼저 밝힌다.** Key Vault는 순수
시크릿(`SecretClient`)뿐 아니라 암호화 키(`KeyClient`)와 X.509
인증서(`CertificateClient`)도 같은 서비스로 관리한다 — 이 파일은
`std/cloud/secrets.md`가 요구하는 시크릿 부분집합만 다룬다(아래 Open
Points).

# Domain

## Class: KeyVault.Client

생성자:
- KeyVault.Client(vaultUrl: string)

메서드:
- getSecretValue(secretName: string, version: string?) -> string
  설명: 실제 `SecretClient.get_secret(name, version=...)`에 대응한다.
  `version`을 생략하면 최신 버전을 가져온다.
- createSecret(name: string, value: string) -> void
- putSecretValue(secretName: string, value: string) -> void
  설명: 실제 `set_secret(name, value)`에 대응한다 — GCP Secret
  Manager처럼 새 버전을 만든다(값을 그 자리에서 덮어쓰지 않는다).

# Interface

## Library

`client = KeyVault.Client("https://my-vault.vault.azure.net")`로
클라이언트를 만든 뒤 `getSecretValue`로 값을 가져와 캐싱합니다.

# Constraints

- 실제 클라이언트 라이브러리 `azure-keyvault-secrets`(Python
  `azure.keyvault.secrets`)에 매핑한다.
- 접근 제어는 두 모델 중 하나다 — (권장) RBAC 역할 할당(예:
  `"Key Vault Secrets User"`, [`std/cloud/azure/rbac.md`](rbac.md)
  참조), 또는 레거시 액세스 정책(vault 자체에 직접 붙이는 권한 목록).
  둘을 섞어 쓰면 혼란스러우므로 하나만 골라 쓰는 것을 권장한다.
- 값을 바꾸면 새 버전이 생긴다 — 이전 버전은 명시적으로 비활성화하기
  전까지 여전히 조회 가능하다.
- **시크릿 값은 절대 로그로 남기면 안 된다**
  ([`std/cloud/secrets.md`](../secrets.md)와 동일한 원칙).

# Examples

## 예제: 저장하고 읽기

호출 (순서대로): `client.createSecret("test-key", "s3cr3t")`,
`client.getSecretValue("test-key")`

기대 동작: 두 번째 호출은 `"s3cr3t"`를 반환한다.

# Open Points

- 암호화 키(`KeyClient`) 관리, 인증서(`CertificateClient`) 관리는
  다루지 않는다 — 이 파일은 시크릿만 다룬다.
- 소프트 삭제(soft-delete)·퍼지 보호(purge protection) 복구 절차는
  다루지 않는다.
