#!specpp 0.1

# Meta

- name: std/cloud/azure/monitor
- version: 0.1.0
- description: KQL(Kusto Query Language)로 로그를 조회하는 Azure Monitor(Log Analytics + Metrics) 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/observability.md`](../observability.md) 추상
계약의 Azure 구현이다 — 같은 계약의 [AWS
구현](../aws/cloudwatch.md)/[GCP 구현](../gcp/monitoring.md)도
참고할 수 있다. 실제 존재하는 서비스이므로 새로 설계할 대상이
아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: AzureMonitorLogs.Client

생성자:
- AzureMonitorLogs.Client(workspaceId: string)

메서드:
- putLogEvents(tableName: string, messages: list<string>) -> void
  설명: 실제로는 Data Collection Rule을 통한
  `LogsIngestionClient.upload(rule_id, stream_name, logs)`에
  대응한다(또는 Application Insights의 `track_trace`).
- getLogEvents(tableName: string, startTime: DateTime?, endTime: DateTime?, kqlQuery: string?) -> list<string>
  설명: 실제로는 `LogsQueryClient.query_workspace(workspace_id, kql,
  timespan)`에 대응한다 — **실제 조회 언어는 KQL(Kusto Query
  Language)이다.** `kqlQuery`를 생략하면 `startTime`/`endTime`만으로
  단순 전체 조회를 근사하지만, 실제 활용은 대부분 KQL을 직접 쓴다
  (예: `"AppTraces | where TimeGenerated > ago(1h)"`).

## Class: AzureMonitorMetrics.Client

메서드:
- putMetricData(namespace: string, metricName: string, value: float, unit: string?, dimensions: Dictionary<string, string>?) -> void
  설명: Application Insights의 `track_metric` 또는 Azure Monitor
  Custom Metrics REST API에 대응한다.
- getMetricStatistics(namespace: string, metricName: string, startTime: DateTime, endTime: DateTime, periodSeconds: int, statistic: string) -> list<(DateTime, float)>
  설명: `MetricsQueryClient.query_resource(...)`에 대응한다.

# Interface

## Library

지표는 이벤트마다 `putMetricData`로 기록합니다. 로그는 버퍼링한 뒤
`putLogEvents`로 보내고, 조회는 간단한 시간 범위면
`getLogEvents(start, end)`로, 복잡한 조건이면 `kqlQuery`를 직접 써서
합니다.

# Constraints

- 실제 클라이언트 라이브러리 `azure-monitor-ingestion`,
  `azure-monitor-query`(Python), 또는 Application Insights SDK에
  매핑한다.
- **KQL은 이 저장소가 다루는 다른 제공자의 조회 방식과 문법이 전혀
  다르다** — AWS CloudWatch Logs Insights, GCP Cloud Logging 필터
  문법 모두 KQL과 호환되지 않는다. 여러 제공자를 동시에 지원해야
  하는 코드라면 이 차이를 흡수하는 레이어가 별도로 필요하다(이
  계약은 그런 레이어를 제공하지 않는다).
- 워크로드 아이덴티티(로그/지표를 쓰는 함수 등)는 관리 ID다 —
  [`std/cloud/azure/rbac.md`](rbac.md) 참조.

# Examples

## 예제: 지표 기록

호출: `metrics.putMetricData("MyApp", "RequestLatencyMs", 123.4, "ms", {"endpoint": "/login"})`

기대 동작: 오류 없이 반환한다.

## 예제: 단순 시간 범위 로그 조회

호출: `logs.getLogEvents("AppTraces", startTime, endTime)`

기대 동작: 그 시간 범위의 로그 메시지 리스트를 반환한다(내부적으로는
`kqlQuery`가 생략됐을 때의 기본 KQL로 변환된다).

# Open Points

- KQL 쿼리 문법 자체(집계, 조인 등)는 모델링하지 않는다 — 필요하면
  `kqlQuery`에 직접 쓴다.
- 경보 규칙, 대시보드/워크북 구성은 다루지 않는다.
