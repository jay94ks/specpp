#!specpp 0.1

# Meta

- name: std/cloud/lambda
- version: 0.1.0
- description: 요청·이벤트에 반응해 코드를 실행하는 서버리스 컴퓨트(AWS Lambda) 실체 명세 — 함수를 호출하는 쪽과 함수 자신(핸들러)의 실제 계약을 함께 다룬다.
- kind: native

# Intent

서버를 직접 띄우고 관리하지 않고, 이벤트(HTTP 요청, 큐 메시지, 파일
업로드 등)가 생길 때만 코드를 실행하고 싶을 때 쓴다.
[`std/system/process.md`](../system/process.md)가 "이미 떠 있는
프로세스를 실행·대기"한다면, 이 패키지는 "요청이 올 때만 실행 환경
자체를 대신 띄워 주는" 관리형 서비스를 다룬다. 실제 존재하는
서비스이므로 새로 설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

두 가지 방향을 함께 다룬다: (1) 다른 코드가 Lambda 함수를 **호출하는**
쪽(`Lambda.Client.invoke`), (2) Lambda 함수 자신이 지켜야 하는 **핸들러
계약**(이벤트를 받아 응답을 돌려주는 함수 모양) — 둘 다 실제 AWS
Lambda API/런타임 계약이다.

# Domain

## Class: Lambda.Context

실행 중인 함수 인스턴스 자신에 대한 정보다(핸들러의 두 번째 인자로
전달된다).

멤버:
- requestId: string — 이번 호출 고유 ID.
- functionName: string
- memoryLimitInMB: int

메서드:
- getRemainingTimeInMillis() -> int
  설명: 이번 호출의 타임아웃까지 남은 시간(밀리초). 타임아웃 직전에
  정리 작업을 할지 판단하는 데 쓴다.

## Class: Lambda.InvokeResult

멤버:
- statusCode: int
- payload: bytes — 함수가 반환한 값(보통 JSON).
- functionError: string? — 함수 실행 중 예외가 발생했다면
  `"Unhandled"`/`"Handled"`. 정상 종료면 null.

## Class: Lambda.Client

메서드:
- invoke(functionName: string, payload: bytes, async: boolean?) -> Lambda.InvokeResult
  설명: 실제 `Invoke` API에 대응한다. `async`가 false(기본값, 실제
  API의 `InvocationType: "RequestResponse"`)면 함수 실행이 끝날 때까지
  기다렸다가 결과를 반환한다. true(`"Event"`)면 큐에 넣기만 하고 즉시
  반환한다 — 이때 `payload`는 항상 빈 결과다.

# Interface

## Library

### 호출하는 쪽
`Lambda.Client().invoke("resize-image", jsonBytes)`처럼 동기로 부르고
결과를 기다리거나, `async: true`로 결과를 기다리지 않고 이벤트만
던집니다.

### 함수 자신 (핸들러)
Lambda 함수는 `(event: bytes, context: Lambda.Context) -> bytes` 모양의
진입점 하나로 작성합니다 — 실제 런타임(Node.js `exports.handler`,
Python `def handler(event, context)` 등)이 요청마다 이 함수를 부르고
반환값을 호출자에게 돌려줍니다. 이 진입점 안에서 하는 일은 이
저장소의 다른 패키지(예: `std/cloud/s3.md`, `std/cloud/dynamodb.md`)를
평범하게 쓰는 일반 코드와 다르지 않다 — Lambda 고유의 부분은 오직
"이벤트를 어떻게 받고 응답을 어떻게 돌려주는가"라는 진입점 모양뿐이다.

# Constraints

- 실제 AWS SDK(`boto3.client("lambda")`의 `invoke`, JS SDK v3의
  `LambdaClient` + `InvokeCommand` 등)에 매핑한다.
- **콜드 스타트(cold start)**: 한동안 호출이 없던 함수는 처음 호출될
  때 실행 환경을 새로 준비하느라 수백 ms~수 초가 더 걸릴 수 있다 —
  지연시간에 민감한 경로라면 이 지연을 감안해야 한다.
- 최대 실행 시간(타임아웃)은 15분이다 — 이보다 오래 걸리는 작업은
  Lambda로 옮길 수 없다(배치 작업 등은 별도 컴퓨트를 쓴다).
- 함수가 실제로 접근할 수 있는 AWS 리소스(S3 버킷, DynamoDB 테이블
  등)는 이 코드가 아니라 함수에 연결된 실행 역할(execution role)의
  권한으로 결정된다 — [`std/cloud/iam.md`](iam.md) 참조. 코드에 접근
  키를 직접 넣지 않는다(다른 `std/cloud/*.md`와 같은 원칙,
  [`std/cloud/s3.md`](s3.md) Constraints 참조).
- 메모리(128MB~10,240MB)를 늘리면 CPU 할당량도 함께 늘어난다(실제
  AWS 과금·성능 모델) — 순수 메모리 절약이 항상 비용을 줄이는 것은
  아니다.

# Examples

## 예제: 동기 호출

호출: `client.invoke("resize-image", jsonBytes)`

기대 동작: 함수 실행이 끝난 뒤 `Lambda.InvokeResult`를 반환한다 —
`functionError`가 null이면 `payload`가 함수의 정상 반환값이다.

## 예제: 핸들러 진입점

호출: 실제 런타임이 이벤트가 들어올 때마다 `handler(event, context)`를
부른다.

기대 동작: `context.getRemainingTimeInMillis()`가 0에 가까워지기 전에
함수가 값을 반환(또는 예외를 던짐)해야 한다 — 그렇지 않으면 타임아웃
오류로 강제 종료된다.

# Open Points

- 함수 버전·별칭(alias), 점진적 배포(트래픽 비율 나누기)는 다루지
  않는다.
- 컨테이너 이미지 기반 배포(ZIP이 아니라 Docker 이미지로 배포하는
  방식)는 다루지 않는다.
- 함수를 [`std/cloud/vpc.md`](vpc.md) 안에 배치하는 것은 다루지
  않는다(그 파일의 Open Points 참고).
