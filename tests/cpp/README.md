# C++ 검증 테스트

`tests/`의 Python 검증이 SPEC.md/std가 Python으로 트랜스파일 가능함을
보였다면, 이 폴더는 같은 패키지들이 **C++**로도 정확히 트랜스파일된다는 것을
검증합니다 — 포인터/참조자 표기(3.1절), `extern`/Constraints에 등장하는
`std::atomic`/`std::mutex`/STL 컨테이너 매핑이 실제로 성립하는지 확인하는
용도입니다.

외부 테스트 프레임워크 없이 `minitest.hpp`(이 폴더 전용의 아주 작은 헬퍼)만
씁니다.

## 구성

- `todo_cli.hpp` — [`examples/todo-cli.md`](../../examples/todo-cli.md) 참조 구현.
- `collections.hpp` — `std/collections/{collection,set,queue,stack,dictionary}.md`
  참조 구현 (STL 컨테이너 기반).
- `concurrency.hpp` — `std/concurrency/{atomic,mutex,thread}.md` 참조 구현
  (`std::atomic`/`std::mutex`/`std::thread` 기반).
- `test_*.cpp` — 각 패키지의 `Examples`를 그대로 옮긴 테스트.
- `test_native_stl.cpp` — `std/native/cpp/{memory,containers}.md`(`kind: native`
  실체 명세)가 실제 STL API와 정확히 일치하는지 확인한다. 이 파일들은 "구현"이
  아니므로, 검증 방향이 다르다: 우리가 STL을 흉내내는 게 아니라 **묘사가
  실제와 맞는지**를 확인한다.

## 실행

```bash
./run.sh
```

또는 개별적으로:

```bash
clang++ -std=c++17 -Wall -pthread -o test_todo_cli.exe test_todo_cli.cpp
./test_todo_cli.exe
```

**컴파일러 참고:** 이 환경에 함께 있는 MSYS2 기본 `g++`(`/usr/bin/g++`)는 표준
헤더가 없는 최소 빌드라 쓸 수 없고, `mingw64/bin/g++`는 `cc1plus.exe`가 아무
출력 없이 비정상 종료해서 원인 파악 전까지는 피했습니다. 대신 LLVM
`clang++`(`C:\Program Files\LLVM\bin\clang++.exe`)로 컴파일·실행을 검증했습니다.
다른 환경에서는 `CXX=g++ ./run.sh`처럼 정상적인 g++를 써도 됩니다.
