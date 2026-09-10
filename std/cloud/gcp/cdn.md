#!specpp 0.1

# Meta

- name: std/cloud/gcp/cdn
- version: 0.1.0
- description: 로드밸런서 백엔드에 붙는 캐싱 정책으로 동작하는 GCP Cloud CDN 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/cdn.md`](../cdn.md) 추상 계약의 GCP 구현이다
— 같은 계약의 [AWS 구현](../aws/cloudfront.md)/[Azure
구현](../azure/cdn.md)도 참고할 수 있다.

**구조적 차이를 먼저 밝힌다.** AWS CloudFront는 "배포(Distribution)"라는
독립된 리소스지만, **Cloud CDN은 독립 리소스가 아니라 Google Cloud
Load Balancing의 백엔드(백엔드 버킷/백엔드 서비스)에 켜는 캐싱
정책이다** — 그래서 이 파일의 `Backend`는 CloudFront의
`Distribution`과 정확히 같은 모양이 아니다. 실제 존재하는 서비스이므로
새로 설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: CloudCdn.Backend

멤버:
- name: string — 백엔드 버킷/서비스 이름.
- domainName: string — 이 백엔드가 연결된 로드밸런서의 프론트엔드
  IP/도메인.

## Class: CloudCdn.Operation

GCP의 비동기 작업(operation) 핸들이다.

멤버:
- id: string
- status: string — `"RUNNING"` 또는 `"DONE"`.

## Class: CloudCdn.Client

메서드:
- getBackend(backendName: string) -> CloudCdn.Backend
- invalidateCache(urlMapName: string, path: string) -> CloudCdn.Operation
  설명: 실제 `UrlMaps.invalidateCache`(`gcloud compute url-maps
  invalidate-cdn-cache`)에 대응한다.
- getOperationStatus(operationId: string) -> string
- getPublicUrl(backend: CloudCdn.Backend, key: string) -> string

# Interface

## Library

[`std/cloud/gcp/storage.md`](storage.md) 버킷을 백엔드 버킷으로 연결한
로드밸런서를 먼저 구성해 둔 뒤(인프라 구성 단계), 콘텐츠가 바뀌면
`invalidateCache`로 캐시를 비웁니다.

# Constraints

- 실제 GCP SDK(`google-cloud-compute`의 `UrlMapsClient` 등)에
  매핑한다.
- 캐시 유효 기간은 오리진(백엔드 버킷의 객체 또는 백엔드 서비스 응답)의
  `Cache-Control` 헤더로 정한다 — 다른 제공자와 같다.
- 무효화는 경로 패턴 단위로 과금되며(요청 수만큼) 비동기다 — 완료
  전까지 일부 엣지가 예전 콘텐츠를 응답할 수 있다.

# Examples

## 예제: 공개 URL 조립

호출: `client.getPublicUrl(backend, "images/logo.png")`
(backend.domainName이 `"1.2.3.4"`인 경우)

기대 동작: `"https://1.2.3.4/images/logo.png"`를 반환한다.

# Open Points

- 로드밸런서(HTTP(S) Load Balancing) 자체의 구성(프론트엔드,
  백엔드 서비스, URL 맵 라우팅 규칙)은 다루지 않는다 — Cloud CDN을
  쓰려면 먼저 이 인프라가 갖춰져 있어야 한다.
- 커스텀 도메인·관리형 TLS 인증서 연결은 다루지 않는다.
