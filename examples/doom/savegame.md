#!specpp 0.1

# Domain

원본 `p_saveg.h`/`p_saveg.c`, `g_game.c`의 저장/불러오기에 대응한다.

## Class: Doom.SaveGame

멤버:
- description: string — 저장 슬롯에 보여줄 설명(예: "E1M3, 체력 80%").
- mapName: string
- player: Doom.Player
- activeSpecials: list<Doom.SectorMover> — [`specials.md`](specials.md)
  참조. 저장 시점에 진행 중이던 문/바닥/플랫폼 등.
- lightFlashes: list<Doom.LightFlash>
- otherActors: list<Doom.Actor> — 플레이어를 뺀 나머지(몬스터, 아이템,
  발사체 등).
- killCount: int
- itemCount: int
- secretCount: int
- levelTimeTics: int

메서드:
[Static]
- Save(game: Doom.Game, description: string) -> Doom.SaveGame
  설명: `game`(`game.md` 참조)의 현재 상태를 스냅샷으로 만든다.
- restore() -> Doom.Game
  설명: 이 스냅샷으로부터 `game.md`의 `Doom.Game`을 다시 만든다 —
  `mapName`으로 맵을 다시 불러온 뒤, `player`/`otherActors`/
  `activeSpecials`/`lightFlashes`/카운터들을 그대로 덮어쓴다.

test_required Doom.SaveGame {
  - `Save`한 직후 `restore()`한 결과는, 그 사이에 아무 tic도 진행하지
    않았다면 원래 `Doom.Game`과 (플레이어 위치·체력·탄약·점수·진행 중인
    특수 효과까지) 관측 가능한 모든 상태가 같다.
}

# Interface

## Library

`game.md`의 `Feature.저장`/`Feature.불러오기`가 이 클래스를 씁니다.

# Constraints

- 저장 파일의 정확한 이진 포맷(원본은 각 필드를 순서대로 이어붙인
  자체 이진 포맷을 쓴다)은 규정하지 않는다 — [`std/text/json.md`](../../std/text/json.md)로
  직렬화하거나, 원본과 같은 이진 포맷을 쓰거나 AI가 선택한다.
- 자동 저장(맵 시작 시 이어하기용)은 다루지 않는다 — 사용자가 명시적으로
  저장할 때만 만든다.

# Open Points

- 여러 저장 슬롯 관리(목록 보여주기, 덮어쓰기 확인)는
  [`std/ui/filedialog.md`](../../std/ui/filedialog.md)를 참고해 구현하는
  것을 권장하며, 이 파일에서 세부 UI까지 규정하지 않는다.
