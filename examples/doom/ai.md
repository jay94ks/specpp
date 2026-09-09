#!specpp 0.1

# Behavior

원본 `p_enemy.c`에 대응한다. "AI"라고 부르지만 실제로는 `actors.md`의
상태 기계에 물려 있는 몇 개의 결정 함수(action)일 뿐이다 — 각 함수는
어떤 `State.action`으로 등록되어, 그 상태에 들어갈 때(또는 그 상태로 있는
동안 매 tic) 호출된다.

## Feature: 대기 중 플레이어 탐지 (A_Look)

설명: `spawnState`처럼 "가만히 있는" 상태의 action으로 등록된다. 매 tic
호출된다.

절차:
1. 이 Actor의 시야(원본 기본값: 앞 180도, 또는 소리로 깨어난 경우 전방위)
   안에 있는 플레이어를 찾는다(`P_LookForPlayers`에 대응) — 벽에 가려
   보이지 않으면(시야 선이 단면 벽에 막히면) 안 보이는 것으로 친다.
2. 찾았으면 `target`을 그 플레이어로 설정하고, `type.seeState`로
   `setState`한다(발견 애니메이션/추격 시작).
3. 못 찾았으면 아무것도 하지 않는다(계속 대기).

## Feature: 추격 (A_Chase)

설명: `seeState`처럼 "쫓는 중" 상태의 action으로 등록된다.

절차:
1. `target`이 없거나 이미 죽었으면 `Feature.대기 중 플레이어 탐지`처럼
   다시 찾는다.
2. `P_CheckMeleeRange`에 대응: target이 `radius + target.radius`보다 살짝
   먼 정도의 근접 거리 안에 있고 이 Actor의 `type.meleeState`가 있으면,
   `Feature.근접 공격 판정`으로 넘어간다.
3. 아니면 `P_CheckMissileRange`에 대응: 일정 확률로(거리와 몬스터 종류에
   따라 다르다 — 가까울수록, 그리고 몬스터마다 정해진 성향일수록 확률이
   높다) `type.missileState`가 있으면 `Feature.원거리 공격 판정`으로
   넘어간다.
4. 둘 다 아니면 `P_Move`에 대응: 지금 바라보는 방향으로 `type.speed`만큼
   이동을 시도한다(`Behavior.이동과 충돌`, `game.md` 참조). 벽이나 다른
   솔리드 Actor에 막히면(또는 낮은 확률로 무작위로) `P_NewChaseDir`에
   대응해 target 쪽을 향하는 새 방향을 고른다.

## Feature: 목표 바라보기 (A_FaceTarget)

설명: 공격 상태에 들어가기 직전 흔히 함께 호출된다.

절차:
1. `angle`을 `target`의 현재 위치를 향하도록 즉시 돌린다.

## Feature: 근접 공격 판정

설명: `meleeState`의 action으로 등록된다.

절차:
1. `Feature.목표 바라보기`를 먼저 실행한다.
2. target이 여전히 근접 거리 안에 있으면, 이 몬스터 종류에 정해진
   피해량(무작위 범위, 예: 1d8*3)만큼 `Behavior.전투 판정`으로 target에
   피해를 준다.

## Feature: 원거리 공격 판정

설명: `missileState`의 action으로 등록된다. 몬스터마다 "발사체를
날린다"(예: Imp의 화염구) 또는 "즉발 명중 판정을 한다"(예: Zombieman의
권총 사격, `A_PosAttack`에 대응) 중 하나다 — `MobjType`에 어느 쪽인지
표시해 둔다(아래 Open Points).

절차 (즉발 명중형, 예: Zombieman):
1. `Feature.목표 바라보기`를 먼저 실행한다.
2. 정확도 오차(무작위로 조준선을 살짝 흔든다)를 적용해 target 방향으로
   가상의 총알선을 그어, 그 선이 target에 먼저 닿으면(벽에 먼저 막히지
   않으면) 명중으로 보고 `Behavior.전투 판정`으로 피해를 준다.

## Feature: 고통과 죽음 (A_Pain / A_Fall 계열)

설명: `Behavior.전투 판정`(`game.md`)이 피해를 입힌 뒤 호출한다.

절차:
1. health가 0보다 크게 남아 있고, 이번 피해가 고통 반응을 일으킬
   확률(몬스터마다 다른 `painChance`)을 넘기면 `type.painState`로
   `setState`한다 — 짧게 움찔한 뒤 다시 `Feature.추격`으로 돌아온다.
2. health가 0 이하가 되면 `type.deathState`로 `setState`하고, `flags`에서
   `MF_SOLID`를 끈다(시체를 밟고 지나갈 수 있게).

# Constraints

- 시야 판정(벽에 가렸는지)은 [`Doom.Map.LineDef`](map.md)를 잇는 가상의
  선이 단면(막힌) 벽을 가로지르는지로 판정한다 — 정확한 원근 투영을 쓰는
  `render.md`의 화면 렌더링과는 무관한, 순수한 2D 기하 판정이다.
- 이동 시도(`P_Move`)가 벽에 막히는지는 `Behavior.이동과 충돌`(`game.md`)과
  같은 규칙을 쓴다 — 몬스터도 플레이어와 같은 충돌 규칙을 따른다.

# Open Points

- `MobjType`에 원거리 공격이 발사체형인지 즉발 명중형인지 구분하는 필드는
  아직 명시적으로 추가하지 않았다 — `actors.md`를 확장할 때
  `missileType: string`(발사체 종류 이름, 없으면 즉발형) 같은 필드로
  추가한다.
- 소리로 인한 각성(`P_NoiseAlert`, 총소리를 듣고 벽 너머 몬스터가 깨어나는
  것)은 이 버전에서 다루지 않는다 — 시야로만 깨어난다.
- 무리 지능(다른 몬스터를 밟고 지나갈 때의 회피, 몬스터끼리의 오인 사격
  등 미세한 원본 동작)은 단순화했다.
