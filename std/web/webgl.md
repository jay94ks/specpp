#!specpp 0.1

# Meta

- name: std/web/webgl
- version: 0.1.0
- description: 셰이더·버텍스 버퍼 기반의 WebGL2에 대한 최소 실체 명세 — std/graphics/opengl3.md와 같은 모양을 브라우저에서 이룬다.
- platform: web
- kind: native

# Intent

[`std/graphics/opengl3.md`](../graphics/opengl3.md)와 같은 목적(정적
지오메트리를 한 번 올리고 유니폼만 갱신해 몇 번의 드로우 콜로 그리기)을
브라우저에서 이루기 위한 것이다. **WebGL2는 사양상 OpenGL ES 3.0이고,
OpenGL ES 3.0은 OpenGL 3.3 코어 프로파일의 기능적 부분집합**이라 —
`GL3`의 메서드 이름·시그니처·의미가 이 패키지의 `WebGL2`와 사실상
그대로 대응한다(`gl.createShader`/`gl.createBuffer`/`gl.bufferData`/
`gl.drawElements`/`gl.drawElementsInstanced` 등). 이미 존재하는
실체이므로 새로 구현할 대상이 아니다(`kind: native`, 1.2절).

# Domain

## Class: WebGL2Context

(불투명 핸들이다 — 실제로는 `canvas.getContext("webgl2")`가 반환하는
`WebGL2RenderingContext`를 가리킨다.)

## Class: WebGLShader / WebGLBuffer / WebGLVertexArrayObject / WebGLTexture

(모두 불투명 핸들이다 — 같은 이름의 실제 WebGL2 객체를 가리킨다.
[`std/graphics/opengl3.md`](../graphics/opengl3.md)의
`GL3.Shader`/`GL3.Buffer`/`GL3.VertexArray`/`GL3.Texture`와 각각
같은 역할이다.)

## Class: WebGL2

메서드:
[Static]
- GetContext(canvasElement: DOM.Element) -> WebGL2Context
  설명: [`std/web/dom.md`](dom.md)로 만든 `<canvas>`에서
  `canvas.getContext("webgl2")`를 얻는다. 지원하지 않는 브라우저면
  오류를 낸다([`std/graphics/opengl3.md`](../graphics/opengl3.md)로
  폴백할 수 없다 — 브라우저 안에서는 그쪽이 애초에 존재하지 않는다).
- CompileShader(ctx: WebGL2Context, vertexSource: string, fragmentSource: string) -> WebGLShader
  설명: `gl.createShader`+`gl.shaderSource`+`gl.compileShader`를 정점/
  프래그먼트 각각에 대해, 그 뒤 `gl.createProgram`+`gl.attachShader`+
  `gl.linkProgram`으로 링크한다. GLSL ES `#version 300 es`를 쓴다(코어
  프로파일 `#version 330 core`와 문법이 거의 같지만 정밀도 한정자
  (`precision mediump float;`)가 필요하다 — 아래 Constraints 참조).
- CreateVertexBuffer(ctx: WebGL2Context, verticesRaw: bytes, layout: list<(int, int)>) -> (WebGLBuffer, WebGLVertexArrayObject)
- CreateIndexBuffer(ctx: WebGL2Context, indices: list<int>) -> WebGLBuffer
- CreateTextureArray(ctx: WebGL2Context, width: int, height: int, layerCount: int, layersRgba: list<bytes>) -> WebGLTexture
  설명: `gl.TEXTURE_2D_ARRAY` + `gl.texImage3D`에 대응한다.
- SetUniformMat4(ctx: WebGL2Context, shader: WebGLShader, name: string, matrix16: list<float>) -> void
- Clear(ctx: WebGL2Context, color: string) -> void
- DrawIndexed(ctx: WebGL2Context, vao: WebGLVertexArrayObject, indexBuffer: WebGLBuffer, indexCount: int, texture: WebGLTexture) -> void
- DrawIndexedInstanced(ctx: WebGL2Context, vao: WebGLVertexArrayObject, indexBuffer: WebGLBuffer, indexCount: int, texture: WebGLTexture, instanceCount: int) -> void
  설명: `gl.drawElementsInstanced`에 대응한다.

# Interface

## Library

[`std/graphics/opengl3.md`](../graphics/opengl3.md)의 `GL3`와 완전히
같은 순서로 씁니다: `GetContext` → `CompileShader` → 맵을 불러올 때 한
번 `CreateVertexBuffer`/`CreateIndexBuffer`/`CreateTextureArray` → 매
프레임 `Clear` → `SetUniformMat4` → `DrawIndexed`/`DrawIndexedInstanced`.

# Constraints

- 헤더/링크가 필요 없다 — 브라우저가 이미 제공하는 전역
  `WebGL2RenderingContext` API다(`<canvas>`의 `getContext("webgl2")`).
- GLSL ES 3.00은 코어 프로파일 GLSL 3.30과 대부분 같지만, 프래그먼트
  셰이더 맨 앞에 `precision mediump float;`(또는 `highp`) 정밀도
  한정자가 있어야 하고, `#version 300 es`를 쓴다 — 데스크톱 GLSL 소스를
  그대로 재사용하려면 이 두 줄만 갈아 끼우면 되는 경우가 많다.
- 텍스처 배열(`TEXTURE_2D_ARRAY`)은 WebGL2에서 기본 지원되지만(WebGL1은
  지원하지 않는다), 일부 저사양 모바일 브라우저는 최대 레이어 수·크기
  제한이 데스크톱 GPU보다 훨씬 낮을 수 있다 — 이 계약은 구체적인 한도를
  규정하지 않는다.

# Examples

## 예제: 정적 지오메트리 한 번 올리고 매 프레임 그대로 그리기

호출: [`std/graphics/opengl3.md`](../graphics/opengl3.md)의 같은
예제와 동일하되, `GL3.*` 대신 `WebGL2.*`를 쓴다.

기대 동작: 같은 결과 — 벽 정점을 매 프레임 다시 계산하지 않고도 카메라
행렬만 갱신해 화면이 정확히 갱신되고, 깊이 버퍼가 앞뒤를 자동으로
가려준다.

# Open Points

- WebGPU(WebGL의 차세대 후속)는 이 버전의 범위 밖이다 — 아직 모든
  주요 브라우저에 안정적으로 있지 않기 때문이다.
- 컨텍스트 손실(`webglcontextlost` 이벤트 — 탭이 백그라운드로 가거나
  GPU 드라이버가 리셋될 때 발생할 수 있다)의 복구는 다루지 않는다.
