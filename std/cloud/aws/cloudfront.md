#!specpp 0.1

# Meta

- name: std/cloud/aws/cloudfront
- version: 0.1.0
- description: 오리진 콘텐츠를 전 세계 엣지에 캐싱해 배포하는 CDN(AWS CloudFront 실제 API 기준) 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/cdn.md`](../cdn.md) 추상 계약의 AWS 구현이다 — 같은 계약의 [GCP 구현](../gcp/cdn.md)/[Azure 구현](../azure/cdn.md)도 참고할 수 있다.

사용자와 지리적으로 먼 오리진 서버 하나가 모든 요청에 직접 응답하는 대신,
사용자와 가까운 엣지 서버가 캐시된 사본으로 대신 응답하게 해 지연시간을
줄이고 오리진 부하를 던다. 이 명세는 실제로 존재하는 여러 CDN 서비스 중
**AWS CloudFront**의 실제 API를 옮긴 것이다 — 새로 설계할 대상이 아니다
(`kind: native`, SPEC.md 1.2절). [`std/cloud/aws/s3.md`](s3.md)로 올린 객체를
오리진으로 두고 이 패키지로 캐싱·배포하는 조합이, 정적 자산(이미지, 빌드
산출물 등)을 배포하는 흔한 실제 구성이다.

# Domain

## Class: Cdn.Distribution

멤버:
- id: string
- domainName: string — 실제 CloudFront가 발급하는 `*.cloudfront.net`
  도메인(커스텀 도메인을 연결했다면 그 도메인일 수도 있다 — 이 계약은
  다루지 않는다, 아래 Open Points).

## Class: Cdn.Invalidation

멤버:
- id: string
- status: string — `"InProgress"` 또는 `"Completed"`.

## Class: Cdn.Client

메서드:
- getDistribution(distributionId: string) -> Cdn.Distribution
- createInvalidation(distributionId: string, paths: list<string>) -> Cdn.Invalidation
  설명: 지정한 경로들(`"/images/*"`처럼 와일드카드 가능)의 엣지 캐시를
  강제로 비운다(`CreateInvalidation`에 대응). **비동기다** — 호출이
  끝나도 즉시 반영되지 않고 보통 수십 초~수 분이 걸린다(아래
  Constraints).
- getInvalidationStatus(distributionId: string, invalidationId: string) -> string
  설명: 무효화 진행 상태를 확인한다.
- getPublicUrl(distribution: Cdn.Distribution, key: string) -> string
  설명: `"https://" + distribution.domainName + "/" + key`를 만드는
  편의 메서드다 — 실제 API 호출이 아니라 순수 문자열 조립이다.

# Interface

## Library

정적 자산을 바꾼 뒤([`std/cloud/aws/s3.md`](s3.md)의 `putObject`로),
바뀐 경로를 `createInvalidation`으로 넘겨 엣지 캐시를 비웁니다.
`getPublicUrl`로 사용자에게 보여줄 실제 URL을 조립합니다.

# Constraints

- 실제 AWS SDK(Python boto3의 `boto3.client("cloudfront")`, JavaScript
  AWS SDK v3의 `CloudFrontClient` + `CreateInvalidationCommand` 등)에
  매핑한다.
- 캐시 유효 기간(TTL)은 CDN 쪽 설정이 아니라 **오리진 객체의
  `Cache-Control`/`Expires` 헤더**로 정한다 — [`std/cloud/aws/s3.md`](s3.md)의
  `putObject`는 아직 `contentType`만 받고 캐시 헤더는 다루지 않으므로,
  실제로 캐시 기간을 제어하려면 그 계약을 확장해야 한다(그 파일의
  Open Points 참고).
- `createInvalidation`은 계정당 매달 처음 1000개 경로까지 무료이고
  그 이상은 경로 수만큼 과금된다(실제 AWS 요금 정책) — 배포마다
  `/*`(전체 무효화) 하나만 부르는 것과 바뀐 파일 경로마다 개별 호출하는
  것 사이의 비용 차이를 고려해야 한다.
- 무효화가 `"Completed"`로 끝나기 전까지는 일부 엣지 서버가 여전히
  예전 콘텐츠를 응답할 수 있다 — 즉시 일관성을 전제하면 안 된다.

# Examples

## 예제: 공개 URL 조립

호출: `client.getPublicUrl(dist, "images/logo.png")` (dist.domainName이
`"d123.cloudfront.net"`인 경우)

기대 동작: `"https://d123.cloudfront.net/images/logo.png"`를 반환한다.

## 예제: 무효화는 즉시 완료되지 않는다

호출 (순서대로): `inv = client.createInvalidation("E1234", ["/images/logo.png"])`,
곧바로 `client.getInvalidationStatus("E1234", inv.id)`

기대 동작: 두 번째 호출은 보통 `"InProgress"`를 반환한다 —
`"Completed"`가 되려면 기다려야 한다.

# Open Points

- Cloudflare/Fastly/Akamai 등 다른 CDN의 실제 API는 다루지 않는다 —
  퍼지(purge) 개념은 비슷하지만 실제 메서드 이름과 인증 방식이
  CloudFront와 다르므로 별도 바인딩이 필요하다.
- 커스텀 도메인 연결과 TLS 인증서(ACM) 발급/연결은 다루지 않는다.
- 캐시 동작 세부 규칙(origin request policy, cache behavior)은 다루지
  않는다 — 기본 캐시 정책을 전제한다.
