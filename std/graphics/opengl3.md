#!specpp 0.1

# Meta

- name: std/graphics/opengl3
- version: 0.1.0
- description: 셰이더·버텍스 버퍼 기반의 OpenGL 3.3+ 코어 프로파일에 대한
  최소 실체 명세 — 정적 지오메트리를 한 번 올려두고 매 프레임 몇 번의
  드로우 콜로 그리는 현대적 렌더링 방식.
- kind: native

# Intent

[`std/graphics/opengl.md`](opengl.md)(레거시 즉시 모드, 매 프레임 사각형을
하나씩 CPU가 순서대로 그린다)와 달리, 지오메트리(정점·인덱스)를 **한 번**
GPU 메모리에 올려두고, 매 프레임에는 카메라 행렬 같은 유니폼(uniform)만
갱신해 몇 번의 드로우 콜로 전체 장면을 그리는 현대적인 방식이다. 앞뒤 순서를
CPU가 직접 계산해 겹치지 않게 그릴 필요가 없다 — **깊이 버퍼(depth
buffer)**가 하드웨어에서 픽셀 단위로 앞뒤를 정확히 가려준다. 이미 존재하는
API이므로 새로 구현할 대상이 아니다(`kind: native`, 1.2절). 플랫폼과
무관하므로 `platform` 필드를 두지 않는다.

[`examples/doom/render.md`](../../examples/doom/render.md)처럼 정적인 맵
지오메트리(벽·바닥·천장)를 매 프레임 다시 계산하지 않고, 몬스터·아이템
같은 동적 객체만 화면 방향을 보는 사각형(빌보드)으로 그려야 하는 3D 장면에
알맞다.

# Domain

## Class: GL3.Shader

(불투명 핸들이다 — 실제로는 컴파일·링크된 `GLuint` 프로그램 객체다.)

## Class: GL3.Buffer

(불투명 핸들이다 — 실제로는 `GLuint` VBO 또는 EBO 이름이다.)

## Class: GL3.VertexArray

(불투명 핸들이다 — 실제로는 `GLuint` VAO 이름이다. 버텍스 버퍼의 레이아웃
(위치·UV·조명값 등 각 속성이 몇 바이트째부터 시작하는지)을 기억한다.)

## Class: GL3.Texture

(불투명 핸들이다 — 실제로는 `GLuint` 텍스처 이름이다. 2D 배열 텍스처
(`GL_TEXTURE_2D_ARRAY`)를 쓰면 벽 텍스처마다 따로 바인딩하지 않고 레이어
인덱스만 바꿔 한 드로우 콜로 여러 텍스처를 쓸 수 있다 — 아래 Constraints
참조.)

## Class: GL3

메서드:
[Static]
- Init(screenWidth: int, screenHeight: int) -> void
  설명: 코어 프로파일 컨텍스트를 만들고(`wglCreateContextAttribsARB` 등
  플랫폼별 확장, 또는 SDL/GLFW 같은 창 라이브러리에 위임), 뷰포트를
  설정하고, 깊이 테스트(`GL_DEPTH_TEST`)를 켠다.
- CompileShader(vertexSource: string, fragmentSource: string) -> GL3.Shader
  설명: GLSL 버텍스·프래그먼트 셰이더 소스를 컴파일·링크한다
  (`glCompileShader` + `glLinkProgram`). 컴파일 실패 시 로그를 담아 예외를
  던진다(`std/system/exception.md` 참조).
- UseShader(shader: GL3.Shader) -> void
- CreateVertexBuffer(verticesRaw: bytes, layout: list<(int, int)>) -> (GL3.Buffer, GL3.VertexArray)
  설명: `verticesRaw`(정점 데이터를 그대로 이어붙인 바이트열)로 VBO를
  만들고, `layout`(각 속성의 `(컴포넌트 개수, 오프셋)` 목록 — 예:
  위치 3개+UV 2개+조명 1개면 `[(3,0),(2,12),(1,20)]`)으로 VAO를 구성한다.
- CreateIndexBuffer(indices: list<int>) -> GL3.Buffer
- CreateTextureArray(width: int, height: int, layerCount: int, layersRgba: list<bytes>) -> GL3.Texture
  설명: 같은 크기의 텍스처 여러 장(예: 맵에 쓰인 모든 벽 텍스처)을 한
  객체에 층(layer)으로 올린다.
- SetUniformMat4(shader: GL3.Shader, name: string, matrix16: list<float>) -> void
  설명: 4x4 행렬(뷰·투영 등)을 유니폼으로 설정한다(`glUniformMatrix4fv`).
- SetUniformFloat(shader: GL3.Shader, name: string, value: float) -> void
- SetUniformVec3(shader: GL3.Shader, name: string, x: float, y: float, z: float) -> void
- Clear(color: string) -> void
  설명: 색 버퍼와 깊이 버퍼를 함께 지운다(`glClear(GL_COLOR_BUFFER_BIT |
  GL_DEPTH_BUFFER_BIT)`).
- DrawIndexed(vao: GL3.VertexArray, indexBuffer: GL3.Buffer, indexCount: int, texture: GL3.Texture) -> void
  설명: `vao`/`indexBuffer`가 가리키는 지오메트리 전체를 삼각형으로
  그린다(`glDrawElements`) — 벽·바닥·천장처럼 미리 만들어 둔 정적
  지오메트리를 매 프레임 그대로 다시 그릴 때 쓴다.
- DrawIndexedInstanced(vao: GL3.VertexArray, indexBuffer: GL3.Buffer, indexCount: int, texture: GL3.Texture, instanceCount: int) -> void
  설명: 같은 지오메트리(빌보드 사각형 하나)를 `instanceCount`번, 인스턴스별
  위치·크기 데이터(별도 인스턴스 버퍼)를 참고해 한 번의 드로우 콜로 그린다
  (`glDrawElementsInstanced`) — 몬스터·아이템 스프라이트를 그릴 때 쓴다.
- SwapBuffers() -> void

# Interface

## Library

`Init` → `CompileShader`(장면용 셰이더 하나, 필요하면 UI용 셰이더 하나 더)
→ 맵을 불러올 때 한 번 `CreateVertexBuffer`/`CreateIndexBuffer`/
`CreateTextureArray`로 정적 지오메트리를 올려둡니다. 매 프레임은
`Clear` → `UseShader` → `SetUniformMat4`(뷰·투영 행렬) →
`DrawIndexed`(맵 지오메트리, 보통 한두 번) → `DrawIndexedInstanced`(스프라이트,
한 번) → `SwapBuffers` 순서로 그립니다 — 프레임마다 정점을 다시 만들거나
업로드하지 않습니다.

# Constraints

- 헤더 `<glad/glad.h>` 또는 `<GL/glew.h>`(코어 프로파일 함수 포인터 로딩용).
  링크: `opengl32.lib`(Windows) 등 + 로더 라이브러리.
- GLSL 버전 `#version 330 core` 이상을 전제한다.
- 벽마다 텍스처를 따로 바인딩해 드로우 콜을 쪼개는 대신
  `GL_TEXTURE_2D_ARRAY`로 묶어서 한 번에 그리는 것을 권장한다 — 드로우
  콜 수가 벽 개수가 아니라 텍스처 배치(batch) 수에 비례하게 된다.
- 알파 테스트(컷아웃 스프라이트)는 고정 함수 `GL_ALPHA_TEST`가 코어
  프로파일에는 없으므로, 프래그먼트 셰이더에서 `discard`로 구현한다.

# Examples

## 예제: 정적 지오메트리 한 번 올리고 매 프레임 그대로 그리기

호출: `shader = GL3.CompileShader(vsSrc, fsSrc)`,
`(vbo, vao) = GL3.CreateVertexBuffer(wallVertices, [(3,0),(2,12),(1,20)])`,
`ebo = GL3.CreateIndexBuffer(wallIndices)` — 맵을 불러올 때 한 번만.
그 뒤 매 프레임: `GL3.Clear("#000000")`, `GL3.UseShader(shader)`,
`GL3.SetUniformMat4(shader, "viewProj", cameraMatrix)`,
`GL3.DrawIndexed(vao, ebo, len(wallIndices), wallTextures)`,
`GL3.SwapBuffers()`.

기대 동작: 벽 정점을 매 프레임 다시 계산하지 않고도, 카메라가 움직이면
`viewProj` 유니폼만 바뀌어 화면의 원근이 정확히 갱신된다. 두 벽이 겹치는
지점은 깊이 버퍼가 자동으로 더 가까운 쪽을 그린다 — CPU가 그리는 순서를
따로 정할 필요가 없다.

# Open Points

- 그림자 매핑, 노멀 매핑 등 더 발전된 셰이더 기법은 이 버전의 범위 밖이다
  — 텍스처 샘플링 + 섹터 조명값 곱셈 정도의 단순 조명만 전제한다.
- 프레임버퍼 객체(오프스크린 렌더링, 포스트 프로세싱)는 다루지 않는다.
