#!specpp 0.1

# Meta

- name: std/system/environment
- version: 0.1.0
- description: 실행 환경 정보(명령행 인자, 환경 변수, 종료 코드)에 대한 접근.

# Intent

프로그램이 자기 자신이 어떻게 실행되었는지(어떤 인자로, 어떤 환경 변수 아래)
알아야 하거나, 특정 종료 코드로 스스로를 끝내야 할 때 쓴다.

# Domain

## Class: Environment

메서드:
[Static]
- args() -> list<string>
  설명: 프로그램 실행 시 전달된 명령행 인자 목록을 반환한다 (실행 파일 자신의
  이름/경로는 포함하지 않는다).
[Static]
- getVariable(name: string) -> string?
  설명: 환경 변수 name의 값을 반환한다. 설정되어 있지 않으면 null.
[Static]
- setVariable(name: string, value: string) -> void
  설명: 이 프로세스(와 이후 만들어지는 자식 프로세스)에 한해 환경 변수를
  설정한다.
[Static]
- exit(code: int) -> void
  설명: 프로그램을 즉시 code 종료 코드로 끝낸다. 이 호출 이후의 코드는 실행되지
  않는다.

# Interface

## Library

다른 패키지는 `Environment.args()`, `Environment.getVariable("PATH")`처럼
클래스 이름으로 바로 씁니다.

# Constraints

- 타겟 언어의 네이티브 접근 수단(C++ `argc`/`argv`, `getenv`, Python `sys.argv`,
  `os.environ`, Java `args`, `System.getenv`, C# `Environment.GetCommandLineArgs`
  등)에 매핑한다.

# Examples

## 예제: 설정되지 않은 환경 변수

호출: `Environment.getVariable("SPP_DOES_NOT_EXIST")`

기대 동작: `null`을 반환한다.

# Open Points

- 환경 변수 전체 목록 열거는 이 버전의 범위 밖이다 — 이름을 아는 특정 변수만
  조회한다.
