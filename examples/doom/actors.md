#!specpp 0.1

# Domain

## Namespace: Doom

원본의 `d_think.h`(thinker), `p_mobj.h`(mobj_t), `info.h`(state_t/mobjinfo_t
테이블)에 대응한다. DOOM의 모든 움직이는 객체(플레이어, 몬스터, 총알,
아이템, 문 등 — 원본은 "mobj"라고 부른다)는 **상태 기계**로 움직인다: 각
객체는 지금 어떤 `State`에 있는지만 알고, 그 State가 몇 tic 동안
지속되는지·다음에 어떤 State로 자동 전이하는지·전이할 때 무엇을 하는지를
정의한다. "몬스터 AI"는 사실 이 상태 기계 전이 규칙과, 상태에 진입할 때
실행되는 함수(action)의 조합일 뿐이다.

## Class: Doom.State

`state_t`에 대응한다.

멤버:
- sprite: string — 스프라이트 이름(4글자, 예: `"POSS"` = Zombieman).
- frame: int — 그 스프라이트의 몇 번째 프레임을 보여줄지.
- duration: int — 이 상태가 지속되는 tic 수(1tic = 1/35초). -1이면 무한 —
  `nextState`로 자동 전이하지 않는다(원본에서 최종 정지 프레임에 쓰는
  방식).
- action: ((Doom.Actor) -> void)? — 이 상태에 들어가는 순간 실행할 함수
  (예: 공격 판정, 총소리 재생, 다음 목표 찾기). 없으면 null.
- nextState: Doom.State? — duration이 다 지나면 자동으로 전이할 상태.
  null이면 그대로 액터가 사라진다(원본의 `S_NULL`).

## Class: Doom.MobjType

원본 `mobjinfo[]` 테이블의 한 행(`mobjinfo_t`)에 대응한다 — "이 종류의
객체는 원래 이렇게 생겼다"는 청사진이다.

멤버:
- name: string — 예: `"Zombieman"`.
- spawnHealth: int
- radius: float
- height: float
- speed: float — 초당 이동 속도.
- flags: int — `MF_SOLID`(충돌함), `MF_SHOOTABLE`(피해를 받음),
  `MF_NOGRAVITY`(중력 무시, 예: 떠다니는 총알), `MF_MISSILE`(같은 종족과는
  충돌하지 않는 발사체), `MF_COUNTKILL`(처치 수에 집계됨) 같은 비트
  플래그를 조합한다.
- spawnState: Doom.State — 생성 직후 상태.
- seeState: Doom.State? — 플레이어를 발견했을 때 전이할 상태(추격 애니메이션).
- painState: Doom.State? — 피해를 입었을 때(반드시 전이하지는 않는다 —
  `game.md`의 `Behavior.전투 판정` 참조).
- meleeState: Doom.State? — 근접 공격.
- missileState: Doom.State? — 원거리 공격.
- deathState: Doom.State? — 사망 애니메이션.

## Class: Doom.Actor

`mobj_t`에 대응한다. 실제로 맵 위에 존재하는 객체 하나(예: 실제로 생성된
Zombieman 한 마리)다.

생성자:
[Static]
- Spawn(type: Doom.MobjType, x: float, y: float, angle: float, sector: Doom.Map.Sector) -> Doom.Actor
  설명: type의 spawnHealth/radius/height 등을 그대로 물려받은 새 Actor를
  만들어 (x, y)에 놓고, `type.spawnState`로 `setState`한다.

멤버:
- type: Doom.MobjType
- x: float
- y: float
- z: float — 바닥으로부터의 높이(대개 `sector.floorHeight`와 같다).
- angle: float
- momX: float
- momY: float
- momZ: float — 다음 tic에 더해질 이동량(원본은 이렇게 관성을 흉내낸다).
- state: Doom.State
- ticsRemaining: int
- health: int
- flags: int — 처음엔 `type.flags`를 그대로 받지만, 게임 중 바뀔 수 있다
  (예: 죽으면 `MF_SOLID`가 꺼진다).
- target: Doom.Actor? — 지금 쫓고 있는(또는 공격하려는) 대상.
- sector: Doom.Map.Sector — 지금 서 있는 섹터
  ([`Doom.Map.BspNode.FindSubsector`](map.md)로 구한다).

메서드:
- setState(newState: Doom.State?) -> void
  설명: 상태를 바꾼다. newState가 null이면 이 Actor를 세계에서 제거한다.
  아니면 `ticsRemaining = newState.duration`으로 맞추고, `newState.action`이
  있으면 그 함수를 (이 Actor를 인자로) 즉시 실행한다.
- tick() -> void
  설명: `P_MobjThinker`에 대응한다. `momX`/`momY`/`momZ`만큼 위치를
  옮기고(충돌 처리는 `game.md`의 `Behavior.이동과 충돌` 참조),
  `ticsRemaining`을 1 줄인다. `ticsRemaining`이 0이 되고
  `state.duration`이 -1이 아니면 `setState(state.nextState)`를 호출한다
  (즉 자동으로 다음 애니메이션 프레임/행동으로 넘어간다).

불변식:
- `ticsRemaining`은 `state.duration`이 -1이 아닌 한 항상 0 이상이다.
- health가 0 이하가 되면 반드시 (즉시는 아니어도) `type.deathState`로
  전이한다 — `game.md`의 `Behavior.전투 판정` 참조.

test_required Doom.Actor {
  - `setState(null)`을 호출하면 이 Actor는 더 이상 world에 없다(제거된다).
  - 상태에 들어간 직후부터 `tick()`을 정확히 `state.duration`번 호출하면,
    그 시점에 `state`는 원래 상태의 `nextState`로 바뀌어 있다.
  - `duration`이 -1인 상태는 `tick()`을 아무리 불러도 `nextState`로
    저절로 넘어가지 않는다.
}

## Class: Doom.Player

`player_t`에 대응한다. 조작 대상은 하나의 `Doom.Actor`(`type` = 전용
플레이어 MobjType)이지만, 화면 표시나 인벤토리처럼 몬스터에는 없는
정보를 따로 담는다.

멤버:
- actor: Doom.Actor
- armor: int — 0~200.
- ammo: map<string, int> — 예: `{"bullets": 50, "shells": 0, "rockets": 0,
  "cells": 0}`.
- keys: list<string> — 갖고 있는 키의 색 목록(예: `["blue", "red"]`).
  카드 키와 스컬 키는 색이 같으면 이 목록에서 구분하지 않는다 —
  `specials.md`의 잠긴 문 판정이 이 색만 확인한다.
- currentWeapon: string — 예: `"pistol"`.
- viewAngle: float — 화면이 바라보는 방향(대개 `actor.angle`과 같지만,
  마우스/조준 보정 등으로 미세하게 다를 수 있다).

# Interface

## Library

`game.md`는 맵을 불러올 때 `Doom.Map.Thing` 목록을 순회하며
`Doom.Actor.Spawn`으로 몬스터·아이템을 배치하고, 매 tic마다 모든 Actor의
`tick()`을 호출합니다. `render.md`는 각 Actor의 `state.sprite`/`frame`으로
어떤 스프라이트를 그릴지 결정합니다.

# Constraints

- 아래 "전체 몬스터 로스터" 표가 원본 `mobjinfo[]`의 실제 수치를 담고
  있다 — `Doom.MobjType` 인스턴스를 몬스터마다 하나씩 만들 때 그 표의
  값을 그대로 쓴다.
- "아이템 로스터"와 "발사체 로스터" 표도 마찬가지로 각각의
  `Doom.MobjType`/픽업 효과를 만들 때 그대로 쓴다 — 아이템은
  `MF_SPECIAL`, 발사체는 `MF_MISSILE|MF_NOGRAVITY`를 `flags`에 포함한다.

# Examples

## 예제: Zombieman의 상태 기계

전제(대표 몬스터 하나만 구체적으로 정의):
```
spawnState  = State(sprite="POSS", frame=0, duration=10, nextState=spawnState)  -- 제자리 대기(순환)
seeState    = State(sprite="POSS", frame=1, duration=4,  nextState=seeState)    -- 추격(순환)
painState   = State(sprite="POSS", frame=6, duration=3,  nextState=seeState)
meleeState  = null   -- Zombieman은 근접 공격이 없다
missileState= State(sprite="POSS", frame=4, duration=10, action=발사, nextState=seeState)
deathState  = State(sprite="POSS", frame=7, duration=5,  nextState=(sprite="POSS", frame=8, duration=-1, nextState=null))

Zombieman = MobjType(name="Zombieman", spawnHealth=20, radius=20, height=56,
                      speed=8, flags=MF_SOLID|MF_SHOOTABLE|MF_COUNTKILL,
                      spawnState=spawnState, seeState=seeState, painState=painState,
                      meleeState=null, missileState=missileState, deathState=deathState)
```

호출: `z = Doom.Actor.Spawn(Zombieman, 100, 200, 0, someSector)`,
`z.setState(z.type.deathState)`, 그 뒤 `tick()`을 5번 호출한다.

기대 동작: 5번째 `tick()` 뒤 `z.state`는 `duration=-1`인 두 번째 사망
프레임으로 바뀌어 있고, 그 뒤로는 `tick()`을 아무리 불러도 상태가
바뀌지 않는다(주저앉은 시체 그대로 남는다 — 원본 DOOM의 실제 동작과
같다).

## 전체 몬스터 로스터

원본 `mobjinfo[]`의 실제 값이다(`doomednum`은 [`Doom.Map.Thing.type`](map.md)에
대응하는 번호 — 맵의 `THINGS` lump가 이 번호로 어떤 몬스터를 어디에
배치할지 가리킨다). `sprite`는 각 `MobjType`의 `spawnState.sprite` 등에
쓰는 4글자 스프라이트 접두사다. `attack`은 `missile`(원거리, 발사체 또는
즉발 명중), `melee`(근접), `both`(둘 다, `ai.md`의 `Feature.추격`이
거리에 따라 고른다), `none`(공격하지 않는다) 중 하나다.

| 이름 | sprite | doomednum | health | radius | height | speed | painChance | mass | attack | 비고 |
|---|---|---|---|---|---|---|---|---|---|---|
| Zombieman | POSS | 3004 | 20 | 20 | 56 | 8 | 200 | 100 | missile | 권총, 즉발 명중 |
| Shotgun Guy | SPOS | 9 | 30 | 20 | 56 | 8 | 170 | 100 | missile | 샷건, 즉발 명중(펠릿 여러 발) |
| Chaingunner | CPOS | 65 | 70 | 20 | 56 | 8 | 170 | 100 | missile | 체인건, 연사 |
| Wolfenstein SS | SSWV | 84 | 50 | 20 | 56 | 8 | 170 | 100 | missile | 권총과 동일한 공격 |
| Imp | TROO | 3001 | 60 | 20 | 56 | 8 | 200 | 100 | both | 근접 발톱 + 원거리 화염구 |
| Demon (Pinky) | SARG | 3002 | 150 | 30 | 56 | 10 | 180 | 400 | melee | 물어뜯기만 한다 |
| Spectre | SARG | 58 | 150 | 30 | 56 | 10 | 180 | 400 | melee | Demon과 동일 + `MF_SHADOW`(반투명, 명중률 낮춤) |
| Lost Soul | SKUL | 3006 | 100 | 16 | 56 | 8 | 256 | 50 | missile | `MF_FLOAT\|MF_NOGRAVITY`, 돌진 공격(`A_SkullAttack`) |
| Cacodemon | HEAD | 3005 | 400 | 31 | 56 | 8 | 128 | 400 | missile | `MF_FLOAT\|MF_NOGRAVITY`, 화염구 |
| Hell Knight | BOS2 | 69 | 500 | 24 | 64 | 8 | 50 | 1000 | both | Baron의 약체 버전(체력만 다름) |
| Baron of Hell | BOSS | 3003 | 1000 | 24 | 64 | 8 | 50 | 1000 | both | 근접 발톱 + 원거리 화염구 |
| Arachnotron | BSPI | 68 | 500 | 64 | 64 | 12 | 128 | 600 | missile | 플라즈마형 연사 |
| Pain Elemental | PAIN | 71 | 400 | 31 | 56 | 8 | 128 | 400 | missile | `MF_FLOAT\|MF_NOGRAVITY`, 죽을 때 Lost Soul을 뱉어낸다 |
| Revenant | SKEL | 66 | 300 | 20 | 56 | 10 | 100 | 500 | both | 원거리는 플레이어를 따라가는 유도 발사체 |
| Mancubus | FATT | 67 | 600 | 48 | 64 | 8 | 80 | 1000 | missile | 화염구 두 발을 부채꼴로 동시 발사 |
| Arch-vile | VILE | 64 | 700 | 20 | 56 | 15 | 10 | 500 | missile | 화염 공격 + 죽은 몬스터를 되살리는 특수 능력(아래 참조) |
| Spider Mastermind | SPID | 7 | 3000 | 128 | 100 | 12 | 40 | 1000 | missile | 체인건형 연사, 보스 |
| Cyberdemon | CYBR | 16 | 4000 | 40 | 110 | 16 | 20 | 1000 | missile | 로켓 발사, 보스 |

불변식(추가):
- `Spectre`는 `Demon`과 모든 수치가 같고 `flags`에 `MF_SHADOW`만
  더해진다 — `ai.md`의 원거리/즉발 공격 명중률 판정에서 `MF_SHADOW`가
  있으면 조준 오차를 원본보다 크게 준다(반투명해서 잘 안 보인다는 설정).

## 아이템 로스터 (픽업)

원본에서 아이템도 몬스터와 같은 `MobjType`/`State` 틀을 그대로 쓰는
Actor다 — 다만 `flags`에 `MF_SPECIAL`이 있어 플레이어가 닿으면 즉시
"먹히고" 사라진다(원본 `P_TouchSpecialThing`에 대응, `game.md`의
`Behavior.이동과 충돌`에서 호출한다). `doomednum`은
[`Doom.Map.Thing.type`](map.md)에 대응한다.

| 이름 | doomednum | 종류 | 효과 |
|---|---|---|---|
| Stimpack | 2011 | health | 체력 +10 (최대 100) |
| Medikit | 2012 | health | 체력 +25 (최대 100) |
| Health Bonus | 2014 | health | 체력 +1 (최대 200 — 이 아이템만 100을 넘길 수 있다) |
| Soulsphere | 2013 | health | 체력 +100 (최대 200) |
| Green Armor | 2018 | armor | armor=100, armorClass=1 |
| Blue Armor | 2019 | armor | armor=200, armorClass=2 |
| Armor Bonus | 2015 | armor | armor +1 (최대 200, 기존 armorClass 유지) |
| Clip | 2007 | ammo | bullets +10 |
| Box of Bullets | 2048 | ammo | bullets +50 |
| Shells | 2008 | ammo | shells +4 |
| Box of Shells | 2049 | ammo | shells +20 |
| Rocket | 2010 | ammo | rockets +1 |
| Box of Rockets | 2046 | ammo | rockets +5 |
| Cell | 2047 | ammo | cells +20 |
| Cell Pack | 17 | ammo | cells +100 |
| Backpack | 8 | ammo | 모든 탄약 종류의 최대치를 2배로 늘리고, 각 탄약을 소량(대략 처음 지급량만큼) 채워준다 |
| Chainsaw | 2005 | weapon | 전기톱 획득 |
| Shotgun | 2001 | weapon | 샷건 획득 |
| Chaingun | 2002 | weapon | 체인건 획득 |
| Rocket Launcher | 2003 | weapon | 로켓 런처 획득 |
| Plasma Rifle | 2004 | weapon | 플라즈마 라이플 획득 |
| BFG9000 | 2006 | weapon | BFG9000 획득 |
| Berserk | 2023 | powerup | 체력이 100 미만이면 100으로 회복 + 주먹(fist) 피해량이 (타이머 없이) 영구히 대폭 상승 |
| Invulnerability | 2022 | powerup | 30초간 모든 피해 무시 |
| Partial Invisibility | 2024 | powerup | 60초간 반투명 — 몬스터의 원거리/즉발 명중률이 낮아진다(Spectre와 같은 원리) |
| Radiation Suit | 2025 | powerup | 60초간 독성 바닥(sector special)의 지속 피해 무시 |
| Computer Area Map | 2026 | powerup | 자동 지도(`automap.md`)의 아직 못 본 벽까지 즉시 공개 |
| Light Amplification Visor | 2045 | powerup | 120초간 전체 밝기를 최대로 고정 |
| Blue Keycard | 5 | key | 파랑 카드 키 획득 |
| Yellow Keycard | 6 | key | 노랑 카드 키 획득 |
| Red Keycard | 13 | key | 빨강 카드 키 획득 |
| Blue Skull Key | 40 | key | 파랑 스컬 키 획득 |
| Yellow Skull Key | 39 | key | 노랑 스컬 키 획득 |
| Red Skull Key | 38 | key | 빨강 스컬 키 획득 |

카드 키와 스컬 키는 서로 다른 물건이지만 `specials.md`의 문 잠금 판정에서
같은 색이면 동등하게 취급된다(예: 파랑 문은 Blue Keycard든 Blue Skull
Key든 열 수 있다). Doom II에서 추가된 Megasphere(83, 체력+방어구 동시
최대 회복)는 이 저장소(오리지널 DOOM)에는 없으므로 포함하지 않았다 —
Super Shotgun과 같은 이유([`weapons.md`](weapons.md) Open Points 참조).

## 발사체 로스터 (몬스터 원거리 공격)

몬스터의 원거리 공격(`missileState.action`)은 대부분 `MF_MISSILE` 플래그를
가진 별도 Actor를 하나 생성해 직선으로 날리는 방식이다(같은 종족끼리는
충돌하지 않는다 — `MF_MISSILE`의 정의). 아래는 그렇게 생성되는 발사체의
`MobjType`들이다. 플레이어가 쏘는 로켓/플라즈마/BFG 볼은 이미
[`weapons.md`](weapons.md)의 피해 공식에 정리되어 있으므로 여기서는
몬스터 발사체만 다룬다.

| 이름 | 발사 주체 | sprite | speed | radius | height | damage | 비고 |
|---|---|---|---|---|---|---|---|
| Imp 화염구 | Imp | BAL1 | 10 | 6 | 8 | `((P_Random()%8)+1)*3` = 3~24 | |
| Cacodemon 화염구 | Cacodemon | BAL2 | 10 | 6 | 8 | `((P_Random()%8)+1)*5` = 5~40 | |
| Baron/Hell Knight 화염구 | Baron of Hell, Hell Knight | BAL7 | 15 | 6 | 8 | `((P_Random()%8)+1)*8` = 8~64 | 둘이 같은 발사체를 공유한다 |
| Mancubus 화염구 | Mancubus | MANF | 20 | 6 | 8 | `((P_Random()%8)+1)*8` = 8~64 | 한 번의 공격에 두 발을 부채꼴로 동시 발사 |
| Arachnotron 플라즈마 | Arachnotron | APLS | 25 | 13 | 8 | 5(고정) | 연사 속도가 빨라 실질 화력이 높다 |
| Revenant 유도 미사일 | Revenant | (원본 확인 필요 — Open Points 참조) | 10 | 11 | 8 | 명중 시 고정 피해(대략 10 내외, 정확한 수치는 원본 확인 필요) | 비행 중 주기적으로 `target`을 향해 각도를 보정하는 유일한 유도 발사체(`A_Tracer`) |
| Lost Soul 돌진 | Lost Soul | (없음 — 발사체가 아니라 몸통 박치기) | 돌진 시 순간 가속 | 16 | 56 | `(P_Random()%8)+1` = 1~8 | 발사체를 만들지 않고 `A_SkullAttack`으로 자기 자신이 목표를 향해 돌진해 접촉 피해를 준다 |

불변식:
- 모든 몬스터 발사체는 `flags`에 `MF_MISSILE`과 `MF_NOGRAVITY`를 갖는다 —
  중력의 영향을 받지 않고 생성 시점의 각도로 등속 직선 비행하다가(Revenant
  유도 미사일만 예외) 무언가에 맞으면 `deathState`(폭발/소멸 애니메이션)로
  전이하고 `game.md`의 `Behavior.전투 판정`을 통해 피해를 준다.

## Feature: 되살리기 (Arch-vile 전용)

Arch-vile의 원거리 공격(`missileState`의 `action`)은 다른 몬스터와
다르다 — 발사체를 쏘는 대신, 시야 안의 죽은 몬스터 하나를 즉시 다시
살린다(원본 `A_VileChase`/`A_Fire` 계열에 대응).

절차:
1. 시야 안에서 `deathState`에 멈춰 있는(부활 가능한) 죽은 Actor를 찾는다.
2. 있으면 그 Actor의 `health`를 `type.spawnHealth`로 되돌리고,
   `flags`에 `MF_SOLID`를 다시 켠 뒤, "일어나는" 애니메이션 상태로
   전이시킨다(대개 `deathState`를 거꾸로 재생하는 것과 비슷한 별도
   상태다).
3. 없으면 대신 화염 공격(원거리 판정, `ai.md`의
   `Feature.원거리 공격 판정`과 같은 방식)을 한다.

# Open Points

- 위 로스터의 각 몬스터마다 `spawnState`~`deathState`(그리고 Lost
  Soul/Pain Elemental/Cacodemon처럼 죽을 때 파편이 튀는 `xdeathState`가
  있는 경우 그것까지)의 정확한 프레임 번호·지속 tic 수는 옮기지
  않았다 — Zombieman 예제와 같은 `State`/`nextState` 연결 방식으로,
  원본 `info.c`의 `states[]` 표에 있는 값을 그대로 채워 넣으면 된다
  (스프라이트 이름·전체 로스터·공격 방식 자체는 이미 위에 정확히
  옮겨져 있다).
- 사운드 재생(`action`이 소리를 내는 경우)은 이 파일에서 다루지 않는다 —
  `game.md`/`sound.md` 참조.
- 아이템·발사체 표에 포함된 `MobjType`들의 `spawnState`~`deathState`
  프레임 번호·지속 tic 수도 몬스터와 마찬가지로 옮기지 않았다 — 같은
  방식으로 원본 `states[]`를 참고해 채우면 된다.
- Revenant 유도 미사일의 정확한 스프라이트 코드와 고정 피해량은 이번에
  확인하지 못했다 — 원본 `info.c`의 `mobjinfo[MT_TRACER]`/해당
  `A_Tracer`·`A_SkelFist` 계열 코드를 직접 확인해 채워야 한다(잘못된
  값을 추측해 넣기보다 비워 두는 쪽을 택했다).
