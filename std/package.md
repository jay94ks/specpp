#!specpp 0.1

# Meta

- name: std
- description: SPP 표준 라이브러리 전체 색인.

# Intent

`std/` 아래에 흩어진 표준 라이브러리 패키지들을 한 곳에서 찾아볼 수 있게 한다.
이 파일 자체는 번역(코드 생성) 대상이 아니라 안내용 색인이다 — 아래 표에 나열된
각 항목이 실제로 참조해서 쓰는 독립된 단일 파일 패키지다 (1.1절 "표준 라이브러리
관례" 참조). 새 표준 라이브러리 패키지를 추가하면 이 표에도 함께 추가한다.

# Interface

## Library

다른 패키지는 아래 표의 "경로" 열에 있는 값을 1.1절의 경로 참조로 그대로
씁니다 (예: `std/text/string.md`).

### 콘솔 입출력

| 경로 | 제공하는 것 |
|---|---|
| `std/stdout.md` | 표준 출력 |
| `std/stderr.md` | 표준 에러 |
| `std/stdin.md` | 표준 입력 |

### 파일 시스템 (`io/`)

| 경로 | 제공하는 것 |
|---|---|
| `std/io/file.md` | 파일 읽기·쓰기, 경로(Path) 조작 |
| `std/io/directory.md` | 디렉터리 생성·삭제·목록 조회 |

### 텍스트 (`text/`)

| 경로 | 제공하는 것 |
|---|---|
| `std/text/string.md` | `string` 조작 함수 모음 |
| `std/text/regex.md` | 정규 표현식 |
| `std/text/json.md` | JSON 직렬화·역직렬화 |

### 컬렉션 (`collections/`, 단일 스레드 전제)

| 경로 | 제공하는 것 |
|---|---|
| `std/collections/collection.md` | 공통 계약(`size`/`isEmpty`) |
| `std/collections/list.md` | `list<T>` 조작 함수 모음 |
| `std/collections/set.md` | 중복 없는 모음 |
| `std/collections/queue.md` | FIFO 큐 |
| `std/collections/stack.md` | LIFO 스택 |
| `std/collections/dictionary.md` | 키-값 연관 배열 |

### 동시성 (`concurrency/`)

| 경로 | 제공하는 것 |
|---|---|
| `std/concurrency/atomic.md` | 원자적 값 래퍼(CAS) |
| `std/concurrency/mutex.md` | 배타적 잠금 |
| `std/concurrency/queue.md` | 스레드 안전 FIFO 큐 |
| `std/concurrency/stack.md` | 스레드 안전 LIFO 스택 |
| `std/concurrency/dictionary.md` | 스레드 안전 키-값 저장소 |
| `std/concurrency/bag.md` | 순서 없는 스레드 안전 모음 |
| `std/concurrency/thread.md` | 스레드 생성·실행·대기 |

### 시스템 (`system/`, .NET `System`에 대응)

| 경로 | 제공하는 것 |
|---|---|
| `std/system/exception.md` | 오류 타입의 공통 기반 클래스 |
| `std/system/math.md` | 수학 상수·함수 |
| `std/system/random.md` | 난수 생성 |
| `std/system/datetime.md` | 특정 시점(날짜·시각) |
| `std/system/timespan.md` | 기간(duration) |
| `std/system/guid.md` | 전역 고유 식별자 |
| `std/system/convert.md` | 기본 타입 변환·파싱 |
| `std/system/environment.md` | 명령행 인자·환경 변수 |
| `std/system/process.md` | 외부 프로세스 실행·대기·종료 |
| `std/system/appdirs.md` | 앱 설정·캐시·데이터 경로 (추상 계약) |
| `std/system/dialog.md` | 알림·확인 대화 상자 (추상 계약) |
| `std/system/debug.md` | 실행 중 조건 검사(assert)·진단 로그, 스펙 추적(4.7절) |

### GUI (`ui/`)

| 경로 | 제공하는 것 |
|---|---|
| `std/ui/widgets.md` | 창·버튼·라벨 (`Window`/`Button`/`Label`), 클릭 이벤트 |
| `std/ui/canvas.md` | 2D 캔버스 창(`CanvasWindow`/`Canvas`), 도형·텍스트 직접 그리기, 키 입력 |
| `std/ui/textbox.md` | 여러 줄 텍스트 편집 상자 (`TextBox`) |
| `std/ui/menu.md` | 창 메뉴 막대 (`MenuBar`/`Menu`/`MenuItem`) |
| `std/ui/filedialog.md` | 네이티브 파일 열기/저장 대화 상자 |

### 네트워킹 (`net/`, .NET `System.Net`에 대응)

| 경로 | 제공하는 것 |
|---|---|
| `std/net/uri.md` | URI 파싱 |
| `std/net/ipendpoint.md` | IP 주소·접속 지점 |
| `std/net/dns.md` | 호스트 이름 조회 |
| `std/net/tcp.md` | TCP 클라이언트·리스너 |
| `std/net/httpclient.md` | HTTP 요청·응답 |

### POSIX 공통 (`posix/`, `platform: linux, macos` — 3.10절)

| 경로 | 제공하는 것 |
|---|---|
| `std/posix/signal.md` | 시그널 등록·전송 |

### Linux 전용 (`linux/`, `platform: linux`)

| 경로 | 제공하는 것 |
|---|---|
| `std/linux/appdirs.md` | XDG 기준 앱 디렉터리 (`AppDirectories` 구현) |
| `std/linux/dialog.md` | zenity/kdialog 기반 대화 상자 (`Dialog` 구현) |

### macOS 전용 (`macos/`, `platform: macos`)

| 경로 | 제공하는 것 |
|---|---|
| `std/macos/appdirs.md` | `~/Library` 기준 앱 디렉터리 (`AppDirectories` 구현) |
| `std/macos/dialog.md` | osascript 기반 대화 상자 (`Dialog` 구현) |

### Windows 전용 (`windows/`, `platform: windows` — 3.10절)

| 경로 | 제공하는 것 |
|---|---|
| `std/windows/registry.md` | 레지스트리 읽기·쓰기 |
| `std/windows/messagebox.md` | 네이티브 메시지 박스 (`Dialog` 구현) |
| `std/windows/consolecontrol.md` | 콘솔 제어 이벤트(Ctrl+C 등) 처리 |
| `std/windows/win32.md` | 순수 Win32 API로 창·버튼 GUI 만들기 (`kind: native`) |
| `std/windows/direct2d.md` | DirectX(Direct2D/DirectWrite) 2D 렌더링 (`kind: native`) |

각 OS 전용 패키지의 `platform` 필드에는 다른 OS를 대상으로 할 때 쓸 수 있는
대체 구현이 `-> fallback: ...`으로 표시되어 있습니다 (3.10절).

### 네이티브 실체 명세 (`native/`, `kind: native` — 1.2절)

아래는 "만들 대상"이 아니라 C/C++에 **이미 존재하는** 표준 라이브러리를 그대로
옮겨 적은 실체 명세입니다. 평범한 패키지를 새로 쓸 때는 대신 위의 추상 계약
(`text/`, `collections/`, `system/` 등)을 쓰고, 이 아래 항목들은 `extern "C"`/
`extern "C++"`(3.9절)로 C/C++ 코드와 직접 맞물려야 할 때만 참조합니다.

| 경로 | 제공하는 것 |
|---|---|
| `std/native/c/stdio.md` | `<stdio.h>` (`FILE*`, `fopen`/`printf` 등) |
| `std/native/c/stdlib.md` | `<stdlib.h>` (`malloc`/`free`/`exit` 등) |
| `std/native/c/string.md` | `<string.h>` (`strlen`/`strcpy`/`memcpy` 등) |
| `std/native/cpp/memory.md` | `<memory>` (`unique_ptr`/`shared_ptr`) |
| `std/native/cpp/containers.md` | `<vector>`/`<string>`/`<unordered_map>` |
| `std/native/cpp/iostream.md` | `<iostream>` (`cout`/`cin`/`cerr`) |

# Open Points

- 이 파일은 1.2절의 "생성 대상"도 "실체 명세"도 아닌, 순수한 안내용 색인이다.
  이런 성격의 파일을 위한 정식 패키지 종류는 아직 SPEC.md에 정의되어 있지
  않다 — 정해지면 이 파일의 Meta도 맞춘다.
