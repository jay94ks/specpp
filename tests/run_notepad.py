"""examples/notepad.md 를 실제 창으로 띄워서 눈으로 확인하기 위한 실행 스크립트."""
from app_notepad import NotepadApp

if __name__ == "__main__":
    app = NotepadApp()
    app.window.run()
