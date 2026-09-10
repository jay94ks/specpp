#!specpp 0.1

# Meta

- name: std/cloud/pubsub
- version: 0.1.0
- description: 토픽 하나에 여러 구독자로 동시에 알림을 보내는 완전관리형 Pub/Sub(팬아웃)에 대한 추상 계약.

# Intent

하나의 이벤트를 여러 다른 시스템에 동시에 알려야 할 때(팬아웃,
fan-out) 쓴다 — 예를 들어 "주문이 생성됨" 이벤트 하나를 이메일 발송
큐, 재고 갱신 큐, 로그 저장소에 동시에 전달한다.
[`std/cloud/queue.md`](queue.md)가 "큐 하나에 쌓아 한 무리의 소비자가
나눠 처리"하는 것이라면, 이 계약은 "메시지 하나를 여러 독립된 구독자
각각에게 전부 전달"하는 것이라는 점이 다르다 — 토픽 하나의 구독자로
큐 여러 개를 걸어 두 개념을 함께 쓰는 것(팬아웃-팬인)이 흔한 실제
구성이다.

# Domain

## Class: PubSub.Subscription

멤버:
- subscriptionId: string
- protocol: string — `"queue"`, `"function"`, `"email"`, `"https"` 등.
- endpoint: string — 프로토콜에 따라 큐 식별자, 함수 식별자, 이메일
  주소, URL 등.

## Class: PubSub.Topic

생성자:
- PubSub.Topic(topicId: string)

메서드:
- publish(message: string, subject: string?) -> void
  설명: 이 토픽의 모든 구독자에게 같은 메시지를 전달한다.
- subscribe(protocol: string, endpoint: string) -> PubSub.Subscription
- unsubscribe(subscriptionId: string) -> void

# Interface

## Library

이벤트가 생기면 `topic.publish(json)`을 한 번 부릅니다 — 이 토픽에
구독을 걸어 둔 쪽이 각자 알아서 그 사본을 받습니다. 발행하는 쪽은
구독자가 몇 개인지, 누구인지 몰라도 됩니다(느슨한 결합).

# Constraints

- 실제 구현은 [`std/cloud/aws/sns.md`](aws/sns.md)(AWS SNS),
  [`std/cloud/gcp/pubsub.md`](gcp/pubsub.md)(GCP Cloud Pub/Sub),
  [`std/cloud/azure/servicebustopics.md`](azure/servicebustopics.md)
  (Azure Service Bus Topics) 중 타겟에 맞는 것을 고른다.
- **세 제공자의 "구독" 모양이 서로 다르다.** SNS는 `subscribe` 호출
  하나로 임의 프로토콜(이메일/HTTPS/큐/함수)을 즉석에서 등록할 수
  있지만, Azure Service Bus Topics는 구독 자체가 토픽 아래 미리
  만들어 둬야 하는 이름 있는(named) 내구성 엔터티이고 풀(pull) 방식이
  기본이다(SNS의 즉석 HTTPS/이메일 푸시에 대응하는 것은 Azure의 별도
  서비스 Event Grid다 — 이 저장소는 아직 다루지 않는다, 아래 Open
  Points). GCP Pub/Sub은 [`std/cloud/queue.md`](queue.md)도 함께
  구현한다는 점이 다르다([`std/cloud/gcp/pubsub.md`](gcp/pubsub.md)
  참고). 정확한 차이는 각 구현 파일을 참고한다.
- 구독자마다 독립적으로 **적어도 한 번 전달**을 보장한다 — 순서는
  기본적으로 보장하지 않는다.
- `"email"`/`"https"` 같은 푸시형 구독은 `subscribe` 호출만으로 바로
  활성화되지 않는 경우가 많다 — 실제로는 확인 절차가 필요할 수 있다
  (제공자별 세부사항은 각 구현 파일 참고).

# Examples

## 예제: 팬아웃

전제: `topic`에 큐 두 개가 구독돼 있다.

호출: `topic.publish("{\"orderId\": 1}")`

기대 동작: 두 큐 모두에서 같은 메시지를 받을 수 있게 된다(각 큐는
독립적으로 전달된다).

# Open Points

- 메시지 필터링(구독마다 특정 속성값만 받도록 거르는 것), 전달 재시도
  정책 세부 설정은 이 버전의 범위 밖이다.
- Azure Event Grid처럼 이 계약보다 더 풍부한 푸시형 이벤트 라우팅
  서비스는 별도로 다루지 않는다.
