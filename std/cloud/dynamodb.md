#!specpp 0.1

# Meta

- name: std/cloud/dynamodb
- version: 0.1.0
- description: 파티션 키로 접근하는 완전관리형 NoSQL 데이터베이스(AWS DynamoDB) 실체 명세.
- kind: native

# Intent

관계형 스키마 없이, 키로 빠르게 읽고 쓰는 대량의 데이터를 다룰 때
쓴다 — 세션, 사용자 프로필, 이벤트 로그 등. 조인이나 임의 조건 검색이
아니라 테이블을 만들 때 정한 키로만 효율적으로 조회할 수 있다는 것이
실제 API의 근본 제약이다. 실제 존재하는 서비스이므로 새로 설계할
대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: DynamoDb.Table

생성자:
- DynamoDb.Table(tableName: string, region: string)
  설명: [`std/cloud/s3.md`](s3.md)의 `S3.Client`와 같은 이유로 접근
  키는 인자로 받지 않는다(환경/IAM 역할에서 읽는다).

메서드:
- putItem(item: Dictionary<string, any>) -> void
  설명: 실제 `PutItem`에 대응한다. `item`은 테이블의 파티션 키(와
  있다면 정렬 키)를 반드시 포함해야 한다 — 같은 키가 이미 있으면
  통째로 덮어쓴다.
- getItem(key: Dictionary<string, any>) -> Dictionary<string, any>?
  설명: `GetItem`에 대응한다. 기본은 최종 일관성(eventually
  consistent) 읽기다(아래 Constraints) — 없으면 null.
- updateItem(key: Dictionary<string, any>, updates: Dictionary<string, any>) -> void
  설명: `UpdateItem`에 대응한다 — `item` 전체가 아니라 지정한 속성만
  바꾼다(`putItem`과 달리 나머지 속성은 그대로 남는다).
- deleteItem(key: Dictionary<string, any>) -> void
- query(partitionKeyValue: any, sortKeyCondition: string?) -> list<Dictionary<string, any>>
  설명: `Query`에 대응한다 — 파티션 키 값은 반드시 같아야 하고,
  정렬 키가 있다면 범위 조건(`sortKeyCondition`, 예:
  `"begins_with(ts, '2026-')"`류)을 함께 줄 수 있다.
- scan(filter: string?) -> list<Dictionary<string, any>>
  설명: `Scan`에 대응한다 — 테이블 전체를 훑는다(아래 Constraints,
  비용·성능 경고).

# Interface

## Library

테이블마다 `table = DynamoDb.Table("Sessions", "ap-northeast-2")`를
만들어 두고, 키를 안다면 `getItem`/`putItem`을, 파티션 키 하나에 속한
여러 항목이 필요하면 `query`를 씁니다. `scan`은 정말 테이블 전체가
필요할 때만 씁니다.

# Constraints

- 실제 AWS SDK(`boto3.resource("dynamodb").Table(...)`, JS SDK v3의
  `DynamoDBClient` + `DynamoDBDocumentClient` 등)에 매핑한다.
- **기본 읽기는 최종 일관성이다** — `putItem` 직후 다른 복제본에서
  `getItem`한 값이 아주 짧은 시간 동안 예전 값일 수 있다(실제 API의
  `ConsistentRead: true` 옵션을 주면 강한 일관성을 쓸 수 있지만 비용이
  두 배다). [`std/cloud/s3.md`](s3.md)(항상 강한 일관성)와 다른
  지점이다.
- 파티션 키(필요하면 정렬 키까지)는 테이블을 만들 때 고정된다 — 그
  키가 아닌 속성으로 효율적으로 조회하려면 별도의 보조 색인(Global
  Secondary Index)을 만들어야 한다(이 버전은 다루지 않는다, 아래 Open
  Points). 색인 없이 임의 속성으로 찾으려면 `scan` + `filter`뿐인데,
  이는 테이블 전체를 훑으므로 느리고 비용이 크다.
- 항목(item) 하나의 크기는 최대 400KB다.
- 온디맨드(호출당 과금)와 프로비저닝(미리 처리량을 예약) 두 용량
  모드가 있다 — 이 계약은 어느 쪽이든 같은 메서드 시그니처로 쓴다.

# Examples

## 예제: 쓰고 키로 읽기

호출 (순서대로): `table.putItem({"userId": "u1", "name": "Jay"})`,
`table.getItem({"userId": "u1"})`

기대 동작: 두 번째 호출은 `{"userId": "u1", "name": "Jay"}`를
반환한다.

## 예제: 파티션 키로 여러 항목 조회

호출: `table.query("u1")` (정렬 키가 `ts`인 테이블에서)

기대 동작: `userId`가 `"u1"`인 모든 항목을 정렬 키 순서로 반환한다.

# Open Points

- 보조 색인(GSI/LSI), 트랜잭션(`TransactWriteItems`), 배치 연산
  (`BatchGetItem`/`BatchWriteItem`), TTL(자동 만료)은 이 버전의 범위
  밖이다.
- 관계형 데이터베이스(RDS 등)에 대응하는 계약은 이 저장소에 아직
  없다 — SQL 기반 접근은 대상 언어의 표준 DB 드라이버에 맡긴다.
