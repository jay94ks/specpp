#!specpp 0.1

# Meta

- name: std/cloud/azure/cdn
- version: 0.1.0
- description: 프로필·엔드포인트 모델과 "퍼지(purge)" 캐시 초기화를 쓰는 Azure CDN 실체 명세.
- kind: native

# Intent

이 패키지는 [`std/cloud/cdn.md`](../cdn.md) 추상 계약의 Azure
구현이다 — 같은 계약의 [AWS 구현](../aws/cloudfront.md)/[GCP
구현](../gcp/cdn.md)도 참고할 수 있다. 실제 존재하는 서비스이므로
새로 설계할 대상이 아니다(`kind: native`, SPEC.md 1.2절).

# Domain

## Class: AzureCdn.Endpoint

멤버:
- name: string
- hostName: string — 실제 엔드포인트가 서빙되는 도메인
  (`*.azureedge.net` 또는 커스텀 도메인).

## Class: AzureCdn.PurgeOperation

멤버:
- id: string
- status: string — `"InProgress"` 또는 `"Succeeded"`.

## Class: AzureCdn.Client

메서드:
- getEndpoint(profileName: string, endpointName: string) -> AzureCdn.Endpoint
- purgeContent(profileName: string, endpointName: string, paths: list<string>) -> AzureCdn.PurgeOperation
  설명: 실제 `endpoints.purge_content(...)`에 대응한다 — 다른
  제공자의 "무효화(invalidation)"에 해당하지만 Azure는 이를
  **"퍼지(purge)"**라고 부른다.
- getPurgeStatus(profileName: string, endpointName: string, operationId: string) -> string
- getPublicUrl(endpoint: AzureCdn.Endpoint, key: string) -> string

# Interface

## Library

정적 자산을 바꾼 뒤 `purgeContent`로 캐시를 비웁니다.

# Constraints

- 실제 Azure SDK(`azure-mgmt-cdn`의 `CdnManagementClient`)에
  매핑한다.
- 이 파일은 클래식 Azure CDN(프로필/엔드포인트 모델)을 다룬다 —
  Microsoft가 최근 권장하는 **Azure Front Door**는 라우팅·WAF까지
  포함한 더 넓은 서비스로, 구성 방식이 상당히 다르다(이 버전은
  다루지 않는다, 아래 Open Points).
- 캐시 유효 기간은 오리진의 `Cache-Control` 헤더로 정하는 것이 다른
  제공자와 같다.
- 퍼지는 비동기이며 완료 전까지 일부 엣지가 예전 콘텐츠를 응답할 수
  있다.

# Examples

## 예제: 공개 URL 조립

호출: `client.getPublicUrl(endpoint, "images/logo.png")`
(endpoint.hostName이 `"myapp.azureedge.net"`인 경우)

기대 동작: `"https://myapp.azureedge.net/images/logo.png"`를
반환한다.

# Open Points

- Azure Front Door(신규 권장 서비스, WAF·글로벌 라우팅 포함)는
  다루지 않는다 — 이 파일은 클래식 CDN 프로필/엔드포인트 모델만
  다룬다.
- 커스텀 도메인·TLS 인증서 연결은 다루지 않는다.
