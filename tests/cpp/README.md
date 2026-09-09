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
- `rps_game.hpp` — [`examples/rock-paper-scissors.md`](../../examples/rock-paper-scissors.md)의
  `# Domain`(`Rps::Game`/`Rps::RoundResult`) 참조 구현. GUI와 무관한 순수 규칙만
  다룬다.
- `rps_win32.cpp` — 같은 예제의 `# Interface` > `## GUI` 참조 구현.
  [`std/windows/win32.md`](../../std/windows/win32.md)(`kind: native`)에서
  기술한 실제 Win32 API(`CreateWindowExW`, `WM_COMMAND` 등)만으로 만든 진짜
  창·버튼 GUI다 — 프레임워크 없음. `run.sh`가 자동으로 돌리는 목록에는 없다
  (실제 창을 띄우는 프로그램이라 자동화 테스트가 아니라 수동 확인용이다).
- `game2048.hpp` — [`examples/2048.md`](../../examples/2048.md)의 `# Domain`
  (`Game2048::Game`) 참조 구현. GUI와 무관한 순수 규칙만 다룬다.
  `test_2048_game.cpp`가 이걸 자동으로 검증한다.
- `game2048_direct2d.cpp` — 같은 예제의 `# Interface` > `## GUI` 참조 구현.
  [`std/windows/win32.md`](../../std/windows/win32.md) +
  [`std/windows/direct2d.md`](../../std/windows/direct2d.md)(둘 다
  `kind: native`)만으로 만든 진짜 **DirectX(Direct2D/DirectWrite)** 렌더링
  GUI다 — 프레임워크 없음. `rps_win32.cpp`와 마찬가지로 수동 확인용이며
  `run.sh` 목록에는 없다.
- `notepad_win32.cpp` — [`examples/notepad.md`](../../examples/notepad.md)의
  `# Interface` > `## GUI` 참조 구현. 순수 Win32 `EDIT` 컨트롤 + 네이티브
  메뉴(`HMENU`) + 공용 파일 대화 상자(`GetOpenFileNameW`/`GetSaveFileNameW`)만
  으로 만들었다. 새로 만들기/열기/저장/다른 이름으로 저장/끝내기(저장 확인
  포함)와 잘라내기/복사/붙여넣기/실행 취소/모두 선택/상태 표시줄(줄·열)을
  다룬다 — 찾기/바꾸기/이동 대화 상자와 자동 줄 바꿈 토글은 시간 관계상
  Python 버전(`tests/app_notepad.py`)에만 구현했다. 수동 확인용, `run.sh`
  목록에는 없다.
- `test_*.cpp` — 각 패키지의 `Examples`를 그대로 옮긴 테스트.
- `test_native_stl.cpp` — `std/native/cpp/{memory,containers,iostream}.md`
  (`kind: native` 실체 명세) 전체가 실제 STL API와 정확히 일치하는지 확인한다.
  이 파일들은 "구현"이 아니므로, 검증 방향이 다르다: 우리가 STL을 흉내내는
  게 아니라 **묘사가 실제와 맞는지**를 확인한다. `Vector`/`UnorderedMap`/
  `BasicString`/스마트 포인터는 STL의 실제 이름을 그대로 쓰므로 `std::` 타입을
  직접 두드려 검증하고, `iostream.md`의 `Ostream`/`Istream`은 SPP가 아직
  연산자 오버로드(`<<`)를 표기하지 못해 `write()`/`readLine()`으로 근사한
  것이므로(그 파일의 Open Points 참조) 작은 래퍼로 그 근사가 실제 스트림
  위에서 의도대로 동작하는지 확인한다.

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
