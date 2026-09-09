#!specpp 0.1

# Meta

- name: std/native/cpp/memory
- version: 0.1.0
- description: C++ 표준 라이브러리의 `<memory>`(스마트 포인터)에 대한 실체 명세.
- kind: native

# Intent

C++ 코드와 맞물려야 하는데 [`std/native/c/stdlib.md`](../c/stdlib.md)의
`malloc`/`free`를 손으로 다루고 싶지 않을 때 쓴다. 소유권(누가 이 메모리를
언제 해제할 책임이 있는지)을 타입 자체로 표현하는 C++의 관용적인 방식이다.

# Domain

## Class: Native.Cpp.UniquePtr<T>

설명: 정확히 하나의 소유자만 갖는 포인터. 복사할 수 없고, 이동만 가능하다.
소유자가 스코프를 벗어나면 자동으로 `T`가 해제된다(RAII).

메서드:
- get() -> T*
  설명: 소유권을 넘기지 않고 내부 포인터만 본다.
- release() -> T*
  설명: 소유권을 포기하고 내부 포인터를 반환한다 — 이후 이 UniquePtr는
  아무것도 소유하지 않는다. 반환된 포인터는 호출한 쪽이 해제할 책임을 진다.
- reset(newPtr: T*) -> void
  설명: 기존에 소유하던 것을 해제하고 newPtr(기본값 null)을 새로 소유한다.

## Class: Native.Cpp.SharedPtr<T>

설명: 여러 소유자가 참조 카운트를 공유하는 포인터. 마지막 소유자가 사라질 때
`T`가 해제된다.

메서드:
- get() -> T*
- use_count() -> int
  설명: 현재 이 대상을 함께 소유하고 있는 SharedPtr 개수를 반환한다.

# Constraints

- 헤더 `<memory>`. `UniquePtr<T>`는 `std::unique_ptr<T>`, `SharedPtr<T>`는
  `std::shared_ptr<T>`에 대응한다.
- 대부분의 SPP 패키지는 3.1절의 `T*`/`T&` 표기만으로 충분하고, 대상 언어가
  가비지 컬렉션을 갖고 있다면 AI가 알아서 관용적인 방식으로 매핑한다(0장
  철학). 이 파일은 **C++로 트랜스파일할 때 소유권을 명시적으로 드러내고
  싶은 경우**에만 참조한다.

# Examples

## 예제: 스코프를 벗어나면 자동 해제

호출: 블록 안에서 `p = Native.Cpp.UniquePtr<Task>(...)`를 만들고 블록을
벗어난다.

기대 동작: 블록을 벗어나는 시점에 별도의 `free`/`delete` 호출 없이 `Task`가
해제된다.

# Open Points

- `WeakPtr<T>`(`std::weak_ptr`)는 다음 버전에서 다룬다.
