# SPEC.md 검증 테스트

이 폴더는 `SPEC.md`와 `std/`, `examples/`의 각 패키지가 실제로 트랜스파일
가능한지 검증하기 위해, **`SPEC.md`만 근거로 Python으로 옮겨 적은 구현**과
그 구현이 각 패키지의 `Examples`(그리고 있다면 `test_required`)를 실제로
만족하는지 확인하는 단위 테스트를 담습니다.

이 폴더의 Python 코드는 SPP 언어의 일부가 아닙니다 — "AI가 SPEC.md를 따라
트랜스파일했을 때 결과가 말이 되는가"를 검증하는 자체 테스트용 도구입니다.

## 구성

- `spp_std/` — `std/`의 각 패키지를 Python으로 옮겨 적은 참조 구현.
- `todo_cli.py` — [`examples/todo-cli.md`](../examples/todo-cli.md)의 참조 구현.
- `test_*.py` — 각 패키지의 `Examples`를 그대로 옮긴 단위 테스트.

## 실행

```bash
cd tests
python -m unittest discover -v
```
