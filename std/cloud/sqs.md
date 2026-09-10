#!specpp 0.1

# Meta

- name: std/cloud/sqs
- version: 0.1.0
- description: 생산자와 소비자를 시간적으로 분리하는 완전관리형 메시지 큐(AWS SQS) 실체 명세.
- kind: native

# Intent

작업을 즉시 처리하지 않고 큐에 쌓아 뒀다가, 소비자가 준비됐을 때(또는
여러 소비자가 나눠서) 꺼내 처리하고 싶을 때 쓴다 — 부하가 몰릴 때
소비자 속도로 완충하거나, 생산자·소비자가 서로 몰라도 되게(느슨한
결합) 만든다. 실제 존재하는 서비스이므로 새로 설계할 대상이 아니다
(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: Sqs.Message

멤버:
- body: string
- receiptHandle: string — 이 특정 수신 건을 가리키는 값. 삭제하거나
  가시성 제한 시간을 늘릴 때 필요하다(아래 Constraints).
- messageId: string

## Class: Sqs.Queue

생성자:
- Sqs.Queue(queueUrl: string)

메서드:
- sendMessage(body: string, delaySeconds: int?) -> void
  설명: 실제 `SendMessage`에 대응한다. `delaySeconds`(최대 900)를
  주면 그 시간이 지나야 소비자에게 보인다.
- receiveMessages(maxMessages: int?, waitTimeSeconds: int?) -> list<Sqs.Message>
  설명: `ReceiveMessage`에 대응한다. `waitTimeSeconds`(최대 20)를
  주면 즉시 빈 결과를 돌려주지 않고 메시지가 도착할 때까지(또는
  시간이 다 될 때까지) 기다린다(롱 폴링, 아래 Constraints). 메시지가
  없으면 빈 리스트를 반환한다 — 오류가 아니다.
- deleteMessage(receiptHandle: string) -> void
  설명: `DeleteMessage`에 대응한다. 처리를 마친 메시지는 **반드시**
  이걸로 지워야 한다 — 그러지 않으면 가시성 제한 시간이 지난 뒤 다른
  소비자에게 다시 보인다(아래 Constraints).

# Interface

## Library

소비자는 `receiveMessages`를 반복 호출(폴링)해 메시지를 받고, 각
메시지를 처리한 뒤 `deleteMessage(msg.receiptHandle)`로 지웁니다.
처리 도중 예외가 나면 지우지 않고 넘어갑니다 — 가시성 제한 시간이
지나면 자동으로 다시 받을 수 있게 됩니다.

# Constraints

- 실제 AWS SDK(`boto3.client("sqs")`, JS SDK v3의 `SQSClient` 등)에
  매핑한다.
- **적어도 한 번(at-least-once) 전달**을 보장한다 — 같은 메시지가
  두 번 이상 배달될 수 있으므로, 소비자의 처리 로직은 같은 메시지를
  두 번 처리해도 결과가 같아야 한다(멱등적이어야 한다).
- **가시성 제한 시간(visibility timeout)**: `receiveMessages`가 반환한
  메시지는 기본 30초 동안 다른 소비자에게 보이지 않는다 — 그 안에
  `deleteMessage`를 부르지 않으면 다시 보이게 된다(오래 걸리는 처리는
  타임아웃을 늘려야 하는데, 이 버전은 그 연장 API를 다루지 않는다,
  아래 Open Points).
- 기본(standard) 큐는 순서를 보장하지 않고 중복이 있을 수 있다 —
  순서가 필요하면 처리량이 더 낮은 FIFO 큐(`.fifo` 접미사)를 따로
  만들어야 한다(이 버전은 standard 큐만 전제한다).
- `waitTimeSeconds > 0`(롱 폴링)을 쓰면 빈 응답 횟수가 줄어 짧은
  폴링보다 API 호출 비용이 준다 — 특별한 이유가 없다면 롱 폴링을
  권장한다.

# Examples

## 예제: 보내고 받고 지우기

호출 (순서대로): `queue.sendMessage("hello")`,
`msgs = queue.receiveMessages(1, 10)`,
`queue.deleteMessage(msgs[0].receiptHandle)`

기대 동작: 두 번째 호출은 `body`가 `"hello"`인 메시지를 담은 리스트를
반환한다. 세 번째 호출 이후 같은 메시지는 다시 받아지지 않는다.

## 예제: 빈 큐

호출: `queue.receiveMessages(1, 0)`

기대 동작: 즉시 빈 리스트를 반환한다 — 오류가 아니다.

# Open Points

- FIFO 큐, 가시성 제한 시간 연장(`ChangeMessageVisibility`), 데드레터
  큐(반복 실패한 메시지를 별도 큐로 보내는 것)는 이 버전의 범위 밖이다.
- 배치 전송/수신(`SendMessageBatch`/`DeleteMessageBatch`)은 다루지
  않는다.
