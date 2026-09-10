#!specpp 0.1

# Meta

- name: std/cloud/gcp/functions
- version: 0.1.0
- description: Cloud Run 위에서 동작하는 GCP Cloud Functions(2세대) 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/function.md`](../function.md) 추상 계약의
GCP 구현이다 — 같은 계약의 [AWS 구현](../aws/lambda.md)/[Azure
구현](../azure/functions.md)도 참고할 수 있다. 실제 존재하는
서비스이므로 새로 설계할 대상이 아니다(`kind: native`, SPEC.md
1.2절).

# Domain

## Class: CloudFunctionsContext

멤버:
- requestId: string
- functionName: string
- memoryLimitInMB: int

메서드:
- getRemainingTimeInMillis() -> int

## Class: CloudFunctionsInvokeResult

멤버:
- statusCode: int
- payload: bytes
- functionError: string?

## Class: CloudFunctions.Client

메서드:
- invoke(functionName: string, payload: bytes, async: boolean?) -> CloudFunctionsInvokeResult
  설명: 실제로는 함수의 HTTPS 트리거 URL을 직접 호출하는 것에
  대응한다(2세대 함수는 내부적으로 Cloud Run 서비스다). `async: true`면
  Eventarc/Pub/Sub([`std/cloud/gcp/pubsub.md`](pubsub.md))로 이벤트를
  발행해 비동기 트리거를 유도하는 방식으로 근사한다.

# Interface

## Library

### 호출하는 쪽
`CloudFunctions.Client().invoke("resize-image", jsonBytes)`처럼
씁니다.

### 함수 자신 (핸들러)
**GCP는 트리거 종류에 따라 진입점 모양이 둘로 나뉜다** —
[`std/cloud/function.md`](../function.md)가 전제하는 단일
`(event, context) -> response` 모양과 다르다:
- HTTP 트리거: `(request) -> response` — 실제
  `@functions_framework.http` 데코레이터가 붙은 함수.
- 이벤트 트리거(Pub/Sub, Cloud Storage 등): `(cloudEvent) -> void` —
  실제 `@functions_framework.cloud_event` 데코레이터가 붙은 함수. 값을
  반환하지 않는다(호출자는 이미 비동기로 기대한다).

# Constraints

- 실제 `functions-framework` 라이브러리와 `gcloud functions deploy`
  (또는 Cloud Functions API)에 매핑한다.
- **최대 실행 시간이 60분까지 가능하다** — 2세대 함수는 내부적으로
  Cloud Run이기 때문이다. [`std/cloud/aws/lambda.md`](../aws/lambda.md)의
  15분 고정 상한보다 훨씬 길다.
- **동시성 모델이 다르다** — Lambda는 인스턴스 하나가 요청 하나만
  처리하지만, Cloud Functions(2세대)는 인스턴스 하나가 여러 요청을
  동시에 처리하도록 설정할 수 있다(Cloud Run의 동시성 설정을 그대로
  물려받는다).
- 콜드 스타트는 AWS/Azure와 마찬가지로 있다.
- 워크로드 아이덴티티는 GCP 서비스 계정이다 —
  [`std/cloud/gcp/iam.md`](iam.md) 참조.

# Examples

## 예제: 동기 호출

호출: `client.invoke("resize-image", jsonBytes)`

기대 동작: 함수 실행이 끝난 뒤 결과를 반환한다.

# Open Points

- Cloud Run으로의 직접 배포(컨테이너 이미지 기반)와의 경계는 다루지
  않는다.
- 1세대 Cloud Functions(다른 실행 모델)는 다루지 않는다 — 2세대만
  전제한다.
