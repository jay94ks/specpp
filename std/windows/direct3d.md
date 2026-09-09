#!specpp 0.1

# Meta

- name: std/windows/direct3d
- version: 0.1.0
- description: 텍스처 입힌 사각형을 그리는 데 필요한 최소 Direct3D 9 부분집합에 대한 실체 명세.
- platform: windows -> fallback: std/graphics/opengl.md
- kind: native

# Intent

[`std/graphics/opengl.md`](../graphics/opengl.md)와 같은 목적(텍스처 사각형
반복해서 그리기)을 DirectX 위에서 이루기 위한 것이다. Direct3D 9의 고정
함수 파이프라인은 셰이더 없이도 텍스처 사각형을 간단히 그릴 수 있어, 이런
용도에는 Direct3D 11보다 훨씬 적합하다 — 이미 존재하는 API이므로 새로
구현할 대상이 아니다(`kind: native`, 1.2절).

# Domain

## Class: D3D.Device

(불투명 핸들이다 — 실제로는 `IDirect3DDevice9*`다.)

## Class: D3D.Texture

(불투명 핸들이다 — 실제로는 `IDirect3DTexture9*`다.)

## Class: D3D

메서드:
[Static]
- CreateDevice(hwnd: HWND, screenWidth: int, screenHeight: int) -> D3D.Device
  설명: hwnd([`std/windows/win32.md`](win32.md) 참조) 위에 그릴 장치를
  만든다(`Direct3DCreate9` + `IDirect3D9::CreateDevice`).
- BeginScene(device: D3D.Device) -> void
- Clear(device: D3D.Device, color: string) -> void
- CreateTexture(device: D3D.Device, width: int, height: int, pixelsRgba: bytes) -> D3D.Texture
  설명: width*height*4바이트(RGBA)의 원시 픽셀로 텍스처를 만든다.
- DrawTexturedQuad(device: D3D.Device, texture: D3D.Texture, x: float, y: float, width: float, height: float, u0: float, v0: float, u1: float, v1: float) -> void
  설명: texture에서 `[u0, v0]`~`[u1, v1]` 구간을 화면의 `(x, y)`~
  `(x+width, y+height)` 사각형에 그린다(변환된 화면 좌표(`D3DFVF_XYZRHW`)를
  쓰는 사각형 스트립 두 삼각형으로 그린다).
- EndScene(device: D3D.Device) -> void
- Present(device: D3D.Device) -> void
  설명: 그린 결과를 화면에 표시한다.

# Interface

## Library

`CreateDevice`를 한 번 부른 뒤, 텍스처마다 `CreateTexture`로 한 번씩
업로드해 재사용합니다. 매 프레임 `BeginScene` → `Clear` → 필요한 만큼
`DrawTexturedQuad` → `EndScene` → `Present` 순서로 그립니다.

# Constraints

- 헤더 `<d3d9.h>`. 링크: `d3d9.lib`.
- Direct3D 11/12의 셰이더·파이프라인 상태 객체 기반 렌더링은 이 버전의
  범위 밖이다 — Direct3D 9의 고정 함수 파이프라인만 쓴다.
- `screenWidth`/`screenHeight`가 바뀌면(창 크기 변경) 장치를 리셋
  (`IDirect3DDevice9::Reset`)해야 한다 — 이 계약은 그 과정을 별도로
  규정하지 않는다.

# Examples

## 예제: 한 프레임 그리기

호출: `device = D3D.CreateDevice(hwnd, 640, 480)`, `D3D.BeginScene(device)`,
`D3D.Clear(device, "#000000")`,
`D3D.DrawTexturedQuad(device, wallTexture, 100, 0, 4, 200, 0.5, 0.0, 0.51, 1.0)`,
`D3D.EndScene(device)`, `D3D.Present(device)`

기대 동작: 검은 배경 위에 `wallTexture`의 얇은 세로 조각 하나가
`(100,0)`~`(104,200)`에 그려진다.

# Open Points

- 알파 블렌딩 상태(`D3DRS_ALPHABLENDENABLE` 등)는 이 버전에서 규정하지
  않는다.
