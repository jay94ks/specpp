#!specpp 0.1

# Meta

- name: std/windows/direct3d11
- version: 0.1.0
- description: 셰이더·버텍스 버퍼 기반의 Direct3D 11에 대한 최소 실체 명세
  — [`std/graphics/opengl3.md`](../graphics/opengl3.md)와 같은 모양(정적
  지오메트리를 한 번 올리고 매 프레임 몇 번의 드로우 콜로 그린다)을
  DirectX 위에서 이룬다.
- platform: windows -> fallback: std/graphics/opengl3.md
- kind: native

# Intent

[`std/windows/direct3d.md`](direct3d.md)(Direct3D 9 고정 함수, 매 프레임
사각형을 하나씩 그린다)와 달리, 셰이더(HLSL)와 버텍스/인덱스 버퍼로 정적
지오메트리를 한 번 GPU에 올려두고, 매 프레임에는 상수 버퍼(카메라 행렬)만
갱신해 몇 번의 `DrawIndexed`로 전체 장면을 그린다 — **깊이-스텐실 버퍼**가
앞뒤 순서를 하드웨어에서 자동으로 가려준다. 이미 존재하는 API이므로 새로
구현할 대상이 아니다(`kind: native`, 1.2절).

# Domain

## Class: D3D11.Device

(불투명 핸들이다 — 실제로는 `ID3D11Device*` + `ID3D11DeviceContext*` +
`IDXGISwapChain*`을 함께 감싼 것이다.)

## Class: D3D11.Shader

(불투명 핸들이다 — 실제로는 컴파일된 `ID3D11VertexShader*` +
`ID3D11PixelShader*` + `ID3D11InputLayout*`을 함께 감싼 것이다.)

## Class: D3D11.Buffer

(불투명 핸들이다 — 실제로는 `ID3D11Buffer*`다. 버텍스/인덱스/상수 버퍼
모두 이 하나의 타입으로 다룬다 — 원본 API도 용도만 다를 뿐 같은
`ID3D11Buffer`다.)

## Class: D3D11.Texture

(불투명 핸들이다 — 실제로는 `ID3D11Texture2D*` + `ID3D11ShaderResourceView*`를
함께 감싼 것이다. 텍스처 배열(`ArraySize > 1`)로 만들면
[`std/graphics/opengl3.md`](../graphics/opengl3.md)의 `CreateTextureArray`와
같은 방식으로 여러 벽 텍스처를 한 번에 묶을 수 있다.)

## Class: D3D11

메서드:
[Static]
- CreateDevice(hwnd: HWND, screenWidth: int, screenHeight: int) -> D3D11.Device
  설명: `D3D11CreateDeviceAndSwapChain`으로 장치·컨텍스트·스왑체인을
  만들고, 깊이-스텐실 버퍼와 뷰를 만들어 파이프라인에 묶는다.
- CompileShader(device: D3D11.Device, hlslSource: string, vertexLayout: list<(string, int)>) -> D3D11.Shader
  설명: HLSL 소스에서 버텍스·픽셀 셰이더를 각각 컴파일한다
  (`D3DCompile` + `CreateVertexShader`/`CreatePixelShader`).
  `vertexLayout`(각 입력 시맨틱 이름과 컴포넌트 수 — 예:
  `[("POSITION",3), ("TEXCOORD",2), ("LIGHT",1)]`)으로 입력 레이아웃도
  함께 만든다.
- CreateVertexBuffer(device: D3D11.Device, verticesRaw: bytes) -> D3D11.Buffer
- CreateIndexBuffer(device: D3D11.Device, indices: list<int>) -> D3D11.Buffer
- CreateConstantBuffer(device: D3D11.Device, sizeBytes: int) -> D3D11.Buffer
  설명: 매 프레임 갱신할 유니폼(뷰·투영 행렬 등)을 담을 버퍼를 만든다.
- UpdateConstantBuffer(device: D3D11.Device, buffer: D3D11.Buffer, dataRaw: bytes) -> void
  설명: `Map`/`memcpy`/`Unmap`(또는 `UpdateSubresource`)으로 상수 버퍼
  내용을 갱신한다.
- CreateTextureArray(device: D3D11.Device, width: int, height: int, layerCount: int, layersRgba: list<bytes>) -> D3D11.Texture
- Clear(device: D3D11.Device, color: string) -> void
  설명: 렌더 타깃과 깊이-스텐실 버퍼를 함께 지운다(`ClearRenderTargetView`
  + `ClearDepthStencilView`).
- DrawIndexed(device: D3D11.Device, shader: D3D11.Shader, vertexBuffer: D3D11.Buffer, indexBuffer: D3D11.Buffer, indexCount: int, texture: D3D11.Texture) -> void
  설명: 파이프라인에 셰이더·버퍼·텍스처를 묶고(`IASetVertexBuffers`
  등) `DrawIndexed`를 호출한다.
- DrawIndexedInstanced(device: D3D11.Device, shader: D3D11.Shader, vertexBuffer: D3D11.Buffer, indexBuffer: D3D11.Buffer, indexCount: int, texture: D3D11.Texture, instanceBuffer: D3D11.Buffer, instanceCount: int) -> void
  설명: 인스턴스별 위치·크기가 담긴 `instanceBuffer`를 두 번째 입력
  슬롯으로 묶어 `DrawIndexedInstanced`를 호출한다 — 스프라이트를 그릴
  때 쓴다.
- Present(device: D3D11.Device) -> void

# Interface

## Library

`CreateDevice` → `CompileShader` → 맵을 불러올 때 한 번
`CreateVertexBuffer`/`CreateIndexBuffer`/`CreateTextureArray`/
`CreateConstantBuffer`로 정적 지오메트리를 올려둡니다. 매 프레임은
`Clear` → `UpdateConstantBuffer`(카메라 행렬) → `DrawIndexed`(맵) →
`DrawIndexedInstanced`(스프라이트) → `Present` 순서로 그립니다.

# Constraints

- 헤더 `<d3d11.h>`, `<d3dcompiler.h>`. 링크: `d3d11.lib`, `d3dcompiler.lib`.
- 알파 테스트는 D3D11에 고정 함수가 없으므로 픽셀 셰이더의 `clip()`
  내장 함수로 구현한다(`std/graphics/opengl3.md`의 `discard`와 같은 역할).
- `screenWidth`/`screenHeight`가 바뀌면 스왑체인과 깊이-스텐실 버퍼를
  다시 만들어야 한다 — 이 계약은 그 과정을 별도로 규정하지 않는다
  (`std/windows/direct3d.md`의 같은 Open Point 참조).

# Examples

## 예제: 정적 지오메트리 한 번 올리고 매 프레임 그대로 그리기

호출: `device = D3D11.CreateDevice(hwnd, 1280, 720)`,
`shader = D3D11.CompileShader(device, hlslSrc, [("POSITION",3),("TEXCOORD",2),("LIGHT",1)])`,
`vb = D3D11.CreateVertexBuffer(device, wallVertices)`,
`ib = D3D11.CreateIndexBuffer(device, wallIndices)`,
`cb = D3D11.CreateConstantBuffer(device, 64)` — 맵을 불러올 때 한 번만.
그 뒤 매 프레임: `D3D11.Clear(device, "#000000")`,
`D3D11.UpdateConstantBuffer(device, cb, viewProjBytes)`,
`D3D11.DrawIndexed(device, shader, vb, ib, len(wallIndices), wallTextures)`,
`D3D11.Present(device)`.

기대 동작: [`std/graphics/opengl3.md`](../graphics/opengl3.md)의 같은
예제와 동일한 결과 — 카메라가 움직여도 정점을 다시 만들 필요가 없고,
겹치는 벽은 깊이 버퍼가 알아서 가려준다.

# Open Points

- 틴트/디퍼드 렌더링, 셰도우 맵 등은 이 버전의 범위 밖이다.
- 멀티스레드 렌더링(지연 컨텍스트, `ID3D11DeviceContext` 여러 개)은
  다루지 않는다 — 단일 즉시 컨텍스트만 전제한다.
