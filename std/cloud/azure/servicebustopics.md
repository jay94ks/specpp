#!specpp 0.1

# Meta

- name: std/cloud/azure/servicebustopics
- version: 0.1.0
- description: 미리 만들어 둔 이름 있는(named) 구독마다 독립된 내구성 큐처럼 동작하는 Azure Service Bus Topics 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/pubsub.md`](../pubsub.md) 추상 계약의 Azure
구현이다 — 같은 계약의 [AWS 구현](../aws/sns.md)/[GCP
구현](../gcp/pubsub.md)도 참고할 수 있다.

**구조적 차이를 먼저 밝힌다.** AWS SNS는 `subscribe` 호출 하나로
이메일/HTTPS/큐 등 임의 프로토콜을 즉석에서 등록할 수 있지만, **Azure
Service Bus의 구독(subscription)은 토픽 아래 미리 만들어 둬야 하는
이름 있는 엔터티이고, 기본이 풀(pull) 방식이다** — 각 구독은 사실상
자기만의 내구성 큐를 갖는다([`std/cloud/queue.md`](../queue.md)와
[`std/cloud/pubsub.md`](../pubsub.md)를 한 서비스 안에서 섞어 놓은
모양에 가깝다). SNS처럼 즉석 HTTPS/이메일 푸시가 필요하면 Azure의
별도 서비스 **Event Grid**를 써야 한다(이 저장소는 아직 다루지
않는다, 아래 Open Points). 실제 존재하는 서비스이므로 새로 설계할
대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: ServiceBusMessage

멤버:
- body: string
- lockToken: string — 이 메시지를 지금 받은 것을 가리키는 값.
  `completeMessage`에 필요하다.
- messageId: string

## Class: ServiceBusTopic.Client

생성자:
- ServiceBusTopic.Client(topicName: string)

메서드:
- publish(message: string, properties: Dictionary<string, string>?) -> void
  설명: 실제 `ServiceBusSender.send_messages(ServiceBusMessage(body))`에
  대응한다.
- createSubscription(subscriptionName: string) -> void
  설명: 발행 **전에** 미리 만들어 둬야 하는 이름 있는 구독을
  만든다 — SNS의 즉석 `subscribe`와 다른 지점이다.

## Class: ServiceBusTopic.Subscription

생성자:
- ServiceBusTopic.Subscription(topicName: string, subscriptionName: string)

메서드:
- receiveMessages(maxMessages: int?) -> list<ServiceBusMessage>
  설명: 실제 `ServiceBusReceiver.receive_messages(...)`에 대응한다.
- completeMessage(message: ServiceBusMessage) -> void
  설명: 실제 `receiver.complete_message(message)`에 대응한다 — Azure의
  확인 응답 용어는 "완료(complete)"다(다른 제공자의
  "삭제"/"확인(acknowledge)"에 해당).

# Interface

## Library

발행하기 전에 구독마다 `createSubscription`으로 이름 있는 엔터티를
먼저 만들어 둡니다. 소비자는 `receiveMessages` + `completeMessage`를
반복합니다(큐를 다루는 것과 사실상 같은 모양이다).

# Constraints

- 실제 클라이언트 라이브러리 `azure-servicebus`(Python
  `azure.servicebus`)에 매핑한다.
- 구독마다 독립적으로 **적어도 한 번 전달**을 보장한다.
- 잠금(lock) 지속 시간(기본 30초, 최대 5분까지 갱신 가능)이 지나면
  다시 보인다는 점이 SQS의 가시성 제한 시간과 같은 역할이다.
- FIFO(세션 사용 시 순서 보장), 데드레터 서브큐(재시도 초과 메시지가
  자동으로 옮겨지는 전용 하위 큐)는 이 서비스에 기본 내장돼 있다 —
  다른 두 제공자는 별도 설정이 필요하다는 점과 다르다(이 버전은 다루지
  않는다, 아래 Open Points).

# Examples

## 예제: 팬아웃 (구독 둘, 미리 생성)

전제: `topic.createSubscription("email-worker")`,
`topic.createSubscription("inventory-worker")`를 미리 호출해 뒀다.

호출: `topic.publish("{\"orderId\": 1}")`

기대 동작: 두 구독 모두 독립적으로 `receiveMessages`로 이 메시지를
받을 수 있게 된다.

# Open Points

- Azure Event Grid(SNS의 즉석 HTTPS/이메일 푸시에 더 가까운 서비스)는
  다루지 않는다.
- 세션(FIFO), 데드레터 서브큐, 메시지 필터(구독 규칙)는 다루지
  않는다.
