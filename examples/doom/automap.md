#!specpp 0.1

# Domain

원본 `am_map.h`/`am_map.c`(자동 지도)에 대응한다. 탭 키(원본 기준) 등을
누르면 3D 시점 대신 지도를 위에서 내려다본 선 그림으로 보여준다.

## Class: Doom.AutoMap

멤버:
- isOpen: boolean — 기본값 false.
- centerX: float
- centerY: float — 지도 화면 가운데가 맵의 어느 좌표를 보여주는지.
- zoom: float — 확대 배율.
- revealedLines: list<Doom.Map.LineDef> — 플레이어가 실제로 가 본 적이
  있어 지도에 표시되는 선들 (전부 표시하지 않는다 — 아래 Behavior 참조).

메서드:
- render(map: Doom.Map, player: Doom.Player, renderer: Doom.Renderer.Backend) -> void
  설명: `revealedLines`를 화면 좌표로 변환해 얇은 선(폭이 1픽셀인
  사각형으로 근사한다)으로 그린다. 매 프레임 선 목록이 바뀔 수 있으므로
  [`Doom.Renderer.Backend.drawUIShapes`](render.md)로 그린다(선이라
  텍스처가 필요 없다). 비밀
  문처럼 아직 안 밝혀진 linedef는 그리지 않는다. 플레이어 위치는 화살표
  모양으로 표시한다.

# Behavior

## Feature: 자동 지도 토글

절차:
1. `isOpen`을 반전시킨다.

## Feature: 지도에 선 드러내기

설명: 매 tic, 플레이어가 새로 지나간 영역의 선을 지도에 추가한다.

절차:
1. 플레이어가 위치한 [`Doom.Map.Subsector`](map.md)의 `segs`가 가리키는
   `lineDef`들 중, `revealedLines`에 아직 없는 것을 추가한다.
2. `lineDef.flags`에 "비밀"로 표시되어 있으면(원본의 secret 플래그) 이
   과정에서 제외한다 — 비밀 문은 실제로 열어야만 드러난다(그 시점에
   플래그가 해제된다).

## Feature: 지도 이동·확대

입력:
- panX: float
- panY: float
- zoomDelta: float

절차:
1. `centerX`/`centerY`를 `panX`/`panY`만큼 옮긴다.
2. `zoom`을 `zoomDelta`만큼 바꾸되, 미리 정한 최소/최대 배율을 벗어나지
   않게 자른다(clamp).

# Constraints

- 색으로 구분되는 벽 종류(빨간 문, 노란 열쇠 문, 비밀 벽 등)는
  단순화했다 — 모든 선을 같은 색으로 그려도 무방하다.

# Open Points

- 전체 맵을 미리 보여주는 치트(`iddt`)는 다루지 않는다.
