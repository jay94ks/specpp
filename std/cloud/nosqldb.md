#!specpp 0.1

# Meta

- name: std/cloud/nosqldb
- version: 0.1.0
- description: 키로 접근하는 완전관리형 NoSQL 데이터베이스에 대한 추상 계약.

# Intent

관계형 스키마 없이, 키로 빠르게 읽고 쓰는 대량의 데이터를 다룰 때
쓴다 — 세션, 사용자 프로필, 이벤트 로그 등. 조인이나 임의 조건 검색이
아니라 테이블(또는 컬렉션)을 만들 때 정한 키로 효율적으로 조회한다는
것이 공통 제약이다.

**이 계약은 근사(approximation)다.** AWS DynamoDB의 파티션/정렬 키
테이블, GCP Firestore의 컬렉션/문서 모델, Azure Cosmos DB의 컨테이너/
파티션 키 모델은 실제 데이터 모델이 서로 꽤 다르다 — 이 계약은 셋 다
표현할 수 있는 최소 공통분모(키로 항목 하나를 넣고 빼고 찾는 것)만
정의한다. 제공자별 실제 구현은 이 계약보다 더 풍부한 기능(예: Firestore/
Cosmos DB의 임의 필드 쿼리)을 제공할 수 있다 — 아래 Constraints 참고.

# Domain

## Class: NoSqlDb.Table

생성자:
- NoSqlDb.Table(tableName: string, region: string)

메서드:
- putItem(item: Dictionary<string, any>) -> void
  설명: `item`은 테이블의 키(파티션 키 등)를 반드시 포함해야 한다 —
  같은 키가 이미 있으면 통째로 덮어쓴다.
- getItem(key: Dictionary<string, any>) -> Dictionary<string, any>?
  설명: 없으면 null.
- updateItem(key: Dictionary<string, any>, updates: Dictionary<string, any>) -> void
  설명: `item` 전체가 아니라 지정한 속성만 바꾼다.
- deleteItem(key: Dictionary<string, any>) -> void
- query(partitionKeyValue: any, sortKeyCondition: string?) -> list<Dictionary<string, any>>
  설명: 파티션 키 값은 반드시 같아야 하고, 정렬 키가 있다면 범위
  조건을 함께 줄 수 있다.
- scan(filter: string?) -> list<Dictionary<string, any>>
  설명: 테이블 전체를 훑는다 — 느리고 비용이 크다(아래 Constraints).

# Interface

## Library

테이블마다 `table = NoSqlDb.Table("Sessions", "ap-northeast-2")`를
만들어 두고, 키를 안다면 `getItem`/`putItem`을, 파티션 키 하나에 속한
여러 항목이 필요하면 `query`를 씁니다. `scan`은 정말 테이블 전체가
필요할 때만 씁니다.

# Constraints

- 실제 구현은 [`std/cloud/aws/dynamodb.md`](aws/dynamodb.md)(AWS
  DynamoDB), [`std/cloud/gcp/firestore.md`](gcp/firestore.md)(GCP
  Firestore), [`std/cloud/azure/cosmosdb.md`](azure/cosmosdb.md)(Azure
  Cosmos DB) 중 타겟에 맞는 것을 고른다.
- 파티션 키(필요하면 정렬 키까지)는 테이블을 만들 때 고정된다 — 그
  키가 아닌 속성으로 효율적으로 조회하려면 제공자별로 보조 색인이나
  추가 쿼리 기능이 필요하다(Firestore/Cosmos DB는 이 계약의 `query`
  시그니처보다 더 풍부한 임의 필드 쿼리를 실제로 지원한다 — 각 구현
  파일 참고).
- 읽기 일관성(쓴 직후 바로 최신 값이 보이는지)은 제공자마다, 심지어
  같은 제공자 안에서도 옵션에 따라 다르다 — 기본값을 그대로 전제하지
  말고 각 구현 파일의 Constraints를 확인한다.
- 항목 하나의 크기 제한은 제공자마다 다르다(예: DynamoDB는 400KB).

# Examples

## 예제: 쓰고 키로 읽기

호출 (순서대로): `table.putItem({"userId": "u1", "name": "Jay"})`,
`table.getItem({"userId": "u1"})`

기대 동작: 두 번째 호출은 `{"userId": "u1", "name": "Jay"}`를
반환한다.

# Open Points

- 보조 색인, 트랜잭션, 배치 연산, TTL(자동 만료)은 이 버전의 범위
  밖이다.
- 관계형 데이터베이스에 대응하는 계약은 이 저장소에 아직 없다 — SQL
  기반 접근은 대상 언어의 표준 DB 드라이버에 맡긴다.
