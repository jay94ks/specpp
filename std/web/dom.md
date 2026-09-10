#!specpp 0.1

# Meta

- name: std/web/dom
- version: 0.1.0
- description: 창·버튼 GUI와 키보드·마우스 원시 입력을 브라우저 DOM으로 만드는 데 필요한 최소 부분집합에 대한 실체 명세.
- platform: web
- kind: native

# Intent

[`std/ui/widgets.md`](../ui/widgets.md)를 JavaScript/TypeScript(또는
WASM에서 JS로 상호운용)로 트랜스파일할 때, 별도 프레임워크(React 등)
없이 브라우저에 이미 있는 DOM API에 직접 바인딩해야 하는 경우를 위한
것이다. 이미 존재하는 실체이므로 새로 구현할 대상이 아니다(`kind:
native`, 1.2절). [`std/windows/win32.md`](../windows/win32.md)가
`Win32.Window`(위젯)와 `Win32.MessageLoop`(원시 입력)로 역할을 나눈
것처럼, 이 패키지도 위젯 바인딩(`DOM.Widget`)과 원시 키보드·마우스
이벤트(`DOM.Input`) 둘을 나눠 제공한다 — [`examples/doom/game.md`](../../examples/doom/game.md)의
`## GUI`처럼 위젯이 아니라 화면 전체를 매 프레임 직접 그리며 키 입력을
직접 받아야 하는 프로그램은 후자만 쓴다.

# Domain

## Class: DOM.Element

(불투명 핸들이다 — 실제로는 `HTMLElement`를 가리킨다. 최상위 창(사실은
`<div>` 하나)과 버튼·라벨 같은 자식 위젯 모두 이 타입 하나로 다뤄진다.)

## Class: DOM.Widget

메서드:
[Static]
- createElement(tagName: string, parent: DOM.Element?) -> DOM.Element
  설명: `document.createElement(tagName)`으로 만들고, `parent`가 있으면
  `parent.appendChild(...)`로 붙인다. `parent`가 없으면 `document.body`에
  붙인다.
- setTextContent(element: DOM.Element, text: string) -> void
  설명: `element.textContent = text`에 대응한다.
- getTextContent(element: DOM.Element) -> string
- setAttribute(element: DOM.Element, name: string, value: string) -> void
- setDisabled(element: DOM.Element, disabled: boolean) -> void
  설명: `element.disabled = disabled`(버튼·입력 요소에만 의미가 있다).
- addEventListener(element: DOM.Element, eventName: string, handler: (DOM.Element) -> void) -> void
  설명: `element.addEventListener(eventName, ...)`에 대응한다. 버튼의
  `onClick`은 `eventName = "click"`으로 매핑한다.
- remove(element: DOM.Element) -> void
  설명: `element.remove()` — 창을 닫는 것에 대응한다.

## Class: DOM.Input

`std/windows/win32.md`의 `Win32.MessageLoop`에 대응하는, 위젯을 거치지 않는
원시 입력이다 — 매 프레임 직접 화면을 그리는 프로그램(캔버스 기반 게임 등)이
쓴다.

메서드:
[Static]
- onKeyDown(handler: (string) -> void) -> void
  설명: `window.addEventListener("keydown", ...)`에 대응한다. 인자는
  `KeyboardEvent.key`(`"ArrowUp"`, `"w"`, `"Escape"` 등) 그대로 넘긴다.
- onKeyUp(handler: (string) -> void) -> void
- onMouseMove(handler: (float, float) -> void) -> void
  설명: 캔버스 좌표계 기준 `(offsetX, offsetY)`를 넘긴다.
- requestAnimationFrame(callback: () -> void) -> int
  설명: `window.requestAnimationFrame`에 대응한다 — 원본 DOOM의 "고정
  35Hz 시뮬레이션 vs 가변 렌더 프레임" 구조([`examples/doom/game.md`](../../examples/doom/game.md)의
  `Feature.틱 진행` 참조)에서 렌더 프레임 쪽 루프로 쓴다. 반환값은
  `cancelAnimationFrame`에 넘길 수 있는 요청 ID다.
- setInterval(callback: () -> void, milliseconds: float) -> int
  설명: 틱(시뮬레이션) 쪽처럼 고정 주기로 실행해야 하는 루프에 쓴다.
  반환값은 `clearInterval`에 넘길 수 있는 타이머 ID다.

# Interface

## Library

위젯 GUI는 `DOM.Widget.createElement`로 요소를 만들고
`addEventListener`로 상호작용을 등록합니다. 캔버스 기반 게임처럼 원시
입력이 필요하면 `DOM.Input`의 이벤트 등록 메서드를 대신(또는 함께) 씁니다.

# Constraints

- `<button>`/`<label>`/`<div>` 같은 실제 태그 이름 선택은 이 계약이
  규정하지 않는다 — `Button`은 보통 `<button>`, `Label`은 `<span>`이나
  `<label>`로 매핑하는 것이 관용적이다.
- 브라우저 샌드박스 안에서 동작하므로(SPEC.md 3.10절의 `platform: web`
  설명 참조) 임의 파일 접근, 원시 소켓 같은 건 이 패키지의 범위가
  아니다 — 저장이 필요하면 [`std/web/storage.md`](storage.md)를 쓴다.
- `DOM.Input.onKeyDown`은 텍스트 입력 요소(`<input>` 등)에 포커스가 가
  있으면 브라우저가 그 요소로 먼저 이벤트를 보낼 수 있다 — 게임처럼
  전역 키 입력이 필요하면 포커스를 뺏기지 않는 요소(예: `document.body`
  또는 `tabindex`를 준 캔버스)에 리스너를 건다.

# Examples

## 예제: 버튼을 누르면 라벨이 바뀐다

호출: `label = DOM.Widget.createElement("span", null)`,
`button = DOM.Widget.createElement("button", null)`,
`DOM.Widget.setTextContent(button, "+1")`,
`DOM.Widget.addEventListener(button, "click", (el) -> DOM.Widget.setTextContent(label, "1"))`,
사용자가 버튼을 클릭한다.

기대 동작: `DOM.Widget.getTextContent(label)`이 `"1"`이 된다
([`std/ui/widgets.md`](../ui/widgets.md)의 같은 예제와 동일한 결과).

# Open Points

- 터치 이벤트(모바일)는 이 버전의 범위 밖이다 — 마우스 이벤트만 다룬다.
- `pointerlock`/`fullscreen` API처럼 게임에 흔히 쓰이는 브라우저 API는
  다루지 않는다.
