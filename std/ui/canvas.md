#!specpp 0.1

# Meta

- name: std/ui/canvas
- version: 0.1.0
- description: 픽셀/도형을 직접 그리는 2D 캔버스 창에 대한 추상 계약.

# Intent

[`std/ui/widgets.md`](widgets.md)의 `Window`/`Button`/`Label`은 이산적인
위젯을 배치하는 GUI에 맞지만, 게임 보드처럼 "매 프레임 직접 그려야 하는"
화면에는 맞지 않는다. 이 패키지는 사각형·텍스트를 직접 그리고, 키보드 입력을
받는 2D 캔버스 창을 추상적으로 정의한다. 실제 그리기는
[`std/windows/direct2d.md`](../windows/direct2d.md) 같은 OS별 네이티브
렌더러로 구현된다.

# Domain

## Class: CanvasWindow

생성자:
- CanvasWindow(title: string, width: int, height: int)

멤버:
이벤트:
- onKeyDown: (key: string) -> void — 사용자가 키를 누르면 발생한다. key는
  `"Up"`/`"Down"`/`"Left"`/`"Right"` 같은 이름이다.
- onRender: (canvas: Canvas) -> void — 화면을 다시 그려야 할 때 발생한다.
  핸들러는 canvas에 그리기 호출만 하면 되고, 언제 실제로 화면에 반영할지는
  창이 알아서 한다.

메서드:
- show() -> void
- close() -> void
- requestRedraw() -> void
  설명: 다음 기회에 `onRender`가 다시 호출되도록 요청한다 — 게임 상태가
  바뀌어서 화면을 갱신해야 할 때 호출한다.

## Interface: Canvas

메서드:
- clear(color: string) -> void
  설명: 캔버스 전체를 color로 지운다.
- fillRect(x: int, y: int, width: int, height: int, color: string) -> void
- drawText(x: int, y: int, text: string, color: string, fontSize: int) -> void

색상은 `"#RRGGBB"` 형태의 16진 문자열로 표기한다.

# Interface

## Library

다른 패키지는 `CanvasWindow`를 만들고 `onKeyDown`/`onRender`에 핸들러를
등록한 뒤 `show()`를 호출합니다. 상태가 바뀔 때마다 `requestRedraw()`를
불러 다시 그리게 합니다.

# Constraints

- 타겟 플랫폼의 관용적인 2D 렌더링 수단(Windows에서는
  [`std/windows/direct2d.md`](../windows/direct2d.md)의 DirectX/Direct2D,
  Python에서는 tkinter `Canvas`, 웹이면 `<canvas>` 등)에 매핑한다.
- `onRender`는 언제든(창 크기 변경, 다른 창에 가렸다가 다시 보일 때 등) 다시
  호출될 수 있다고 가정하고 항상 `canvas.clear(...)`부터 전체를 다시 그린다
  — 이전 프레임과의 차이만 그리는 최적화는 이 계약이 요구하지 않는다.
- GUI가 없는 실행 환경에서는 쓸 수 없다 (`std/ui/widgets.md`와 동일한 제약).

# Examples

## 예제: 키 입력에 따라 다시 그린다

호출: `onKeyDown`에 `(key) -> requestRedraw()` 등록. 사용자가 방향키를 누른다.

기대 동작: `onRender`가 다시 호출된다.

# Open Points

- 이미지·스프라이트 그리기, 클리핑 영역 지정은 이 버전의 범위 밖이다.
