# SPEC.md 검증 테스트

이 폴더는 `SPEC.md`와 `std/`, `examples/`의 각 패키지가 실제로 트랜스파일
가능한지 검증하기 위해, **`SPEC.md`만 근거로 Python으로 옮겨 적은 구현**과
그 구현이 각 패키지의 `Examples`(그리고 있다면 `test_required`)를 실제로
만족하는지 확인하는 단위 테스트를 담습니다.

이 폴더의 Python 코드는 SPP 언어의 일부가 아닙니다 — "AI가 SPEC.md를 따라
트랜스파일했을 때 결과가 말이 되는가"를 검증하는 자체 테스트용 도구입니다.

## 구성

- `spp_std/` — `std/`의 각 패키지를 Python으로 옮겨 적은 참조 구현
  (`ui_.py`는 `std/ui/widgets.md`, `canvas_.py`는 `std/ui/canvas.md`,
  `textbox_.py`/`menu_.py`/`filedialog_.py`는 각각 `std/ui/textbox.md`/
  `menu.md`/`filedialog.md`를 tkinter로 옮긴 것).
- `todo_cli.py` — [`examples/todo-cli.md`](../examples/todo-cli.md)의 참조 구현 (CLI).
- `rps.py` — [`examples/rock-paper-scissors.md`](../examples/rock-paper-scissors.md)의
  참조 구현 (버튼 GUI).
- `game2048.py`/`app2048.py` — [`examples/2048.md`](../examples/2048.md)의 참조
  구현. `game2048.py`는 GUI와 무관한 순수 규칙, `app2048.py`는
  `std/ui/canvas.md` 기반 GUI 배선(Windows/DirectX 대신 tkinter Canvas로
  검증 — 2048.md의 Constraints가 허용하는 대체 렌더러).
- `notepad.py`/`app_notepad.py` — [`examples/notepad.md`](../examples/notepad.md)의
  참조 구현. `notepad.py`는 GUI와 무관한 순수 로직(열기/저장/dirty 추적/찾기·
  바꾸기), `app_notepad.py`는 메뉴·텍스트 상자·파일 대화 상자 배선이다.
- `run_rps.py`/`run_2048.py`/`run_notepad.py` — 자동 테스트가 아니라, 실제
  창을 띄워서 눈으로 확인하기 위한 실행 스크립트다.
- `test_*.py` — 각 패키지의 `Examples`를 그대로 옮긴 단위 테스트. GUI가 있는
  것들은 실제 창을 띄우지 않고(`Window`/`CanvasWindow`가 생성 즉시
  `withdraw`한다) 위젯 생성·이벤트 배선·규칙만 검증한다.
- `doom_*.py` — [`examples/doom/`](../examples/doom/)의 참조 구현. 각 spec
  파일(`wad.md`/`map.md`/`actors.md`/`weapons.md`/`specials.md`/`ai.md`/
  `sound.md`/`netplay.md`/`savegame.md`/`hud.md`/`automap.md`/`menu.md`/
  `intermission.md`/`game.md`)마다 같은 이름의 모듈이 하나씩 있다.
  `doom_render_mesh.py`/`doom_gl_math.py`/`doom_ui_geometry.py`는
  `render.md`(현대적 GPU 렌더링)의 순수 로직(정점/인덱스 생성, 행렬 계산,
  2D 오버레이 지오메트리) — OpenGL에 의존하지 않아 GPU 없이도 테스트할 수
  있다.
- `app_doom.py`/`run_doom.py` — tkinter + CPU 레이캐스팅으로 근사한 플레이
  가능한 창(빠르고 의존성이 없다).
- `app_doom_gl.py`/`doom_render_gl_backend.py` — **실제** 셰이더/VBO/VAO/EBO/
  깊이 버퍼/인스턴스 드로우를 쓰는 진짜 OpenGL 3.3 렌더러(`render.md`가
  기술하는 현대적 렌더링을 문자 그대로 구현한 것). `pygame`(창·컨텍스트
  생성)과 `PyOpenGL`이 필요하다 — 이 저장소에서 유일하게 표준 라이브러리를
  벗어나는 예외다(`pip install pygame PyOpenGL PyOpenGL_accelerate`).
  텍스트는 raw OpenGL에 폰트가 없어서 `pygame.font`(SDL_ttf)로 그린 뒤
  텍스처로 올려 그린다 — 한글 렌더링에는 반드시 한글 글리프가 있는
  폰트(맑은 고딕 등)를 써야 한다(Consolas 등 서구권 고정폭 폰트는 한글이
  깨져 보인다).
- `examples/doom/assets/doom1.wad` — id Software가 무료 재배포를 허용한
  셰어웨어 IWAD(E1, "Knee-Deep in the Dead"). `doom_wad.py`/`doom_map.py`의
  실제 검증 대상이자, 두 GUI 빌드가 플레이하는 실제 맵(`E1M1`)이다.

## 실행

```bash
cd tests
python -m unittest discover -v
```

실제 GUI를 보려면:

```bash
python run_rps.py       # 가위바위보
python run_2048.py      # 2048
python run_notepad.py   # 메모장
python run_doom.py      # DOOM (tkinter + CPU 레이캐스팅)
python app_doom_gl.py   # DOOM (실제 OpenGL 3.3 렌더러 — pygame/PyOpenGL 필요)
```
