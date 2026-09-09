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
- specRef: string? — 이 오류를 일으킨 조건이 적힌 스펙 위치(SPEC.md 4.7절의
  추적 주석과 같은 `패키지 경로#섹션.이름` 형식). **스펙 작성자가 채우는 값이
  아니라, AI가 코드를 생성할 때 자동으로 주입하는 값**이다 (아래 Constraints
  참조). 없으면(null) 이 값을 채울 수 없었다는 뜻이다.

생성자:
- Exception(message: string)
  설명: message를 그대로 저장한다. specRef는 null로 둔다.
- Exception(message: string, specRef: string)
  설명: message와 specRef를 그대로 저장한다. 이 오버로드는 **AI가 생성하는
  코드가 자동으로 쓰는 것**이지, 스펙 작성자가 절차·`예외:` 규칙에 직접 이
  문자열을 적으라는 뜻이 아니다.

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
- Feature/Method의 `예외:` 규칙으로부터 오류를 던지는 코드를 생성할 때는,
  AI가 **항상** 두 번째 생성자로 `specRef`를 채운다 (SPEC.md 4.7절) — 지금
  번역하고 있는 Method/Feature가 무엇인지는 AI가 이미 알고 있으므로, 별도
  지시 없이도 코드 생성 시점에 자동으로 채워 넣는다. 스펙 작성자가 이 값을
  직접 쓸 필요는 없다.

# Examples

## 예제: 하위 오류 타입 만들기

```markdown
## Class: Todo.ValidationError extends Exception
```

호출: `throw ValidationError("title은 필수입니다")`

기대 동작: `.message`가 `"title은 필수입니다"`인 예외가 발생하고, 처리되지 않으면
프로그램 실행이 중단된다.

## 예제: AI가 생성한 코드는 스펙 위치를 자동으로 담는다

전제: 위 `Todo.ValidationError`가 `examples/todo-cli.md`의 `Behavior.할 일
추가` Feature에 적힌 `예외:` 규칙("title이 비어있으면...")으로부터 생성된
것이다. 스펙에는 `specRef` 문자열이 어디에도 등장하지 않는다.

AI가 생성하는 코드(의사코드): `throw ValidationError("title은 필수입니다",
"examples/todo-cli.md#Behavior.할 일 추가")`

기대 동작: `.specRef`가 `"examples/todo-cli.md#Behavior.할 일 추가"`인 예외가
발생한다 — 이 값으로 오류를 일으킨 규칙이 적힌 스펙 위치를 바로 찾을 수 있다.
이 문자열은 AI가 트랜스파일 시점에 자동으로 채운 것이다.

# Open Points

- 스택 트레이스, 원인 예외 체이닝(inner exception) 등 진단 정보는 이 버전의
  범위 밖이다 — 필요하면 타겟 언어의 관용적인 방식을 그대로 노출해도 된다.
