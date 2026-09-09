"""examples/rock-paper-scissors.md 를 실제 창으로 띄워서 눈으로 확인하기 위한 실행 스크립트.

tests/rps.py(참조 구현)를 그대로 가져다 실제 이벤트 루프로 돌린다. tests/의
자동화 테스트(test_rps.py)와 달리 이 스크립트는 창을 실제로 보여준다.
"""
from rps import RpsApp

if __name__ == "__main__":
    app = RpsApp()
    app.window.run()
