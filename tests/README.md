# SPEC.md 검증 테스트

이 폴더는 `SPEC.md`와 `std/`, `examples/`의 각 패키지가 실제로 트랜스파일
가능한지 검증하기 위해, **`SPEC.md`만 근거로 Python으로 옮겨 적은 구현**과
그 구현이 각 패키지의 `Examples`(그리고 있다면 `test_required`)를 실제로
만족하는지 확인하는 단위 테스트를 담습니다.

이 폴더의 Python 코드는 SPP 언어의 일부가 아닙니다 — "AI가 SPEC.md를 따라
트랜스파일했을 때 결과가 말이 되는가"를 검증하는 자체 테스트용 도구입니다.

## 구성

- `spp_std/` — `std/`의 각 패키지를 Python으로 옮겨 적은 참조 구현
  (`spp_std/ui_.py`는 `std/ui/widgets.md`를, `spp_std/canvas_.py`는
  `std/ui/canvas.md`를 tkinter로 옮긴 것).
- `todo_cli.py` — [`examples/todo-cli.md`](../examples/todo-cli.md)의 참조 구현 (CLI).
- `rps.py` — [`examples/rock-paper-scissors.md`](../examples/rock-paper-scissors.md)의
  참조 구현 (버튼 GUI).
- `game2048.py`/`app2048.py` — [`examples/2048.md`](../examples/2048.md)의 참조
  구현. `game2048.py`는 GUI와 무관한 순수 규칙, `app2048.py`는
  `std/ui/canvas.md` 기반 GUI 배선(Windows/DirectX 대신 tkinter Canvas로
  검증 — 2048.md의 Constraints가 허용하는 대체 렌더러).
- `run_rps.py`/`run_2048.py` — 자동 테스트가 아니라, 실제 창을 띄워서 눈으로
  확인하기 위한 실행 스크립트다.
- `test_*.py` — 각 패키지의 `Examples`를 그대로 옮긴 단위 테스트. GUI가 있는
  것들은 실제 창을 띄우지 않고(`Window`/`CanvasWindow`가 생성 즉시
  `withdraw`한다) 위젯 생성·이벤트 배선·게임 규칙만 검증한다.

## 실행

```bash
cd tests
python -m unittest discover -v
```

실제 GUI를 보려면:

```bash
python run_rps.py     # 가위바위보
python run_2048.py    # 2048
```
