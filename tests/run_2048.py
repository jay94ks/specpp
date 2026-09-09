"""examples/2048.md 를 실제 창으로 띄워서 눈으로 확인하기 위한 실행 스크립트."""
from app2048 import Game2048App

if __name__ == "__main__":
    app = Game2048App()
    app.window.run()
