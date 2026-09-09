#!specpp 0.1

# Meta

- name: std/linux/appdirs
- version: 0.1.0
- description: XDG 기준 디렉터리 규약에 따라 앱 설정·캐시·데이터 경로를 계산한다.
- platform: linux -> fallback: std/macos/appdirs.md

# Intent

Linux(및 다른 XDG 규약을 따르는 유닉스 계열)에서 [`std/system/appdirs.md`](../system/appdirs.md)의
`AppDirectories` 계약을 구현한다.

# Domain

## Class: LinuxAppDirectories implements AppDirectories

메서드:
- configHome(appName: string) -> string
  설명: 환경 변수 `XDG_CONFIG_HOME`이 있으면 `그 값/appName`, 없으면
  `~/.config/appName`을 반환한다.
- cacheHome(appName: string) -> string
  설명: `XDG_CACHE_HOME`이 있으면 `그 값/appName`, 없으면 `~/.cache/appName`을
  반환한다.
- dataHome(appName: string) -> string
  설명: `XDG_DATA_HOME`이 있으면 `그 값/appName`, 없으면
  `~/.local/share/appName`을 반환한다.

(디렉터리를 미리 만들어 둔다는 불변식은 [`AppDirectories`](../system/appdirs.md)
공통 계약에 있습니다 — 여기서는 되풀이하지 않습니다.)

# Interface

## Library

다른 패키지는 `LinuxAppDirectories().configHome("todo-cli")`처럼 씁니다.

# Constraints

- [XDG Base Directory 규약](https://specifications.freedesktop.org/basedir-spec/)의
  기본값을 따른다. 환경 변수 조회는 [`std/system/environment.md`](../system/environment.md)로,
  경로 조립은 [`std/io/file.md`](../io/file.md)의 `Path`로 구현한다.

# Examples

## 예제: 환경 변수가 없을 때 기본값

전제: `XDG_CONFIG_HOME` 환경 변수가 설정되어 있지 않다.

호출: `LinuxAppDirectories().configHome("todo-cli")`

기대 동작: 사용자 홈 디렉터리 아래 `.config/todo-cli`를 반환한다 (없으면 만든
뒤 반환한다).

# Open Points

- 시스템 전역(`/etc/xdg` 등) 설정 위치 조회는 이 버전의 범위 밖이다 — 사용자
  개인 위치만 다룬다.
