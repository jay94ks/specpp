#!specpp 0.1

# Meta

- name: std/io/directory
- version: 0.1.0
- description: 디렉터리(폴더)를 만들고 지우고 목록을 조회하는 수단.

# Intent

[`std/io/file`](file.md)이 파일 하나를 다룬다면, 이 패키지는 그 파일들이 담긴
디렉터리 자체를 다룬다.

# Domain

## Class: Directory

메서드:
[Static]
- exists(path: string) -> boolean
[Static]
- create(path: string) -> void
  설명: path에 디렉터리를 만든다. 중간 경로가 없으면 함께 만든다. 이미
  존재하면 아무 일도 하지 않는다.
[Static]
- delete(path: string, recursive: boolean) -> void
  설명: 디렉터리를 삭제한다. recursive가 false인데 안이 비어있지 않으면
  오류를 낸다. recursive가 true면 내용물까지 모두 지운다.
[Static]
- listFiles(path: string) -> list<string>
  설명: path 바로 아래(하위 디렉터리 재귀 없이)에 있는 파일·디렉터리 경로
  목록을 반환한다.

# Interface

## Library

다른 패키지는 `Directory.create(path)`, `Directory.listFiles(path)`처럼
클래스 이름으로 바로 씁니다.

# Constraints

- 타겟 언어의 네이티브 디렉터리 조작(C++ `<filesystem>`, Python
  `os`/`pathlib`, Java `java.nio.file.Files`, C# `System.IO.Directory` 등)에
  매핑한다.

# Examples

## 예제: 만들고 존재 확인

호출 (순서대로): `Directory.create("out")`, `Directory.exists("out")`

기대 동작: 두 번째 호출은 `true`를 반환한다.

## 예제: 목록 조회

호출: `Directory.create("out")`, `File.writeAllText("out/a.txt", "")`,
`Directory.listFiles("out")`

기대 동작: `"out/a.txt"`를 포함한 list를 반환한다.

# Open Points

- 심볼릭 링크, 권한(permission) 조회·설정은 이 버전의 범위 밖이다.
