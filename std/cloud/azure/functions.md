#!specpp 0.1

# Meta

- name: std/cloud/azure/functions
- version: 0.1.0
- description: function.json 바인딩 선언으로 트리거·입출력이 정해지는 Azure Functions 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/function.md`](../function.md) 추상 계약의
Azure 구현이다 — 같은 계약의 [AWS 구현](../aws/lambda.md)/[GCP
구현](../gcp/functions.md)도 참고할 수 있다. 실제 존재하는
서비스이므로 새로 설계할 대상이 아니다(`kind: native`, SPEC.md
1.2절).

# Domain

## Class: AzureFunctionsContext

멤버:
- invocationId: string
- functionName: string

메서드:
- getRemainingTimeInMillis() -> int
  설명: Azure Functions에는 이 값을 직접 주는 API가 없다 — 함수
  시작 시각과 호스팅 플랜별 타임아웃(아래 Constraints)으로 근사해야
  한다.

## Class: AzureFunctionsInvokeResult

멤버:
- statusCode: int
- payload: bytes
- functionError: string?

## Class: AzureFunctions.Client

메서드:
- invoke(functionName: string, payload: bytes, async: boolean?) -> AzureFunctionsInvokeResult
  설명: 실제로는 함수의 HTTP 트리거 URL(함수 키 포함)을 직접
  호출하는 것에 대응한다.

# Interface

## Library

### 호출하는 쪽
`AzureFunctions.Client().invoke("resize-image", jsonBytes)`처럼
씁니다.

### 함수 자신 (핸들러)
**Azure Functions는 진입점 시그니처를 코드가 아니라
`function.json`의 바인딩 선언(트리거/입력/출력)으로 정한다** —
[`std/cloud/function.md`](../function.md)가 전제하는 단일
`(event, context) -> response` 모양보다 선언적이고 확장 가능하다.
HTTP 트리거는 보통 `(req: HttpRequest) -> HttpResponse`(Python) 같은
모양이지만, 정확한 시그니처는 언어별 바인딩 확장에 달려 있다 — 이
계약은 이 선언적 바인딩 시스템 자체를 모델링하지 않는다(아래 Open
Points).

# Constraints

- 실제 Azure Functions 런타임(Python `azure.functions` 패키지 등)에
  매핑한다.
- **호스팅 플랜에 따라 타임아웃이 다르다** — Consumption 플랜은
  기본 5분(최대 10분까지 구성 가능, HTTP 트리거는 230초 하드
  제한), Premium/Dedicated 플랜은 더 길게(무제한에 가깝게) 설정할 수
  있다. [`std/cloud/aws/lambda.md`](../aws/lambda.md)의 15분 고정,
  [`std/cloud/gcp/functions.md`](../gcp/functions.md)의 60분과 달리
  Azure는 플랜 선택이 곧 타임아웃 선택이다.
- Consumption 플랜은 콜드 스타트가 있다 — Premium 플랜은 항상 준비된
  인스턴스를 유지해 콜드 스타트를 없앨 수 있다(비용과 맞바꾼다).
- 워크로드 아이덴티티는 관리 ID(Managed Identity)다 —
  [`std/cloud/azure/rbac.md`](rbac.md) 참조.

# Examples

## 예제: 동기 호출

호출: `client.invoke("resize-image", jsonBytes)`

기대 동작: 함수 실행이 끝난 뒤 결과를 반환한다.

# Open Points

- `function.json` 바인딩 시스템 자체(다양한 트리거/입력/출력 확장)는
  모델링하지 않는다 — HTTP 트리거만 전제한다.
- Durable Functions(장기 실행 오케스트레이션)는 다루지 않는다.
