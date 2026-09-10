#!specpp 0.1

# Meta

- name: std/cloud/observability
- version: 0.1.0
- description: 로그를 모으고 지표(metric)를 기록·조회하는 관측성(observability) 서비스에 대한 추상 계약.

# Intent

여러 서버·함수에 흩어진 로그를 한 곳에서 찾아보거나, "요청 처리 시간"
같은 수치를 시계열로 쌓아 그래프로 보거나 임계값을 넘으면 알림을
받고 싶을 때 쓴다. [`std/system/debug.md`](../system/debug.md)가 실행
중인 프로그램 하나 안에서의 진단(assert, 로그)을 다룬다면, 이 계약은
그 로그·지표를 **여러 인스턴스에 걸쳐 중앙에 모으고 나중에 조회하는**
쪽을 다룬다.

# Domain

## Class: ObservabilityLogs.Client

메서드:
- putLogEvents(logGroup: string, logStream: string, messages: list<string>) -> void
  설명: 메시지를 하나씩 보내지 않고 모아서(batch) 보내는 것이 공통
  권장 방식이다(아래 Constraints).
- getLogEvents(logGroup: string, logStream: string, startTime: DateTime?, endTime: DateTime?) -> list<string>

## Class: ObservabilityMetrics.Client

메서드:
- putMetricData(namespace: string, metricName: string, value: float, unit: string?, dimensions: Dictionary<string, string>?) -> void
- getMetricStatistics(namespace: string, metricName: string, startTime: DateTime, endTime: DateTime, periodSeconds: int, statistic: string) -> list<(DateTime, float)>
  설명: `statistic`은 `"Average"`/`"Sum"`/`"Maximum"`/`"Minimum"`/
  `"SampleCount"` 중 하나다.

# Interface

## Library

지표는 이벤트가 생길 때마다 `putMetricData`로 바로바로 기록합니다.
로그는 여러 줄을 모아 뒀다가 주기적으로 `putLogEvents`로 한 번에
보냅니다.

# Constraints

- 실제 구현은 [`std/cloud/aws/cloudwatch.md`](aws/cloudwatch.md)(AWS
  CloudWatch), [`std/cloud/gcp/monitoring.md`](gcp/monitoring.md)(GCP
  Cloud Logging/Monitoring),
  [`std/cloud/azure/monitor.md`](azure/monitor.md)(Azure Monitor) 중
  타겟에 맞는 것을 고른다.
- **로그 조회 질의 언어가 제공자마다 다르다.** 이 계약의
  `getLogEvents(startTime, endTime)`는 단순 시간 범위 필터로
  근사한 것이다 — 실제로는 Azure Monitor는 KQL(Kusto Query Language),
  GCP는 자체 필터 문법, AWS는 CloudWatch Logs Insights 질의 언어를
  쓴다. 복잡한 조회가 필요하면 각 구현 파일에서 제공자 고유 질의
  언어를 직접 써야 한다(아래 Open Points).
- `putLogEvents`를 호출마다 한 줄씩 부르면 API 호출 수가 급격히
  늘어난다 — 로그를 버퍼링한 뒤 한 번에 보내는 것이 표준 관례다.
- 지표 집계 최소 해상도(보통 1분)와 보존 기간은 제공자마다 다르다.

# Examples

## 예제: 지표 기록

호출: `metrics.putMetricData("MyApp", "RequestLatencyMs", 123.4, "Milliseconds", {"Endpoint": "/login"})`

기대 동작: 오류 없이 반환한다.

## 예제: 로그 쓰고 조회

호출 (순서대로): `logs.putLogEvents("myapp", "instance-1", ["시작됨"])`,
`logs.getLogEvents("myapp", "instance-1")`

기대 동작: 두 번째 호출의 결과 리스트에 `"시작됨"`이 들어 있다.

# Open Points

- 경보(Alarm, 임계값을 넘으면 알리는 것)는 다루지 않는다 — 걸면
  [`std/cloud/pubsub.md`](pubsub.md)로 알림을 받는 조합이 흔하다.
- 제공자 고유 로그 질의 언어(KQL 등), 대시보드 구성은 다루지 않는다.
