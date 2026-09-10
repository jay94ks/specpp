#!specpp 0.1

# Meta

- name: std/web/canvas
- version: 0.1.0
- description: 픽셀/도형을 직접 그리는 2D 캔버스 창을 브라우저 `<canvas>`로 만드는 데 필요한 최소 부분집합에 대한 실체 명세.
- platform: web
- kind: native

# Intent

[`std/ui/canvas.md`](../ui/canvas.md)를 웹으로 트랜스파일할 때 쓴다.
[`std/windows/direct2d.md`](../windows/direct2d.md)가 Windows에서 하는
역할을 브라우저의 `<canvas>` + `CanvasRenderingContext2D`("2d" 컨텍스트)로
대신한다. 이미 존재하는 실체이므로 새로 구현할 대상이 아니다(`kind:
native`, 1.2절).

# Domain

## Class: Canvas2DContext

(불투명 핸들이다 — 실제로는 `canvas.getContext("2d")`가 반환하는
`CanvasRenderingContext2D`를 가리킨다.)

## Class: WebCanvas2D

메서드:
[Static]
- CreateContext(canvasElement: DOM.Element, width: int, height: int) -> Canvas2DContext
  설명: [`std/web/dom.md`](dom.md)로 만든 `<canvas>` 요소의 `width`/`height`
  속성을 설정하고 `"2d"` 컨텍스트를 얻는다.
- Clear(ctx: Canvas2DContext, color: string) -> void
  설명: `ctx.fillStyle = color; ctx.fillRect(0, 0, width, height)`로
  근사한다(`clearRect` + 배경색 다시 채우기와 동등하다).
- FillRect(ctx: Canvas2DContext, x: float, y: float, width: float, height: float, color: string) -> void
  설명: `ctx.fillStyle = color; ctx.fillRect(x, y, width, height)`.
- DrawText(ctx: Canvas2DContext, x: float, y: float, text: string, color: string, fontSize: float) -> void
  설명: `ctx.font = fontSize + "px sans-serif"; ctx.fillStyle = color;
  ctx.fillText(text, x, y)`에 대응한다 — Canvas 2D는 처음부터 텍스트를
  그릴 수 있어([`std/graphics/opengl3.md`](../graphics/opengl3.md)/
  [`std/web/webgl.md`](webgl.md)와 달리) 별도 텍스처 래스터라이즈가
  필요 없다.
- DrawImage(ctx: Canvas2DContext, image: DOM.Element, x: float, y: float, width: float, height: float) -> void
  설명: `ctx.drawImage(image, x, y, width, height)` — 이미 디코딩된
  `<img>` 요소(또는 `ImageBitmap`)를 그린다.

# Interface

## Library

`CreateContext`로 컨텍스트를 하나 얻어 두고, 매 프레임(보통
`DOM.Input.requestAnimationFrame` 콜백 안에서) `Clear` → 필요한
`FillRect`/`DrawText`/`DrawImage` 호출 순서로 그립니다.

# Constraints

- 헤더/링크가 필요 없다 — 브라우저가 이미 제공하는 전역 `HTMLCanvasElement`
  API다.
- `std/ui/canvas.md`의 `onRender` 이벤트는
  [`std/web/dom.md`](dom.md)의 `DOM.Input.requestAnimationFrame`으로
  구현한다 — 매 프레임 콜백 안에서 `onRender` 핸들러를 호출한다.
- 좌표·크기는 CSS 픽셀 기준이다 — 고해상도(레티나 등) 디스플레이에서
  선명하게 그리려면 `canvas.width`를 `devicePixelRatio`만큼 키우고
  `ctx.scale(devicePixelRatio, devicePixelRatio)`를 호출해야 하지만, 이
  계약은 그 보정을 규정하지 않는다(아래 Open Points).

# Examples

## 예제: 사각형 하나를 그린다

호출: `ctx = WebCanvas2D.CreateContext(canvasEl, 400, 400)`,
`WebCanvas2D.Clear(ctx, "#FFFFFF")`,
`WebCanvas2D.FillRect(ctx, 10, 10, 100, 100, "#FFCC00")`

기대 동작: 흰 배경 위에 (10,10)에서 시작하는 100x100 크기의 노란
사각형이 그려진다([`std/windows/direct2d.md`](../windows/direct2d.md)의
같은 예제와 동일한 결과).

# Open Points

- 고해상도 디스플레이 보정(`devicePixelRatio`)은 다루지 않는다.
- 이미지 스무딩(`imageSmoothingEnabled`) 설정은 대상 언어의 기본값을
  따른다.
