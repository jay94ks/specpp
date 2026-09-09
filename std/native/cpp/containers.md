#!specpp 0.1

# Meta

- name: std/native/cpp/containers
- version: 0.1.0
- description: C++ 표준 라이브러리 컨테이너(`std::vector`, `std::unordered_map`)에 대한 실체 명세.
- kind: native

# Intent

C++ 코드와 직접 맞물려야 할 때 쓴다. 평범한 SPP 패키지는 이 대신 3.1절의
`list<T>`/`map<K, V>` primitive나 [`std/collections/`](../../collections/)의
추상 계약을 쓴다 — 이 파일은 그것들이 C++에서 실제로 어떤 이름과 모양으로
존재하는지에 대한 실체 명세다. 메서드 이름은 SPP 관례(camelCase)가 아니라
**STL의 실제 이름(snake_case)**을 그대로 쓴다.

# Domain

## Class: Native.Cpp.Vector<T>

메서드:
- push_back(item: T) -> void
- pop_back() -> void
- at(index: int) -> T&
  설명: index가 범위를 벗어나면 예외(`std::out_of_range`)를 던진다.
- size() -> int
- empty() -> boolean
- clear() -> void

## Class: Native.Cpp.BasicString

설명: `std::string`. [`std/text/string.md`](../../text/string.md)의 `String`과
개념은 같지만, 이 클래스는 그 실제 C++ 타입 자체를 가리킨다.

메서드:
- length() -> int
- append(text: string) -> void
- substr(start: int, count: int) -> string
- c_str() -> string
  설명: 널 종료된 원시 문자열 뷰를 반환한다 —
  [`std/native/c/`](../c/)의 C 함수에 넘길 때 쓴다.

## Class: Native.Cpp.UnorderedMap<K, V>

메서드:
- insert(key: K, value: V) -> void
- at(key: K) -> V&
  설명: key가 없으면 예외(`std::out_of_range`)를 던진다.
- count(key: K) -> int
  설명: key가 있으면 1, 없으면 0 (`std::unordered_map`은 중복 키를 허용하지
  않으므로 항상 0 또는 1이다).
- erase(key: K) -> void
- size() -> int

# Constraints

- 헤더 `<vector>`, `<string>`, `<unordered_map>`.
- 반복자(iterator) 기반 API(`begin()`/`end()`, 범위 기반 `for`, `find()`가
  반환하는 iterator 등)는 SPP가 아직 반복자 개념을 정의하지 않아 이 버전의
  범위 밖이다 — 위에 나열된, 값을 직접 주고받는 메서드만 다룬다 (아래 Open
  Points 참조).

# Examples

## 예제: 값을 넣고 확인

호출: `v = Native.Cpp.Vector<int>()`, `v.push_back(1)`, `v.push_back(2)`,
`v.size()`

기대 동작: 마지막 호출은 `2`를 반환한다.

# Open Points

- 반복자 기반 API, `operator[]`처럼 SPP의 메서드 호출 표기로 자연스럽게
  옮기기 애매한 연산자 오버로드는 SPP에 해당 개념(3.x절)이 정의되면 추가한다.
