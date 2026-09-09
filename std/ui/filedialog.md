#!specpp 0.1

# Meta

- name: std/ui/filedialog
- version: 0.1.0
- description: 파일을 열거나 저장할 위치를 사용자에게 직접 고르게 하는 네이티브 대화 상자.

# Intent

"열기"/"다른 이름으로 저장" 메뉴처럼, 파일 시스템의 어디를 읽고 쓸지
사용자가 직접 탐색해서 고르게 해야 할 때 쓴다.
[`std/io/file.md`](../io/file.md)가 "이미 아는 경로"를 읽고 쓰는 것이라면,
이 패키지는 그 경로 자체를 사용자에게 물어보는 것이다.

# Domain

## Class: FileDialog

메서드:
[Static]
- showOpen(title: string, filters: list<string>) -> string?
  설명: 파일 열기 대화 상자를 띄운다. filters는 `"텍스트 문서 (*.txt)"`처럼
  사람이 읽을 필터 설명의 목록이다. 사용자가 파일을 고르면 그 절대 경로를,
  취소하면 null을 반환한다. 대화 상자가 닫힐 때까지 호출한 쪽을 블로킹한다.
[Static]
- showSave(title: string, filters: list<string>, suggestedName: string) -> string?
  설명: 파일 저장 대화 상자를 띄운다. suggestedName은 기본으로 채워질
  파일명이다. 사용자가 위치를 고르면 그 절대 경로를, 취소하면 null을
  반환한다. 이미 존재하는 파일을 골랐을 때 덮어쓸지 확인하는 것은 이
  대화 상자 자체의 기본 동작이다(별도로 구현할 필요 없다).

# Interface

## Library

다른 패키지는 `FileDialog.showOpen("열기", ["텍스트 문서 (*.txt)", "모든
파일 (*.*)"])`처럼 클래스 이름으로 바로 씁니다. 반환값이 null이면 사용자가
취소한 것이므로 이어지는 동작(파일 읽기 등)을 하지 않습니다.

# Constraints

- 타겟 플랫폼의 네이티브 파일 선택 대화 상자(Windows의 공용 대화 상자
  `GetOpenFileNameW`/`GetSaveFileNameW` — [`std/windows/win32.md`](../windows/win32.md)
  참조, Python `tkinter.filedialog` 등)에 매핑한다.
- 콘솔 전용(GUI 없는) 환경에서는 쓸 수 없다 — [`std/ui/widgets.md`](widgets.md)와
  같은 제약을 따른다.

# Examples

## 예제: 취소하면 null

호출: `FileDialog.showOpen("열기", ["모든 파일 (*.*)"])`. 사용자가 "취소"를
누른다.

기대 동작: `null`을 반환한다.

# Open Points

- 여러 파일을 한 번에 선택하는 것(다중 선택)은 이 버전의 범위 밖이다.
