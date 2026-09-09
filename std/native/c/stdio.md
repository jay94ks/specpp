#!specpp 0.1

# Meta

- name: std/native/c/stdio
- version: 0.1.0
- description: C 표준 라이브러리의 `<stdio.h>`에 대한 실체 명세.
- kind: native

# Intent

이 패키지는 **새로 만들 대상이 아니라, C 언어에 이미 존재하는 `<stdio.h>`를
있는 그대로 옮겨 적은 것**이다(SPEC.md 1.2절, `kind: native`). 다른 패키지가
`extern "C" { ... }`(3.9절) 블록으로 C 코드와 맞물려야 할 때, 또는 이미 있는
C 라이브러리를 호출해야 할 때 "이 함수는 이렇게 생겼다"는 계약으로 참조한다.
메서드 이름은 우리 표기 관례(camelCase)가 아니라 **실제 C 함수 이름을 그대로**
쓴다 — 이 패키지는 정확히 그 실체를 가리켜야 하기 때문이다.

# Domain

## Class: FILE

(불투명 핸들이다 — 멤버를 드러내지 않는다. 항상 `FILE*` 형태로만 다룬다.)

## Class: Native.C.Stdio

메서드:
[Static]
- fopen(path: string, mode: string) -> FILE*
  설명: 파일을 연다. 실패하면 null 포인터를 반환한다(C의 관례 그대로 — 예외를
  던지지 않는다).
[Static]
- fclose(stream: FILE*) -> int
  설명: 스트림을 닫는다. 성공하면 0을 반환한다.
[Static]
- fread(buffer: bytes&, size: int, count: int, stream: FILE*) -> int
  설명: 실제로 읽은 원소 개수를 반환한다.
[Static]
- fwrite(buffer: bytes, size: int, count: int, stream: FILE*) -> int
[Static]
- printf(format: string, args: list<any>) -> int
  설명: 표준 출력에 서식화된 텍스트를 쓴다. 가변 인자(`...`)는 `args`로
  뭉뚱그려 표현한다 — 실제 바인딩에서는 타겟 언어의 가변 인자·서식 문자열
  방식을 그대로 쓴다.
[Static]
- fprintf(stream: FILE*, format: string, args: list<any>) -> int

# Constraints

- 헤더 `<stdio.h>`. 정적 링크든 동적 링크든 C 런타임에 이미 존재하므로 별도
  구현이 필요 없다 — `extern "C" (static or shared)`(3.9절)로 연결 방식만
  고르면 된다.
- 이 패키지가 기술하는 함수들은 이미 [`std/stdout.md`](../../stdout.md),
  [`std/stdin.md`](../../stdin.md), [`std/io/file.md`](../../io/file.md)가
  더 높은 추상 수준에서 다루는 것과 같은 기능이다 — 일반적인 SPP 패키지를
  새로 쓸 때는 이 파일이 아니라 그쪽을 쓴다. 이 파일은 C 코드와 직접 맞물려야
  하는 낮은 수준의 상호운용에만 쓴다.

# Examples

## 예제: 열고 쓰고 닫기

호출: `f = Native.C.Stdio.fopen("a.txt", "w")`,
`Native.C.Stdio.fprintf(f, "%s", ["hi"])`, `Native.C.Stdio.fclose(f)`

기대 동작: `a.txt` 파일에 `"hi"`가 쓰인다.

# Open Points

- 가변 인자 서식 문자열(`%d`, `%s` 등)의 타입 안전성 검사는 이 계약의 범위
  밖이다 — C 자체가 검사하지 않는 것과 같다.
