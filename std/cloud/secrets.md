#!specpp 0.1

# Meta

- name: std/cloud/secrets
- version: 0.1.0
- description: 비밀번호·API 키 같은 민감한 값을 코드에 하드코딩하지 않고 안전하게 저장·조회하는 관리형 시크릿 저장소에 대한 추상 계약.

# Intent

DB 비밀번호, 외부 API 키처럼 코드나 환경 변수에 평문으로 두면 안 되는
값을 다룰 때 쓴다. 이 저장소가 이미 강조해 온 원칙 — 접근 키를 코드에
심지 않는다([`std/cloud/objectstorage.md`](objectstorage.md) 등) — 를
그 값 자체(비밀번호 등)에도 적용하는 서비스다.

# Domain

## Class: Secrets.Client

메서드:
- getSecretValue(secretId: string) -> string
  설명: 없으면 오류를 낸다. 값은 보통 JSON 문자열로 저장돼 있는
  경우가 많다 — 파싱은 호출하는 쪽의 몫이다.
- createSecret(name: string, value: string) -> void
- putSecretValue(secretId: string, value: string) -> void
  설명: 기존 시크릿의 값을 새 버전으로 교체한다.

# Interface

## Library

애플리케이션 시작 시(또는 처음 필요할 때) 한 번
`client.getSecretValue("prod/db/password")`로 값을 가져와 **직접
캐싱**해 재사용합니다 — 요청마다 부르지 않습니다.

# Constraints

- 실제 구현은
  [`std/cloud/aws/secretsmanager.md`](aws/secretsmanager.md)(AWS
  Secrets Manager),
  [`std/cloud/gcp/secretmanager.md`](gcp/secretmanager.md)(GCP Secret
  Manager), [`std/cloud/azure/keyvault.md`](azure/keyvault.md)(Azure
  Key Vault) 중 타겟에 맞는 것을 고른다.
- **Azure Key Vault는 이 계약보다 범위가 넓다** — 순수 시크릿뿐 아니라
  암호화 키·X.509 인증서도 같은 서비스로 관리한다. 이 계약은 그중
  시크릿 부분집합만 다룬다(아래 Open Points).
- 값 변경이 새 "버전"으로 쌓이는지(GCP/Azure), 이전 값 위에 그대로
  갱신되는지는 제공자마다 다르다 — 각 구현 파일 참고.
- `getSecretValue` 호출은 보통 호출당 과금되고 네트워크 왕복이 있다 —
  요청마다 부르지 말고 애플리케이션 안에서 캐싱하는 것이 공통 권장
  방식이다.
- **시크릿 값은 절대 로그로 남기면 안 된다.**

# Examples

## 예제: 저장하고 읽기

호출 (순서대로): `client.createSecret("test/key", "s3cr3t")`,
`client.getSecretValue("test/key")`

기대 동작: 두 번째 호출은 `"s3cr3t"`를 반환한다.

## 예제: 없는 시크릿

호출: `client.getSecretValue("없는/키")`

기대 동작: 오류를 낸다.

# Open Points

- 자동 회전(rotation) 훅의 정확한 계약은 제공자마다 다르다 — 각 구현
  파일 참고.
- 암호화 키·인증서 관리(Key Vault의 확장 기능)는 다루지 않는다.
- 세밀한 접근 제어는 [`std/cloud/accesscontrol.md`](accesscontrol.md)의
  범위이며 여기서는 다루지 않는다.
