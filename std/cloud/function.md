#!specpp 0.1

# Meta

- name: std/cloud/function
- version: 0.1.0
- description: 요청·이벤트에 반응해 코드를 실행하는 서버리스 컴퓨트에 대한 추상 계약 — 함수를 호출하는 쪽과 함수 자신(핸들러)의 계약을 함께 다룬다.

# Intent

서버를 직접 띄우고 관리하지 않고, 이벤트(HTTP 요청, 큐 메시지, 파일
업로드 등)가 생길 때만 코드를 실행하고 싶을 때 쓴다.
[`std/system/process.md`](../system/process.md)가 "이미 떠 있는
프로세스를 실행·대기"한다면, 이 계약은 "요청이 올 때만 실행 환경
자체를 대신 띄워 주는" 관리형 서비스를 다룬다.

두 가지 방향을 함께 다룬다: (1) 다른 코드가 함수를 **호출하는**
쪽(`Function.Client.invoke`), (2) 함수 자신이 지켜야 하는 **핸들러
계약**(이벤트를 받아 응답을 돌려주는 함수 모양).

# Domain

## Class: Function.Context

실행 중인 함수 인스턴스 자신에 대한 정보다(핸들러의 두 번째 인자로
전달된다).

멤버:
- requestId: string
- functionName: string
- memoryLimitInMB: int

메서드:
- getRemainingTimeInMillis() -> int

## Class: Function.InvokeResult

멤버:
- statusCode: int
- payload: bytes
- functionError: string? — 실행 중 예외가 발생했다면 값이 있다.
  정상 종료면 null.

## Class: Function.Client

메서드:
- invoke(functionName: string, payload: bytes, async: boolean?) -> Function.InvokeResult
  설명: `async`가 false(기본값)면 함수 실행이 끝날 때까지 기다렸다가
  결과를 반환한다. true면 즉시 반환한다 — 이때 `payload`는 빈 결과다.

# Interface

## Library

### 호출하는 쪽
`Function.Client().invoke("resize-image", jsonBytes)`처럼 동기로
부르고 결과를 기다리거나, `async: true`로 이벤트만 던집니다.

### 함수 자신 (핸들러)
함수는 `(event: bytes, context: Function.Context) -> bytes` 모양의
진입점 하나로 작성합니다 — 실제 런타임이 요청마다 이 함수를 부르고
반환값을 호출자에게 돌려줍니다.

# Constraints

- 실제 구현은 [`std/cloud/aws/lambda.md`](aws/lambda.md)(AWS Lambda),
  [`std/cloud/gcp/functions.md`](gcp/functions.md)(GCP Cloud
  Functions), [`std/cloud/azure/functions.md`](azure/functions.md)
  (Azure Functions) 중 타겟에 맞는 것을 고른다.
- **핸들러 진입점의 실제 모양은 제공자마다 다르다.** Lambda는 이
  계약처럼 `(event, context) -> response` 단일 시그니처지만, GCP
  2세대 함수는 HTTP 트리거(`(request) -> response`)와 이벤트 트리거
  (`(cloudEvent) -> void`)로 나뉘고, Azure Functions는 함수마다
  `function.json`에 선언한 바인딩(트리거/입력/출력)에 따라 시그니처가
  달라진다 — 정확한 차이는 각 구현 파일 참고.
- **최대 실행 시간(타임아웃)이 제공자마다 다르다** — 예를 들어 AWS
  Lambda는 15분 고정 상한이지만 GCP 2세대 함수는 최대 60분까지
  가능하다(내부적으로 Cloud Run 기반이기 때문이다). 오래 걸리는
  작업을 서버리스 함수로 옮길 수 있는지는 타겟에 따라 달라진다.
- 함수가 실제로 접근할 수 있는 리소스는 이 코드가 아니라 함수에
  연결된 워크로드 아이덴티티(실행 역할/서비스 계정/관리 ID)의 권한으로
  결정된다 — [`std/cloud/accesscontrol.md`](accesscontrol.md) 참조.
- 콜드 스타트(한동안 호출이 없던 함수를 처음 부를 때 수백 ms~수 초
  더 걸리는 것)는 세 제공자 모두에 있다.

# Examples

## 예제: 동기 호출

호출: `client.invoke("resize-image", jsonBytes)`

기대 동작: 함수 실행이 끝난 뒤 `Function.InvokeResult`를 반환한다 —
`functionError`가 null이면 `payload`가 함수의 정상 반환값이다.

# Open Points

- 함수 버전·별칭, 점진적 배포는 다루지 않는다.
- 컨테이너 이미지 기반 배포는 다루지 않는다.
- VPC/가상 네트워크 안에 함수를 배치하는 것은 다루지 않는다
  ([`std/cloud/network.md`](network.md) 참고).
