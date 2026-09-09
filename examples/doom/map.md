#!specpp 0.1

# Domain

## Namespace: Doom.Map

원본의 맵 lump들(`doomdata.h`의 `mapvertex_t`/`maplinedef_t`/
`mapsidedef_t`/`mapsector_t`/`mapthing_t`, `p_setup.c`의 로딩 코드,
BSP 관련 `mapnode_t`/`mapseg_t`/`mapsubsector_t`)에 대응한다. 한 맵(예:
`"E1M1"`)은 WAD 안에서 그 이름표 lump 바로 뒤에 이어지는 고정된 순서의
lump들(`THINGS`, `LINEDEFS`, `SIDEDEFS`, `VERTEXES`, `SEGS`, `SSECTORS`,
`NODES`, `SECTORS`, ...)로 이루어진다. 각 lump는 같은 크기의 레코드가
빈틈없이 이어진 이진 배열이다.

## Class: Doom.Map.Vertex

`mapvertex_t`에 대응한다 (레코드 4바이트: `short x, y`).

멤버:
- x: float
- y: float

## Class: Doom.Map.Sector

`mapsector_t`에 대응한다.

멤버:
- floorHeight: float
- ceilingHeight: float
- floorTexture: string — 바닥에 쓸 flat(수평 텍스처) 이름.
- ceilingTexture: string
- lightLevel: int — 0~255.
- special: int — 특수 효과 번호(예: 깜빡이는 조명, 데미지 바닥). 0이면 없음.
- tag: int — 이 섹터를 대상으로 하는 linedef 특수 효과와 짝짓는 식별자.

## Class: Doom.Map.SideDef

`mapsidedef_t`에 대응한다. 한 linedef의 한쪽 면에 어떤 텍스처를 어떻게
붙일지를 담는다.

멤버:
- textureOffsetX: float
- textureOffsetY: float
- topTexture: string — 위쪽 텍스처 이름 (인접 섹터 천장 높이 차이가 있을 때).
- bottomTexture: string — 아래쪽 텍스처 이름.
- middleTexture: string — 가운데 텍스처 이름 (한쪽만 있는 벽, 즉 막힌 벽에서
  주로 쓰인다).
- sector: Doom.Map.Sector — 이 면이 속한 섹터.

## Class: Doom.Map.LineDef

`maplinedef_t`에 대응한다. 벽 하나(양쪽 섹터를 가를 수도, 막힌 한쪽 벽일
수도 있다)를 나타낸다.

멤버:
- v1: Doom.Map.Vertex
- v2: Doom.Map.Vertex
- flags: int — 예: 막혀 있는지(양면인지 단면인지), 상단/하단 텍스처를
  위/아래 어디에 맞춰 그릴지 등을 나타내는 비트 플래그.
- special: int — 문 열기, 바닥 올리기 같은 특수 효과 번호. 0이면 없음.
- tag: int — 이 효과가 적용될 섹터를 찾는 데 쓰는 식별자
  (`Sector.tag`와 맞춘다).
- frontSide: Doom.Map.SideDef
- backSide: Doom.Map.SideDef? — 양면 벽(예: 창문, 통로)이면 있고, 완전히
  막힌 단면 벽이면 null.

불변식:
- backSide가 null이면 이 linedef는 통과할 수 없다(원본의 `ML_TWOSIDED`
  플래그가 꺼져 있는 것과 같다).

## Class: Doom.Map.Thing

`mapthing_t`에 대응한다. 맵에 미리 배치된 몬스터·아이템·플레이어 시작
위치 등을 나타낸다. 실제 게임 객체(`Doom.Actor`, `actors.md` 참조)는 맵을
불러올 때 이 정보로부터 생성된다.

멤버:
- x: float
- y: float
- angle: float — 도(degree) 단위, 바라보는 방향.
- type: int — 개체 종류 번호(원본의 `mobjinfo` 테이블 인덱스에 대응 —
  `actors.md`의 `Doom.MobjType` 참조).
- flags: int — 난이도(이지/보통/하드에서 등장 여부), 멀티플레이 전용 여부
  등의 비트 플래그.

## 반가시성 자료구조 (BSP)

원본은 렌더링 시점에 매번 가시성을 계산하지 않고, 맵을 불러올 때 미리
계산해 둔 이진 공간 분할(BSP) 트리를 순회한다(`r_bsp.c`).

## Class: Doom.Map.Seg

`mapseg_t`에 대응한다. LineDef 하나(또는 그 일부 — 다른 섹터에 잘려
나뉜 조각)를 가리키는, BSP 순회 단위다.

멤버:
- v1: Doom.Map.Vertex
- v2: Doom.Map.Vertex
- angle: float
- lineDef: Doom.Map.LineDef — 원본이 되는 벽.
- side: int — 0이면 lineDef의 앞면, 1이면 뒷면을 쓴다는 뜻.
- offset: float — lineDef의 시작점부터 이 seg의 시작점까지 거리(텍스처를
  이어 붙일 때 오프셋으로 쓴다).

## Class: Doom.Map.Subsector

`mapsubsector_t`에 대응한다. BSP 트리의 리프(leaf) 노드 — 더 이상 나눌 수
없는, 볼록(convex)하다고 보장되는 영역이다.

멤버:
- segs: list<Doom.Map.Seg>
- sector: Doom.Map.Sector — 이 영역이 속한 섹터.

## Class: Doom.Map.BspNode

`mapnode_t`에 대응한다. 분할선 하나와 그 앞/뒤에 있는 자식(다른 BspNode
또는 Subsector)을 가진다.

멤버:
- x: float
- y: float
- dx: float
- dy: float — `(x, y)`에서 `(dx, dy)` 방향으로 이어지는 분할선.
- frontChild: Doom.Map.BspNode | Doom.Map.Subsector
- backChild: Doom.Map.BspNode | Doom.Map.Subsector
- frontBoundingBox: (float, float, float, float) — 앞쪽 자식을 감싸는
  사각형(top, bottom, left, right) — 렌더링 시 화면에 보이지도 않는
  가지를 빨리 건너뛰는 데 쓴다.
- backBoundingBox: (float, float, float, float)

메서드:
[Static]
- PointOnSide(x: float, y: float, node: Doom.Map.BspNode) -> int
  설명: 점 `(x, y)`가 이 노드의 분할선 앞쪽(0)인지 뒤쪽(1)인지 판정한다
  (`R_PointOnSide`에 대응). 분할선의 방향 벡터 `(dx, dy)`와 점까지의
  벡터의 외적(cross product) 부호로 판정한다.
[Static]
- FindSubsector(x: float, y: float, root: Doom.Map.BspNode) -> Doom.Map.Subsector
  설명: 트리 루트에서 시작해 `PointOnSide`로 매번 앞/뒤를 고르며 리프
  (Subsector)에 도달할 때까지 내려간다. 어떤 위치가 어느 섹터에 속하는지
  찾을 때(플레이어 현재 위치의 섹터 판정 등) 쓴다.

test_required Doom.Map.BspNode {
  - `FindSubsector`가 반환한 Subsector의 `segs` 중 적어도 하나는 그
    지점이 속한 `sector`와 같은 섹터를 가리킨다.
  - `PointOnSide`는 분할선 위에 정확히 있는 점이 아닌 한, 트리를 아무리
    깊이 타고 내려가도 결정할 수 없는(모호한) 결과를 내지 않는다 — 항상
    0 또는 1을 반환한다.
}

## Class: Doom.Map

한 맵(예: `"E1M1"`) 전체를 담는다.

멤버:
- name: string
- vertices: list<Doom.Map.Vertex>
- lineDefs: list<Doom.Map.LineDef>
- sectors: list<Doom.Map.Sector>
- subsectors: list<Doom.Map.Subsector>
- bspRoot: Doom.Map.BspNode
- things: list<Doom.Map.Thing>

생성자:
[Static]
- Load(wad: Doom.WadFile, mapName: string) -> Doom.Map
  설명: wad에서 mapName 바로 뒤에 이어지는 `THINGS`/`LINEDEFS`/
  `SIDEDEFS`/`VERTEXES`/`SEGS`/`SSECTORS`/`NODES`/`SECTORS` lump들을
  차례로 읽어 이 클래스의 값들을 채운다. `mapnode_t.children`의 최상위
  비트가 켜져 있으면 그 자식은 Subsector 인덱스, 꺼져 있으면 다른
  BspNode 인덱스다 — 이 구분에 따라 `frontChild`/`backChild`를
  BspNode/Subsector 중 하나로 연결한다.

# Interface

## Library

`render.md`는 `Doom.Map.BspNode.FindSubsector`로 시작해 트리를 앞에서
뒤 순서로 순회하며 화면에 그립니다. `game.md`는 `Doom.Map.Load`로 맵을
불러오고, `Doom.Map.Thing` 목록으로 액터를 배치합니다.

# Constraints

- 좌표·거리는 3.1절의 `float`로 표기했다 — 원본은 성능·결정성을 위해
  16.16 고정소수점(`fixed_t`)을 쓴다. 리플레이나 멀티플레이 동기화처럼
  결정론적 재현이 중요하면 고정소수점으로 구현하는 것을 권장한다
  (`game.md`의 Open Points 참조).

# Examples

## 예제: 점이 속한 섹터 찾기

전제: 맵이 불러와져 있고, 플레이어 시작 위치는 어느 한 섹터 안에 있다.

호출: `Doom.Map.BspNode.FindSubsector(playerX, playerY, map.bspRoot).sector`

기대 동작: 플레이어가 실제로 서 있는 섹터(바닥/천장 높이, 조명 등)를
반환한다.

# Open Points

- 없음 — `map.md`는 원본의 맵 자료구조를 그대로 옮기는 데 집중했다. 남은
  단순화(예: 세그먼트 병합 최적화 생략)는 `game.md`의 Open Points에
  정리되어 있다.
