#!specpp 0.1

# Meta

- name: std/graphics/opengl
- version: 0.1.0
- description: 텍스처 입힌 사각형을 그리는 데 필요한 최소 OpenGL 부분집합에 대한 실체 명세.
- kind: native

# Intent

2D 텍스처 사각형(칼럼, 스프라이트, 스프라이트 시트의 한 조각 등)을 반복해서
그려야 하는 화면(대표적으로 [`examples/doom/render.md`](../../examples/doom/render.md)
같은 레트로 스타일 3D 렌더러)을 위한 것이다. 이미 존재하는 API이므로 새로
구현할 대상이 아니다(`kind: native`, 1.2절). 셰이더 파이프라인이 아니라
레거시(고정 함수) OpenGL 1.x의 즉시 모드(immediate mode)를 쓴다 — 이런
용도에는 그걸로 충분히 간단하고 정확하기 때문이다. 플랫폼과 무관하므로
`platform` 필드를 두지 않는다.

# Domain

## Class: GL.Texture

(불투명 핸들이다 — 실제로는 `GLuint` 텍스처 이름이다.)

## Class: GL

메서드:
[Static]
- Init(screenWidth: int, screenHeight: int) -> void
  설명: 뷰포트를 설정하고, 왼쪽 위가 (0,0)이고 아래로 갈수록 y가 커지는
  화면 좌표계로 정사영(orthographic) 투영을 설정한다(`glViewport` +
  `glOrtho`).
- Clear(color: string) -> void
  설명: 화면 전체를 color로 지운다.
- CreateTexture(width: int, height: int, pixelsRgba: bytes) -> GL.Texture
  설명: width*height*4바이트(RGBA)의 원시 픽셀로 텍스처를 만든다
  (`glGenTextures` + `glTexImage2D`).
- BindTexture(texture: GL.Texture) -> void
- DrawTexturedQuad(x: float, y: float, width: float, height: float, u0: float, v0: float, u1: float, v1: float) -> void
  설명: 현재 바인딩된 텍스처에서 `[u0, v0]`~`[u1, v1]`(0.0~1.0 정규화 좌표)
  구간을 화면의 `(x, y)`~`(x+width, y+height)` 사각형에 그린다. 폭이 1인
  아주 얇은 사각형으로 부르면 "세로 열(column) 하나 그리기"가 된다.
- SwapBuffers() -> void
  설명: 그린 결과를 화면에 표시한다. 실제 구현은 플랫폼별 버퍼 교체(Windows의
  `wglSwapBuffers`, X11의 `glXSwapBuffers` 등)를 대상 언어의 관용적인 창
  생성 코드와 함께 쓴다.

# Interface

## Library

`Init`을 한 번 부른 뒤, 텍스처마다 `CreateTexture`로 한 번씩 업로드해
재사용합니다. 매 프레임 `Clear` → 필요한 만큼 `BindTexture`/
`DrawTexturedQuad` → `SwapBuffers` 순서로 그립니다.

# Constraints

- 헤더 `<GL/gl.h>`(플랫폼별 컨텍스트 생성은 별도 — Windows는 `wgl*`, Linux는
  `glX*`). 링크: `opengl32.lib`(Windows) 또는 `-lGL`(Linux) 등.
- 셰이더·버텍스 버퍼 기반의 코어 프로파일(OpenGL 3.2+)은 이 버전의 범위
  밖이다 — 호환(compatibility) 프로파일의 고정 함수 파이프라인만 쓴다.

# Examples

## 예제: 텍스처의 왼쪽 절반만 그린다

호출: `GL.BindTexture(t)`, `GL.DrawTexturedQuad(0, 0, 32, 64, 0.0, 0.0, 0.5, 1.0)`

기대 동작: 텍스처의 왼쪽 절반이 화면의 `(0,0)`~`(32,64)` 사각형에 그려진다.

# Open Points

- 알파 블렌딩·깊이 테스트 활성화 여부는 이 버전에서 규정하지 않는다 — 호출
  하는 쪽(예: [`examples/doom/render.md`](../../examples/doom/render.md))이
  필요에 따라 설정한다.
