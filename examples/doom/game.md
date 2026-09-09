#!specpp 0.1

# Domain

원본 `g_game.h`/`g_game.c`(전체 게임 상태·틱 루프), `p_user.c`(플레이어
이동), `p_map.c`/`p_maputl.c`(충돌 판정), `p_inter.c`(전투/아이템 상호작용),
`p_tick.c`(전체 thinker 목록 진행)에 대응한다.

## Class: Doom.Game

멤버:
- map: Doom.Map
- player: Doom.Player
- actors: list<Doom.Actor> — player.actor를 포함한, 지금 살아있는 모든
  Actor.
- specials: list<Doom.SectorMover> — [`specials.md`](specials.md) 참조.
- lightFlashes: list<Doom.LightFlash>
- renderer: Doom.Renderer
- soundSystem: Doom.SoundSystem — [`sound.md`](sound.md) 참조.
- netGame: Doom.NetGame? — [`netplay.md`](netplay.md) 참조. 싱글
  플레이면 null.
- demo: Doom.Demo? — 녹화 중이거나 재생 중이면 있다.
- hud: Doom.Hud
- automap: Doom.AutoMap
- menuStack: Doom.MenuStack
- tic: int — 기본값 0. 1 증가할 때마다 1/35초가 지난 것으로 친다(원본의
  고정 35Hz 시뮬레이션 속도).
- killCount: int
- itemCount: int
- secretCount: int

생성자:
[Static]
- Start(wad: Doom.WadFile, mapName: string) -> Doom.Game
  설명: `Doom.Map.Load`로 맵을 불러오고, `map.things`를 순회하며 플레이어
  시작 위치는 `player.actor`로, 나머지(몬스터·아이템 모두 —
  [`actors.md`](actors.md)의 몬스터·아이템 로스터가 각각의
  `Thing.type` ↔ `MobjType`/픽업 대응을 정의한다)는 `Doom.Actor.Spawn`으로
  `actors`에 채운다. 이때 각 맵의 몬스터 종류별 마릿수를 세어 나중에
  `Feature.맵 종료 조건`/`intermission.md`에서 쓸 처치율 기준을 잡는다.

# Behavior

## Feature: 틱 진행

설명: `G_Ticker`에 대응한다. 매 1/35초(원본의 고정 시뮬레이션 속도)마다
정확히 한 번 실행된다 — 렌더링 프레임 속도와는 독립적이다(프레임이 더
빠르면 같은 화면을 그대로 다시 그리고, 더 느리면 여러 틱을 한 번에
처리해 따라잡는다).

절차:
1. `menuStack.stack`이 비어 있지 않으면(메뉴가 열려 있으면) 게임 시뮬레이션은
   멈추고 `menu.md`의 입력 처리만 한다 — 아래 단계를 건너뛴다.
2. [`netplay.md`](netplay.md)의 `Feature.틱 명령 수집`으로 이번 tic의
   `Doom.TicCmd`를 얻는다(싱글 플레이/멀티플레이/데모 재생 중 어느
   쪽이든 이 한 단계가 대신 처리한다 — 멀티플레이라면
   `isReadyToAdvance(tic)`가 true가 될 때까지 이 tic 전체가 미뤄진다).
   얻은 명령을 `Feature.이동과 충돌`, `Feature.발사 입력 처리`,
   `Feature.사용 키 처리`에 넘긴다.
3. `actors`의 각 Actor에 대해 `tick()`을 호출한다
   ([`actors.md`](actors.md) 참조 — 몬스터라면 이 안에서
   [`ai.md`](ai.md)의 행동 함수도 실행된다).
4. `player`의 `Doom.PlayerWeapon.tick()`을 호출한다.
5. `specials`/`lightFlashes`의 각 항목에 `Feature.특수 효과 진행`
   ([`specials.md`](specials.md))을 적용한다.
6. `automap.md`의 `Feature.지도에 선 드러내기`를 실행한다.
7. `soundSystem.updateListenerPosition(player)`를 호출한다.
8. `tic`을 1 증가시킨다.
9. `Feature.맵 종료 조건`을 확인한다.

## Feature: 이동과 충돌

설명: `P_XYMovement`/`PTR_SlideTraverse`에 대응. Actor(플레이어 포함)가
`momX`/`momY`만큼 움직이려 할 때 실제로 얼마나 움직일 수 있는지 정한다.

입력:
- actor: Doom.Actor
- deltaX: float
- deltaY: float

절차:
1. `(actor.x + deltaX, actor.y + deltaY)`를 중심으로 `actor.radius`만큼의
   원이 가로지르는 모든 [`Doom.Map.LineDef`](map.md)를 찾는다.
2. 그중 통과할 수 없는 것이 있으면(양면이 아니거나, 양면이어도 두 섹터의
   바닥 높이 차이가 `actor`가 넘을 수 있는 단차(원본 기본 24 map 단위)보다
   크거나, 천장까지 남은 높이가 `actor.height`보다 낮으면) 이동을 그
   벽에 막히지 않는 만큼만(벽을 따라 미끄러지도록, slide move) 줄인다.
3. 같은 원이 다른 솔리드(`MF_SOLID`) Actor와 겹치면(단, `MF_MISSILE`인
   Actor는 같은 종족끼리는 서로 무시한다) 마찬가지로 이동을 막는다.
   `MF_SPECIAL`(아이템)인 Actor와 겹치면 막지 않는 대신
   `Feature.아이템 획득`을 실행한다.
4. 막히지 않은 만큼 `actor.x`/`actor.y`를 갱신하고,
   [`Doom.Map.BspNode.FindSubsector`](map.md)로 `actor.sector`를 다시
   구한다.
5. 넘은 문턱이 있어 바닥 높이가 바뀌었으면 `actor.z`를 새 바닥 높이에
   맞춘다(계단을 오르내리는 것처럼 보이게 한다) — `MF_NOGRAVITY`가 없는
   한 z는 항상 `sector.floorHeight` 이상으로 유지된다.

test_required Doom.Game {
  - `Feature.이동과 충돌`은 단면(통과 불가) linedef를 절대로 뚫고
    지나가게 하지 않는다.
  - `Feature.이동과 충돌`에서 이동이 완전히 막혀도(벽에 정면으로
    부딪혀도) 오류 없이 그 자리에 머문다(이동량이 0이 되는 것으로
    처리된다) — 예외를 던지지 않는다.
}

## Feature: 아이템 획득

설명: `P_TouchSpecialThing`에 대응. `Feature.이동과 충돌`에서 플레이어(만—
몬스터는 아이템을 줍지 않는다)의 충돌 원이 `MF_SPECIAL` Actor와 겹쳤을 때
호출된다.

입력:
- item: Doom.Actor (`MF_SPECIAL`이 켜진, [`actors.md`](actors.md) 아이템
  로스터 중 하나로 스폰된 Actor)
- player: Doom.Player

절차:
1. `item`을 스폰할 때 기록해 둔 아이템 이름으로
   [`actors.md`](actors.md)의 "아이템 로스터" 표에서 대응하는 `apply(player)`
   함수를 찾아 실행한다(체력/방어구 회복, 탄약 지급, 무기 교체, 키 획득 등).
2. `itemCount`를 1 늘린다.
3. `item`을 `setState(null)`로 세계에서 제거한다(효과음도 함께 낸다 —
   `sound.md` 참조).

## Feature: 전투 판정

설명: `P_DamageMobj`에 대응. 피해를 입히는 모든 경로(근접, 원거리 명중,
크러셔, 바닥 데미지 등)가 공통으로 거친다.

입력:
- target: Doom.Actor
- damage: int
- inflictor: Doom.Actor? — 피해를 준 주체(없으면 환경 피해).

절차:
1. `target.flags`에 `MF_SHOOTABLE`이 없으면 아무 일도 하지 않는다.
2. `target`이 플레이어면 먼저 `armor`로 일부를 흡수한다(원본 기본: 초록
   갑옷은 1/3, 파란 갑옷은 1/2을 갑옷에서, 나머지를 체력에서 깎는다).
3. `target.health`를 `damage`만큼 줄인다. 0 밑으로는 내려가지 않는다.
4. `inflictor`가 있고 `target.target`이 비어 있으면(아직 아무도 쫓고
   있지 않으면) `target.target = inflictor`로 정해 반격하게 한다(몬스터가
   서로를 실수로 맞혀 싸우게 되는 원본의 유명한 동작도 이 규칙에서
   나온다).
5. [`ai.md`](ai.md)의 `Feature.고통과 죽음`을 호출한다 — 그 결과로
   painState/deathState로 전이하면, 각 상태에 정해진 고통/죽음 효과음을
   `target`의 위치에서 [`sound.md`](sound.md)의 `Feature.효과음 재생`으로
   낸다.
6. `target`이 죽었고 `target.type.flags`에 `MF_COUNTKILL`이 있으면
   `killCount`를 1 늘린다.

## Feature: 발사 입력 처리

설명: `P_FireWeapon`/`A_WeaponReady`에 대응.

절차:
1. 현재 무기(`player.currentWeapon`이 가리키는 [`Doom.WeaponType`](weapons.md))의
   `ammoType`이 있으면, `player.ammo[ammoType] >= ammoPerShot`인지
   확인한다. 부족하면 아무 일도 하지 않는다(원본은 자동으로 다음 무기로
   바꾼다 — 이 버전은 단순화해 그냥 발사되지 않는다, 아래 Open Points
   참조).
2. `PlayerWeapon.setState(type.attackState)`를 호출한다.
3. `attackState`의 `action`이 실행되며, 먼저 그 무기의 발사음을
   `player.actor`의 위치에서 [`sound.md`](sound.md)의
   `Feature.효과음 재생`으로 낸다. 그 뒤 `player.ammo[ammoType]`을
   `ammoPerShot`만큼 줄이고, 명중 판정(즉발형은 조준선을 그어 첫 번째로
   맞는 대상에 `Feature.전투 판정`, 발사체형은 `Doom.Actor.Spawn`으로
   `MF_MISSILE`이 켜진 발사체 Actor를 만들어 `momX`/`momY`를 조준
   방향으로 준다)을 한다.

## Feature: 사용 키 처리

설명: `P_UseLines`에 대응.

절차:
1. `player.actor`의 바로 앞, 짧은 거리 안에 있는 첫 번째
   [`Doom.Map.LineDef`](map.md)를 찾는다.
2. 있으면 [`specials.md`](specials.md)의
   `Feature.선을 밟아 특수 효과 발동`을 `trigger = Use`로 호출한다.

## Feature: 맵 종료 조건

설명: 원본은 "출구" 선(special이 맵 종료인 linedef)을 밟거나, 그 맵의
모든 몬스터를 처치하면(일부 특수 맵) 종료된다.

절차:
1. 플레이어가 종료용 special을 가진 linedef를 밟으면
   [`intermission.md`](intermission.md)의 `Feature.스테이지 클리어 전환`을
   실행하고 `Feature.틱 진행`을 멈춘다.

# Interface

## GUI

[`std/ui/widgets.md`](../../std/ui/widgets.md)의 `Window`(또는
[`std/windows/win32.md`](../../std/windows/win32.md)의 `HWND`) 하나
전체를 3D 시점(`render.md`) 또는 메뉴 화면(`menu.md`) 또는 자동 지도
(`automap.md`) 또는 인터미션(`intermission.md`) 중 그 순간 활성 화면
하나로 채운다. 방향키/마우스로 이동·시야 회전, Ctrl(또는 좌클릭)로 발사,
스페이스로 사용, Tab으로 자동 지도 토글, Esc로 메뉴를 연다.

# Constraints

- 입력 장치(키보드/마우스/게임패드)를 실제로 읽는 방법은 대상 언어·
  플랫폼의 관용적인 방식(Windows는
  [`std/windows/win32.md`](../../std/windows/win32.md)의 `WM_KEYDOWN`
  등)을 따른다 — 이 명세는 그 원시 입력을 [`netplay.md`](netplay.md)의
  `Doom.TicCmd`로 압축한 뒤에는 로컬 재생이든 네트워크든 데모 재생이든
  구분하지 않는다.
- 좌표·거리·속도는 3.1절의 `float`로 표기했다 — 원본은 16.16
  고정소수점(`fixed_t`)을 쓴다. `netplay.md`가 설명하듯, 네트워크
  플레이나 데모의 정확한 재현이 중요하면 이 명세도 `float` 대신
  고정소수점으로 구현하는 것을 강하게 권장한다 — 대상 언어·CPU마다
  다른 부동소수점 반올림이 몇 분 안에 참가자 사이의 상태를 어긋나게
  만들 수 있다.

# Examples

## 예제: 벽에 막힌 이동

전제: Actor 바로 앞 1 map 단위 거리에 단면(통과 불가) linedef가 있다.

호출: `Feature.이동과 충돌`을 그 벽 방향으로 10 map 단위 이동 시도로
실행한다.

기대 동작: Actor는 벽 앞까지만 이동하고(벽을 뚫지 않는다), 벽과 나란한
성분이 있다면 그만큼은 미끄러지듯 이동한다.

## 예제: 체력이 다하면 처치 수가 오른다

전제: `target`은 `MF_COUNTKILL`이 켜진 몬스터이고 `health`가 5다.

호출: `Feature.전투 판정`을 `damage=10`으로 실행한다.

기대 동작: `target.health`는 0이 되고, `target.state`는
`type.deathState`로 바뀌며(`ai.md` 참조), `killCount`가 1 늘어난다.

## 예제: 탄약이 없으면 발사되지 않는다

전제: `player.currentWeapon`은 shotgun이고 `player.ammo["shells"] == 0`.

호출: `Feature.발사 입력 처리`

기대 동작: `PlayerWeapon.state`가 바뀌지 않는다(여전히 `readyState`).

# Open Points

이 명세는 원본 `linuxdoom-1.10`의 게임플레이 시스템(WAD 로딩, 맵/BSP
지오메트리, 렌더링 파이프라인, 액터 상태 기계·AI, 무기, 특수 효과,
이동·충돌·전투, 효과음·음악, 락스텝 멀티플레이·데모, HUD, 자동 지도,
메뉴, 인터미션/피날레, 저장/불러오기)를 전부 다뤘다. 아래는 의도적으로
이 버전에 옮기지 않은, 순수한 1993년 당시 구현 세부사항이다.

- **메모리 관리(`z_zone.c`)**: 원본의 커스텀 메모리 zone 할당자는 1993년
  당시의 메모리 제약 때문이었다 — 대상 언어의 기본 메모리 관리(가비지
  컬렉션 또는 RAII)에 맡긴다(0장 철학).
- **저수준 시스템 계층**(`i_video.c`, `i_sound.c`, `i_net.c`,
  `i_system.c`): 이 파일들은 1993년 당시 DOS/리눅스에 대한 저수준
  플랫폼 코드였다 — 이 명세에서는 그 역할을
  [`std/graphics/opengl3.md`](../../std/graphics/opengl3.md)/
  [`std/windows/direct3d11.md`](../../std/windows/direct3d11.md)(영상),
  [`std/audio/openal.md`](../../std/audio/openal.md)/
  [`std/windows/directsound.md`](../../std/windows/directsound.md)(음향),
  [`std/net/udp.md`](../../std/net/udp.md)(네트워크),
  [`std/windows/win32.md`](../../std/windows/win32.md)(창·입력)로
  대체했다.
- **아이템·발사체 프레임 타이밍**: `actors.md`에 몬스터 18종·아이템
  전종·몬스터 발사체 전종의 실제 수치(체력·피해·탄약 종류 등)를 모두
  채웠다 — 남은 것은 각 `MobjType`의 `spawnState`~`deathState` 정확한
  프레임 번호·지속 tic 수(순수 애니메이션 타이밍)뿐이다(`actors.md`의
  Open Points 참조, Zombieman 예제와 같은 방식으로 채우면 된다).
- **난이도별 차이**(이지/하드모드의 몬스터 배치·데미지·탄약 배율)는
  다루지 않는다.
- **네트워크 참가자 발견·연결 관리**와 **패킷 유실 보정**은
  [`netplay.md`](netplay.md)의 Open Points에 정리되어 있다.
- **MUS→MIDI 변환의 정확한 바이트 포맷**은 [`sound.md`](sound.md)의
  Open Points에 정리되어 있다.
