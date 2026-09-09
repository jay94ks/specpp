"""examples/doom/ 스펙 검증 참조 구현을 실제로 플레이해 보는 실행 스크립트.

examples/doom/assets/doom1.wad(id Software 셰어웨어, E1 "Knee-Deep in the
Dead")를 읽어 E1M1을 불러오고, tkinter 창에서 실시간으로 플레이할 수 있게
한다.

조작: W/S 전진·후진, A/D 좌우 회전, ←/→ 좌우 이동(strafe), Space 발사,
E 사용(문 열기).
"""
import os
import random
import sys
import tkinter as tk

from app_doom import DoomApp
from doom_game import Game
from doom_wad import WadFile

DEFAULT_WAD = os.path.join(os.path.dirname(__file__), "..", "examples", "doom", "assets", "doom1.wad")


def main():
    wad_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_WAD
    map_name = sys.argv[2] if len(sys.argv) > 2 else "E1M1"

    wad = WadFile(wad_path)
    game = Game.Start(wad, map_name, rng=random.Random(1).random)

    root = tk.Tk()
    DoomApp(root, game)
    root.mainloop()


if __name__ == "__main__":
    main()
