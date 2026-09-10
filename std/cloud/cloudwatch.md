#!specpp 0.1

# Meta

- name: std/cloud/cloudwatch
- version: 0.1.0
- description: 로그를 모으고 지표(metric)를 기록·조회하는 관측성(observability) 서비스(AWS CloudWatch) 실체 명세.
- kind: native

# Intent

여러 서버·함수에 흩어진 로그를 한 곳에서 찾아보거나, "요청 처리 시간"
같은 수치를 시계열로 쌓아 그래프로 보거나 임계값을 넘으면 알림을
받고 싶을 때 쓴다. [`std/system/debug.md`](../system/debug.md)가 실행
중인 프로그램 하나 안에서의 진단(assert, 로그)을 다룬다면, 이 패키지는
그 로그·지표를 **여러 인스턴스에 걸쳐 중앙에 모으고 나중에 조회하는**
쪽을 다룬다. 실제 존재하는 서비스이므로 새로 설계할 대상이 아니다
(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: CloudWatchLogs.Client

메서드:
- putLogEvents(logGroup: string, logStream: string, messages: list<string>) -> void
  설명: 실제 `PutLogEvents`에 대응한다. 메시지를 하나씩 보내지 않고
  모아서(batch) 보내는 것이 실제 권장 방식이다(아래 Constraints).
- getLogEvents(logGroup: string, logStream: string, startTime: DateTime?, endTime: DateTime?) -> list<string>
  설명: 저장된 로그를 시간 범위로 조회한다.

## Class: CloudWatchMetrics.Client

메서드:
- putMetricData(namespace: string, metricName: string, value: float, unit: string?, dimensions: Dictionary<string, string>?) -> void
  설명: 실제 `PutMetricData`에 대응한다. `dimensions`는 같은 지표를
  세분화하는 태그다(예: `{"Endpoint": "/login"}`).
- getMetricStatistics(namespace: string, metricName: string, startTime: DateTime, endTime: DateTime, periodSeconds: int, statistic: string) -> list<(DateTime, float)>
  설명: `statistic`은 `"Average"`/`"Sum"`/`"Maximum"`/`"Minimum"`/
  `"SampleCount"` 중 하나다. `periodSeconds` 단위로 집계된 시계열을
  반환한다.

# Interface

## Library

지표는 이벤트가 생길 때마다(요청 처리 끝, 오류 발생 등)
`putMetricData`로 바로바로 기록합니다. 로그는 여러 줄을 모아 뒀다가
주기적으로(또는 버퍼가 차면) `putLogEvents`로 한 번에 보냅니다. 조회는
대시보드나 배치 작업에서 `getMetricStatistics`/`getLogEvents`로 합니다.

# Constraints

- 실제 AWS SDK(`boto3.client("cloudwatch")`/`boto3.client("logs")`,
  JS SDK v3의 `CloudWatchClient`/`CloudWatchLogsClient` 등)에
  매핑한다.
- `putLogEvents`를 호출마다 한 줄씩 부르면 API 호출 수가 급격히
  늘어난다 — 실제로는 로그를 짧은 시간(수 초) 또는 일정 개수만큼
  버퍼링한 뒤 한 번에 보내는 것이 표준 관례다(많은 언어의 로깅
  라이브러리가 CloudWatch 핸들러로 이 배칭을 대신해 준다).
- 표준 해상도 지표는 최소 1분 단위로 집계된다 — 더 촘촘한(1초 단위)
  고해상도 지표는 비용이 더 든다(이 계약은 구분하지 않는다).
- 지표는 기본 15개월, 로그는 그룹마다 설정한 보존 기간(기본은
  무제한)이 지나면 사라진다 — 장기 보관이 필요하면
  [`std/cloud/s3.md`](s3.md)로 내보내는 것이 실제 흔한 패턴이다.

# Examples

## 예제: 지표 기록

호출: `metrics.putMetricData("MyApp", "RequestLatencyMs", 123.4, "Milliseconds", {"Endpoint": "/login"})`

기대 동작: 오류 없이 반환한다 — 이후
`getMetricStatistics("MyApp", "RequestLatencyMs", ..., "Average")`로
조회하면 이 값이 집계에 반영돼 있다.

## 예제: 로그 쓰고 조회

호출 (순서대로): `logs.putLogEvents("myapp", "instance-1", ["시작됨"])`,
`logs.getLogEvents("myapp", "instance-1")`

기대 동작: 두 번째 호출의 결과 리스트에 `"시작됨"`이 들어 있다.

# Open Points

- 경보(Alarm, 임계값을 넘으면 알리는 것)는 다루지 않는다 — 실제로
  걸면 [`std/cloud/sns.md`](sns.md)로 알림을 받는 조합이 흔하다.
- 로그 필터 패턴 쿼리(CloudWatch Logs Insights), 대시보드 구성은
  다루지 않는다.
