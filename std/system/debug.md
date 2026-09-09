#!specpp 0.1

# Meta

- name: std/system/debug
- version: 0.1.0
- description: 개발 중에 조건을 검사하고, 스펙 위치를 남기며 진단 메시지를 남기는 수단.

# Intent

`test_required`(3.9절)가 명세 시점에 지켜야 할 무결성 조건이라면, 이 패키지는
**실행 중에** 같은 조건을 검사하기 위한 것이다. 조건이 깨지면 프로그램을
멈추고, [`std/system/exception.md`](exception.md)의 `specRef`와 같은 방식으로
"이 조건은 스펙 어디에 적혀 있었는가"를 함께 남겨서 SPEC.md 4.7절의 디버깅
흐름(오류에서 멈추면 구현과 스펙 중 원하는 쪽으로 들어갈 수 있다)을 뒷받침한다.

# Domain

## Class: Debug

메서드:
[Static]
- assert(condition: boolean, message: string, specRef: string) -> void
  설명: condition이 false이면 프로그램을 멈추고 message와 specRef(4.7절 형식)를
  함께 보고한다. condition이 true이면 아무 일도 하지 않는다. **specRef는
  스펙 작성자가 채우는 인자가 아니다** — 불변식이 적힌 Class/Method를 AI가
  번역하며 이 호출을 생성할 때, 그 위치를 가리키는 값을 자동으로 채운다
  (SPEC.md 4.7절, [`Exception.specRef`](exception.md)와 같은 원칙).
- assert(condition: boolean, message: string) -> void
  설명: `specRef` 없이 검사한다. 이 오버로드는 검사할 조건이 특정 스펙 위치에
  묶이지 않을 때(예: 코드 자체의 방어적 점검)를 위한 것이다.
[Static]
- trace(message: string) -> void
  설명: 진단용 메시지를 남긴다. 정상 실행 경로에 영향을 주지 않는다 — 릴리스
  빌드에서는 아무 일도 하지 않도록 꺼둘 수 있다(아래 Constraints 참조).

# Interface

## Library

스펙 작성자는 절차나 불변식에 "이 조건은 실행 중에도 확인한다"는 의도만
자연어로 적어두면 됩니다 — 예: `## Class: Todo.Task`의 불변식에 "title은
공백만으로 이루어질 수 없다"가 있으면, AI는 이를 실제 로직뿐 아니라
`Debug.assert(...)` 호출로도 반영할 수 있습니다. `specRef` 인자는 AI가
자동으로 채우므로, 작성자가 직접 `Debug.assert(...)`를 호출하는 코드를 쓸
필요는 없습니다.

# Constraints

- 타겟 언어의 네이티브 assert(C의 `assert()`, Python `assert`, Java
  `assert`, C++ `assert()`/`static_assert` 등)에 매핑한다. `trace`는 로깅
  프레임워크나 조건부 컴파일된 디버그 출력에 매핑한다.
- `assert` 실패 시 무엇을 하는지(프로그램 종료, 예외 발생, 디버거 중단)는
  타겟 언어·빌드 구성의 관용적인 방식을 따른다 — 이 계약은 "정상적으로 계속
  실행되면 안 된다"는 것만 보장한다.
- 릴리스(최적화) 빌드에서 `assert`/`trace`를 완전히 제거할지는 AI 재량이다 —
  단, 제거하면 그 조건이 실제로 성립하는지 다시는 확인되지 않는다는 뜻이므로,
  무결성에 중요한 조건이면 [`test_required`](../../SPEC.md)로 미리 검증해
  두는 것을 권장한다.

# Examples

## 예제: 조건이 깨지면 멈춘다

호출: `Debug.assert(false, "여기 오면 안 됨")`

기대 동작: 프로그램이 멈추고 `"여기 오면 안 됨"`을 보고한다.

## 예제: AI가 생성한 코드는 스펙 위치를 자동으로 담는다

전제: 위 호출이 `Todo.Task`의 불변식("title은 공백만으로 이루어질 수 없다")을
지키는지 실행 중에도 확인하기 위해 AI가 생성한 코드다.

AI가 생성하는 코드(의사코드): `Debug.assert(title.trim() != "", "title은
공백만으로 이루어질 수 없다", "examples/todo-cli.md#Domain.Class:Todo.Task")`

기대 동작: 조건이 깨지면 `specRef`로 그 불변식이 적힌 위치까지 바로 찾을 수
있다.

# Open Points

- 디버그/릴리스 같은 빌드 구성을 SPP 언어 차원에서 어떻게 선언할지는 아직
  정의되어 있지 않다 — 필요해지면 3.10절의 `platform`과 비슷한 방식으로
  추가한다.
