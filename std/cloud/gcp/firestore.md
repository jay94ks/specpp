#!specpp 0.1

# Meta

- name: std/cloud/gcp/firestore
- version: 0.1.0
- description: 컬렉션·문서 모델의 완전관리형 NoSQL 데이터베이스인 GCP Firestore(Native 모드) 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/nosqldb.md`](../nosqldb.md) 추상 계약의 GCP
구현이다 — 같은 계약의 [AWS 구현](../aws/dynamodb.md)/[Azure
구현](../azure/cosmosdb.md)도 참고할 수 있다.

**모델 차이를 먼저 밝힌다.** DynamoDB의 "테이블/파티션 키·정렬 키"
모델과 달리, Firestore는 "컬렉션/문서" 모델이다 — 문서마다 고유 ID가
있고(직접 지정하거나 자동 생성), 임의의 필드로 쿼리할 수 있다(적절한
색인이 자동/수동으로 구성돼 있다면). 이 덕분에 실제 `query`는
추상 계약의 `(partitionKeyValue, sortKeyCondition)` 시그니처보다
더 풍부하다 — 아래 Domain 참고. 실제 존재하는 서비스이므로 새로
설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: Firestore.Collection

생성자:
- Firestore.Collection(collectionPath: string, project: string?)

메서드:
- setDocument(docId: string, data: Dictionary<string, any>) -> void
  설명: 실제 `document(docId).set(data)`에 대응한다. docId가 이미
  있으면 덮어쓴다.
- getDocument(docId: string) -> Dictionary<string, any>?
  설명: `document(docId).get()`에 대응한다. 없으면 null.
- updateDocument(docId: string, updates: Dictionary<string, any>) -> void
  설명: `document(docId).update(updates)`에 대응한다 — 지정한 필드만
  바꾼다.
- deleteDocument(docId: string) -> void
- query(field: string, op: string, value: any) -> list<Dictionary<string, any>>
  설명: 실제 `where(field, op, value).stream()`에 대응한다. `op`는
  `"=="`, `"<"`, `">"`, `"array-contains"` 등 실제 Firestore가
  지원하는 연산자다 — DynamoDB의 파티션 키 제약과 달리 **임의 필드**로
  쿼리할 수 있다.
- listDocuments() -> list<Dictionary<string, any>>
  설명: 컬렉션 전체를 훑는다(`std/cloud/nosqldb.md`의 `scan`에 대응).

# Interface

## Library

`col = Firestore.Collection("sessions", "my-project")`를 만든 뒤
`setDocument`/`getDocument`로 문서를 쓰고 읽습니다. 키가 아닌 필드로
찾아야 하면 `query`를 씁니다(색인이 없으면 실제로는 콘솔이 색인 생성
링크를 알려준다 — 이 계약은 색인 관리를 다루지 않는다, 아래 Open
Points).

# Constraints

- 실제 클라이언트 라이브러리 `google-cloud-firestore`(Python
  `google.cloud.firestore`, Node.js `@google-cloud/firestore` 등)에
  매핑한다.
- 단일 문서 읽기/쓰기는 강한 일관성을 보장한다. 컬렉션 그룹 쿼리 등
  일부 고급 쿼리는 제약이 있을 수 있다 — 세부 사항은 실제 Firestore
  문서를 따른다.
- 문서 하나의 크기는 최대 1MiB다.
- 복합 쿼리(여러 필드를 동시에 조건으로 거는 것)는 실제로는 복합
  색인을 미리 만들어 둬야 한다 — 이 계약은 단일 필드 `query`만
  다룬다.

# Examples

## 예제: 쓰고 문서 ID로 읽기

호출 (순서대로): `col.setDocument("u1", {"name": "Jay"})`,
`col.getDocument("u1")`

기대 동작: 두 번째 호출은 `{"name": "Jay"}`를 반환한다.

## 예제: 필드로 쿼리

호출: `col.query("name", "==", "Jay")`

기대 동작: `name` 필드가 `"Jay"`인 모든 문서를 반환한다 — 이 문서들이
같은 파티션 키를 공유할 필요가 없다는 점이
[`std/cloud/aws/dynamodb.md`](../aws/dynamodb.md)의 `query`와 다르다.

# Open Points

- 복합 색인 관리, 트랜잭션, 하위 컬렉션(subcollection), 실시간 구독
  (`onSnapshot`)은 이 버전의 범위 밖이다.
