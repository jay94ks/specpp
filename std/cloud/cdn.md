#!specpp 0.1

# Meta

- name: std/cloud/cdn
- version: 0.1.0
- description: 오리진 콘텐츠를 전 세계 엣지에 캐싱해 배포하는 CDN에 대한 추상 계약.

# Intent

사용자와 지리적으로 먼 오리진 서버 하나가 모든 요청에 직접 응답하는
대신, 사용자와 가까운 엣지 서버가 캐시된 사본으로 대신 응답하게 해
지연시간을 줄이고 오리진 부하를 던다.
[`std/cloud/objectstorage.md`](objectstorage.md)로 올린 정적 자산을
오리진으로 두고 이 계약으로 캐싱·배포하는 조합이 흔한 실제 구성이다.

# Domain

## Class: Cdn.Distribution

멤버:
- id: string
- domainName: string — 이 배포가 실제로 서빙되는 도메인.

## Class: Cdn.Invalidation

멤버:
- id: string
- status: string — `"InProgress"` 또는 `"Completed"`.

## Class: Cdn.Client

메서드:
- getDistribution(distributionId: string) -> Cdn.Distribution
- createInvalidation(distributionId: string, paths: list<string>) -> Cdn.Invalidation
  설명: 지정한 경로들(`"/images/*"`처럼 와일드카드 가능)의 엣지 캐시를
  강제로 비운다. **비동기다** — 즉시 반영되지 않고 보통 수십 초~수
  분이 걸린다.
- getInvalidationStatus(distributionId: string, invalidationId: string) -> string
- getPublicUrl(distribution: Cdn.Distribution, key: string) -> string
  설명: `"https://" + distribution.domainName + "/" + key`를 만드는
  편의 메서드다.

# Interface

## Library

정적 자산을 바꾼 뒤, 바뀐 경로를 `createInvalidation`으로 넘겨 엣지
캐시를 비웁니다. `getPublicUrl`로 사용자에게 보여줄 실제 URL을
조립합니다.

# Constraints

- 실제 구현은 [`std/cloud/aws/cloudfront.md`](aws/cloudfront.md)(AWS
  CloudFront), [`std/cloud/gcp/cdn.md`](gcp/cdn.md)(GCP Cloud CDN),
  [`std/cloud/azure/cdn.md`](azure/cdn.md)(Azure CDN) 중 타겟에 맞는
  것을 고른다 — 세 제공자가 이 계약을 실제로 구성하는 방식은 상당히
  다르다(예: GCP는 "배포"라는 독립 리소스가 아니라 로드밸런서 백엔드에
  붙는 캐싱 정책이다, Azure는 "무효화"를 "퍼지(purge)"라고 부른다) —
  정확한 차이는 각 구현 파일을 참고한다.
- 캐시 유효 기간(TTL)은 CDN 쪽 설정이 아니라 **오리진 객체의
  `Cache-Control`/`Expires` 헤더**로 정하는 것이 세 제공자 공통이다.
- 무효화가 `"Completed"`로 끝나기 전까지는 일부 엣지 서버가 여전히
  예전 콘텐츠를 응답할 수 있다 — 즉시 일관성을 전제하면 안 된다.

# Examples

## 예제: 공개 URL 조립

호출: `client.getPublicUrl(dist, "images/logo.png")` (dist.domainName이
`"d123.example.net"`인 경우)

기대 동작: `"https://d123.example.net/images/logo.png"`를 반환한다.

## 예제: 무효화는 즉시 완료되지 않는다

호출 (순서대로): `inv = client.createInvalidation("dist-1", ["/images/logo.png"])`,
곧바로 `client.getInvalidationStatus("dist-1", inv.id)`

기대 동작: 두 번째 호출은 보통 `"InProgress"`를 반환한다.

# Open Points

- 커스텀 도메인 연결과 TLS 인증서 발급/연결은 다루지 않는다.
- 캐시 동작 세부 규칙(origin request policy, cache behavior)은 다루지
  않는다 — 기본 캐시 정책을 전제한다.
- 무효화 비용 정책(경로 수당 과금 등)은 제공자마다 다르다 — 각 구현
  파일을 참고한다.
