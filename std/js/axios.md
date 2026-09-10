#!specpp 0.1

# Meta

- name: std/js/axios
- version: 0.1.0
- description: JavaScript/TypeScript에서 사실상 표준처럼 쓰이는 axios HTTP 클라이언트 라이브러리에 대한 실체 명세.
- kind: native

# Intent

[`std/net/httpclient.md`](../net/httpclient.md)의 추상 계약을
JavaScript/TypeScript(Node.js 또는 브라우저)로 구현할 실제 선택지 중
하나다. 표준 내장 `fetch`가 다른 선택지지만(그 파일 Constraints 참조),
axios(npm 패키지 — 언어 표준 라이브러리는 아니지만 생태계 전체에서
사실상 표준처럼 쓰인다)는 요청/응답 가로채기(interceptor), 자동 JSON
직렬화, 업로드/다운로드 진행률, Node·브라우저 양쪽에서 동일하게
동작하는 것 같은 `fetch`에 없는 기능을 제공한다. 실제 존재하는
라이브러리이므로 새로 설계할 대상이 아니다(`kind: native`, SPEC.md
1.2절).

# Domain

## Class: Axios.Response

멤버:
- data: any — 실제 응답 본문. `Content-Type`이 JSON이면 이미 파싱된
  객체다(자동 변환, 아래 Constraints).
- status: int
- statusText: string
- headers: Dictionary<string, string>

## Class: Axios.Error

[`std/system/exception.md`](../system/exception.md)의 하위 타입이다.

멤버:
- message: string
- code: string? — 예: `"ECONNABORTED"`(타임아웃).
- response: Axios.Response? — 서버가 실제로 응답했다면(4xx/5xx 포함)
  그 응답. 연결 자체가 실패했다면 null.

## Class: Axios.RequestConfig

멤버:
- url: string?
- method: string? — 기본값 `"GET"`.
- baseURL: string?
- headers: Dictionary<string, string>?
- params: Dictionary<string, string>? — 쿼리 문자열로 직렬화된다.
- data: any? — 요청 본문. 객체면 자동으로 JSON 직렬화된다.
- timeout: int? — 밀리초. 기본값 `0`(무제한).

## Class: Axios.Instance

이 클래스의 모든 메서드는 실제로는 Promise를 반환한다 — 대상 언어의
비동기 관용구(`async`/`await` 등)로 감싼다
([`std/web/storage.md`](../web/storage.md)의 `WebFileStorage`와 같은
근사).

메서드:
- get(url: string, config: Axios.RequestConfig?) -> Axios.Response
- post(url: string, data: any?, config: Axios.RequestConfig?) -> Axios.Response
- put(url: string, data: any?, config: Axios.RequestConfig?) -> Axios.Response
- patch(url: string, data: any?, config: Axios.RequestConfig?) -> Axios.Response
- delete(url: string, config: Axios.RequestConfig?) -> Axios.Response
- request(config: Axios.RequestConfig) -> Axios.Response
  설명: 위 메서드들은 모두 이것의 편의 래퍼다.

[Static]
- create(config: Axios.RequestConfig) -> Axios.Instance
  설명: baseURL/headers 등 공통 설정을 미리 박아 둔 인스턴스를 만든다
  (`axios.create(...)`에 대응). 모듈이 기본 내보내는 `axios` 자체도
  이미 만들어진 `Axios.Instance` 하나로 취급한다 — `axios.get(...)`은
  `Axios.Instance.get(...)`과 같다.

# Interface

## Library

공통 헤더·baseURL이 있으면 `api = Axios.create({baseURL: "..."})`로
인스턴스를 만들어 재사용합니다. 필요하면 `interceptors`로 모든 요청/
응답에 공통 로직(토큰 첨부, 401 처리 등)을 끼워 넣습니다(interceptors
자체의 세부 계약은 이 버전에서 다루지 않습니다, 아래 Open Points).

# Constraints

- 실제 npm 패키지 `axios`에 매핑한다.
- **상태 코드로 성공/실패를 감추지 않는
  [`std/net/httpclient.md`](../net/httpclient.md)의 `send`와 달리, axios는
  기본적으로 2xx가 아닌 응답을 `Axios.Error`로 던진다**(`error.response`에
  실제 응답이 담겨 있다) — `fetch`나 이 저장소의 추상 `HttpClient.send`가
  항상 정상적으로 값을 반환하는 것과 다른, axios 고유의 실제 동작이다.
  `validateStatus` 설정으로 이 동작을 끌 수 있지만, 이 계약은 기본
  동작만 다룬다.
- `Content-Type: application/json` 응답은 `response.data`가 이미 파싱된
  객체로 자동 변환된다 — 직접 `JSON.parse`할 필요가 없다.
- Node.js와 브라우저 양쪽에서 같은 코드로 동작한다(내부적으로 Node에서는
  `http`/`https` 모듈을, 브라우저에서는 `XMLHttpRequest`를 쓰지만 이
  차이는 axios가 감춘다) — 그래서 [`std/web/`](../web/) 패키지들과 달리
  `platform: web` 제약을 두지 않는다.

# Examples

## 예제: GET 요청 (JSON 자동 파싱)

호출: `api.get("/users/1")`

기대 동작: 서버가 `{"id": 1, "name": "..."}`를 JSON으로 응답하면,
반환된 `Axios.Response`의 `data`는 이미 파싱된 객체다(`data.id`가
`1`).

## 예제: 4xx 응답은 예외로 던져진다

호출: `api.get("/users/없는아이디")`

기대 동작: 서버가 `404`를 응답하면 이 호출은 `Axios.Error`를 던진다 —
`error.response.status`가 `404`.

# Open Points

- interceptors(요청/응답 가로채기)의 정확한 등록/해제 계약, 업로드/
  다운로드 진행률 이벤트, `AbortController` 기반 요청 취소는 이
  버전에서 다루지 않는다.
- 파일 업로드(`multipart/form-data`, `FormData`)는 다루지 않는다.
