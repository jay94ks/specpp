# SPP — Specification-oriented Pseudo-language for AI

![status](https://img.shields.io/badge/status-idea%20stage-yellow)
![spec version](https://img.shields.io/badge/spec-SPP%200.1-blue)
![docs](https://img.shields.io/badge/docs-SPEC.md-lightgrey)

**"실행되지 않는 언어."**

> ⚠️ **아직 아이디어 구상 단계입니다.** 문법, 표준 라이브러리 구성, 여기 적힌
> 설계 결정들 모두 확정된 것이 아니라 예제로 검증하며 계속 바뀌는 중입니다.
> 안정된 릴리스가 아니라 진행 중인 설계 실험으로 봐주세요.

SPP(.md)는 프로그램을 직접 실행하기 위한 언어가 아니라, AI(Claude, GPT 등)에게
"무엇을 만들어야 하는지"를 모호함 없이 전달하기 위한 **명세 기술 언어**입니다.

- SPP 파일은 컴파일러가 아니라 **AI가 읽고 이해**합니다.
- AI는 `SPEC.md`(언어 정의서)만 보고 `.md` 파일을 실제 실행 가능한 프로그램(원하는 언어/스택)으로
  번역(트랜스파일)합니다.
- 문법은 자연어와 가벼운 구조화 마크업을 섞은 형태로, 사람이 쓰기 쉽고 AI가 해석하기 쉬운 균형을 목표로 합니다.

## 구성

- [`SPEC.md`](SPEC.md) — SPP 언어 정의서. 문법, 섹션 구조, 표기법, 그리고 **AI 트랜스파일 지침**을 담고 있습니다.
  이 저장소에서 가장 중요한 문서입니다.
- [`examples/`](examples/) — SPP로 작성된 예제 명세 파일들.
- [`std/`](std/) — 표준 라이브러리. 아래 [표준 라이브러리](#표준-라이브러리) 참고.
- [`tests/`](tests/) — SPEC.md·std가 실제로 트랜스파일 가능한지 Python·C++
  참조 구현으로 검증하는 테스트.

## 빠른 사용법 (AI에게)

1. `SPEC.md` 전체를 읽는다.
2. 대상 `.md` 파일을 읽는다.
3. `SPEC.md`의 "AI 트랜스파일 지침"을 따라 실행 가능한 프로그램으로 번역한다.
4. `.md` 파일의 `Examples` 섹션이 실제로 통과하는지 검증한다.

## 표준 라이브러리

전체 목록과 각 패키지 설명은 [`std/package.md`](std/package.md)에 SPP 명세
형식으로 정리되어 있습니다. 폴더 구성만 간단히 보면:

| 폴더 | 내용 |
|---|---|
| [`std/`](std/) (루트) | 콘솔 입출력 — `stdout`/`stderr`/`stdin` |
| [`std/text/`](std/text/) | 문자열·정규식·JSON |
| [`std/collections/`](std/collections/) | `list`/`Set`/`Queue`/`Stack`/`Dictionary` |
| [`std/concurrency/`](std/concurrency/) | 원자적 값·잠금·스레드·스레드 안전 컬렉션 |
| [`std/io/`](std/io/) | 파일·디렉터리 |
| [`std/system/`](std/system/) | 예외·수학·시간·환경 변수·프로세스·디버깅 등 (.NET `System`에 대응) |
| [`std/net/`](std/net/) | URI·DNS·TCP·UDP·HTTP (.NET `System.Net`에 대응) |
| [`std/cloud/`](std/cloud/) | 클라우드 인프라 — 오브젝트 스토리지·CDN·NoSQL DB·큐·Pub/Sub·서버리스 함수·시크릿·관측성·IAM·VPC 추상 계약 + AWS/GCP/Azure `kind: native` 구현 |
| [`std/ui/`](std/ui/) | GUI 위젯·캔버스·메뉴·텍스트 상자·파일 대화 상자 |
| [`std/graphics/`](std/graphics/) | OpenGL 렌더링 — 레거시 즉시 모드(1.x)와 셰이더·버텍스 버퍼 기반 현대적 렌더링(3.3+) 둘 다 (`kind: native`, 플랫폼 무관) |
| [`std/audio/`](std/audio/) | OpenAL 위치 기반 효과음 (`kind: native`, 플랫폼 무관) |
| [`std/windows/`](std/windows/) · [`std/linux/`](std/linux/) · [`std/macos/`](std/macos/) | OS별 API (레지스트리, Direct3D 9/11, DirectSound, 네이티브 대화 상자 등) |
| [`std/web/`](std/web/) | 브라우저 API — DOM/Canvas/WebGL2/Web Audio/localStorage·IndexedDB (`platform: web`) |
| [`std/js/`](std/js/) | JS/TS 생태계 서드파티 라이브러리 — axios (`kind: native`) |
| [`std/posix/`](std/posix/) | Linux·macOS 공통(POSIX) API |
| [`std/native/`](std/native/) | C/C++ 표준 라이브러리 자체에 대한 실체 명세 |

## 상태

초기 설계 단계 (SPP 0.1). 문법과 지침은 실제 예제로 검증하며 계속 다듬어갑니다.
