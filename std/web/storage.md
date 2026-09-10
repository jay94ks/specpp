#!specpp 0.1

# Meta

- name: std/web/storage
- version: 0.1.0
- description: 브라우저 안에서 실행 사이에 데이터를 남기는 데 필요한 최소 localStorage/IndexedDB 부분집합에 대한 실체 명세.
- platform: web
- kind: native

# Intent

[`std/io/file.md`](../io/file.md)는 "디스크의 임의 경로에 파일을 읽고
쓴다"는 것을 전제하는데, **브라우저 샌드박스 안에는 그런 파일시스템이
없다**(SPEC.md 3.10절 참조) — 그래서 이 패키지는 `std/io/file.md`의
`kind: native` 바인딩이 아니라, **모양이 다른 대안**이다: 경로가 아니라
키(key) 하나로 값을 저장하고 꺼낸다. 설정 저장, 저장된 게임 진행
([`examples/doom/savegame.md`](../../examples/doom/savegame.md) 같은)처럼
"실행 사이에 상태를 남긴다"는 **목적**은 같지만, "임의 경로의 파일"이라는
**모양**은 웹에서 성립하지 않는다는 것을 이 패키지 자체가 보여준다.

# Domain

## Class: WebStorage

작은 문자열 값(수 MB 이하)에 적합하다 — 동기(synchronous) API다.

메서드:
[Static]
- getItem(key: string) -> string?
  설명: `localStorage.getItem(key)`에 대응한다. 없으면 null.
- setItem(key: string, value: string) -> void
  설명: `localStorage.setItem(key, value)`에 대응한다. 저장 공간이
  가득 차면(보통 브라우저당 5~10MB) 오류를 낸다.
- removeItem(key: string) -> void
- keys() -> list<string>
  설명: 저장된 모든 키를 나열한다(`Object.keys(localStorage)`에 대응).

## Class: WebFileStorage

바이너리 데이터나 큰 값에 적합하다 — 비동기(Promise 기반) API다.
[`examples/doom/savegame.md`](../../examples/doom/savegame.md)처럼
바이너리 스냅샷을 통째로 저장해야 하는 경우 `WebStorage`(문자열,
작은 용량)보다 이쪽을 쓴다.

메서드:
[Static]
- writeAllBytes(key: string, content: bytes) -> void
  설명: IndexedDB에 `content`를 `key`로 저장한다(`indexedDB.open` +
  객체 저장소 트랜잭션에 대응 — 실제로는 비동기이므로 대상 언어의
  `async`/`Promise` 관용구로 감싼다, 아래 Constraints 참조).
- readAllBytes(key: string) -> bytes
  설명: 저장된 적 없으면 오류를 낸다([`std/io/file.md`](../io/file.md)의
  `File.readAllBytes`와 같은 규칙 — 조용히 빈 값을 반환하지 않는다).
- exists(key: string) -> boolean
- delete(key: string) -> void

# Interface

## Library

작고 자주 바뀌지 않는 값(설정 등)은 `WebStorage.getItem`/`setItem`처럼
동기로 바로 씁니다. 저장된 게임처럼 크거나 바이너리인 값은
`WebFileStorage`를 `await`(또는 대상 언어의 비동기 관용구)로 씁니다.

# Constraints

- `WebStorage`는 동기 API이므로 메인 스레드를 잠깐 막을 수 있다 —
  큰 값에는 쓰지 않는다.
- `WebFileStorage`는 실제로는 전부 비동기(Promise/콜백)다 — 이 계약은
  대상 언어가 `async`/`await`를 지원하면 그렇게, 아니면 콜백이나
  코루틴 등 그 언어의 관용적인 비동기 처리로 감싸는 것을 전제하고
  동기 시그니처로 근사했다.
- 두 저장소 모두 **같은 오리진(origin, 프로토콜+도메인+포트)** 안에서만
  공유된다 — 다른 사이트의 데이터에 접근할 수 없다.
- 사용자가 브라우저 설정에서 사이트 데이터를 지우거나 시크릿 모드를
  쓰면 저장된 내용이 사라질 수 있다 — `std/io/file.md`의 디스크 파일과
  달리 이 저장소는 사용자가 언제든 지울 수 있다는 것을 전제로
  설계해야 한다.

# Examples

## 예제: 쓰고 다시 읽기

호출 (순서대로): `WebStorage.setItem("volume", "0.8")`,
`WebStorage.getItem("volume")`

기대 동작: 두 번째 호출은 `"0.8"`을 반환한다.

## 예제: 없는 키 읽기는 null (WebStorage) / 오류 (WebFileStorage)

호출: `WebStorage.getItem("없는키")`

기대 동작: `null`을 반환한다 — `std/io/file.md`의 `File.readAllText`(오류를
낸다)와 다르다는 점에 주의한다. `WebFileStorage.readAllBytes`는
`File.readAllBytes`와 같이 오류를 낸다.

# Open Points

- IndexedDB의 인덱스·커서·트랜잭션 격리 수준처럼 더 정교한 기능은 이
  버전의 범위 밖이다 — 키-값 하나를 저장하고 꺼내는 것만 다룬다.
- 저장 공간 할당량(quota) 초과를 미리 확인하는 API(`navigator.storage.estimate`)는
  다루지 않는다.
