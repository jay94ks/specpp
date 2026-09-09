#!specpp 0.1

# Meta

- name: todo-cli
- version: 0.1.0
- description: 터미널에서 사용하는 간단한 할 일 관리 CLI. 할 일을 추가하고, 완료
  처리하고, 목록을 조회할 수 있다.
- target: 미지정 — AI가 상황에 맞게 제안
- tags: cli, todo, example

# Intent

할 일을 잊지 않고 터미널에서 빠르게 기록하고 확인하고 싶다. 별도 서버나 계정 없이,
로컬에서 혼자 쓰는 가벼운 도구를 원한다. GUI나 동기화 같은 부가 기능은 필요 없다.

# Domain

## Class: Todo.Task

멤버:
- id: int — 1부터 시작하는 순번. 프로그램 내에서 고유.
- title: string — 1~200자, 필수
- done: boolean — 기본값 false
- createdAt: datetime — 생성 시각, 자동 기록

메서드:
- markDone() → void
  설명: done을 true로 바꾼다. 이미 true이면 아무 일도 하지 않는다 (멱등).

불변식:
- title은 공백만으로 이루어질 수 없다 (trim 후 빈 문자열이면 안 됨).
- id는 삭제되어도 재사용되지 않는다.

test_required Todo.Task {
  - title이 공백만으로는 생성될 수 없다.
  - markDone()을 두 번 호출해도 예외 없이 done=true를 유지한다.
}

# Behavior

## Feature: 할 일 추가

설명: 새로운 Task를 만들어 목록에 추가한다.

입력:
- title: string (필수)

절차:
1. title을 trim한다.
2. trim 결과가 비어있으면 예외를 낸다.
3. 새 id를 발급한다 (지금까지 발급된 가장 큰 id + 1, 처음이면 1).
4. Task를 생성한다 (done=false, createdAt=현재 시각).
5. 저장소에 추가하고 저장한다.

출력:
- 성공 시: 생성된 Task의 id와 title

예외:
- title이 비어있거나 공백뿐이면 ValidationError("title은 필수입니다")

## Feature: 할 일 완료 처리

설명: 지정한 id의 Task를 완료 상태로 바꾼다.

입력:
- id: int (필수)

절차:
1. 저장소에서 해당 id의 Task를 찾는다.
2. 없으면 예외를 낸다.
3. Todo.Task.markDone()을 호출한다 (멱등이므로 이미 완료 상태여도 안전하다).
4. 저장한다.

출력:
- 성공 시: 완료 처리된 Task의 id와 title

예외:
- 해당 id가 없으면 NotFoundError("Task #{id}를 찾을 수 없습니다")

## Feature: 할 일 목록 조회

설명: 저장된 모든 Task를 조회한다.

입력:
- all: boolean (선택, 기본값 false) — true면 완료된 항목도 포함, false면 미완료만 표시

절차:
1. all=false면 done=false인 Task만 걸러낸다. all=true면 전체를 가져온다.
2. id 오름차순으로 정렬한다.

출력:
- Task 목록 (id, title, done 상태를 포함)

예외:
- 없음. 결과가 없으면 빈 목록을 반환한다.

# Interface

## CLI

| 명령 | 설명 | 매핑되는 Feature |
|---|---|---|
| `todo add <title>` | 할 일 추가 | 할 일 추가 |
| `todo done <id>` | 완료 처리 | 할 일 완료 처리 |
| `todo list` | 미완료 목록 조회 | 할 일 목록 조회 (all=false) |
| `todo list --all` | 전체 목록 조회 | 할 일 목록 조회 (all=true) |

출력 형식 (사람이 읽기 위한 텍스트):
- `add` 성공: `✔ 추가됨: <title> (#<id>)`
- `done` 성공: `✔ 완료: <title> (#<id>)`
- `list` 각 줄: `[<x 또는 공백>] #<id> <title>` — done이면 x, 아니면 공백
- 에러 발생 시: `✘ <에러 메시지>` 를 표준 에러로 출력하고 종료 코드 1

# Constraints

- 외부 네트워크 접근이나 계정/로그인 기능을 포함하지 않는다.
- 저장 데이터는 로컬 파일 시스템에만 보관한다 (구체적 형식은 Open Points 참조).
- 프로그램은 매 명령 실행마다 새로 시작되고 종료된다 (상주 프로세스 아님). 따라서
  상태는 실행 사이에 파일로 영속되어야 한다.

# Examples

## 예제: 빈 목록에서 시작해 할 일 추가

입력: `todo add "우유 사기"`

기대 출력:
```
✔ 추가됨: 우유 사기 (#1)
```

## 예제: 두 번째 할 일 추가 시 id 증가

입력 (순서대로 실행):
```
todo add "우유 사기"
todo add "청소하기"
```

기대 출력 (두 번째 명령 결과):
```
✔ 추가됨: 청소하기 (#2)
```

## 예제: 제목이 빈 문자열이면 실패

입력: `todo add "   "`

기대 결과: 종료 코드 1, 표준 에러에 `✘ title은 필수입니다` 출력

## 예제: 완료 처리 후 기본 목록에서 제외됨

입력 (순서대로 실행):
```
todo add "우유 사기"
todo done 1
todo list
```

기대 출력 (list 결과): 빈 목록 (아무 줄도 출력되지 않음)

## 예제: --all 옵션으로 완료 항목도 조회

입력 (예제 4에 이어서): `todo list --all`

기대 출력:
```
[x] #1 우유 사기
```

## 예제: 존재하지 않는 id 완료 처리 시 실패

입력: `todo done 999` (아직 해당 id의 Task가 없는 상태)

기대 결과: 종료 코드 1, 표준 에러에 `✘ Task #999를 찾을 수 없습니다` 출력

# Open Points

- 저장 형식: AI가 자유롭게 결정 (권장: 사용자 홈 디렉터리 아래 JSON 파일 하나,
  예: `~/.todo-cli/tasks.json`).
- 파일이 없을 때(첫 실행) 동작: 빈 목록으로 간주하고 자동 생성한다.
- 동시 실행(여러 프로세스가 동시에 파일에 쓰는 상황)은 이 버전에서 고려하지 않는다.
- 색상 출력 여부: AI 재량 (터미널이 지원하면 사용해도 되고, 안 해도 됨. 단 Examples의
  텍스트 자체는 그대로 포함되어야 한다).
