#!specpp 0.1

# Domain

원본 `wi_stuff.h`/`wi_stuff.c`(인터미션 — 스테이지 클리어 뒤 통계 화면)와
`f_finale.h`/`f_finale.c`(에피소드 종료 텍스트/캐스트 크롤)에 대응한다.

## Class: Doom.Intermission

멤버:
- finishedMapName: string
- nextMapName: string?
- killPercent: int — 0~100.
- itemPercent: int — 0~100.
- secretPercent: int — 0~100.
- parTimeTics: int — 이 맵의 기준(par) 시간.
- playerTimeTics: int — 실제로 걸린 시간.

메서드:
- render(renderer: Doom.Renderer.Backend) -> void
  설명: "MAP01 완료" 같은 제목과, 위 세 퍼센트·시간을 숫자가 하나씩
  올라가는 애니메이션으로 보여준다 — 퍼센트 막대 같은 도형은
  [`Doom.Renderer.Backend.drawUIShapes`](render.md)로, 제목·숫자 글자는
  [`Doom.Renderer.Backend.drawUIText`](render.md)로 그린다(원본
  특유의 카운트업 연출).

## Class: Doom.Finale

멤버:
- text: string — 에피소드/게임 종료 시 보여줄 줄글(원본은 타자기처럼
  한 글자씩 나타난다).
- castOfCharacters: list<string>? — 마지막 에피소드 클리어 시 등장하는
  몬스터 이름들의 순차 소개("캐스트 크롤").

# Behavior

## Feature: 스테이지 클리어 전환

설명: `game.md`의 `Feature.맵 종료 조건`이 만족되면 실행된다.

절차:
1. 현재 맵에서 처치한 몬스터 수·전체 몬스터 수, 획득한 아이템·전체
   아이템 수, 발견한 비밀 구역·전체 비밀 구역 수로 세 퍼센트를 계산한다.
2. `Doom.Intermission`을 만들어 보여주고, 숫자를 0에서 실제 값까지
   빠르게 세는 연출을 재생한다.
3. 확인 입력을 받으면 `nextMapName`이 있으면 그 맵을
   `game.md`의 `Feature.맵 불러오기`로 시작하고, 없으면(에피소드 마지막
   맵) `Feature.에피소드 종료 연출`로 넘어간다.

## Feature: 에피소드 종료 연출

절차:
1. `Doom.Finale.text`를 한 글자씩 나타나는 효과로 보여준다.
2. 마지막 에피소드라면, 이어서 등장한 몬스터 종류를 하나씩 화면
   가운데에서 걸어 나오게 하며 이름을 보여주는 `castOfCharacters` 연출을
   재생한다.

# Constraints

- 정확한 배경 그림, 텍스트 내용(에피소드별 스토리 문구)은 옮기지 않았다
  — 구조만 정의한다.

# Open Points

- 카운트업 애니메이션의 정확한 속도, 보너스 사운드 타이밍은 다루지
  않는다.
