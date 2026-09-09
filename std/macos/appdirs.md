#!specpp 0.1

# Meta

- name: std/macos/appdirs
- version: 0.1.0
- description: macOS의 `~/Library` 규약에 따라 앱 설정·캐시·데이터 경로를 계산한다.
- platform: macos -> fallback: std/linux/appdirs.md

# Intent

macOS에서 [`std/system/appdirs.md`](../system/appdirs.md)의 `AppDirectories`
계약을 구현한다.

# Domain

## Class: MacAppDirectories implements AppDirectories

메서드:
- configHome(appName: string) -> string
  설명: `~/Library/Application Support/appName`을 반환한다 (macOS는 설정과
  데이터를 같은 위치에 두는 관례를 쓴다).
- cacheHome(appName: string) -> string
  설명: `~/Library/Caches/appName`을 반환한다.
- dataHome(appName: string) -> string
  설명: `~/Library/Application Support/appName`을 반환한다 (`configHome`과
  같다 — macOS 관례상 설정·데이터가 구분되지 않는다).

(디렉터리를 미리 만들어 둔다는 불변식은 [`AppDirectories`](../system/appdirs.md)
공통 계약에 있습니다 — 여기서는 되풀이하지 않습니다.)

# Interface

## Library

다른 패키지는 `MacAppDirectories().cacheHome("todo-cli")`처럼 씁니다.

# Constraints

- Apple의 [파일 시스템 프로그래밍 가이드](https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/)에서
  권장하는 위치를 따른다.

# Examples

## 예제: 설정과 데이터가 같은 위치

호출: `MacAppDirectories().configHome("todo-cli")`,
`MacAppDirectories().dataHome("todo-cli")`

기대 동작: 두 호출은 같은 경로를 반환한다.

# Open Points

- 샌드박스(App Sandbox) 환경에서의 컨테이너 경로 차이는 이 버전의 범위 밖이다.
