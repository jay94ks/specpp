#!specpp 0.1

# Domain

원본 `m_menu.h`/`m_menu.c`(메인 메뉴, 옵션 화면)에 대응한다. 이 메뉴는
[`std/ui/menu.md`](../../std/ui/menu.md)의 창 메뉴 막대가 아니라, DOOM
안에서 3D 화면 대신 그려지는 자체 화면(새 게임/옵션/저장/불러오기/게임
종료 같은 항목이 세로로 나열된 이미지)이다.

## Class: Doom.MenuItem

멤버:
- label: string — 화면에 그릴 텍스트/그래픽 이름.
- kind: enum(Action | Toggle | Slider | Submenu)
- action: (() -> void)? — `kind = Action`일 때 선택하면 실행할 함수.
- submenu: Doom.Menu? — `kind = Submenu`일 때 들어갈 하위 메뉴.

## Class: Doom.Menu

멤버:
- title: string
- items: list<Doom.MenuItem>
- selectedIndex: int — 기본값 0.

메서드:
- render(renderer: Doom.Renderer.Backend) -> void
  설명: 3D 장면 렌더링을 건너뛰고, 대신 이 메뉴의 배경 이미지와 각
  `items`를 세로로 나열해
  [`Doom.Renderer.Backend.drawUIOverlay`](render.md)로 그린다.
  `selectedIndex`의 항목은 강조 표시한다(원본은 옆에 깜빡이는 해골
  커서를 그린다).

## Class: Doom.MenuStack

멤버:
- stack: list<Doom.Menu> — 마지막 항목이 지금 보이는 메뉴. 하위 메뉴에
  들어가면 push, 뒤로 가면 pop한다.

# Behavior

## Feature: 메뉴 열기/닫기

절차:
1. 게임 중 메뉴 키를 누르면, 현재 진행 중인 게임을 tic 진행 없이 멈추고
   (`game.md`의 `Feature.틱 진행` 참조) 최상위 `Doom.Menu`를
   `MenuStack.stack`에 넣는다.
2. 메뉴가 열려 있을 때 취소 키를 누르면 `stack`에서 하나를 pop한다.
   `stack`이 비면 메뉴를 닫고 게임을 다시 진행한다.

## Feature: 메뉴 항목 선택

입력:
- direction: enum(Up | Down) — 커서 이동, 또는
- confirm: boolean — 선택 확정.

절차:
1. `direction`이 있으면 `selectedIndex`를 위/아래로 한 칸 옮긴다(범위를
   벗어나면 반대쪽 끝으로 순환한다).
2. `confirm`이면 선택된 `Doom.MenuItem`의 `kind`에 따라: `Action`이면
   `action()`을 실행, `Submenu`면 `submenu`를 `MenuStack.stack`에
   push, `Toggle`/`Slider`면 그 항목이 제어하는 설정값을 바꾼다.

# Constraints

- 항목 하나하나(예: "New Game" → "Choose Skill" → "새 게임 시작")를
  전부 나열하지 않는다 — `Doom.Menu`/`Doom.MenuItem`이 그 구조를
  표현하는 틀이고, 실제 메뉴 트리(항목 이름, 순서, 하위 메뉴 구성)는
  원본 `m_menu.c`의 `MainMenu`/`OptionsMenu`/`NewGameMenu` 등 배열을
  그대로 옮기는 것을 권장한다.

# Open Points

- 메뉴 항목 하나하나의 정확한 목록·순서는 옮기지 않았다.
- 슬라이더(음량, 밝기 등)의 정확한 단계 수는 다루지 않는다.
