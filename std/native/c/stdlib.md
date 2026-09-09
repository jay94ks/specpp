#!specpp 0.1

# Meta

- name: std/native/c/stdlib
- version: 0.1.0
- description: C 표준 라이브러리의 `<stdlib.h>` 중 메모리·프로세스 관련 함수에 대한 실체 명세.
- kind: native

# Intent

[`std/native/c/stdio.md`](stdio.md)와 같은 이유로 존재한다 — C 코드와 직접
맞물려야 할 때, 특히 수동 메모리 관리(`malloc`/`free`)처럼 SPP의 다른 어떤
패키지도 대신할 수 없는 저수준 연산을 가리키기 위한 것이다.

# Domain

## Class: Native.C.Stdlib

메서드:
[Static]
- malloc(size: int) -> void*
  설명: size 바이트만큼 초기화되지 않은 메모리를 할당해 그 시작 주소를
  반환한다. 실패하면 null 포인터를 반환한다.
[Static]
- calloc(count: int, size: int) -> void*
  설명: `count * size` 바이트를 0으로 초기화해 할당한다.
[Static]
- realloc(ptr: void*, newSize: int) -> void*
  설명: 이미 할당된 ptr의 크기를 newSize로 바꾼다. 필요하면 다른 주소로
  옮겨질 수 있다 — 반환값을 새 주소로 써야 한다.
[Static]
- free(ptr: void*) -> void
  설명: malloc/calloc/realloc으로 할당한 메모리를 해제한다. `free`한 뒤 같은
  포인터를 다시 `free`하거나 접근하면 정의되지 않은 동작이다 — 이 계약은 그런
  오용을 막아주지 않는다.
[Static]
- exit(code: int) -> void
  설명: 프로그램을 즉시 code 종료 코드로 끝낸다.
[Static]
- atoi(text: string) -> int
[Static]
- atof(text: string) -> float

# Constraints

- 헤더 `<stdlib.h>`.
- `malloc`/`calloc`/`realloc`/`free`가 짝을 이뤄야 한다는 것(모든 할당은 정확히
  한 번 해제되어야 한다)은 이 계약이 강제하지 않는다 — 사용하는 쪽의 책임이다.
  가능하면 [`std/native/cpp/memory.md`](../cpp/memory.md)의 스마트 포인터로
  이 책임을 대신 지우는 것을 권장한다.
- 이 패키지가 다루는 "동적 메모리 할당" 자체는 대부분의 SPP 패키지에서는
  필요 없다 — 타겟 언어의 가비지 컬렉션·소유권 시스템에 맡긴다(0장 철학).
  이 파일은 C 코드와 직접 맞물려야 할 때만 쓴다.

# Examples

## 예제: 할당하고 해제

호출: `p = Native.C.Stdlib.malloc(16)`, `Native.C.Stdlib.free(p)`

기대 동작: 16바이트가 할당되었다가 해제된다.

# Open Points

- 없음.
