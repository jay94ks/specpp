#!specpp 0.1

# Meta

- name: std/system/appdirs
- version: 0.1.0
- description: 앱 설정·캐시·데이터를 저장할 표준 위치를 가리키는 추상 계약.

# Intent

설정 파일이나 캐시를 어디에 둬야 하는지는 운영체제마다 관례가 다르다
(Windows는 `%APPDATA%`, Linux는 XDG 기준 디렉터리, macOS는 `~/Library/...`).
이 인터페이스는 "이런 위치들이 필요하다"는 것만 추상적으로 정의하고, 실제
경로 규칙은 OS별 구현([`std/linux/appdirs.md`](../linux/appdirs.md),
[`std/macos/appdirs.md`](../macos/appdirs.md))에 맡긴다.
[`std/windows/registry.md`](../windows/registry.md)가 Windows에서의 설정 저장
방식이라면, 이 인터페이스는 파일 기반 설정 저장이 필요한 Linux/macOS(그리고
필요하면 Windows도)를 위한 것이다.

# Domain

## Interface: AppDirectories

메서드:
- configHome(appName: string) -> string
  설명: appName의 설정 파일을 둘 디렉터리 경로를 반환한다.
- cacheHome(appName: string) -> string
  설명: appName의 캐시(다시 만들 수 있는, 없어져도 되는 데이터)를 둘 디렉터리
  경로를 반환한다.
- dataHome(appName: string) -> string
  설명: appName의 영구 데이터를 둘 디렉터리 경로를 반환한다.

불변식:
- 세 메서드 모두, 반환하는 디렉터리가 아직 없으면 만들어 놓고 반환한다 —
  호출한 쪽이 별도로 디렉터리 존재를 확인·생성할 필요가 없다. 이 불변식은
  모든 구현([`LinuxAppDirectories`](../linux/appdirs.md),
  [`MacAppDirectories`](../macos/appdirs.md) 등)에 공통으로 적용된다.

# Interface

## Library

프로그램은 실행되는 OS에 맞는 구현([`LinuxAppDirectories`](../linux/appdirs.md)
또는 [`MacAppDirectories`](../macos/appdirs.md))을 골라 씁니다. 여러 OS를
대상으로 한다면 1.1절의 "제약 조건" 참조로 `AppDirectories`를 요구 사항만
적어두고, AI가 대상 OS에 맞는 구현을 자동으로 골라 연결하게 할 수도 있습니다.

# Open Points

- 이 인터페이스의 Windows 구현(`%APPDATA%`/`%LOCALAPPDATA%` 기반)은 아직
  작성되지 않았다 — 필요해지면 [`std/windows/`](../windows/) 아래에 추가한다.
