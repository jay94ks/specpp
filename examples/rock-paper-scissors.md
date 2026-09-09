#!specpp 0.1

# Meta

- name: rock-paper-scissors
- version: 0.1.0
- description: 컴퓨터를 상대로 하는 가위바위보 GUI 게임.
- target: 미지정 — AI가 상황에 맞게 제안 (GUI가 있어야 하므로 4.2절 참조).

# Intent

버튼을 클릭해서 컴퓨터와 가위바위보를 겨루는 간단한 GUI 게임이 필요하다.
콘솔이 아니라 창을 띄우고 마우스로 조작하는 형태여야 한다.

# Domain

## Class: Rps.RoundResult

멤버:
- playerChoice: enum(Rock | Paper | Scissors)
- computerChoice: enum(Rock | Paper | Scissors)
- outcome: enum(Win | Lose | Draw) — 플레이어 기준 결과.

생성자:
- RoundResult(playerChoice: enum(Rock | Paper | Scissors), computerChoice: enum(Rock | Paper | Scissors), outcome: enum(Win | Lose | Draw))

## Class: Rps.Game

멤버:
- playerScore: int — 기본값 0.
- computerScore: int — 기본값 0.

생성자:
- Game()
  설명: 컴퓨터가 무작위로(Rock/Paper/Scissors 각각 동일한 확률로) 고르도록
  한다.
- Game(computerChooser: () -> enum(Rock | Paper | Scissors))
  설명: 컴퓨터의 선택을 고르는 방법을 직접 지정한다 — 자동 테스트에서 결과를
  고정하고 싶을 때 쓴다.

메서드:
- play(playerChoice: enum(Rock | Paper | Scissors)) -> Rps.RoundResult
  설명: 컴퓨터의 선택을 정하고, 가위바위보 규칙에 따라 승패를 가른 뒤 점수를
  갱신하고 결과를 반환한다.
  절차:
  1. computerChooser()를 호출해 컴퓨터의 선택을 얻는다.
  2. 규칙에 따라 판정한다 — Rock은 Scissors를 이기고, Scissors는 Paper를
     이기고, Paper는 Rock을 이긴다. 두 선택이 같으면 무승부다.
  3. 플레이어가 이겼으면 playerScore를, 컴퓨터가 이겼으면 computerScore를
     1 늘린다. 무승부면 둘 다 그대로 둔다.
  4. playerChoice, computerChoice, outcome을 담은 RoundResult를 만들어
     반환한다.

불변식:
- playerScore, computerScore는 절대 음수가 되지 않는다.

test_required Rps.Game {
  - Rock 대 Scissors, Scissors 대 Paper, Paper 대 Rock은 항상 앞의 것이
    이긴다.
  - 같은 선택끼리는 항상 무승부이고, 이 경우 점수는 바뀌지 않는다.
}

# Behavior

## Feature: 한 라운드 진행

설명: 사용자가 화면의 바위/보/가위 버튼 중 하나를 누르면 한 라운드를 겨룬다.

입력:
- choice: enum(Rock | Paper | Scissors) — 사용자가 누른 버튼.

절차:
1. `Rps.Game.play(choice)`를 호출한다.
2. 결과 Label에 승/패/무와 두 선택을 사람이 읽을 문구로 표시한다 (예: "당신:
   바위 / 컴퓨터: 가위 — 이겼습니다!").
3. 점수 Label을 최신 점수로 갱신한다 (예: "당신 3 : 2 컴퓨터").

출력:
- 성공 시: `Rps.RoundResult`.

예외:
- 없음.

# Interface

## GUI

[`std/ui/widgets.md`](../std/ui/widgets.md) 기반으로 창 하나에 다음을
배치한다.

| 위젯 | 역할 |
|---|---|
| Button "✊ 바위" | `Behavior.한 라운드 진행`을 `choice = Rock`으로 실행 |
| Button "✋ 보" | `Behavior.한 라운드 진행`을 `choice = Paper`로 실행 |
| Button "✌️ 가위" | `Behavior.한 라운드 진행`을 `choice = Scissors`로 실행 |
| Label (결과) | 가장 최근 라운드의 결과 문구 표시 |
| Label (점수) | 누적 점수 표시 |

세 버튼의 `onClick` 핸들러가 각각 `Behavior.한 라운드 진행`을 실행하고, 그
결과로 두 Label을 갱신합니다. `Rps.Game`은 창이 열릴 때 `Game()`(기본
생성자, 무작위 컴퓨터)으로 한 번만 만들어 재사용합니다.

# Constraints

- GUI가 없는 실행 환경에서는 이 게임을 실행할 수 없다 —
  [`std/ui/widgets.md`](../std/ui/widgets.md)의 Constraints를 그대로 따른다.
- 라운드 사이에 애니메이션·지연 연출은 요구하지 않는다 — 버튼을 누르면 결과가
  즉시 반영되면 된다.

# Examples

## 예제: 플레이어가 이긴다

전제: `computerChooser`가 항상 `Scissors`를 반환한다.

호출: `game.play(Rock)`

기대 동작: `outcome`은 `Win`이다. `playerScore`가 1 증가하고 `computerScore`는
그대로다.

## 예제: 플레이어가 진다

전제: `computerChooser`가 항상 `Paper`를 반환한다.

호출: `game.play(Rock)`

기대 동작: `outcome`은 `Lose`이다. `computerScore`가 1 증가하고
`playerScore`는 그대로다.

## 예제: 비긴다

전제: `computerChooser`가 항상 `Rock`을 반환한다.

호출: `game.play(Rock)`

기대 동작: `outcome`은 `Draw`이다. 두 점수 모두 그대로다.

## 예제: 여러 라운드에 걸쳐 점수가 누적된다

전제: `computerChooser`가 항상 `Scissors`를 반환한다.

호출 (순서대로): `game.play(Rock)`, `game.play(Rock)`

기대 동작: 두 라운드 모두 `Win`이다 (Rock은 항상 Scissors를 이긴다). 두 번의
호출 뒤 `playerScore`는 2다.

# Open Points

- 세 판 먼저 이기면 종료 같은 게임 종료 조건은 이 버전에 없다 — 점수는
  계속 누적되기만 한다.
- 효과음, 애니메이션은 이 버전의 범위 밖이다.
