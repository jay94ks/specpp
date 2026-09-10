#!specpp 0.1

# Meta

- name: std/cloud/azure/storagequeue
- version: 0.1.0
- description: 메시지 ID와 팝 영수증(pop receipt)을 함께 써야 삭제되는 Azure Queue Storage 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/queue.md`](../queue.md) 추상 계약의 Azure
구현이다 — 같은 계약의 [AWS 구현](../aws/sqs.md)/[GCP
구현](../gcp/pubsub.md)도 참고할 수 있다. 실제 존재하는 서비스이므로
새로 설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: StorageQueue.Message

멤버:
- content: string
- messageId: string
- popReceipt: string — 이번에 이 메시지를 받은 것 자체를 가리키는
  값. **삭제하려면 `messageId`와 `popReceipt`를 함께 줘야 한다** —
  SQS의 단일 `receiptHandle`과 API 모양이 다르다(아래 Constraints).

## Class: StorageQueue.Queue

생성자:
- StorageQueue.Queue(queueName: string)

메서드:
- sendMessage(content: string, visibilityDelaySeconds: int?) -> void
  설명: 실제 `send_message(content, visibility_timeout=...)`에
  대응한다.
- receiveMessages(maxMessages: int?, visibilityTimeoutSeconds: int?) -> list<StorageQueue.Message>
  설명: `receive_messages(max_messages=, visibility_timeout=)`에
  대응한다.
- deleteMessage(message: StorageQueue.Message) -> void
  설명: 실제 `delete_message(message.id, message.pop_receipt)`에
  대응한다 — [`std/cloud/queue.md`](../queue.md)의 `ackToken` 하나가
  아니라 `messageId` + `popReceipt` 조합이 필요하다.

# Interface

## Library

`queue = StorageQueue.Queue("my-queue")`를 만든 뒤
`sendMessage`/`receiveMessages`/`deleteMessage(message)`를 씁니다 —
`deleteMessage`에는 받은 `StorageQueue.Message` 객체를 통째로
넘깁니다(내부적으로 `messageId`와 `popReceipt`를 함께 씁니다).

# Constraints

- 실제 클라이언트 라이브러리 `azure-storage-queue`(Python
  `azure.storage.queue`)에 매핑한다.
- **적어도 한 번 전달**을 보장한다 — 소비자 로직은 멱등적이어야
  한다.
- 가시성 제한 시간(기본 30초)이 지나면 다시 보인다는 점은 SQS와
  같지만, 삭제에 `messageId` + `popReceipt` 두 값이 함께 필요하다는
  것이 실제 API 시그니처의 차이다.
- 메시지 기본 보존 기간은 7일이다(최대 값을 명시적으로 늘려 사실상
  무제한에 가깝게 설정할 수 있다) — SQS의 기본 4일(최대 14일)보다
  길다.
- 메시지 내용은 기본적으로 base64로 인코딩해서 저장하는 것이 실제
  SDK의 관례다(XML 페이로드 제약 때문) — 이 계약은 인코딩을 감춘
  `content: string`으로 다룬다.

# Examples

## 예제: 보내고 받고 지우기

호출 (순서대로): `queue.sendMessage("hello")`,
`msgs = queue.receiveMessages(1, 10)`,
`queue.deleteMessage(msgs[0])`

기대 동작: 두 번째 호출은 `content`가 `"hello"`인 메시지를 담은
리스트를 반환한다. 세 번째 호출 이후 같은 메시지는 다시 받아지지
않는다.

# Open Points

- 큐 메타데이터, 최대 큐 크기(500TB), 가시성 제한 시간 연장 API는
  다루지 않는다.
