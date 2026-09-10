#!specpp 0.1

# Meta

- name: std/cloud/gcp/pubsub
- version: 0.1.0
- description: 큐(pull 구독)와 팬아웃(다중 구독) 둘 다를 하나로 통합해 제공하는 GCP Cloud Pub/Sub 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/queue.md`](../queue.md)**와**
[`std/cloud/pubsub.md`](../pubsub.md) **두 추상 계약 모두**의 GCP
구현이다 — GCP에는 AWS SQS나 Azure Queue Storage에 정확히 대응하는
독립 서비스가 없고, 대신 Pub/Sub 하나가 두 역할을 다 한다: 토픽에
구독을 하나만 두면 큐처럼(그 구독을 pull하는 소비자들이 메시지를
나눠 받는다), 여러 개 두면 팬아웃처럼(각 구독이 독립적으로 전체
메시지 사본을 받는다) 동작한다. `std/cloud/queue.md`의 [AWS
구현](../aws/sqs.md)/[Azure 구현](../azure/storagequeue.md),
`std/cloud/pubsub.md`의 [AWS 구현](../aws/sns.md)/[Azure
구현](../azure/servicebustopics.md)도 참고할 수 있다. 실제 존재하는
서비스이므로 새로 설계할 대상이 아니다(`kind: native`, SPEC.md
1.2절).

# Domain

## Class: PubSubMessage

멤버:
- data: string
- ackId: string
- messageId: string
- attributes: Dictionary<string, string>?

## Class: PubSubTopic

생성자:
- PubSubTopic(topicId: string, project: string?)

메서드:
- publish(message: string, attributes: Dictionary<string, string>?) -> void
  설명: 실제 `PublisherClient.publish(topic_path, data)`에 대응한다.
- createSubscription(subscriptionId: string, pushEndpoint: string?) -> PubSubSubscription
  설명: `pushEndpoint`를 주면 푸시 구독(메시지가 올 때마다 그
  HTTPS 엔드포인트로 즉시 호출), 안 주면 풀 구독을 만든다.

## Class: PubSubSubscription

생성자:
- PubSubSubscription(subscriptionId: string)

메서드:
- pull(maxMessages: int?) -> list<PubSubMessage>
  설명: 풀 구독에서 메시지를 가져온다(`SubscriberClient.pull`에
  대응). 구독 하나만 있으면 이 메서드가
  [`std/cloud/queue.md`](../queue.md)의 `receiveMessages`에 대응한다.
- acknowledge(ackId: string) -> void
  설명: `SubscriberClient.acknowledge`에 대응한다 — SQS의
  `deleteMessage`와 같은 역할이다.

# Interface

## Library

큐처럼 쓰려면 토픽에 구독을 하나만 만들고 `pull` + `acknowledge`를
반복합니다. 팬아웃이 필요하면 같은 토픽에 구독을 여러 개 만듭니다 —
각 구독이 독립적으로 전체 메시지를 받습니다.

# Constraints

- 실제 클라이언트 라이브러리 `google-cloud-pubsub`(Python
  `google.cloud.pubsub_v1`)에 매핑한다.
- **적어도 한 번 전달**을 보장한다 — 소비자 로직은 멱등적이어야
  한다.
- 확인 응답 기한(ack deadline, 기본 10초, 최대 600초까지 연장 가능)은
  SQS의 가시성 제한 시간과 같은 역할이다 — 기한 안에
  `acknowledge`하지 않으면 다시 전달된다.
- 순서 보장은 기본적으로 없다 — 메시지 순서 키(ordering key)를 쓰면
  같은 키 안에서만 순서를 보장할 수 있다(이 버전은 다루지 않는다).
- 권한은 GCP IAM 역할(`roles/pubsub.publisher`/`roles/pubsub.subscriber`
  등)로 제어한다 — [`std/cloud/gcp/iam.md`](iam.md) 참조.

# Examples

## 예제: 큐처럼 쓰기 (구독 하나)

호출 (순서대로): `topic.publish("hello")`, `msgs = sub.pull(1)`,
`sub.acknowledge(msgs[0].ackId)`

기대 동작: 두 번째 호출은 `data`가 `"hello"`인 메시지를 담은 리스트를
반환한다. 세 번째 호출 이후 같은 메시지는 다시 받아지지 않는다.

## 예제: 팬아웃 (구독 둘)

전제: 같은 토픽에 구독 A, B가 있다.

호출: `topic.publish("event")`

기대 동작: A, B 양쪽에서 독립적으로 `pull`하면 둘 다 이 메시지를
받을 수 있다.

# Open Points

- 순서 키, 데드레터 토픽, 메시지 필터링, 스트리밍 pull은 이 버전의
  범위 밖이다.
