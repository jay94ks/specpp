#!specpp 0.1

# Domain

원본 `p_spec.h`/`p_doors.c`/`p_floor.c`/`p_ceilng.c`/`p_plats.c`/
`p_lights.c`/`p_switch.c`/`p_telept.c`에 대응한다. [`Doom.Map.LineDef`](map.md)나
[`Doom.Map.Sector`](map.md)의 `special` 번호가 0이 아니면, 어떤 조건(플레이어가
그 선을 밟거나, 스위치를 누르거나, 맵 시작 시 자동으로)이 되었을 때 문이
열리거나 바닥이 움직이거나 조명이 바뀌는 식으로 동작한다. 이런 "지금
진행 중인 움직임"은 각각 독립된 thinker(원본의 `thinker_t`를 상속한 여러
구조체 — `vldoor_t`, `floormove_t`, `ceiling_t`, `plat_t`, `lightflash_t`
등)로 표현되고, 매 tic마다 자신의 목표를 향해 조금씩 움직인다.

## Interface: Doom.SectorMover

문/바닥/천장/플랫폼처럼 "섹터의 바닥 또는 천장 높이를 시간에 걸쳐
움직이는" 모든 특수 효과가 공통으로 갖는 모양이다.

메서드:
- tick() -> boolean
  설명: 목표를 향해 한 tic만큼 움직인다. 목표에 도달해서 이 효과가 끝났으면
  false를 반환한다(호출하는 쪽이 이 thinker를 제거한다) — 계속 진행
  중이면 true.

## Class: Doom.Door implements Doom.SectorMover

원본 `vldoor_t`에 대응한다.

멤버:
- sector: Doom.Map.Sector
- kind: enum(Open | Close | OpenThenClose | CloseThenOpen)
- targetCeilingHeight: float
- speed: float — 초당 높이 변화량(원본 기본값: 초당 2 map 단위 * 35tic ≈
  느린 문, 빠른 문은 4배).
- waitTicsRemaining: int — 열려 있는 상태를 유지할 남은 tic 수(`kind`가
  `OpenThenClose`일 때).
- requiredKey: string? — null이 아니면 `"blue"`/`"yellow"`/`"red"` 중
  하나(잠긴 문). 활성화한 Actor가 [`actors.md`](actors.md)의 카드 키 또는
  스컬 키 중 같은 색을 하나라도 갖고 있어야 문이 열린다 — 카드/스컬
  구분 없이 색만 같으면 동등하게 취급한다.

test_required Doom.Door {
  - `kind = Open`인 문은 `tick()`을 계속 부르면 결국
    `sector.ceilingHeight == targetCeilingHeight`가 되고 `tick()`이
    false를 반환한다.
  - 문 밑에 플레이어나 몬스터가 끼어 있으면(천장이 그 위치의 바닥+어떤
    Actor의 높이보다 낮아지려 하면) 닫히는 문은 다시 여는 쪽으로 되돌아간다
    (원본의 끼임 방지 동작).
}

## Class: Doom.FloorMover implements Doom.SectorMover

원본 `floormove_t`에 대응한다. 문과 같은 모양이지만 바닥 높이를 움직인다
— 올라오는 바닥(크러셔가 아닌 한) 도중에 Actor가 끼면 즉시 피해를 준다는
점이 문과 다르다.

멤버:
- sector: Doom.Map.Sector
- targetFloorHeight: float
- speed: float
- crush: boolean — true면 도중에 낀 Actor에게 피해를 준다(멈추지 않는다).

## Class: Doom.Ceiling implements Doom.SectorMover

원본 `ceiling_t`에 대응한다. 크러셔(예: 위아래로 반복 움직이며 짓누르는
천장)를 포함한다.

멤버:
- sector: Doom.Map.Sector
- topHeight: float
- bottomHeight: float
- speed: float
- direction: enum(Up | Down)
- repeats: boolean — true면 top/bottom에 닿을 때마다 방향을 뒤집으며
  계속 반복한다(크러셔).
- crush: boolean

## Class: Doom.Platform implements Doom.SectorMover

원본 `plat_t`에 대응한다("리프트"). 바닥이 두 높이 사이를 오간다.

멤버:
- sector: Doom.Map.Sector
- lowHeight: float
- highHeight: float
- speed: float
- direction: enum(Up | Down)
- waitTicsRemaining: int
- repeatsForever: boolean

## Class: Doom.LightFlash

원본 `lightflash_t`류(깜빡이는 형광등, 촛불처럼 흔들리는 빛 등 여러
변형이 있다 — 이 명세는 대표로 하나만 정의한다)에 대응한다. `tick()`이
`Doom.SectorMover`처럼 "끝났다"는 개념 없이 계속 반복된다는 점이 다르다.

멤버:
- sector: Doom.Map.Sector
- maxLight: int
- minLight: int
- ticsUntilNextChange: int

메서드:
- tick() -> void
  설명: `ticsUntilNextChange`를 줄이다가 0이 되면
  `sector.lightLevel`을 `maxLight`/`minLight` 중 하나로 무작위로
  바꾸고, 다음 변경까지의 tic 수도 무작위로 새로 정한다.

# Behavior

## Feature: 선을 밟아 특수 효과 발동

설명: 플레이어(또는 몬스터, 선의 종류에 따라 다르다)가 `special`이 0이
아닌 [`Doom.Map.LineDef`](map.md)를 가로지르거나(walkover), 그 선에
바짝 붙어 사용 키를 누르거나(use), 또는 총으로 쏘았을 때(shoot) 발동한다
— 어느 방식인지는 `special` 번호 자체가 정한다(원본은 번호 범위/규칙으로
walkover/use/shoot를 구분한다).

입력:
- lineDef: Doom.Map.LineDef
- trigger: enum(Walkover | Use | Shoot)
- activator: Doom.Actor

절차:
1. `lineDef.special`과 `trigger`가 실제로 일치하는 조합인지 확인한다.
   아니면 아무 일도 하지 않는다.
2. `lineDef.tag`와 같은 `tag`를 가진 모든 [`Doom.Map.Sector`](map.md)를
   찾는다(문처럼 선 하나가 특정 섹터 하나만 여는 경우는 예외적으로
   `lineDef.backSide.sector`를 직접 쓴다).
2b. 만들 것이 `requiredKey`가 있는 `Doom.Door`이고 `activator`가
   플레이어인데 그 색의 카드/스컬 키를 하나도 갖고 있지 않으면, 문을
   열지 않고 "필요한 키" 안내 메시지(및 실패음, `sound.md` 참조)만 내고
   끝낸다. 몬스터는 이 검사 없이 문을 지나다니지 못한다는 제약을 그대로
   따른다(원본과 동일 — 잠긴 문은 몬스터도 못 연다).
3. `special` 번호가 뜻하는 종류(문 열기, 바닥 올리기, 플랫폼, 조명 변경 등)
   에 맞는 `Doom.Door`/`Doom.FloorMover`/`Doom.Ceiling`/`Doom.Platform`/
   `Doom.LightFlash` 인스턴스를 만들어 활성 thinker 목록에 추가한다.
4. 한 번만 동작하는 종류(예: 문 한 번 열기)면 `lineDef.special`을 0으로
   되돌려 다시 발동하지 않게 한다. 반복 동작하는 종류는 그대로 둔다.

## Feature: 특수 효과 진행

설명: 매 tic, 활성화된 모든 `Doom.SectorMover`/`Doom.LightFlash`를
갱신한다.

절차:
1. 활성 thinker 목록의 각 항목에서 `tick()`을 호출한다.
2. `Doom.SectorMover`이고 `tick()`이 false를 반환했으면(목표에 도달해
   끝났으면) 목록에서 제거한다.

## Feature: 스위치 텍스처 전환

설명: `Feature.선을 밟아 특수 효과 발동`이 `trigger = Use`이고 실제로
효과가 발동됐을 때, 그 선의 벽 텍스처가 "눌린" 모습으로 바뀌는 시각
효과(원본 `p_switch.c`의 `SWITCHES` lump 기반 텍스처 짝 테이블).

절차:
1. `lineDef.frontSide`의 텍스처 이름이 알려진 "안 눌린" 스위치 텍스처와
   일치하면, 그 짝인 "눌린" 텍스처로 바꾼다.
2. 한 번만 동작하는 스위치가 아니면(원본 용어로 "buttons"), 약 1초(35
   tic) 뒤 원래 텍스처로 되돌린다.

## Feature: 텔레포트

설명: 원본 `p_telept.c`. `special`이 텔레포트인 선을 밟으면.

절차:
1. `lineDef.tag`와 같은 `tag`를 가진 [`Doom.Map.Thing`](map.md) 중
   텔레포트 목적지로 표시된 것을 찾는다.
2. 활성화한 Actor를 그 위치로 즉시 옮기고, 각도를 그 목적지 Thing의
   `angle`로 맞춘다. 잠깐의 정지 상태(순간이동 애니메이션)를 부여해
   그 tic 동안은 조작을 받지 않는다.

# Constraints

- 원본이 갖는 특수 효과 번호(약 130여 종, 문 속도·방향 조합마다 다른
  번호가 있다)를 전부 나열하지 않는다 — 위 다섯 가지 `Doom.SectorMover`
  구현체와 `Feature.선을 밟아 특수 효과 발동`의 절차가 그 번호들이
  공통으로 따르는 틀이다. 실제 번호 ↔ 파라미터 매핑표는 원본
  `p_spec.h`의 상수 정의를 그대로 옮기는 것을 권장한다.

# Open Points

- 번호 ↔ 정확한 속도/높이/반복 여부 매핑표는 옮기지 않았다.
- 크러셔가 Actor를 눌러 죽이는 정확한 피해량·타이밍은 단순화했다.
