#!specpp 0.1

# Meta

- name: std/io/file
- version: 0.1.0
- description: 파일을 읽고 쓰고, 경로 문자열을 다루는 수단.

# Intent

[`stdout`](../stdout.md)/[`stdin`](../stdin.md)이 콘솔과의 입출력이라면, 이
패키지는 디스크의 파일과의 입출력이다. 설정 저장, 로그 기록, 데이터 불러오기처럼
실행 사이에 상태를 남겨야 하는 모든 상황에 쓰인다.

# Domain

## Class: Path

메서드:
[Static]
- combine(parts: list<string>) -> string
  설명: 경로 조각들을 타겟 플랫폼의 구분자로 이어붙인다 (예: `["a", "b.txt"]` →
  `"a/b.txt"`).
[Static]
- fileName(path: string) -> string
  설명: 경로의 마지막 구성 요소(파일명)를 반환한다.
[Static]
- extension(path: string) -> string?
  설명: 파일명의 확장자(마지막 `.` 뒤)를 반환한다. 없으면 null.
[Static]
- directoryName(path: string) -> string
  설명: 마지막 구성 요소를 뺀 나머지 디렉터리 경로를 반환한다.

## Class: File

메서드:
[Static]
- exists(path: string) -> boolean
[Static]
- readAllText(path: string) -> string
  설명: 파일 전체를 UTF-8 텍스트로 읽어 반환한다. 파일이 없으면 오류를 낸다.
[Static]
- writeAllText(path: string, content: string) -> void
  설명: content로 파일을 덮어쓴다. 파일이 없으면 새로 만든다. 상위 디렉터리가
  없으면 오류를 낸다.
[Static]
- appendText(path: string, content: string) -> void
  설명: 파일 끝에 content를 이어 쓴다. 파일이 없으면 새로 만든다.
[Static]
- delete(path: string) -> void
  설명: 파일을 삭제한다. 없으면 아무 일도 하지 않는다.
[Static]
- readAllBytes(path: string) -> bytes
[Static]
- writeAllBytes(path: string, content: bytes) -> void

# Interface

## Library

다른 패키지는 `File.readAllText(path)`, `File.writeAllText(path, text)`처럼
클래스 이름으로 바로 씁니다.

# Constraints

- 타겟 언어의 네이티브 파일 I/O(C++ `<fstream>`, Python `open`/`pathlib`, Java
  `java.nio.file.Files`, C# `System.IO.File`/`Path` 등)에 매핑한다.
- 경로 구분자(`/` vs `\`)는 `Path.combine`을 거치면 타겟 플랫폼에 맞게 처리된다
  — 호출하는 쪽이 직접 `/`나 `\`를 문자열에 하드코딩하지 않는 것을 권장한다.

# Examples

## 예제: 쓰고 다시 읽기

호출 (순서대로): `File.writeAllText("a.txt", "hi")`, `File.readAllText("a.txt")`

기대 동작: 두 번째 호출은 `"hi"`를 반환한다.

## 예제: 없는 파일 읽기는 오류

호출: `File.readAllText("없는파일.txt")` (해당 경로에 파일이 없는 상태)

기대 동작: 오류가 발생한다 (빈 문자열을 조용히 반환하지 않는다).

# Open Points

- 파일 잠금, 스트리밍(전체를 메모리에 올리지 않고 부분적으로 읽고 쓰는 것)은
  이 버전의 범위 밖이다.
