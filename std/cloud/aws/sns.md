#!specpp 0.1

# Meta

- name: std/cloud/aws/sns
- version: 0.1.0
- description: 토픽 하나에 여러 구독자로 동시에 알림을 보내는 완전관리형 Pub/Sub(AWS SNS) 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/pubsub.md`](../pubsub.md) 추상 계약의 AWS 구현이다 — 같은 계약의 [GCP 구현](../gcp/pubsub.md)/[Azure 구현](../azure/servicebustopics.md)도 참고할 수 있다.

하나의 이벤트를 여러 다른 시스템에 동시에 알려야 할 때(팬아웃,
fan-out) 쓴다 — 예를 들어 "주문이 생성됨" 이벤트 하나를 이메일 발송
큐, 재고 갱신 큐, 로그 저장소에 동시에 전달한다.
[`std/cloud/aws/sqs.md`](sqs.md)가 "큐 하나에 쌓아 한 무리의 소비자가
나눠 처리"하는 것이라면, 이 패키지는 "메시지 하나를 여러 독립된
구독자 각각에게 전부 전달"하는 것이라는 점이 다르다 — 실제로 SNS
토픽 하나의 구독자로 SQS 큐 여러 개를 걸어 두 개념을 함께 쓰는 것이
흔한 실제 구성이다(팬아웃-팬인). 실제 존재하는 서비스이므로 새로
설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: Sns.Subscription

멤버:
- subscriptionArn: string
- protocol: string — `"sqs"`, `"lambda"`, `"email"`, `"https"` 등.
- endpoint: string — 프로토콜에 따라 큐 ARN, 함수 ARN, 이메일 주소,
  URL 등.

## Class: Sns.Topic

생성자:
- Sns.Topic(topicArn: string)

메서드:
- publish(message: string, subject: string?) -> void
  설명: 실제 `Publish`에 대응한다. 이 토픽의 모든 구독자에게 같은
  메시지를 전달한다. `subject`는 이메일 구독일 때 제목으로 쓰인다.
- subscribe(protocol: string, endpoint: string) -> Sns.Subscription
  설명: `Subscribe`에 대응한다. `protocol`이 `"email"`/`"https"`면
  실제로는 확인(confirmation) 절차가 먼저 필요하다(아래 Constraints).
- unsubscribe(subscriptionArn: string) -> void

# Interface

## Library

이벤트가 생기면 `topic.publish(json)`을 한 번 부릅니다 — 이 토픽에
구독을 걸어 둔 쪽(SQS 큐, Lambda 함수 등)이 각자 알아서 그 사본을
받습니다. 발행하는 쪽은 구독자가 몇 개인지, 누구인지 몰라도 됩니다
(느슨한 결합).

# Constraints

- 실제 AWS SDK(`boto3.client("sns")`, JS SDK v3의 `SNSClient` 등)에
  매핑한다.
- 구독자마다 독립적으로 **적어도 한 번 전달**을 보장한다 — 순서는
  보장하지 않는다(표준 토픽 기준. FIFO 토픽은 이 버전에서 다루지
  않는다, 아래 Open Points).
- `"email"`/`"https"` 프로토콜 구독은 `subscribe` 호출만으로 바로
  활성화되지 않는다 — 실제로는 확인 메일/콜백
  (`SubscriptionConfirmation` 요청)을 받아야 활성화된다.
  `"sqs"`/`"lambda"` 구독은(대상 리소스의 정책이 SNS의 발행을
  허용하도록 설정돼 있다면) 별도 확인 없이 바로 활성화된다.
- 메시지 크기는 최대 256KB다([`std/cloud/aws/sqs.md`](sqs.md)와 같은
  실제 제약).

# Examples

## 예제: 팬아웃

전제: `topic`에 SQS 큐 두 개가 구독돼 있다.

호출: `topic.publish("{\"orderId\": 1}")`

기대 동작: 두 큐 모두에서 같은 메시지를 `receiveMessages`로 받을 수
있게 된다(각 큐는 독립적으로 전달된다).

## 예제: 이메일 구독은 즉시 활성화되지 않는다

호출: `topic.subscribe("email", "a@example.com")`

기대 동작: 반환된 `Sns.Subscription`은 만들어지지만, 수신자가 확인
메일의 링크를 누르기 전까지는 실제로 메시지가 전달되지 않는다.

# Open Points

- FIFO 토픽, 메시지 필터링(구독마다 특정 속성값만 받도록 거르는 것),
  전달 재시도 정책 세부 설정은 이 버전의 범위 밖이다.
- HTTP(S) 구독 엔드포인트의 확인 콜백 처리 절차는 다루지 않는다.
