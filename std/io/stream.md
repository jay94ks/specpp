#!specpp 0.1

# Meta

- name: std/io/stream
- version: 0.1.0
- description: 순차적으로 읽고 쓰는 바이트 스트림에 대한 추상 계약.

# Intent

파일 전체·네트워크 응답 전체를 한 번에 메모리에 올리기엔 너무 크거나
(대용량 파일, 다운로드), 데이터가 아직 전부 도착하지 않은 상태
(네트워크 스트리밍)에서 조금씩 읽고 쓰고 싶을 때 쓴다.
[`std/io/file.md`](file.md)의 `readAllBytes`/`writeAllBytes`,
[`std/net/httpclient.md`](../net/httpclient.md)/
[`std/net/httpserver.md`](../net/httpserver.md)의 `body: bytes`는 전체를
한 번에 다루는 것을 전제하는데 — 이 계약은 그 반대다: 얼마나 큰지
몰라도 일부씩 순서대로 처리한다.

# Domain

## Interface: Stream

메서드:
- read(buffer: bytes, offset: int, count: int) -> int
  설명: 최대 `count`바이트를 `buffer`의 `offset` 위치부터 채우고,
  실제로 읽은 바이트 수를 반환한다. 스트림 끝에 도달했으면 `0`을
  반환한다 — 오류가 아니다.
- write(buffer: bytes, offset: int, count: int) -> void
- seek(offset: int, origin: string) -> int
  설명: `origin`은 `"begin"`/`"current"`/`"end"` 중 하나. 이동한 뒤의
  절대 위치를 반환한다. 모든 스트림이 seek을 지원하지는 않는다(예:
  네트워크 소켓) — 지원하지 않으면 오류를 낸다(아래 Constraints).
- flush() -> void
- close() -> void
- readAll() -> bytes
  설명: 끝까지 남은 데이터를 전부 읽어 한 번에 반환하는 편의
  메서드다 — 결국 [`std/io/file.md`](file.md)의 `readAllBytes`가 하던
  일이지만, 이 계약 위에서는 "필요하면 부분씩, 편하면 한 번에" 둘
  다 고를 수 있다.

## Class: MemoryStream implements Stream

메모리 버퍼를 감싸는 가장 기본적인 구현이다 — 테스트나, 작은 데이터를
`Stream` 인터페이스로 다뤄야 하는 API에 넘길 때 쓴다.

생성자:
- MemoryStream()
- MemoryStream(initial: bytes)
  설명: `initial`을 초기 내용으로 채운 채 시작한다.

# Interface

## Library

큰 데이터를 다루는 API는 `bytes` 대신 `Stream`을 받거나 반환하도록
설계합니다. 이미 메모리에 있는 작은 데이터를 그런 API에 넘겨야 하면
`MemoryStream(data)`로 감쌉니다.

# Constraints

- 대상 언어의 표준 스트림 추상(Python `io.RawIOBase`/
  `io.BufferedIOBase`, Java `InputStream`/`OutputStream`, C# `Stream`,
  C++ `std::istream`/`std::ostream`, Node.js `stream.Readable`/
  `stream.Writable` 등)에 매핑한다.
- seek을 지원하지 않는 스트림(네트워크 소켓, 일부 압축 스트림)에
  seek을 호출하면 오류를 낸다.
- 이 계약을 실제로 쓰는 다른 패키지(`std/io/file.md`,
  `std/net/httpclient.md`, `std/net/httpserver.md` 등)가 전체-버퍼
  방식과 스트림 방식을 동시에 지원할지는 각 패키지가 정한다 — 이
  계약 자체는 그 결정을 강제하지 않는다.

# Examples

## 예제: MemoryStream 쓰고 다시 읽기

호출 (순서대로): `s = MemoryStream()`,
`s.write([104, 105], 0, 2)` (`"hi"`에 해당하는 바이트),
`s.seek(0, "begin")`, `buf = bytes(2)`, `s.read(buf, 0, 2)`

기대 동작: 마지막 호출은 `2`(읽은 바이트 수)를 반환하고, `buf`에는
`[104, 105]`가 담긴다.

## 예제: 스트림 끝

호출: 이미 끝까지 읽은 스트림에 `read(buf, 0, 10)`

기대 동작: `0`을 반환한다 — 오류가 아니다.

# Open Points

- 비동기 스트림(코루틴 기반 read/write, 예:
  [`std/native/cpp/nhttp/async.md`](../native/cpp/nhttp/async.md)의
  `io::stream`)은 이 계약이 강제하지 않는다 — 이 추상 계약은 동기
  시그니처로 쓰고, 대상 언어가 비동기가 자연스러우면 그 언어의
  관용구로 근사한다.
