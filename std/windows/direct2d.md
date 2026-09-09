#!specpp 0.1

# Meta

- name: std/windows/direct2d
- version: 0.1.0
- description: Direct2D/DirectWrite로 2D 도형·텍스트를 그리는 데 필요한 최소 부분집합에 대한 실체 명세.
- platform: windows
- kind: native

# Intent

[`std/ui/canvas.md`](../ui/canvas.md)를 Windows에서 DirectX 기반으로
트랜스파일할 때 쓴다. Direct2D는 Direct3D 위에서 동작하는 DirectX의 2D
그래픽 API로, 게임 보드처럼 사각형과 텍스트를 반복해서 그려야 하는 화면에
적합하다. 이미 Windows(DirectX)에 존재하는 API이므로 새로 구현할 대상이
아니다(`kind: native`, 1.2절). 실제로는 COM 인터페이스(`ID2D1Factory`,
`ID2D1HwndRenderTarget`, `ID2D1SolidColorBrush`, DirectWrite의
`IDWriteFactory`/`IDWriteTextFormat`)의 메서드 호출이지만, 여기서는 그 역할을
정적 메서드로 근사했다(아래 Constraints 참조).

# Domain

## Class: D2D1RenderTarget

(불투명 핸들. `ID2D1HwndRenderTarget*`을 가리킨다.)

## Class: D2D1Brush

(불투명 핸들. `ID2D1SolidColorBrush*`을 가리킨다.)

## Class: Direct2D

메서드:
[Static]
- CreateHwndRenderTarget(hwnd: HWND, width: int, height: int) -> D2D1RenderTarget
  설명: `ID2D1Factory::CreateHwndRenderTarget`에 대응한다. 지정한 Win32 창
  (`HWND`, [`std/windows/win32.md`](win32.md) 참조) 위에 그릴 렌더 타깃을
  만든다.
- BeginDraw(target: D2D1RenderTarget) -> void
- EndDraw(target: D2D1RenderTarget) -> void
  설명: `BeginDraw`/`EndDraw` 사이의 호출만 실제로 화면에 반영된다.
- Clear(target: D2D1RenderTarget, color: string) -> void
- CreateSolidColorBrush(target: D2D1RenderTarget, color: string) -> D2D1Brush
  설명: color(`"#RRGGBB"`)에 대응하는 단색 브러시를 만든다.
- FillRectangle(target: D2D1RenderTarget, x: float, y: float, width: float, height: float, brush: D2D1Brush) -> void
- DrawText(target: D2D1RenderTarget, x: float, y: float, width: float, height: float, text: string, fontSize: float, brush: D2D1Brush) -> void
  설명: DirectWrite로 텍스트 서식을 만들고 그리는 과정
  (`IDWriteFactory::CreateTextFormat` + `ID2D1RenderTarget::DrawText`)을
  하나로 근사했다.
- Resize(target: D2D1RenderTarget, width: int, height: int) -> void
  설명: 창 크기가 바뀌었을 때 렌더 타깃 크기를 맞춘다
  (`ID2D1HwndRenderTarget::Resize`).

# Interface

## Library

`CreateHwndRenderTarget`으로 렌더 타깃을 하나 만들어 두고, 매 프레임
`BeginDraw` → `Clear` → 필요한 `FillRectangle`/`DrawText` 호출 → `EndDraw`
순서로 그립니다. 브러시는 색상마다 미리 만들어 재사용하는 것을 권장합니다.

# Constraints

- 헤더 `<d2d1.h>`, `<dwrite.h>`. 링크: `d2d1.lib`, `dwrite.lib`.
- 실제 COM 인터페이스 사용(참조 카운트 관리, `HRESULT` 확인, 팩토리 생성
  (`D2D1CreateFactory`) 등)은 이 계약에서 함수 이름과 역할만 대응시켰을 뿐,
  세부 사항은 C++의 COM/Direct2D 관용구를 그대로 따른다.
- 좌표·크기는 실제로는 부동소수점(`FLOAT`, DIP 단위)이다 — 이미 3.1절의
  `float` 타입으로 표기했다.
- `EndDraw`는 `D2DERR_RECREATE_TARGET`을 반환할 수 있다(예: 그래픽 디바이스
  분실) — 이 경우 렌더 타깃을 다시 만들어야 한다. 이 계약은 그 재시도
  로직까지 규정하지 않는다.

# Examples

## 예제: 사각형 하나를 그린다

호출: `target = Direct2D.CreateHwndRenderTarget(hwnd, 400, 400)`,
`Direct2D.BeginDraw(target)`, `Direct2D.Clear(target, "#FFFFFF")`,
`brush = Direct2D.CreateSolidColorBrush(target, "#FFCC00")`,
`Direct2D.FillRectangle(target, 10, 10, 100, 100, brush)`,
`Direct2D.EndDraw(target)`

기대 동작: 흰 배경 위에 (10,10)에서 시작하는 100x100 크기의 노란 사각형이
그려진다.

# Open Points

- 텍스트 정렬(가운데 정렬 등), 안티앨리어싱 모드 지정은 이 버전의 범위
  밖이다 — 대상 언어의 관용적인 기본값을 따른다.
