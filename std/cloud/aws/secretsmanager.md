#!specpp 0.1

# Meta

- name: std/cloud/aws/secretsmanager
- version: 0.1.0
- description: 비밀번호·API 키 같은 민감한 값을 코드에 하드코딩하지 않고 안전하게 저장·조회하는 관리형 시크릿 저장소(AWS Secrets Manager) 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/secrets.md`](../secrets.md) 추상 계약의 AWS 구현이다 — 같은 계약의 [GCP 구현](../gcp/secretmanager.md)/[Azure 구현](../azure/keyvault.md)도 참고할 수 있다.

DB 비밀번호, 외부 API 키처럼 코드나 환경 변수에 평문으로 두면 안 되는
값을 다룰 때 쓴다. 이 저장소가 이미 강조해 온 원칙 — 접근 키를
코드에 심지 않는다([`std/cloud/aws/s3.md`](s3.md) Constraints 등) — 를
그 값 자체(비밀번호 등)에도 적용하는 서비스다. 실제 존재하는
서비스이므로 새로 설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: SecretsManager.Client

메서드:
- getSecretValue(secretId: string) -> string
  설명: 실제 `GetSecretValue`에 대응한다. 없으면 오류를 낸다. 값은
  보통 JSON 문자열(예: `{"username": "...", "password": "..."}`)로
  저장돼 있는 경우가 많다 — 파싱은 호출하는 쪽의 몫이다.
- createSecret(name: string, value: string) -> void
- putSecretValue(secretId: string, value: string) -> void
  설명: 기존 시크릿의 값을 새 버전으로 교체한다 — 이전 버전도 잠시
  동안(회전 도중 롤백을 위해) 함께 보관된다(아래 Constraints).

# Interface

## Library

애플리케이션 시작 시(또는 처음 필요할 때) 한 번
`client.getSecretValue("prod/db/password")`로 값을 가져와 **직접
캐싱**해 재사용합니다 — 요청마다 부르지 않습니다(아래 Constraints).

# Constraints

- 실제 AWS SDK(`boto3.client("secretsmanager")`, JS SDK v3의
  `SecretsManagerClient` 등)에 매핑한다.
- `getSecretValue` 호출은 호출당 과금되고 네트워크 왕복이 있다 —
  요청마다 부르지 말고 애플리케이션 안에서 캐싱한 뒤, 시크릿 회전
  주기(아래)보다 짧은 간격으로만 다시 불러오는 것이 실제 권장
  방식이다(AWS가 공식 캐싱 클라이언트 라이브러리도 별도로 제공할
  정도다).
- **자동 회전(rotation)**을 설정하면 정해진 주기마다 값이 자동으로
  바뀐다 — 실제로는 회전용 [`std/cloud/aws/lambda.md`](lambda.md) 함수가
  트리거된다. 이 계약은 회전 함수 자체의 계약(4단계
  create/set/test/finish 시크릿)은 다루지 않는다(아래 Open Points).
- **시크릿 값은 절대 로그로 남기면 안 된다** — `getSecretValue`의
  반환값을 [`std/stdout.md`](../../stdout.md)나
  [`std/system/debug.md`](../../system/debug.md)로 출력하는 코드는 이
  계약을 어기는 것으로 취급한다.

# Examples

## 예제: 저장하고 읽기

호출 (순서대로): `client.createSecret("test/key", "s3cr3t")`,
`client.getSecretValue("test/key")`

기대 동작: 두 번째 호출은 `"s3cr3t"`를 반환한다.

## 예제: 없는 시크릿

호출: `client.getSecretValue("없는/키")`

기대 동작: 오류를 낸다.

# Open Points

- 자동 회전 Lambda 함수 자체의 4단계 계약(createSecret/setSecret/
  testSecret/finishSecret)은 다루지 않는다.
- 시크릿에 대한 세밀한 접근 제어(리소스 정책)는
  [`std/cloud/aws/iam.md`](iam.md)의 범위이며 여기서는 다루지 않는다.
- 비슷한 목적의 더 저렴한 대안인 SSM Parameter Store(민감하지 않은
  설정값에 흔히 쓰인다)는 별도 패키지로 다루지 않는다.
