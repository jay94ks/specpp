#!specpp 0.1

# Meta

- name: std/native/c/string
- version: 0.1.0
- description: C 표준 라이브러리의 `<string.h>`에 대한 실체 명세.
- kind: native

# Intent

[`std/native/c/stdio.md`](stdio.md)와 같은 이유로 존재한다 — C의 널 종료
바이트 문자열(`char*`)을 직접 다뤄야 하는 상호운용 상황을 위한 것이다.
평범한 SPP 패키지는 이 대신 [`std/text/string.md`](../../text/string.md)의
`string` 기반 연산을 쓴다.

# Domain

## Class: Native.C.CString

메서드:
[Static]
- strlen(text: string) -> int
  설명: 널 종료 문자까지의 바이트 수를 반환한다(유니코드 코드 포인트 수가
  아니다 — 3.1절의 다른 `string` 연산과 다른 점이다).
[Static]
- strcpy(dest: bytes&, src: string) -> void
  설명: src를 dest에 널 종료 문자까지 복사한다. dest가 충분히 크지 않으면
  정의되지 않은 동작(버퍼 오버플로)이다 — 이 계약은 그런 오용을 막아주지
  않는다.
[Static]
- strcmp(a: string, b: string) -> int
  설명: 사전순으로 a가 b보다 앞이면 음수, 뒤면 양수, 같으면 0.
[Static]
- strcat(dest: bytes&, src: string) -> void
  설명: dest 끝에 src를 이어붙인다. `strcpy`와 같은 오버플로 위험이 있다.
[Static]
- memcpy(dest: bytes&, src: bytes, count: int) -> void
  설명: count 바이트를 그대로 복사한다(문자열 여부와 무관하게 이진 데이터에도
  쓴다).
[Static]
- memset(dest: bytes&, value: int, count: int) -> void
  설명: dest의 앞 count 바이트를 value로 채운다.

# Constraints

- 헤더 `<string.h>`.
- `strcpy`/`strcat`/`memcpy`/`memset`은 대상 버퍼가 충분히 큰지 스스로
  보장해야 한다 — C 자체가 그렇듯 이 계약도 경계를 검사하지 않는다. 가능하면
  경계를 검사하는 변형(`strncpy` 등)을 쓰거나, 애초에
  [`std/text/string.md`](../../text/string.md)처럼 더 안전한 상위 계약을
  쓰는 것을 권장한다.

# Examples

## 예제: 비교

호출: `Native.C.CString.strcmp("a", "b")`

기대 동작: 음수를 반환한다 (`"a"`가 `"b"`보다 사전순으로 앞).

# Open Points

- 없음.
