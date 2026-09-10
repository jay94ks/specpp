#!specpp 0.1

# Meta

- name: std/cloud/queue
- version: 0.1.0
- description: 생산자와 소비자를 시간적으로 분리하는, 순서를 보장하지 않는 완전관리형 메시지 큐(pull 방식)에 대한 추상 계약.

# Intent

작업을 즉시 처리하지 않고 큐에 쌓아 뒀다가, 소비자가 준비됐을 때(또는
여러 소비자가 나눠서) 꺼내 처리하고 싶을 때 쓴다 — 부하가 몰릴 때
소비자 속도로 완충하거나, 생산자·소비자가 서로 몰라도 되게(느슨한
결합) 만든다. [`std/cloud/pubsub.md`](pubsub.md)가 "메시지 하나를 여러
독립된 구독자 각각에게 전부 전달"한다면, 이 계약은 "큐 하나에 쌓아 한
무리의 소비자가 나눠 처리"한다는 점이 다르다.

# Domain

## Class: Queue.Message

멤버:
- body: string
- ackToken: string — 이 특정 수신 건을 가리키는 값. 삭제(확인 응답)
  하거나 가시성 제한 시간을 늘릴 때 필요하다.
- messageId: string

## Class: Queue.Client

생성자:
- Queue.Client(queueId: string)

메서드:
- sendMessage(body: string, delaySeconds: int?) -> void
- receiveMessages(maxMessages: int?, waitSeconds: int?) -> list<Queue.Message>
  설명: `waitSeconds`를 주면 메시지가 도착할 때까지(또는 시간이 다
  될 때까지) 기다린다(롱 폴링). 메시지가 없으면 빈 리스트를 반환한다
  — 오류가 아니다.
- deleteMessage(ackToken: string) -> void
  설명: 처리를 마친 메시지는 **반드시** 이걸로 지워야 한다 — 그러지
  않으면 가시성 제한 시간이 지난 뒤 다른 소비자에게 다시 보인다.

# Interface

## Library

소비자는 `receiveMessages`를 반복 호출(폴링)해 메시지를 받고, 각
메시지를 처리한 뒤 `deleteMessage(msg.ackToken)`로 지웁니다. 처리
도중 예외가 나면 지우지 않고 넘어갑니다 — 가시성 제한 시간이 지나면
자동으로 다시 받을 수 있게 됩니다.

# Constraints

- 실제 구현은 [`std/cloud/aws/sqs.md`](aws/sqs.md)(AWS SQS),
  [`std/cloud/gcp/pubsub.md`](gcp/pubsub.md)(GCP Cloud Pub/Sub의 pull
  구독), [`std/cloud/azure/storagequeue.md`](azure/storagequeue.md)
  (Azure Queue Storage) 중 타겟에 맞는 것을 고른다.
- **GCP에는 SQS/Queue Storage에 정확히 대응하는 독립 서비스가 없다**
  — GCP는 큐와 팬아웃을 Pub/Sub 하나로 통합했다(pull 구독 하나만 두면
  큐처럼, 여러 구독을 두면 팬아웃처럼 동작한다). 그래서
  [`std/cloud/gcp/pubsub.md`](gcp/pubsub.md)는 이 계약과
  [`std/cloud/pubsub.md`](pubsub.md) 둘 다의 GCP 구현이다 — 이 저장소가
  이전에도 (예: [`std/web/storage.md`](../web/storage.md)에서) 해 온 것처럼,
  모양이 다른 것을 억지로 같다고 하지 않고 있는 그대로 기록했다.
- **적어도 한 번(at-least-once) 전달**을 보장한다 — 같은 메시지가
  두 번 이상 배달될 수 있으므로, 소비자의 처리 로직은 멱등적이어야
  한다.
- 기본 구성은 순서를 보장하지 않는다 — 순서가 필요하면 제공자별 옵션
  (예: SQS FIFO 큐)을 따로 켜야 한다(이 버전은 다루지 않는다).

# Examples

## 예제: 보내고 받고 지우기

호출 (순서대로): `queue.sendMessage("hello")`,
`msgs = queue.receiveMessages(1, 10)`,
`queue.deleteMessage(msgs[0].ackToken)`

기대 동작: 두 번째 호출은 `body`가 `"hello"`인 메시지를 담은 리스트를
반환한다. 세 번째 호출 이후 같은 메시지는 다시 받아지지 않는다.

# Open Points

- FIFO(순서 보장) 큐, 가시성 제한 시간 연장, 데드레터 큐는 이 버전의
  범위 밖이다.
- 배치 전송/수신은 다루지 않는다.
