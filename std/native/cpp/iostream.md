#!specpp 0.1

# Meta

- name: std/native/cpp/iostream
- version: 0.1.0
- description: C++ 표준 라이브러리의 `<iostream>`(전역 스트림 객체)에 대한 실체 명세.
- kind: native

# Intent

C++ 코드와 직접 맞물려야 할 때 쓴다. 평범한 SPP 패키지는 이 대신
[`std/stdout.md`](../../stdout.md)/[`std/stdin.md`](../../stdin.md)/
[`std/stderr.md`](../../stderr.md)를 쓴다 — 그 세 계약이 결국 이 실체에
바인딩된다.

# Domain

## globals

package_like cout: Native.Cpp.Ostream — 표준 출력 스트림.
package_like cerr: Native.Cpp.Ostream — 표준 에러 스트림 (버퍼링 없음).
package_like cin: Native.Cpp.Istream — 표준 입력 스트림.

## Interface: Native.Cpp.Ostream

메서드:
- write(text: string) -> void
  설명: 실제 C++에서는 `<<` 연산자로 쓰지만(`std::cout << text`), SPP는 아직
  연산자 오버로드 표기가 없으므로 메서드 호출로 나타낸다 (아래 Open Points).
- flush() -> void

## Interface: Native.Cpp.Istream

메서드:
- readLine() -> string?
  설명: `std::getline(stream, line)`에 대응한다. 더 읽을 내용이 없으면(EOF)
  null.

# Constraints

- 헤더 `<iostream>`. `cout`/`cerr`/`cin`은 이미 존재하는 전역 객체이므로
  이 패키지 자체가 무언가를 생성하지 않는다.
- 실제 C++ 코드에서는 `std::cout << "hi" << std::endl;`처럼 `<<` 연산자
  체이닝으로 쓴다 — 이 파일의 `write()`는 그것을 SPP가 표현할 수 있는
  형태로 근사한 것이다.

# Examples

## 예제: 표준 출력에 쓰기

호출: `Native.Cpp.cout.write("Hello World")`

기대 동작: 표준 출력에 `Hello World`가 쓰인다 (실제 C++ 트랜스파일 결과는
`std::cout << "Hello World";`).

# Open Points

- 연산자 오버로드(`<<`, `>>`) 자체를 SPP 표기로 어떻게 나타낼지는 아직
  정의되어 있지 않다 — 정해지면 이 파일도 그 표기로 바꾼다.
