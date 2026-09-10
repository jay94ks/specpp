#!specpp 0.1

# Meta

- name: std/cloud/gcp/monitoring
- version: 0.1.0
- description: GCP Cloud Logging(로그)과 Cloud Monitoring(지표) 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/observability.md`](../observability.md) 추상
계약의 GCP 구현이다 — 같은 계약의 [AWS
구현](../aws/cloudwatch.md)/[Azure 구현](../azure/monitor.md)도
참고할 수 있다. 실제 존재하는 서비스이므로 새로 설계할 대상이
아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: CloudLogging.Client

메서드:
- putLogEvents(logName: string, messages: list<string>) -> void
  설명: 실제 `Logger.log_text` 반복 호출(또는 `Logger.batch()`로
  묶어 보내기)에 대응한다.
- getLogEvents(logName: string, startTime: DateTime?, endTime: DateTime?) -> list<string>
  설명: 실제로는 `list_entries(filter_=...)`에 시간 범위를 필터
  문자열로 넣어 대응한다(추상 계약의 단순 시간 범위보다 실제 필터
  문법은 훨씬 풍부하다 — 이 버전은 시간 범위만 다룬다).

## Class: CloudMonitoring.Client

메서드:
- putMetricData(namespace: string, metricName: string, value: float, unit: string?, dimensions: Dictionary<string, string>?) -> void
  설명: 실제 `create_time_series(...)`에 대응한다 — 커스텀 지표는
  실제로 `custom.googleapis.com/<namespace>/<metricName>` 형식의
  지표 타입 문자열이 필요하다.
- getMetricStatistics(namespace: string, metricName: string, startTime: DateTime, endTime: DateTime, periodSeconds: int, statistic: string) -> list<(DateTime, float)>
  설명: `list_time_series(...)`에 대응한다.

# Interface

## Library

지표는 이벤트마다 `putMetricData`로, 로그는 버퍼링한 뒤
`putLogEvents`로 보냅니다.

# Constraints

- 실제 클라이언트 라이브러리 `google-cloud-logging`,
  `google-cloud-monitoring`(Python)에 매핑한다.
- 커스텀 지표 타입은 반드시 `custom.googleapis.com/` 접두어가
  붙는다.
- **로그 기반 지표(log-based metric)**: 로그 필터에서 직접 지표를
  파생시킬 수 있는 GCP 고유 기능이 있다 — AWS/Azure에는 정확히
  대응하는 것이 없다(이 버전은 다루지 않는다, 아래 Open Points).
- 권한은 GCP IAM 역할(`roles/logging.logWriter`,
  `roles/monitoring.metricWriter` 등)로 제어한다.

# Examples

## 예제: 지표 기록

호출: `metrics.putMetricData("MyApp", "RequestLatencyMs", 123.4, "ms", {"endpoint": "/login"})`

기대 동작: 오류 없이 반환한다.

## 예제: 로그 쓰고 조회

호출 (순서대로): `logs.putLogEvents("myapp", ["시작됨"])`,
`logs.getLogEvents("myapp")`

기대 동작: 두 번째 호출의 결과 리스트에 `"시작됨"`이 들어 있다.

# Open Points

- 로그 기반 지표, 대시보드, 고급 필터 문법은 이 버전의 범위 밖이다.
- 경보 정책은 다루지 않는다 — [`std/cloud/gcp/pubsub.md`](pubsub.md)와
  연동하는 조합이 흔하다.
