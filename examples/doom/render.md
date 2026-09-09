#!specpp 0.1

# Domain

원본 `r_main.c`/`r_bsp.c`/`r_segs.c`/`r_plane.c`/`r_things.c`/`r_draw.c`에
대응한다. 원본(1993)은 존 카맥이 설명한 방식 그대로 **BSP 트리를 앞에서 뒤
순서로 순회하며, 화면의 각 세로 열(column)마다 "이미 그려졌는지"를
추적**해 오버드로우 없이 소프트웨어로 픽셀을 채웠다 — 당시엔 하드웨어
깊이 버퍼가 없었기 때문에 CPU가 직접 그리는 순서를 관리해야 했다.

이 명세는 그 결과(어떤 벽이 화면의 어디에, 얼마나 크게, 어떤 조명으로
보이는지)는 원본과 똑같이 재현하되, **현대적인 렌더링 방식**을 쓴다: 맵을
불러올 때 벽·바닥·천장 지오메트리(정점·인덱스)를 **한 번** GPU에 올려두고,
매 프레임에는 카메라(플레이어 위치·시야각) 유니폼만 갱신해 몇 번의 드로우
콜로 전체를 그린다. 어떤 벽이 다른 벽을 가리는지는 더 이상 CPU가 계산하지
않는다 — **하드웨어 깊이 버퍼(z-buffer)**가 픽셀 단위로 정확히 가려준다.
그래서 원본의 "화면 열 하나하나를 채웠는지 추적"하는 정교한 부기(bookkeeping)
전체가 통째로 필요 없어진다(아래 Open Points).

BSP 트리([`Doom.Map.BspNode`](map.md))는 그래도 두 가지로 여전히 쓸모
있다: (1) `Doom.Map.Subsector`는 BSP 분할의 결과로 **항상 볼록(convex)**이
보장되므로, 바닥/천장을 삼각형 부채꼴(triangle fan)로 간단히 채울 수 있는
단위가 된다(볼록 다각형이 아니면 이렇게 간단히 삼각분할할 수 없다). (2) 맵이
아주 크면(원본처럼 방이 수백 개면) 화면에 아예 안 보이는 가지 전체를 GPU에
보내기 전에 걸러내는 성긴(coarse) 컬링에 여전히 쓸 수 있다 — 다만 이
버전의 작은 맵 규모에서는 필수가 아니다(아래 Open Points).

## Class: Doom.Renderer

메서드:
- init(screenWidth: int, screenHeight: int) -> void
- buildLevelMesh(map: Doom.Map) -> void
  설명: 이 파일의 핵심 준비 단계. `Feature.레벨 지오메트리 만들기`가 이
  메서드의 알고리즘을 정의한다. **맵을 불러올 때 딱 한 번만** 호출한다 —
  문이 움직여 섹터 높이가 바뀌어도 이 메서드를 다시 부르지 않는다(아래
  Constraints 참조).
- beginFrame() -> void
- renderView(player: Doom.Player, map: Doom.Map) -> void
  설명: `Feature.한 프레임 렌더링`이 이 메서드의 알고리즘을 정의한다.
- endFrame() -> void
  설명: 그려진 프레임을 화면에 낸다.

## Interface: Doom.Renderer.Backend

`Doom.Renderer`가 실제로 화면에 픽셀을 내놓기 위해 기대는 최소 계약이다.
[`std/graphics/opengl3.md`](../../std/graphics/opengl3.md)의 `GL3`나
[`std/windows/direct3d11.md`](../../std/windows/direct3d11.md)의 `D3D11`이
이 계약을 만족한다(둘 다 셰이더 컴파일/정적 버텍스·인덱스 버퍼/유니폼
갱신/인덱스 드로우라는 같은 모양을 갖고 있다 — 아래 Constraints 참조).

메서드:
- compileShader(vertexSource: string, fragmentSource: string) -> int
  설명: 셰이더를 컴파일해 식별자를 반환한다. `renderView`가 시작되기
  전, `init` 직후 한 번만 부른다.
- clear(color: string) -> void
  설명: 색 버퍼와 깊이 버퍼를 함께 지운다(`GL3.Clear`/`D3D11.Clear`에
  대응).
- uploadMesh(verticesRaw: bytes, indices: list<int>, layout: list<(int, int)>) -> (int, int)
  설명: 정점·인덱스 데이터를 GPU 버퍼로 올리고 `(vertexBufferId,
  indexBufferId)`를 반환한다. `buildLevelMesh`에서 맵마다 한 번만 부른다.
- uploadTextureArray(width: int, height: int, layersRgba: list<bytes>) -> int
  설명: 텍스처 여러 장을 한 배열로 올리고 식별자를 반환한다(같은 드로우
  콜 안에서 벽마다 다른 텍스처를 쓸 수 있게 한다).
- setUniformMat4(shader: int, name: string, matrix16: list<float>) -> void
- drawIndexed(shader: int, vertexBufferId: int, indexBufferId: int, indexCount: int, textureId: int) -> void
  설명: 정적 지오메트리(레벨 전체 또는 텍스처 배치 하나) 전체를 삼각형
  으로 그린다. 앞뒤 순서는 깊이 버퍼가 알아서 처리한다 — 호출 순서는
  결과에 영향을 주지 않는다.
- drawIndexedInstanced(shader: int, vertexBufferId: int, indexBufferId: int, indexCount: int, textureId: int, instanceDataRaw: bytes, instanceCount: int) -> void
  설명: 빌보드 사각형 하나를 `instanceCount`번(인스턴스마다
  위치·크기·텍스처 레이어가 담긴 `instanceDataRaw`를 참고해) 한 드로우
  콜로 그린다. 몬스터·아이템 스프라이트를 그릴 때 쓴다.
- drawUIShapes(verticesRaw: bytes, vertexCount: int, primitive: enum(Triangles | Lines)) -> void
  설명: [`hud.md`](hud.md)의 체력·방어구 막대, 얼굴, 열쇠 아이콘,
  [`automap.md`](automap.md)의 지도 선처럼 텍스처 없이 정점 색만으로
  그리는 2D 오버레이를 그린다. 매 프레임 내용이 바뀌므로 그때그때 작은
  동적 버퍼로 다시 채운다(레벨 지오메트리처럼 한 번 올려두고 재사용하는
  대상이 아니다).
- drawUIText(quadsRaw: bytes, quadCount: int, textureId: int) -> void
  설명: 글자(숫자, 메뉴 항목 이름 등)를 그린다. OpenGL/Direct3D 자체에는
  글꼴 렌더링이 없으므로, 대상 언어·플랫폼의 폰트 API(예: 실제 구현이
  쓴 Python `pygame.font`, C++라면 `Direct2D`/`DirectWrite`나
  FreeType)로 문자열을 비트맵으로 래스터라이즈한 뒤 `textureId`로
  업로드하고, 그 텍스처를 씌운 사각형(들)을 그린다 — `drawUIShapes`와
  달리 반드시 텍스처가 필요하다(아래 Constraints 참조).

## Class: Doom.Sprite

원본 `vissprite_t`(화면에 실제로 보이는 스프라이트 하나,
[`actors.md`](actors.md)에 대응)에 대응한다. `render.md`가 매 프레임
임시로 만든다 — 저장되는 데이터가 아니며, `drawIndexedInstanced`에 넘길
인스턴스 데이터 한 줄이 된다.

멤버:
- actor: Doom.Actor
- worldX: float
- worldY: float
- worldZ: float — 빌보드 중심의 3D 위치(카메라 쪽 GPU 셰이더가 이 점을
  화면 방향으로 확장해 사각형을 만든다 — CPU가 화면 좌표를 미리 계산하지
  않는다).
- scale: float
- textureLayer: int — `actor.state.sprite`/`frame`이 가리키는, 텍스처
  배열 안에서의 층 번호.

# Behavior

## Feature: 레벨 지오메트리 만들기

설명: `Doom.Renderer.buildLevelMesh`에 대응한다. 맵을 불러올 때 한 번
실행되며, 원본의 `R_StoreWallRange`/`R_MakeSpans`가 매 프레임 하던 계산을
**미리 다 끝내 둔다**.

절차:
1. 맵의 모든 [`Doom.Map.LineDef`](map.md)에 대해, 그 벽이 실제로 화면에
   드러날 수 있는 부분(단면 벽은 바닥~천장 전체, 양면 벽은 앞/뒤 섹터의
   높이 차이가 있는 위쪽/아래쪽 구간)을 세로로 긴 사각형(두 삼각형)
   정점으로 만든다. UV는 `seg.offset`/텍스처 크기로 계산하고, 정점마다
   그 벽이 속한 섹터의 `lightLevel`을 조명 속성으로 함께 담는다.
2. 맵의 모든 [`Doom.Map.Subsector`](map.md)에 대해(볼록성이 보장되므로),
   바닥은 `floorHeight`에서, 천장은 `ceilingHeight`에서 삼각형 부채꼴로
   채운다. 정점 UV는 맵 좌표를 그대로 텍스처 좌표로 쓰고(flat 텍스처는
   원본에서 벽에 상대적이지 않고 맵 절대 좌표 기준이다), 조명 속성은
   그 `Subsector.sector.lightLevel`이다.
3. 벽/바닥/천장에 쓰인 텍스처 이름을 모아 중복 없이
   `Doom.Renderer.Backend.uploadTextureArray`로 한 번에 올린다.
4. 위 정점들을 텍스처 배치(같은 텍스처를 쓰는 것끼리)별로 묶어
   `Doom.Renderer.Backend.uploadMesh`로 올리고, 반환된 버퍼 식별자들을
   기억해 둔다.

test_required Doom.Renderer {
  - `buildLevelMesh`가 만드는 각 `Doom.Map.Subsector` 바닥/천장 삼각형
    부채꼴은 정확히 `segs`의 정점 개수 - 2개의 삼각형으로 이루어진다
    (볼록 다각형의 삼각분할 공식).
  - 문이 열리거나 닫혀 섹터의 `ceilingHeight`가 바뀌어도, 이미 올려 둔
    버텍스 버퍼의 정점 좌표 자체는 그 문에 해당하는 부분을 제외하면
    바뀌지 않는다 — `buildLevelMesh`를 다시 부르지 않는다(대신
    `specials.md`가 문이 움직이는 섹터의 정점만 갱신하거나, 문처럼 자주
    움직이는 지오메트리는 별도의 작은 동적 버퍼로 분리해 관리한다, 아래
    Open Points 참조).
}

## Feature: 한 프레임 렌더링

설명: `R_RenderPlayerView`에 대응하지만, 원본처럼 화면을 픽셀 단위로
채워 나가는 대신 GPU에 몇 번의 드로우 콜을 내리는 것으로 끝난다.

절차:
1. `beginFrame()`을 호출하고, `Doom.Renderer.Backend.clear`로 색 버퍼와
   깊이 버퍼를 함께 지운다.
2. 뷰 행렬의 카메라 위치(눈높이)를 정한다: `player.actor.z` + 눈높이(원본
   기본값 41 map 단위)를 쓰되, 지금 서 있는
   [`Doom.Map.Sector`](map.md)의 `ceilingHeight`를 넘지 않게 자른다
   (`min(actor.z + 눈높이, sector.ceilingHeight - 4)`) — 원본
   `P_CalcHeight`가 하는 일과 같다. 이 클램프가 없으면 천장이 낮은
   구간에서 카메라가 천장 지오메트리 안쪽으로 들어가 버려, 실제로는
   막혀 있는 벽/천장을 마치 뚫고 들어간 것처럼 보이게 된다(수평 충돌은
   멀쩡히 동작하는데도 그렇다 — `game.md`의 `Feature.이동과 충돌`과는
   별개의, 순수히 카메라 쪽 버그다). `player.viewAngle`과 이 위치로부터
   뷰 행렬을, 시야각(원본 기본값 90도)으로부터 투영 행렬을 계산해 곱한
   뒤, `Doom.Renderer.Backend.setUniformMat4`로 셰이더에 올린다.
3. `Feature.레벨 지오메트리 만들기`에서 미리 만들어 둔 텍스처 배치마다
   `Doom.Renderer.Backend.drawIndexed`를 한 번씩 호출한다 — 몇 개의
   서브섹터가 화면에 보이는지와 무관하게, 텍스처 배치 수만큼만 호출한다
   (원본은 화면에 보이는 세그먼트 수만큼 그렸다 — 이 방식이 훨씬 적은
   드로우 콜로 끝난다).
4. `Feature.스프라이트 그리기`를 실행한다.
5. `endFrame()`을 호출한다.

test_required Doom.Renderer {
  - `Feature.한 프레임 렌더링`이 부르는 `drawIndexed`/`drawIndexedInstanced`
    횟수는 화면에 보이는 벽 세그먼트 개수가 아니라 텍스처 배치 개수 +
    스프라이트 드로우 1회에 비례한다 — 방이 커져도(세그먼트가 늘어도)
    텍스처 종류가 같으면 드로우 콜 수는 늘지 않는다.
  - 두 벽이 화면에서 겹치는 경우, 그리는 순서(드로우 콜 순서)를 어떻게
    바꿔도 최종 화면은 항상 카메라에 더 가까운 벽이 보인다(깊이 테스트가
    보장한다) — 원본처럼 앞에서 뒤 순서로 그릴 필요가 없다.
  - 카메라 눈높이는 지금 서 있는 섹터의 `ceilingHeight - 4`를 절대
    넘지 않는다 — 아무리 낮은 천장 밑이라도(원본의 웅크린 통로 등)
    카메라가 천장 지오메트리 안으로 들어가지 않는다.
}

## Feature: 스프라이트 그리기

설명: `R_DrawVisSprite`에 대응한다. 몬스터·아이템·발사체는 항상 카메라를
향한 평평한 사각형(빌보드)으로 그려진다.

절차:
1. 시야 절두체(frustum) 안에 있는 [`Doom.Actor`](actors.md) 목록을
   `Doom.Sprite`로 변환한다(위치·`actor.state.sprite`+`frame`로 정해지는
   텍스처 배열 층 번호).
2. 그 목록 전체를 인스턴스 데이터 하나로 이어붙여
   `Doom.Renderer.Backend.drawIndexedInstanced`를 **한 번만** 호출한다.
   버텍스 셰이더가 각 인스턴스의 `worldX`/`worldY`/`worldZ`를 카메라의
   오른쪽·위쪽 벡터로 확장해 항상 화면을 보는 사각형을 만든다(원본은
   CPU가 8방향 회전 스프라이트 중 하나를 골랐지만, 이 방식은 스프라이트
   원본 그림 자체가 방향별로 준비되어 있지 않은 한 회전 방향을 셰이더가
   자동으로 처리하지 않는다는 점은 동일하다 — 텍스처 층 선택은 여전히
   `actor.angle`과 카메라 방향의 상대각으로 CPU가 고른다).
3. 픽셀 셰이더는 스프라이트 텍스처의 알파가 문턱값 이하인 픽셀을
   버린다(`discard`/`clip`) — 불투명한 부분만 깊이 버퍼에 기록되므로,
   원본처럼 스프라이트를 뒤에서 앞 순서로 정렬해 그릴 필요가 없다(투명한
   가장자리끼리 겹치는 아주 드문 경우만 예외, 아래 Open Points 참조).

# Interface

## GUI

원본은 자체 소프트웨어 렌더러가 전체 화면 버퍼를 채우고 팔레트를 입혀
한 번에 표시한다. 이 명세는 최종 출력 단계만
[`std/graphics/opengl3.md`](../../std/graphics/opengl3.md) 또는
[`std/windows/direct3d11.md`](../../std/windows/direct3d11.md)에 맡긴다.

# Constraints

- `Doom.Renderer.Backend`는 OpenGL로는 `GL3.CompileShader`/
  `GL3.CreateVertexBuffer`+`CreateIndexBuffer`/`GL3.CreateTextureArray`+
  `GL3.DrawIndexed`/`DrawIndexedInstanced`로, Direct3D로는 `D3D11`의
  같은 이름 메서드로 구현한다 — 둘 다 "정적 지오메트리를 한 번 올리고
  유니폼만 갱신해 몇 번의 드로우 콜로 그린다"는 같은 모양이라
  `Doom.Renderer` 자체의 알고리즘(위 Behavior)은 어느 쪽을 쓰든
  바뀌지 않는다.
- 문/플랫폼처럼 섹터 높이가 자주 바뀌는 지오메트리는 매 tic 전체
  버텍스 버퍼를 다시 만들지 않는다 — 그 섹터에 속한 정점만 골라 별도의
  작은 동적 버퍼로 분리하거나(권장), 정점 셰이더에 섹터별 높이 오프셋을
  유니폼/스토리지 버퍼로 넘겨 GPU에서 계산하게 한다. 이 명세는 둘 중
  어느 구현을 쓸지 규정하지 않는다.
- 텍스처는 [`Doom.Palette`](wad.md)로 팔레트 인덱스를 실제 RGBA로 바꾼
  뒤 텍스처 배열에 올린다(맵을 불러올 때 한 번만).
- 이 버전은 [`std/graphics/opengl.md`](../../std/graphics/opengl.md)/
  [`std/windows/direct3d.md`](../../std/windows/direct3d.md)의 레거시
  즉시 모드(매 프레임 사각형을 CPU가 하나씩 그리는 방식)를 대체한다 —
  다만 그쪽이 훨씬 단순하므로, 아주 작은 맵을 빠르게 검증만 하고 싶다면
  여전히 유효한 선택이다(성능·확장성을 포기하는 대신 구현이 짧다).
- HUD/메뉴/자동 지도처럼 매 프레임 내용이 바뀌는 2D 오버레이는
  `drawUIShapes`/`drawUIText`로 그린다 — 이건 레벨 지오메트리와 달리
  "한 번 올리고 재사용" 대상이 아니라 매 프레임 새로 만드는 작은 동적
  버퍼다.
- `drawUIText`가 만드는 텍스처는 문자열마다(그리고 색마다) 다르므로,
  같은 문자열을 다시 그릴 때 매번 폰트를 다시 래스터라이즈하지 않도록
  (문자열, 색) 조합을 키로 텍스처를 캐시해 재사용하는 것을 권장한다 —
  체력·탄약처럼 값이 자주 바뀌는 문자열은 캐시가 계속 늘어날 수 있으니,
  실제 구현은 오래 안 쓰인 항목을 정리하는 정책을 둘 수 있다(이 명세는
  구체적인 캐시 무효화 정책을 규정하지 않는다).

# Examples

## 예제: 정면 벽 하나

전제: 플레이어가 정면으로 5 map 단위 떨어진, 폭 64 텍스처 벽을 마주 보고
있다. `buildLevelMesh`가 이미 맵 전체 지오메트리를 올려 둔 상태다.

호출: `Feature.한 프레임 렌더링`

기대 동작: 뷰·투영 행렬만 새로 계산해 유니폼으로 올리고, 미리 만들어 둔
벽 지오메트리를 텍스처 배치당 한 번의 `drawIndexed`로 그린다 — 화면
가운데 부분에 그 벽의 텍스처가 (거리에 따라 정해진 높이로) 그려지고,
화면 좌우 가장자리로 갈수록 원근에 따라 약간 좁아 보인다. 이 벽 정점
자체를 다시 계산하거나 다시 올리지 않는다.

# Open Points

- 조명은 원본의 32단계 조명표 + 시야 각도별 감쇠(안개 낀 듯한 효과) 대신
  정점의 `lightLevel` 속성을 프래그먼트 셰이더에서 거리 기반 감쇠와 함께
  곱하는 것으로 단순화했다 — 픽셀 단위로 계산된다는 점은 원본보다
  오히려 더 정밀하다.
- 원본의 화면 열 캐싱(`solidsegs`, "이미 그려진 열" 추적)은 이 버전에
  아예 없다 — 깊이 버퍼가 그 역할을 완전히 대신하므로 옮길 필요가
  없어졌다.
- 문/플랫폼이 움직이는 동안 정점을 갱신하는 정확한 구현 방식(동적 버퍼
  분리 vs GPU 계산)은 규정하지 않는다 — 위 Constraints 참조.
- 아주 큰 맵에서 화면 밖 서브섹터를 GPU에 아예 보내지 않는
  절두체/PVS(potentially-visible-set) 컬링은 다루지 않는다 — 이 저장소
  규모의 맵(`E1M1` 등)은 전체를 다 보내도 문제 없다고 전제한다.
- 투명한 스프라이트 가장자리끼리 겹칠 때(예: 창살 너머로 다른 스프라이트가
  비치는 경우)의 정확한 알파 블렌딩 순서는 다루지 않는다 — 알파 테스트
  (완전 불투명 또는 완전 버림)만 전제한다.
- 하늘(sky) 텍스처의 특수 처리(항상 무한히 먼 원통형 텍스처로 그리는
  것)는 다루지 않는다 — 평범한 벽/평면 텍스처처럼 취급한다.
