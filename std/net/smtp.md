#!specpp 0.1

# Meta

- name: std/net/smtp
- version: 0.1.0
- description: SMTP로 이메일을 보내는 수단.

# Intent

회원가입 확인, 비밀번호 재설정, 알림처럼 프로그램이 이메일을 발송해야
할 때 쓴다.

# Domain

## Class: MailAttachment

멤버:
- fileName: string
- content: bytes
- mimeType: string

## Class: MailMessage

멤버:
- from: string
- to: list<string>
- subject: string
- body: string
- isHtml: boolean — 기본값 false(일반 텍스트).
- attachments: list<MailAttachment>? — 없으면 첨부 없음.

## Class: SmtpClient

생성자:
- SmtpClient(host: string, port: int, useTls: boolean = true)

메서드:
- authenticate(username: string, password: string) -> void
  설명: 인증이 필요 없는 서버(내부망 릴레이 등)라면 부르지 않아도
  된다.
- send(message: MailMessage) -> void
  설명: 서버가 메시지를 거부하면(수신자 없음, 인증 실패 등) 오류를
  낸다.

# Interface

## Library

`client = SmtpClient("smtp.example.com", 587)`로 만든 뒤
`client.authenticate(user, password)`, 마지막으로
`client.send(MailMessage(...))`를 씁니다.

# Constraints

- 대상 언어의 SMTP 클라이언트(Python `smtplib`, Java `jakarta.mail`,
  C# `System.Net.Mail.SmtpClient`, Node.js `nodemailer` 등)에
  매핑한다.
- 자격 증명(`authenticate`의 `password`)은
  [`std/cloud/secrets.md`](../cloud/secrets.md) 같은 시크릿 저장소에서
  가져오지, 코드에 직접 심지 않는다(이 저장소의 반복 원칙).
- `useTls`가 true면 STARTTLS(또는 포트에 따라 암묵적 TLS)로
  연결한다 — 평문으로 자격 증명을 보내지 않는다.

# Examples

## 예제: 텍스트 메일 발송

호출:
```
client = SmtpClient("smtp.example.com", 587)
client.authenticate("bot@example.com", "password")
client.send(MailMessage(from: "bot@example.com", to: ["user@example.com"],
  subject: "가입을 환영합니다", body: "환영합니다!"))
```

기대 동작: 오류 없이 반환하면 발송 요청이 서버에 접수된 것이다(수신
확인까지 보장하지는 않는다).

# Open Points

- 대용량 첨부, DKIM/SPF 서명, 반송(bounce) 처리는 이 버전의 범위
  밖이다.
- API 기반 이메일 발송 서비스(SendGrid, AWS SES API 호출 등)는 SMTP
  프로토콜이 아니라 각 서비스의 HTTP API를 쓰므로 이 계약과 다른
  별도의 `kind: native` 바인딩이 필요하다 — 이 버전은 다루지 않는다.
