#!specpp 0.1

# Meta

- name: std/cloud/azure/cosmosdb
- version: 0.1.0
- description: SQL 유사 쿼리 언어와 다중 일관성 수준을 지원하는 Azure Cosmos DB(Core/SQL API) 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/nosqldb.md`](../nosqldb.md) 추상 계약의
Azure 구현이다 — 같은 계약의 [AWS
구현](../aws/dynamodb.md)/[GCP 구현](../gcp/firestore.md)도 참고할 수
있다. 실제 존재하는 서비스이므로 새로 설계할 대상이 아니다
(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: CosmosDb.Container

생성자:
- CosmosDb.Container(containerName: string, databaseName: string, partitionKeyPath: string)

메서드:
- upsertItem(item: Dictionary<string, any>) -> void
  설명: 실제 `container.upsert_item(item)`에 대응한다 — DynamoDB의
  `putItem`과 달리 이름 자체가 "upsert"다(있으면 갱신, 없으면 생성).
- getItem(itemId: string, partitionKeyValue: any) -> Dictionary<string, any>?
  설명: `container.read_item(item_id, partition_key)`에 대응한다.
  **항목 ID와 파티션 키 값을 둘 다 줘야 한다** — 둘 중 하나만으로는
  점 조회(point read)를 할 수 없다.
- deleteItem(itemId: string, partitionKeyValue: any) -> void
- query(sqlQuery: string, partitionKeyValue: any?) -> list<Dictionary<string, any>>
  설명: 실제 `container.query_items(query, partition_key=...)`에
  대응한다. `sqlQuery`는 진짜 SQL과 비슷한 문자열(예:
  `"SELECT * FROM c WHERE c.status = 'active'"`)이다 —
  DynamoDB의 조건식(condition expression)보다 훨씬 표현력이 크다.
- listItems() -> list<Dictionary<string, any>>
  설명: `SELECT * FROM c` 전체 조회에 대응한다
  ([`std/cloud/nosqldb.md`](../nosqldb.md)의 `scan`에 대응).

# Interface

## Library

`container = CosmosDb.Container("items", "mydb", "/userId")`를 만든
뒤 `upsertItem`/`getItem`을 씁니다. 파티션 키가 아닌 조건으로 찾아야
하면 실제 SQL과 비슷한 문자열을 `query`에 씁니다.

# Constraints

- 실제 클라이언트 라이브러리 `azure-cosmos`(Python)에 매핑한다.
- **일관성 수준을 계정 단위로 5가지 중 골라 설정할 수 있다** —
  Strong, Bounded Staleness, Session(기본값), Consistent Prefix,
  Eventual. AWS DynamoDB(강한/최종 두 가지)나 GCP Firestore(사실상
  강한 일관성 고정)보다 훨씬 세밀하게 조절할 수 있다는 것이 Cosmos
  DB의 실제 차별점이다.
- 점 조회(`getItem`/`deleteItem`)는 항목 ID와 파티션 키 값을 **둘 다**
  필요로 한다 — DynamoDB는 키 딕셔너리 하나로 충분하다는 점과 API
  시그니처가 다르다.
- 쿼리 언어가 SQL과 비슷한 실제 문자열이다 — DynamoDB의 `query`
  조건식이나 Firestore의 `where(field, op, value)`보다 표현력이
  크지만, 인젝션에 준하는 실수(문자열을 직접 이어붙이는 것)를
  피해야 한다(매개변수화된 쿼리를 쓴다).

# Examples

## 예제: 쓰고 ID+파티션 키로 읽기

호출 (순서대로):
`container.upsertItem({"id": "i1", "userId": "u1", "name": "Jay"})`,
`container.getItem("i1", "u1")`

기대 동작: 두 번째 호출은 `{"id": "i1", "userId": "u1", "name": "Jay"}`를
반환한다.

## 예제: SQL 유사 쿼리

호출: `container.query("SELECT * FROM c WHERE c.name = 'Jay'")`

기대 동작: `name` 필드가 `"Jay"`인 모든 항목을 반환한다 — 파티션
키와 무관한 필드로도 조회할 수 있다(다만 파티션 키를 함께 주지 않으면
실제로는 모든 파티션을 훑는 비용이 든다).

# Open Points

- 여러 API(Core/SQL 외 MongoDB/Cassandra/Gremlin/Table 호환 API)는
  다루지 않는다 — 이 파일은 Core/SQL API만 전제한다.
- 트랜잭션 배치(같은 파티션 키 안에서의 원자적 배치 연산)는 다루지
  않는다.
