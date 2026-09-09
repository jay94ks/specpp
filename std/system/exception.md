#!specpp 0.1

# Meta

- name: std/system/exception
- version: 0.1.0
- description: 모든 오류 타입의 공통 기반이 되는 예외 클래스.

# Intent

`ValidationError`, `NotFoundError`처럼 명세 전반에서 자연스럽게 써온 오류들이
공통으로 가져야 할 최소한의 형태(오류 메시지)를 표준화한다. 새 오류 타입을 만들
때마다 처음부터 다시 정의하지 않고, 이 클래스를 상속(`extends`, 3.4절)해서 쓴다.

# Domain

## Class: Exception

멤버:
- message: string — 오류 내용을 사람이 읽을 수 있게 설명하는 메시지.

생성자:
- Exception(message: string)
  설명: message를 그대로 저장한다.

# Interface

## Library

다른 패키지는 이 클래스를 `extends`해서 자신만의 오류 타입을 만듭니다.

```markdown
## Class: Todo.ValidationError extends Exception
```

# Constraints

- 타겟 언어의 네이티브 예외 체계(C++ `std::exception`, Python `Exception`,
  Java `RuntimeException`, JavaScript `Error` 등)를 상속·구현해서 매핑한다.
  `throw`/`raise`처럼 그 언어의 관용적인 예외 발생·전파 방식을 그대로 쓴다.

# Examples

## 예제: 하위 오류 타입 만들기

```markdown
## Class: Todo.ValidationError extends Exception
```

호출: `throw ValidationError("title은 필수입니다")`

기대 동작: `.message`가 `"title은 필수입니다"`인 예외가 발생하고, 처리되지 않으면
프로그램 실행이 중단된다.

# Open Points

- 스택 트레이스, 원인 예외 체이닝(inner exception) 등 진단 정보는 이 버전의
  범위 밖이다 — 필요하면 타겟 언어의 관용적인 방식을 그대로 노출해도 된다.
