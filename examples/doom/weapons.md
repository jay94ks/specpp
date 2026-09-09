#!specpp 0.1

# Domain

원본 `p_pspr.h`/`p_pspr.c`(플레이어 스프라이트/무기)에 대응한다. 무기도
`actors.md`의 `Doom.State` 상태 기계와 같은 방식으로 움직인다 — 다만
세계 안의 Actor가 아니라 화면 앞에 떠 있는(1인칭 시점의) "플레이어
스프라이트"로 그려진다.

## Class: Doom.WeaponType

원본 `weaponinfo[]` 테이블의 한 행에 대응한다.

멤버:
- name: string — 예: `"pistol"`, `"shotgun"`, `"chaingun"`,
  `"rocketLauncher"`, `"plasmaRifle"`, `"bfg9000"`, `"chainsaw"`,
  `"fist"`.
- ammoType: string? — `ammo` map의 어떤 키를 쓰는지(`"bullets"`,
  `"shells"`, `"rockets"`, `"cells"`). null이면 탄약을 쓰지 않는다(주먹,
  전기톱).
- ammoPerShot: int — 한 번 쏠 때 소비하는 탄약 수.
- upState: Doom.State — 화면 아래에서 위로 들어 올리는 애니메이션.
- downState: Doom.State — 다른 무기로 바꿀 때 내리는 애니메이션.
- readyState: Doom.State — 발사 대기(조준) 상태 — 여기서 입력을 받는다.
- attackState: Doom.State — 발사 애니메이션(액션 함수가 실제 피해 판정을
  한다).
- flashState: Doom.State? — 총구 화염 오버레이(있으면 attackState와 겹쳐
  그린다).

## Class: Doom.PlayerWeapon

`Doom.Player`가 들고 있는 무기 하나의 현재 재생 상태.

멤버:
- type: Doom.WeaponType
- state: Doom.State
- ticsRemaining: int

메서드:
- setState(newState: Doom.State) -> void
  설명: `actors.md`의 `Doom.Actor.setState`와 같은 규칙 — 상태를 바꾸고
  `ticsRemaining`을 그 상태의 `duration`으로 맞춘 뒤, `action`이 있으면
  실행한다. 무기는 `nextState`가 항상 있어서(null로 사라지지 않는다) 계속
  순환한다.
- tick() -> void
  설명: `ticsRemaining`을 줄이고 0이 되면 `state.nextState`로 전이한다
  (`actors.md`의 `Doom.Actor.tick`과 같은 규칙).

# Interface

## Library

`game.md`의 `Behavior.발사 입력 처리`가 `PlayerWeapon`을
`readyState`에서 `attackState`로 전이시키고, `render.md`가 매 프레임
`state.sprite`/`frame`으로 화면 앞의 무기 스프라이트를 그립니다.

# Constraints

- 아래 "전체 무기 로스터" 표가 원본 `weaponinfo[]`가 담고 있는 실제
  무기 구성(탄약 종류·소비량, 근접/원거리 여부)을 담고 있다.

# Examples

## 예제: 권총 발사 한 번

전제: `pistol.readyState.action`은 "발사 입력이 있으면
`pistolWeapon.setState(pistol.attackState)`를 호출한다"이고,
`pistol.attackState`는 `duration=4`, `action`=탄약 1발 소비 +
`Behavior.원거리 공격 판정`과 같은 방식으로 화면 정면을 향해 명중 판정,
`nextState`=`pistol.flashState`(짧게 총구 화염을 보여준 뒤 다시
`readyState`로 돌아옴)다.

호출: 발사 입력, 그 뒤 `tick()`을 4번 호출한다.

기대 동작: `ammo["bullets"]`가 1 줄어 있고, 조준선 위 첫 대상이 맞았다면
피해를 입었으며, `pistolWeapon.state`는 `flashState`를 거쳐 다시
`readyState`로 돌아와 있다.

## 예제: 탄약이 없으면 쏠 수 없다

전제: `ammo["shells"] == 0`이고 현재 무기가 shotgun이다.

호출: 발사 입력

기대 동작: `attackState`로 전이하지 않는다(`game.md`의
`Behavior.발사 입력 처리`가 탄약을 먼저 확인한다).

## 전체 무기 로스터

원본은 무기 8종(권총은 시작 무기, 맨손은 항상 갖고 있다)을 갖는다.
`hitscan`은 즉발 명중(조준선을 그어 판정), `projectile`은 실제
`MF_MISSILE` Actor를 만들어 날리는 방식이다. 총알류(권총/샷건/체인건)의
피해량은 원본에서 5, 10, 15 중 하나를 균등한 확률로 무작위로 고르는
공통 공식(`P_DamageMobj`에 넘기기 전 `((P_Random() % 3) + 1) * 5`)을
쓴다.

| 이름 | ammoType | ammoPerShot | 방식 | 발당 피해(펠릿/발사체 수) | 비고 |
|---|---|---|---|---|---|
| fist | null | 0 | 근접 | 2~20 무작위 (`((P_Random()%10)+1)*2`) | 항상 소지, 크리티컬 시 2배 |
| chainsaw | null | 0 | 근접 | fist와 같은 공식 | fist보다 공격 속도가 빠르고, 잡으면 대상에게 붙어 계속 공격하기 쉽다 |
| pistol | bullets | 1 | hitscan | 5/10/15 무작위 1발 | 시작 무기 |
| shotgun | shells | 1 | hitscan | 5/10/15 무작위 **7발**을 부채꼴로 동시 발사 | |
| chaingun | bullets | 1(방아쇠 유지 시 연사) | hitscan | 5/10/15 무작위 1발 씩, 연사 | 발사 애니메이션이 2단계로 번갈아 재생된다 |
| rocketLauncher | rockets | 1 | projectile | 직격 20~152(기본 20 + 무작위 최대 132) + 폭발 반경 피해(거리에 따라 감쇠) | 자기 자신도 근처에서 쏘면 폭발 피해를 입을 수 있다 |
| plasmaRifle | cells | 1 | projectile | 5~40 무작위(`5 + P_Random()%8` 씩, 두 번 더함) | 빠른 연사 속도 |
| bfg9000 | cells | **40** | projectile | 중심 폭발 100~800 + 명중 시 주변 대상에 흩뿌려지는 추적 광선 다수(각각 소량 추가 피해) | 가장 강력하지만 탄약 소비가 크다 |

# Open Points

- 각 무기 `readyState`~`flashState`의 정확한 프레임 번호·지속 tic 수는
  옮기지 않았다 — 위 표의 탄약·피해 공식은 이미 정확히 옮겨져 있으므로,
  애니메이션 타이밍만 원본 `info.c`의 `states[]`를 참고해 채우면 된다.
- 이지/노멀/하드 난이도에 따른 데미지·탄약 배율 차이는 다루지 않는다.
- 무기 전환 중(내리는/올리는 애니메이션 중) 입력을 어떻게 큐잉하는지는
  단순화했다 — 애니메이션이 끝나야 다음 입력을 받는다.
- Doom II에서 추가된 슈퍼샷건은 이 저장소(`id-software/DOOM`, 오리지널
  DOOM)의 원본 `weaponinfo[]`에는 없으므로 포함하지 않았다 — 추가한다면
  `shotgun`과 같은 틀에 펠릿 20발, 산탄 피해를 더 크게 잡는 식으로
  넣을 수 있다.
