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

이 색인은 두 그룹으로 나뉩니다 — 어떤 패키지가 **추상 계약**(대상 언어·
플랫폼에 자유롭게 매핑됨)인지, 아니면 특정 플랫폼·제공자의 **실체 명세**
(`kind: native`, 실제 API를 그대로 옮긴 것)인지가 이 저장소 전체에서 가장
중요한 구분이기 때문입니다(SPEC.md 1.2절). 네트워킹·클라우드 서비스처럼
한 섹션 안에 추상 계약과 그 구체적인 `kind: native` 구현을 함께 보여주는
경우도 있습니다 — 관련 내용을 한곳에서 보는 게 낫다고 판단한 예외입니다.

**목차**
- **범용 추상 계약** — 콘솔 입출력, 파일 시스템, 텍스트, 컬렉션, 동시성,
  시스템, GUI, 네트워킹, 클라우드 서비스
- **플랫폼·제공자별 실체 명세** — POSIX, Linux, macOS, Windows, 웹 전용,
  JavaScript 생태계, 그래픽스, 오디오, 네이티브 실체 명세

## 범용 추상 계약

이 그룹의 패키지는 기본적으로 **추상 계약**이다 — Meta에 `kind` 필드가
없고, 대상 언어·플랫폼의 관용적인 방식에 AI가 자유롭게 매핑한다(SPEC.md
1.2절). 네트워킹·클라우드 서비스 섹션은 예외적으로 추상 계약과 그
`kind: native` 구현을 함께 보여준다(각 섹션 설명 참고).

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
| `std/net/udp.md` | 연결 없는 데이터그램(UDP) 통신 |
| `std/net/httpserver.md` | HTTP 서버 — 리스너·요청/응답·라우터·미들웨어 (`std/native/cpp/nhttp/server.md`가 C/C++ 기본 구현) |
| `std/net/staticfiles.md` | 조건부 GET·Range 지원 정적 파일 서빙 (`std/native/cpp/nhttp/static.md`가 C/C++ 기본 구현) |
| `std/net/websocket.md` | WebSocket 서버 엔드포인트 (`std/native/cpp/nhttp/websocket.md`가 C/C++ 기본 구현) |
| `std/net/reverseproxy.md` | 라운드로빈 리버스 프록시 (`std/native/cpp/nhttp/reverseproxy.md`가 C/C++ 기본 구현) |

### 클라우드 서비스 (`cloud/`)

[`std/ui/widgets.md`](ui/widgets.md) + `windows/win32.md`/`web/dom.md`와
같은 "추상 계약 + 제공자별 `kind: native` 구현" 패턴을 클라우드
인프라에도 적용한 것이다 — `std/cloud/*.md`(추상 계약, 아래 표)는
어느 제공자를 타겟하든 참조 코드가 그대로 유지되게 하고, 실제
트랜스파일은 항상 `aws/`/`gcp/`/`azure/` 하위의 구체적인 구현으로
이뤄진다. 세 제공자의 실제 API 모양이 근본적으로 다른 지점(예: GCP는
큐와 팬아웃을 Pub/Sub 하나로 통합한다, Azure RBAC는 AWS/GCP와 권한
모델 자체가 다르다)은 각 파일이 얼버무리지 않고 명시한다 — 정확한
차이는 각 파일의 Constraints/Intent를 참고한다.

`accesscontrol.md`/`network.md`(IAM/VPC류)는 다른 항목과 달리
애플리케이션 런타임이 아니라 배포·인프라 구성 단계에서 주로 쓰인다
(각 파일 Intent 참고).

#### 추상 계약

| 경로 | 제공하는 것 |
|---|---|
| `std/cloud/objectstorage.md` | 버킷·키 기반 오브젝트 스토리지 |
| `std/cloud/cdn.md` | 엣지 캐싱·배포 CDN |
| `std/cloud/nosqldb.md` | 키 기반 완전관리형 NoSQL 데이터베이스 |
| `std/cloud/queue.md` | 완전관리형 메시지 큐(pull, 팬아웃 아님) |
| `std/cloud/pubsub.md` | 팬아웃 Pub/Sub 알림 |
| `std/cloud/function.md` | 서버리스 함수 호출·핸들러 계약 |
| `std/cloud/secrets.md` | 비밀번호·API 키 등 시크릿 저장·조회 |
| `std/cloud/observability.md` | 로그 수집·지표 기록/조회 |
| `std/cloud/accesscontrol.md` | 접근 권한(역할·정책) 정의 (IAM) |
| `std/cloud/network.md` | 가상 네트워크 격리·보안 그룹 (VPC) |

#### AWS 구현 (`aws/`, `kind: native`)

| 경로 | 구현하는 추상 계약 |
|---|---|
| `std/cloud/aws/s3.md` | objectstorage.md (S3) |
| `std/cloud/aws/cloudfront.md` | cdn.md (CloudFront) |
| `std/cloud/aws/dynamodb.md` | nosqldb.md (DynamoDB) |
| `std/cloud/aws/sqs.md` | queue.md (SQS) |
| `std/cloud/aws/sns.md` | pubsub.md (SNS) |
| `std/cloud/aws/lambda.md` | function.md (Lambda) |
| `std/cloud/aws/secretsmanager.md` | secrets.md (Secrets Manager) |
| `std/cloud/aws/cloudwatch.md` | observability.md (CloudWatch) |
| `std/cloud/aws/iam.md` | accesscontrol.md (IAM) |
| `std/cloud/aws/vpc.md` | network.md (VPC) |

#### GCP 구현 (`gcp/`, `kind: native`)

| 경로 | 구현하는 추상 계약 |
|---|---|
| `std/cloud/gcp/storage.md` | objectstorage.md (Cloud Storage) |
| `std/cloud/gcp/cdn.md` | cdn.md (Cloud CDN) |
| `std/cloud/gcp/firestore.md` | nosqldb.md (Firestore) |
| `std/cloud/gcp/pubsub.md` | queue.md **+** pubsub.md (Cloud Pub/Sub — GCP는 두 계약을 한 서비스로 통합) |
| `std/cloud/gcp/functions.md` | function.md (Cloud Functions) |
| `std/cloud/gcp/secretmanager.md` | secrets.md (Secret Manager) |
| `std/cloud/gcp/monitoring.md` | observability.md (Cloud Logging/Monitoring) |
| `std/cloud/gcp/iam.md` | accesscontrol.md (Cloud IAM) |
| `std/cloud/gcp/vpc.md` | network.md (VPC 방화벽 규칙) |

#### Azure 구현 (`azure/`, `kind: native`)

| 경로 | 구현하는 추상 계약 |
|---|---|
| `std/cloud/azure/blobstorage.md` | objectstorage.md (Blob Storage) |
| `std/cloud/azure/cdn.md` | cdn.md (Azure CDN) |
| `std/cloud/azure/cosmosdb.md` | nosqldb.md (Cosmos DB) |
| `std/cloud/azure/storagequeue.md` | queue.md (Queue Storage) |
| `std/cloud/azure/servicebustopics.md` | pubsub.md (Service Bus Topics) |
| `std/cloud/azure/functions.md` | function.md (Azure Functions) |
| `std/cloud/azure/keyvault.md` | secrets.md (Key Vault) |
| `std/cloud/azure/monitor.md` | observability.md (Azure Monitor) |
| `std/cloud/azure/rbac.md` | accesscontrol.md (Azure RBAC) |
| `std/cloud/azure/vnet.md` | network.md (Virtual Network/NSG) |

## 플랫폼·제공자별 실체 명세

이 그룹의 패키지는 전부 `kind: native`다 — 실제로 존재하는 OS API, 브라우저
API, 서드파티 라이브러리, 또는 C/C++ 표준 라이브러리 자체를 그대로 옮겨 적은
것이며 새로 설계할 대상이 아니다(SPEC.md 1.2절). 위 클라우드 서비스의
`aws/`/`gcp/`/`azure/` 구현도 성격은 같지만, 그 추상 계약과 나란히 보는 게
더 유용해 위 그룹에 남겨 뒀다.

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
| `std/windows/direct3d.md` | DirectX(Direct3D 9) 고정 함수 텍스처 사각형 렌더링 (`kind: native`) |
| `std/windows/direct3d11.md` | DirectX(Direct3D 11) 셰이더·버텍스 버퍼 기반 렌더링 (`kind: native`) |
| `std/windows/directsound.md` | DirectX(DirectSound) 위치 기반 효과음 재생 (`kind: native`) |

각 OS 전용 패키지의 `platform` 필드에는 다른 OS를 대상으로 할 때 쓸 수 있는
대체 구현이 `-> fallback: ...`으로 표시되어 있습니다 (3.10절).

### 웹 전용 (`web/`, `platform: web` — 3.10절)

전통적인 OS가 아니라 브라우저 샌드박스를 대상으로 할 때 씁니다(3.10절의
`platform: web` 설명 참조) — 나머지는 위 OS 전용 패키지들과 같은 관례를
따릅니다.

| 경로 | 제공하는 것 |
|---|---|
| `std/web/dom.md` | 브라우저 DOM으로 창·버튼 GUI 만들기 + 원시 키보드·마우스 입력 (`kind: native`) |
| `std/web/canvas.md` | `<canvas>`(2D 컨텍스트)로 직접 그리기 렌더링 (`kind: native`) |
| `std/web/webgl.md` | WebGL2 셰이더·버텍스 버퍼 기반 렌더링 (`kind: native`) |
| `std/web/webaudio.md` | Web Audio API 위치 기반 효과음 재생 (`kind: native`) |
| `std/web/storage.md` | localStorage/IndexedDB 기반 영속 저장 (`kind: native`) |

### JavaScript 생태계 (`js/`, `kind: native`, 플랫폼 무관)

특정 OS나 브라우저가 아니라 JavaScript/TypeScript 언어 생태계 자체에
묶인, 사실상 표준처럼 쓰이는 서드파티 라이브러리의 실체 명세다 — Node.js와
브라우저 양쪽에서 동일하게 쓸 수 있어 `platform` 필드를 두지 않는다.

| 경로 | 제공하는 것 |
|---|---|
| `std/js/axios.md` | HTTP 클라이언트 (axios — `std/net/httpclient.md`의 실제 구현 선택지) |

### 그래픽스 (`graphics/`, `kind: native`, 플랫폼 무관)

| 경로 | 제공하는 것 |
|---|---|
| `std/graphics/opengl.md` | 텍스처 사각형 그리기 (레거시 OpenGL 1.x 즉시 모드) |
| `std/graphics/opengl3.md` | 셰이더·버텍스 버퍼 기반 렌더링 (OpenGL 3.3+ 코어 프로파일) |

### 오디오 (`audio/`, `kind: native`, 플랫폼 무관)

| 경로 | 제공하는 것 |
|---|---|
| `std/audio/openal.md` | 위치 기반 효과음 재생 (OpenAL) |

### 네이티브 실체 명세 (`native/`, `kind: native` — 1.2절)

아래는 "만들 대상"이 아니라 C/C++에 **이미 존재하는** 표준 라이브러리나
특정 서드파티 라이브러리를 그대로 옮겨 적은 실체 명세입니다. 평범한
패키지를 새로 쓸 때는 대신 위의 추상 계약(`text/`, `collections/`,
`system/` 등)을 쓰고, 이 아래 항목들은 `extern "C"`/`extern "C++"`
(3.9절)로 C/C++ 코드와 직접 맞물려야 할 때만 참조합니다.

| 경로 | 제공하는 것 |
|---|---|
| `std/native/c/stdio.md` | `<stdio.h>` (`FILE*`, `fopen`/`printf` 등) |
| `std/native/c/stdlib.md` | `<stdlib.h>` (`malloc`/`free`/`exit` 등) |
| `std/native/c/string.md` | `<string.h>` (`strlen`/`strcpy`/`memcpy` 등) |
| `std/native/cpp/memory.md` | `<memory>` (`unique_ptr`/`shared_ptr`) |
| `std/native/cpp/containers.md` | `<vector>`/`<string>`/`<unordered_map>` |
| `std/native/cpp/iostream.md` | `<iostream>` (`cout`/`cin`/`cerr`) |

**서드파티 라이브러리 (`native/cpp/nhttp/`, `platform: linux, windows`) —
SPP가 네이티브 HTTP 서버 구현에 기본으로 채택하는 라이브러리.**
코루틴 기반 HTTP/1.1·HTTP/2 서버 라이브러리
[jay94ks/libnhttp](https://github.com/jay94ks/libnhttp) 하나를 그
라이브러리 자신의 모듈 경계(서버/라우팅, 정적 파일·가상 호스팅,
WebSocket, 리버스 프록시, TLS, 비동기 실행 계층, 플러그인)에 따라 여러
단일 파일 패키지로 나눠 옮겼다 — [`std/js/axios.md`](js/axios.md)와
같은 성격(추상 계약이 아니라 실제 라이브러리 하나를 그대로 옮긴 것)
이다. 대상이 C/C++이고 웹 서버(REST API, 정적 파일, WebSocket, 리버스
프록시 등)를 만들어야 한다면, 사용자가 다른 라이브러리를 명시적으로
지정하지 않는 한 AI는 처음부터 소켓·HTTP를 직접 구현하는 대신 이
계열을 우선 채택한다(각 파일의 Intent 참고).

| 경로 | 제공하는 것 |
|---|---|
| `std/native/cpp/nhttp/server.md` | HTTP 리스너·요청/응답·REST 라우터 핵심 |
| `std/native/cpp/nhttp/static.md` | 정적 파일 서빙(overlay)·가상 호스팅(vhost) |
| `std/native/cpp/nhttp/websocket.md` | WebSocket 엔드포인트 |
| `std/native/cpp/nhttp/reverseproxy.md` | 라운드로빈 리버스 프록시 |
| `std/native/cpp/nhttp/tls.md` | OpenSSL 기반 TLS 컨텍스트 |
| `std/native/cpp/nhttp/async.md` | `task<T>` 코루틴·`io_context` 리액터 |
| `std/native/cpp/nhttp/plugin.md` | 서버 생명주기·요청 훅 플러그인 시스템 |

# Open Points

- 이 파일은 1.2절의 "생성 대상"도 "실체 명세"도 아닌, 순수한 안내용 색인이다.
  이런 성격의 파일을 위한 정식 패키지 종류는 아직 SPEC.md에 정의되어 있지
  않다 — 정해지면 이 파일의 Meta도 맞춘다.
