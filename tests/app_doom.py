"""examples/doom/game.md의 Doom.Game을 실제로 조작할 수 있는 tkinter 창.

examples/doom/render.md가 규정한 "화면 열마다 거리를 계산해 텍스처 사각형을
그린다"는 알고리즘을 doom_render_raycast.py의 단순 레이캐스팅으로 근사해서
Canvas 위에 그린다 — 실제 텍스처 이미지는 디코딩하지 않고(그건 이 스펙
검증의 범위 밖이다, wad.md Open Points 참조) 벽마다 다른 색으로 근사한다.

3D 시점 위에 hud.md(체력/탄약/얼굴 표정 상태 표시줄), menu.md(Esc로 여는
자체 화면 메뉴), automap.md(Tab으로 여는 위에서 본 지도)까지 얹어 game.md의
"## GUI" Interface(그 순간 활성 화면 하나로 전체를 채운다)를 그대로 따른다.

실제 게임 로직(이동/충돌/AI/전투/문/아이템 획득/얼굴 표정/지도 선 공개)은
doom_game.py의 Game.tick과 doom_hud.py/doom_automap.py/doom_menu.py를 그대로
호출한다 — 이 파일은 입력을 모아 넘기고 결과를 그리는 GUI 배선만 담당한다.
"""
import colorsys
import math
import tkinter as tk

from doom_game import Game
from doom_intermission import make_intermission
from doom_menu import Menu, MenuItem
from doom_render_raycast import build_wall_segments, render_columns

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 400
VIEW_HEIGHT = 344  # 3D 시점이 차지하는 높이 (아래 HUD_HEIGHT는 별도).
HUD_HEIGHT = CANVAS_HEIGHT - VIEW_HEIGHT
NUM_COLUMNS = 160
FOV_DEG = 90.0
NOMINAL_WALL_HEIGHT = 64.0
TICS_PER_SECOND = 35
MOVE_SPEED = 400  # forwardMove 단위 (game.tick 안에서 0.01배 되어 map 단위로 바뀐다).
TURN_SPEED = 6  # tic당 회전 각도(도).

FORWARD_KEYS = {"w": 1, "Up": 1, "s": -1, "Down": -1}
STRAFE_KEYS = {"Left": -1, "Right": 1}
TURN_KEYS = {"a": -1, "d": 1}

KEY_COLORS = {"blue": "#3b6fd1", "yellow": "#d1c53b", "red": "#d13b3b"}


def _column_color(colorSeed, lightLevel, dist, maxDist=1200.0):
    hue = (abs(colorSeed) % 360) / 360.0
    brightness = max(0.15, min(1.0, lightLevel / 255.0))
    fog = max(0.25, 1.0 - dist / maxDist)
    v = brightness * fog
    r, g, b = colorsys.hsv_to_rgb(hue, 0.45, v)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def _health_bar_color(ratio):
    if ratio > 0.66:
        return "#39c25a"
    if ratio > 0.33:
        return "#d1c53b"
    return "#d13b3b"


class DoomApp:
    def __init__(self, root, game):
        self.root = root
        self.game = game
        self.root.title("DOOM (SPP reference build) — E1M1")

        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="black",
                                 highlightthickness=0)
        self.canvas.pack()

        self.pressed = set()
        self.fire_pending = False
        self.use_pending = False
        self.running = True

        self.prev_health = game.player.health
        self.prev_kills = game.killCount
        self.hit_direction = None
        self.hit_flash_tics = 0
        self.intermission = None

        root.bind("<KeyPress>", self._on_key_down)
        root.bind("<KeyRelease>", self._on_key_up)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.projPlaneDist = (CANVAS_WIDTH / 2) / math.tan(math.radians(FOV_DEG / 2))
        self._loop()

    # ------------------------------------------------------------------
    # 입력
    # ------------------------------------------------------------------
    def _build_main_menu(self):
        return Menu("DOOM", [
            MenuItem("계속하기", "Action", action=lambda: self.game.menuStack.closeOneLevel()),
            MenuItem("자동 지도 켜기/끄기", "Action", action=lambda: self.game.automap.toggle()),
            MenuItem("게임 종료", "Action", action=self._on_close),
        ])

    def _on_key_down(self, event):
        key = event.keysym

        # spp-source: examples/doom/menu.md#Feature:_메뉴_열기/닫기,_메뉴_항목_선택
        if self.game.menuStack.isOpen:
            if key == "Up":
                self.game.menuStack.moveSelection("Up")
            elif key == "Down":
                self.game.menuStack.moveSelection("Down")
            elif key == "Return":
                self.game.menuStack.confirmSelection()
            elif key == "Escape":
                self.game.menuStack.closeOneLevel()
            return

        if key == "Escape":
            self.game.menuStack.open(self._build_main_menu())
            return
        if key == "Tab":
            self.game.automap.toggle()
            return

        self.pressed.add(key)
        if key == "space":
            self.fire_pending = True
        elif key in ("e", "E"):
            self.use_pending = True

    def _on_key_up(self, event):
        self.pressed.discard(event.keysym)

    def _on_close(self):
        self.running = False
        self.root.destroy()

    def _build_raw_input(self):
        forward = 0
        for key, sign in FORWARD_KEYS.items():
            if key in self.pressed:
                forward = sign * MOVE_SPEED
        side = 0
        for key, sign in STRAFE_KEYS.items():
            if key in self.pressed:
                side = sign * MOVE_SPEED
        turn = 0
        for key, sign in TURN_KEYS.items():
            if key in self.pressed:
                turn = sign * TURN_SPEED

        buttons = 0
        if self.fire_pending:
            buttons |= 0x1
            self.fire_pending = False
        if self.use_pending:
            buttons |= 0x2
            self.use_pending = False

        return {"forwardMove": forward, "sideMove": side, "angleTurn": turn, "buttons": buttons}

    # ------------------------------------------------------------------
    # 틱 루프
    # ------------------------------------------------------------------
    def _loop(self):
        if not self.running:
            return
        self.game.tick(self._build_raw_input())
        self._update_face_state()
        self._update_intermission()
        self._render()
        self.root.after(int(1000 / TICS_PER_SECOND), self._loop)

    # spp-source: examples/doom/intermission.md#Feature:_스테이지_클리어_전환
    def _update_intermission(self):
        if self.game.exited and self.intermission is None:
            self.intermission = make_intermission(
                finishedMapName=self.game.map.name, nextMapName=None,
                killCount=self.game.killCount, totalKills=self.game.totalKills,
                itemCount=self.game.itemCount, totalItems=self.game.totalItems,
                secretCount=self.game.secretCount, totalSecrets=0,
                parTimeTics=35 * 90, playerTimeTics=self.game.tic,
            )

    def _update_face_state(self):
        player = self.game.player
        damaged = player.health < self.prev_health
        justKilled = self.game.killCount > self.prev_kills
        if damaged:
            self.hit_flash_tics = 8
        elif self.hit_flash_tics > 0:
            self.hit_flash_tics -= 1

        # spp-source: examples/doom/hud.md#Feature:_얼굴_표정_갱신
        self.face_frame = self.game.hud.updateFace(
            player,
            justDamagedFromDirection=("front" if damaged else None),
            justKilled=justKilled,
        )
        self.prev_health = player.health
        self.prev_kills = self.game.killCount

    # ------------------------------------------------------------------
    # 렌더링 — game.md의 "## GUI": 그 순간 활성 화면 하나로 전체를 채운다.
    # ------------------------------------------------------------------
    def _render(self):
        self.canvas.delete("all")

        if self.intermission is not None:
            self._render_intermission()
            return

        if self.game.automap.isOpen:
            self._render_automap()
        else:
            self._render_3d_view()

        self._render_hud()

        if self.game.menuStack.isOpen:
            self._render_menu()

    def _render_3d_view(self):
        actor = self.game.player.actor
        segments = build_wall_segments(self.game.map)
        columns = render_columns(segments, actor.x, actor.y, actor.angle, FOV_DEG, NUM_COLUMNS)

        colWidth = CANVAS_WIDTH / NUM_COLUMNS
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, VIEW_HEIGHT / 2, fill="#1a1a2e", width=0)
        self.canvas.create_rectangle(0, VIEW_HEIGHT / 2, CANVAS_WIDTH, VIEW_HEIGHT, fill="#2b2115", width=0)

        for i, (dist, colorSeed, sector) in enumerate(columns):
            x0 = i * colWidth
            x1 = x0 + colWidth + 1
            if dist is None:
                continue
            lightLevel = sector.lightLevel if sector is not None else 160
            wallHeight = (NOMINAL_WALL_HEIGHT * self.projPlaneDist) / max(dist, 1.0)
            y0 = max(0.0, VIEW_HEIGHT / 2 - wallHeight / 2)
            y1 = min(VIEW_HEIGHT, VIEW_HEIGHT / 2 + wallHeight / 2)
            color = _column_color(colorSeed, lightLevel, dist)
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0)

        self._render_monsters(actor)

        if self.hit_flash_tics > 0:
            alpha = self.hit_flash_tics / 8.0
            shade = "#" + format(int(0x40 * alpha), "02x") + "0000"
            self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, VIEW_HEIGHT, fill=shade,
                                          stipple="gray50", width=0)

        if self.game.player.health <= 0:
            self.canvas.create_text(CANVAS_WIDTH / 2, VIEW_HEIGHT / 2, text="YOU DIED",
                                     fill="#ff2020", font=("Consolas", 28, "bold"))

    def _render_monsters(self, actor):
        rad = math.radians(actor.angle)
        forward = (math.cos(rad), math.sin(rad))
        right = (-forward[1], forward[0])
        halfFovRad = math.radians(FOV_DEG / 2)

        visible = []
        for other in self.game.monsters():
            if other.isRemoved or not (other.flags & 2):  # MF_SHOOTABLE
                continue
            dx, dy = other.x - actor.x, other.y - actor.y
            dist = math.hypot(dx, dy)
            if dist < 1.0 or dist > 2000.0:
                continue
            forwardComp = dx * forward[0] + dy * forward[1]
            rightComp = dx * right[0] + dy * right[1]
            if forwardComp <= 1.0:
                continue
            angleOff = math.atan2(rightComp, forwardComp)
            if abs(angleOff) > halfFovRad:
                continue
            screenX = CANVAS_WIDTH / 2 + math.tan(angleOff) * self.projPlaneDist
            size = (other.type.radius * 2 * self.projPlaneDist) / dist
            visible.append((dist, screenX, size, other))

        visible.sort(key=lambda v: -v[0])  # 먼 것부터 그려 가까운 게 위로 오게 한다.
        for dist, screenX, size, mob in visible:
            color = "#c81414" if mob.health > 0 else "#555555"
            top = VIEW_HEIGHT / 2 - size / 2
            bottom = VIEW_HEIGHT / 2 + size / 2
            self.canvas.create_rectangle(screenX - size / 3, top, screenX + size / 3, bottom,
                                          fill=color, outline="")
            self.canvas.create_text(screenX, top - 8, text=mob.type.name, fill="white",
                                     font=("Consolas", 8))

    # ------------------------------------------------------------------
    # automap.md
    # ------------------------------------------------------------------
    def _render_automap(self):
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, VIEW_HEIGHT, fill="#000000", width=0)
        automap = self.game.automap
        actor = self.game.player.actor
        scale = 0.18 * automap.zoom
        cx, cy = CANVAS_WIDTH / 2, VIEW_HEIGHT / 2

        def to_screen(x, y):
            return cx + (x - actor.x) * scale, cy - (y - actor.y) * scale

        # spp-source: examples/doom/automap.md#Class:Doom.AutoMap.render
        for line in automap.revealedLines:
            sx1, sy1 = to_screen(line.v1.x, line.v1.y)
            sx2, sy2 = to_screen(line.v2.x, line.v2.y)
            color = "#39c25a" if line.isPassable else "#c8c8c8"
            self.canvas.create_line(sx1, sy1, sx2, sy2, fill=color, width=1)

        rad = math.radians(actor.angle)
        arrow = [
            (actor.x + math.cos(rad) * 14, actor.y + math.sin(rad) * 14),
            (actor.x + math.cos(rad + 2.6) * 8, actor.y + math.sin(rad + 2.6) * 8),
            (actor.x + math.cos(rad - 2.6) * 8, actor.y + math.sin(rad - 2.6) * 8),
        ]
        pts = [to_screen(x, y) for x, y in arrow]
        self.canvas.create_polygon(pts, fill="#ffcc00", outline="")
        self.canvas.create_text(8, 8, anchor="nw", fill="#39c25a", font=("Consolas", 10),
                                 text="자동 지도 (Tab으로 닫기)")

    # ------------------------------------------------------------------
    # hud.md — 상태 표시줄 + 얼굴 표정
    # ------------------------------------------------------------------
    def _draw_face(self, cx, cy, r):
        category = getattr(self, "face_frame", "STFST")
        base = category.split("_")[0]
        grin = "GRIN" in category
        hit = "HIT" in category

        skin = {
            "STFST": "#e2a76f", "STFKILL": "#e2a76f", "STFOUCH": "#d98f5a",
            "STFEVL": "#c96a4a", "STFDEAD0": "#7a7a7a",
        }.get(base, "#e2a76f")

        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=skin, outline="#2a1a10", width=2)

        eyeDx = r * 0.35
        eyeDy = -r * 0.15
        eyeR = r * 0.16 if base != "STFEVL" else r * 0.22
        pupilShift = r * 0.06 if hit else 0.0

        if base == "STFDEAD0":
            for sign in (-1, 1):
                ex, ey = cx + sign * eyeDx, cy + eyeDy
                self.canvas.create_line(ex - 5, ey - 5, ex + 5, ey + 5, fill="black", width=2)
                self.canvas.create_line(ex - 5, ey + 5, ex + 5, ey - 5, fill="black", width=2)
            self.canvas.create_line(cx - r * 0.4, cy + r * 0.4, cx + r * 0.4, cy + r * 0.4,
                                     fill="black", width=2)
            return

        for sign in (-1, 1):
            ex, ey = cx + sign * eyeDx, cy + eyeDy
            self.canvas.create_oval(ex - eyeR, ey - eyeR, ex + eyeR, ey + eyeR, fill="white", outline="black")
            pr = eyeR * 0.45
            self.canvas.create_oval(ex - pr + pupilShift, ey - pr, ex + pr + pupilShift, ey + pr, fill="black")

        mouthY = cy + r * 0.42
        if grin:
            self.canvas.create_arc(cx - r * 0.45, mouthY - r * 0.3, cx + r * 0.45, mouthY + r * 0.25,
                                    start=200, extent=140, style="arc", outline="black", width=2)
        elif base == "STFST":
            self.canvas.create_line(cx - r * 0.3, mouthY, cx + r * 0.3, mouthY, fill="black", width=2)
        elif base == "STFKILL":
            self.canvas.create_arc(cx - r * 0.35, mouthY - r * 0.1, cx + r * 0.35, mouthY + r * 0.35,
                                    start=20, extent=140, style="arc", outline="black", width=2)
        else:  # STFOUCH / STFEVL — 고통스러운 표정, 입을 벌린다.
            self.canvas.create_oval(cx - r * 0.22, mouthY - r * 0.15, cx + r * 0.22, mouthY + r * 0.25,
                                     fill="#3a1010", outline="black")

    def _key_icon(self, x, y, size, color, owned):
        if owned:
            self.canvas.create_rectangle(x, y, x + size, y + size, fill=color, outline="#101010")
        else:
            self.canvas.create_rectangle(x, y, x + size, y + size, fill="#202020", outline="#404040")

    def _render_hud(self):
        player = self.game.player
        y0 = VIEW_HEIGHT
        self.canvas.create_rectangle(0, y0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="#141414", width=0)
        self.canvas.create_line(0, y0, CANVAS_WIDTH, y0, fill="#3a3a3a", width=2)

        # 얼굴.
        faceCx, faceCy = 34, y0 + HUD_HEIGHT / 2
        self._draw_face(faceCx, faceCy, 24)

        # 체력.
        healthRatio = max(0.0, min(1.0, player.health / max(player.maxHealth, 1)))
        bx, by, bw, bh = 76, y0 + 10, 110, 12
        self.canvas.create_rectangle(bx, by, bx + bw, by + bh, outline="#606060")
        self.canvas.create_rectangle(bx, by, bx + bw * healthRatio, by + bh,
                                      fill=_health_bar_color(healthRatio), width=0)
        self.canvas.create_text(bx, by - 2, anchor="sw", fill="#e0e0e0", font=("Consolas", 9),
                                 text=f"체력 {player.health}")

        # 방어구.
        armorRatio = max(0.0, min(1.0, player.armor / 200.0))
        ay = by + bh + 8
        self.canvas.create_rectangle(bx, ay, bx + bw, ay + bh, outline="#606060")
        self.canvas.create_rectangle(bx, ay, bx + bw * armorRatio, ay + bh, fill="#3b6fd1", width=0)
        self.canvas.create_text(bx, ay - 2, anchor="sw", fill="#e0e0e0", font=("Consolas", 9),
                                 text=f"방어구 {player.armor}")

        # 무기/탄약.
        weaponX = bx + bw + 24
        ammoType = self.game.playerWeapon.type.ammoType
        ammoText = f"{player.ammo.get(ammoType, 0)}" if ammoType else "-"
        self.canvas.create_text(weaponX, y0 + 14, anchor="nw", fill="#e0e0e0", font=("Consolas", 11, "bold"),
                                 text=player.currentWeapon)
        self.canvas.create_text(weaponX, y0 + 30, anchor="nw", fill="#e0e0e0", font=("Consolas", 14, "bold"),
                                 text=f"탄약 {ammoText}")

        # 열쇠.
        keyX = weaponX + 120
        for i, color_name in enumerate(("blue", "yellow", "red")):
            self._key_icon(keyX + i * 18, y0 + 12, 14, KEY_COLORS[color_name], color_name in player.keys)

        # 처치/아이템/tic 카운터.
        statsX = keyX + 3 * 18 + 20
        self.canvas.create_text(statsX, y0 + 12, anchor="nw", fill="#a0a0a0", font=("Consolas", 9),
                                 text=f"처치 {self.game.killCount}/{self.game.totalKills}")
        self.canvas.create_text(statsX, y0 + 28, anchor="nw", fill="#a0a0a0", font=("Consolas", 9),
                                 text=f"아이템 {self.game.itemCount}/{self.game.totalItems}")
        self.canvas.create_text(CANVAS_WIDTH - 8, y0 + 8, anchor="ne", fill="#606060",
                                 font=("Consolas", 8), text=f"tic {self.game.tic}")
        self.canvas.create_text(CANVAS_WIDTH - 8, CANVAS_HEIGHT - 8, anchor="se", fill="#606060",
                                 font=("Consolas", 8), text="Esc 메뉴  Tab 지도")

    # ------------------------------------------------------------------
    # menu.md
    # ------------------------------------------------------------------
    def _render_menu(self):
        menu = self.game.menuStack.current
        boxW, boxH = 260, 60 + 28 * len(menu.items)
        x0 = (CANVAS_WIDTH - boxW) / 2
        y0 = (VIEW_HEIGHT - boxH) / 2

        self.canvas.create_rectangle(x0, y0, x0 + boxW, y0 + boxH, fill="#101018", outline="#606080", width=2)
        self.canvas.create_text(x0 + boxW / 2, y0 + 22, text=menu.title, fill="#ffcc00",
                                 font=("Consolas", 14, "bold"))

        for i, item in enumerate(menu.items):
            iy = y0 + 56 + i * 28
            selected = i == menu.selectedIndex
            color = "#ffcc00" if selected else "#d0d0d0"
            prefix = "▶ " if selected else "   "
            self.canvas.create_text(x0 + boxW / 2, iy, text=prefix + item.label, fill=color,
                                     font=("Consolas", 12))

    # ------------------------------------------------------------------
    # intermission.md — 스테이지 클리어 화면. game.md의 "## GUI"대로 이 화면이
    # 열려 있을 때는 3D 시점/HUD/메뉴 대신 이 화면 하나가 전체를 채운다.
    # ------------------------------------------------------------------
    def _render_intermission(self):
        im = self.intermission
        self.canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill="#0a0a0a", width=0)
        self.canvas.create_text(CANVAS_WIDTH / 2, 50, text=f"{im.finishedMapName} 완료",
                                 fill="#ffcc00", font=("Consolas", 22, "bold"))

        rows = [
            ("처치", im.killPercent, "#d13b3b"),
            ("아이템", im.itemPercent, "#3b6fd1"),
            ("비밀", im.secretPercent, "#39c25a"),
        ]
        barX, barW = CANVAS_WIDTH / 2 - 140, 220
        for i, (label, percent, color) in enumerate(rows):
            y = 130 + i * 50
            self.canvas.create_text(barX - 10, y, anchor="e", fill="#e0e0e0",
                                     font=("Consolas", 12), text=label)
            self.canvas.create_rectangle(barX, y - 10, barX + barW, y + 10, outline="#606060")
            self.canvas.create_rectangle(barX, y - 10, barX + barW * percent / 100.0, y + 10,
                                          fill=color, width=0)
            self.canvas.create_text(barX + barW + 30, y, fill="#e0e0e0", font=("Consolas", 12),
                                     text=f"{percent}%")

        timeText = f"시간 {im.playerTimeTics // 35}초  (기준 {im.parTimeTics // 35}초)"
        self.canvas.create_text(CANVAS_WIDTH / 2, 300, fill="#a0a0a0", font=("Consolas", 11), text=timeText)
        self.canvas.create_text(CANVAS_WIDTH / 2, CANVAS_HEIGHT - 30, fill="#606060",
                                 font=("Consolas", 10), text="셰어웨어 마지막 맵 — 다음 맵 없음")
