"""examples/doom/render.md의 현대적 GPU 렌더링(셰이더/버텍스 버퍼/깊이 버퍼/
인스턴스 드로우)을 실제로 구현한 플레이 가능한 창.

tests/app_doom.py(tkinter + CPU 레이캐스팅)와 같은 게임 로직
(doom_game.py의 Game.tick)을 그대로 쓰지만, 화면에 내놓는 방식은
std/graphics/opengl3.md 스타일 — 맵을 불러올 때 벽/바닥/천장 정점을 한 번
GPU에 올려두고(doom_render_mesh.py), 매 프레임에는 카메라 유니폼만
갱신해서 몇 번의 드로우 콜(레벨 1~2회 + 스프라이트 인스턴스 1회 + UI
오버레이 1~2회)로 그린다. OpenGL 자체는 이 프로젝트의 다른 예제들처럼
표준 라이브러리만으로는 만들 수 없는 실제 그래픽 API이므로(kind: native),
PyOpenGL + pygame(창·컨텍스트 생성)을 그대로 쓴다.
"""
import math

import pygame
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_LINES, GL_TRIANGLES,
    glClear, glClearColor, glDisable, glEnable, glUseProgram, glViewport,
)

from doom_game import Game
from doom_gl_math import ortho, perspective, right_and_up_from_view, view_from_player
from doom_menu import Menu, MenuItem
from doom_render_gl_backend import (
    LEVEL_FRAGMENT_SHADER, LEVEL_VERTEX_SHADER, SPRITE_FRAGMENT_SHADER, SPRITE_VERTEX_SHADER,
    TEXT_FRAGMENT_SHADER, TEXT_VERTEX_SHADER, UI_FRAGMENT_SHADER, UI_VERTEX_SHADER,
    LevelMeshGpu, SpriteBillboardGpu, TextRenderer, UiOverlayGpu,
    compile_shader_program, set_uniform_mat4, set_uniform_vec3,
)
from doom_render_mesh import build_level_mesh
from doom_ui_geometry import face_triangles, health_bar_color, hud_bar_geometry, key_icon_geometry, rect, thick_line

SCREEN_W, SCREEN_H = 960, 600
EYE_HEIGHT = 41.0
FOV_DEG = 90.0
TICS_PER_SECOND = 35
MOVE_SPEED = 400
TURN_SPEED = 6

FORWARD_KEYS = {pygame.K_w: 1, pygame.K_UP: 1, pygame.K_s: -1, pygame.K_DOWN: -1}
STRAFE_KEYS = {pygame.K_LEFT: -1, pygame.K_RIGHT: 1}
TURN_KEYS = {pygame.K_a: -1, pygame.K_d: 1}

MONSTER_COLOR = (0.78, 0.08, 0.08)
DEAD_MONSTER_COLOR = (0.33, 0.33, 0.33)


class DoomGlApp:
    def __init__(self, game):
        self.game = game
        pygame.init()
        # 깊이 버퍼를 명시적으로 요청해야 한다 — 요청하지 않으면 SDL/GL 컨텍스트에
        # 깊이 버퍼가 아예 안 만들어져서 glEnable(GL_DEPTH_TEST)가 조용히 아무
        # 효과가 없고, 먼 벽이 가까운 벽을 뚫고 그려지는("벽이 투과되어 보이는")
        # 증상이 생긴다.
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("DOOM (SPP reference build, modern GL) — E1M1")

        depthBits = pygame.display.gl_get_attribute(pygame.GL_DEPTH_SIZE)
        if depthBits <= 0:
            raise RuntimeError(f"depth buffer not available (GL_DEPTH_SIZE={depthBits})")

        glEnable(GL_DEPTH_TEST)
        glClearColor(0.05, 0.05, 0.1, 1.0)

        self.levelShader = compile_shader_program(LEVEL_VERTEX_SHADER, LEVEL_FRAGMENT_SHADER)
        self.spriteShader = compile_shader_program(SPRITE_VERTEX_SHADER, SPRITE_FRAGMENT_SHADER)
        self.uiShader = compile_shader_program(UI_VERTEX_SHADER, UI_FRAGMENT_SHADER)
        self.textShader = compile_shader_program(TEXT_VERTEX_SHADER, TEXT_FRAGMENT_SHADER)
        self.text = TextRenderer(fontSize=18)

        # spp-source: examples/doom/render.md#Feature:_레벨_지오메트리_만들기 — 맵당 한 번.
        meshData = build_level_mesh(game.map)
        self.levelMesh = LevelMeshGpu(meshData)
        self.sprites = SpriteBillboardGpu()
        self.ui = UiOverlayGpu()

        self.projMatrix = perspective(FOV_DEG, SCREEN_W / SCREEN_H, 1.0, 4000.0)
        self.orthoMatrix = ortho(0, SCREEN_W, SCREEN_H, 0, -1, 1)

        self.pressed = set()
        self.fire_pending = False
        self.use_pending = False
        self.running = True
        self.clock = pygame.time.Clock()

        self.prev_health = game.player.health
        self.prev_kills = game.killCount
        self.hit_flash_tics = 0
        self.face_frame = "STFST"

    # ------------------------------------------------------------------
    def _build_main_menu(self):
        return Menu("DOOM", [
            MenuItem("계속하기", "Action", action=lambda: self.game.menuStack.closeOneLevel()),
            MenuItem("자동 지도 켜기/끄기", "Action", action=lambda: self.game.automap.toggle()),
            MenuItem("게임 종료", "Action", action=lambda: setattr(self, "running", False)),
        ])

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._on_key_down(event.key)
            elif event.type == pygame.KEYUP:
                self.pressed.discard(event.key)

    def _on_key_down(self, key):
        if self.game.menuStack.isOpen:
            if key == pygame.K_UP:
                self.game.menuStack.moveSelection("Up")
            elif key == pygame.K_DOWN:
                self.game.menuStack.moveSelection("Down")
            elif key == pygame.K_RETURN:
                self.game.menuStack.confirmSelection()
            elif key == pygame.K_ESCAPE:
                self.game.menuStack.closeOneLevel()
            return

        if key == pygame.K_ESCAPE:
            self.game.menuStack.open(self._build_main_menu())
            return
        if key == pygame.K_TAB:
            self.game.automap.toggle()
            return

        self.pressed.add(key)
        if key == pygame.K_SPACE:
            self.fire_pending = True
        elif key == pygame.K_e:
            self.use_pending = True

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

    def _update_face_state(self):
        player = self.game.player
        damaged = player.health < self.prev_health
        justKilled = self.game.killCount > self.prev_kills
        if damaged:
            self.hit_flash_tics = 8
        elif self.hit_flash_tics > 0:
            self.hit_flash_tics -= 1
        self.face_frame = self.game.hud.updateFace(
            player, justDamagedFromDirection=("front" if damaged else None), justKilled=justKilled,
        )
        self.prev_health = player.health
        self.prev_kills = self.game.killCount

    # ------------------------------------------------------------------
    def run(self):
        while self.running:
            self._handle_events()
            self.game.tick(self._build_raw_input())
            self._update_face_state()
            self._render()
            pygame.display.flip()
            self.clock.tick(TICS_PER_SECOND)
        pygame.quit()

    def render_once(self):
        """헤드리스가 아닌 단발성 검증(스크린샷 등)을 위해 한 프레임만 그린다."""
        self._handle_events()
        self._render()
        pygame.display.flip()

    # ------------------------------------------------------------------
    def _render(self):
        glViewport(0, 0, SCREEN_W, SCREEN_H)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.game.automap.isOpen:
            self._render_automap()
        else:
            self._render_3d()

        self._render_hud()
        if self.game.menuStack.isOpen:
            self._render_menu()

    def _view_and_cam(self):
        actor = self.game.player.actor
        # 원본 P_CalcHeight처럼, 눈 높이가 지금 서 있는 섹터의 천장을 뚫고
        # 올라가지 않게 자른다 — 안 그러면 낮은 천장 구간에서 카메라가
        # 천장 지오메트리 안쪽에 들어가 버려("벽을 뚫고 들어간다"의 실제
        # 원인은 대부분 이거였다 — 수평 충돌이 아니라 수직 클리핑 누락).
        maxEyeY = actor.sector.ceilingHeight - 4.0
        eyeY = min(actor.z + EYE_HEIGHT, max(actor.z, maxEyeY))
        view = view_from_player(actor.x, eyeY, actor.y, actor.angle)
        viewProj = self._mul(self.projMatrix, view)
        return view, viewProj, (actor.x, eyeY, actor.y)

    @staticmethod
    def _mul(a, b):
        from doom_gl_math import multiply
        return multiply(a, b)

    def _render_3d(self):
        view, viewProj, camPos = self._view_and_cam()

        glUseProgram(self.levelShader)
        set_uniform_mat4(self.levelShader, "uViewProj", viewProj)
        set_uniform_vec3(self.levelShader, "uCamPos", camPos)
        self.levelMesh.draw()

        # spp-source: examples/doom/render.md#Feature:_스프라이트_그리기
        right, up = right_and_up_from_view(view)
        instanceFloats = []
        count = 0
        for mob in self.game.monsters():
            if mob.isRemoved:
                continue
            color = MONSTER_COLOR if mob.health > 0 else DEAD_MONSTER_COLOR
            cx, cy, cz = mob.x, mob.z + mob.type.height / 2, mob.y
            w = mob.type.radius * 2
            h = mob.type.height
            instanceFloats.extend([cx, cy, cz, w, h, color[0], color[1], color[2]])
            count += 1

        glUseProgram(self.spriteShader)
        set_uniform_mat4(self.spriteShader, "uViewProj", viewProj)
        set_uniform_vec3(self.spriteShader, "uCamRight", right)
        set_uniform_vec3(self.spriteShader, "uCamUp", up)
        self.sprites.draw_instances(instanceFloats, count)

    def _render_automap(self):
        automap = self.game.automap
        actor = self.game.player.actor
        scale = 0.18 * automap.zoom
        cx, cy = SCREEN_W / 2, SCREEN_H / 2

        def to_screen(x, y):
            return cx + (x - actor.x) * scale, cy - (y - actor.y) * scale

        verts = []
        for line in automap.revealedLines:
            sx1, sy1 = to_screen(line.v1.x, line.v1.y)
            sx2, sy2 = to_screen(line.v2.x, line.v2.y)
            color = (0.22, 0.76, 0.35) if line.isPassable else (0.8, 0.8, 0.8)
            verts.extend([sx1, sy1, color[0], color[1], color[2], sx2, sy2, color[0], color[1], color[2]])

        glUseProgram(self.uiShader)
        set_uniform_mat4(self.uiShader, "uOrtho", self.orthoMatrix)
        glDisable(GL_DEPTH_TEST)
        self.ui.draw(verts, primitive=GL_LINES)

        rad = math.radians(actor.angle)
        arrow = [
            (actor.x + math.cos(rad) * 14, actor.y + math.sin(rad) * 14),
            (actor.x + math.cos(rad + 2.6) * 8, actor.y + math.sin(rad + 2.6) * 8),
            (actor.x + math.cos(rad - 2.6) * 8, actor.y + math.sin(rad - 2.6) * 8),
        ]
        pts = [to_screen(x, y) for x, y in arrow]
        tri = []
        for x, y in pts:
            tri.extend([x, y, 1.0, 0.8, 0.0])
        self.ui.draw(tri, primitive=GL_TRIANGLES)
        self.text.draw(self.textShader, self.orthoMatrix, "자동 지도 (Tab으로 닫기)", 10, 10,
                        color255=(60, 220, 90))
        glEnable(GL_DEPTH_TEST)

    def _render_hud(self):
        player = self.game.player
        y0 = SCREEN_H - 90
        verts = rect(0, y0, SCREEN_W, SCREEN_H, (0.08, 0.08, 0.08))

        verts += face_triangles(50, y0 + 45, 38, self.face_frame)

        healthRatio = max(0.0, min(1.0, player.health / max(player.maxHealth, 1)))
        verts += hud_bar_geometry(120, y0 + 16, 180, 18, healthRatio, health_bar_color(healthRatio))
        armorRatio = max(0.0, min(1.0, player.armor / 200.0))
        verts += hud_bar_geometry(120, y0 + 44, 180, 18, armorRatio, (0.23, 0.44, 0.82))

        keyX = 340
        for i, colorName in enumerate(("blue", "yellow", "red")):
            verts += key_icon_geometry(keyX + i * 26, y0 + 16, 20, colorName, colorName in player.keys)

        if self.hit_flash_tics > 0:
            alpha = self.hit_flash_tics / 8.0
            verts += rect(0, 0, SCREEN_W, SCREEN_H - 90, (0.4 * alpha, 0.0, 0.0))

        glUseProgram(self.uiShader)
        set_uniform_mat4(self.uiShader, "uOrtho", self.orthoMatrix)
        glDisable(GL_DEPTH_TEST)
        self.ui.draw(verts, primitive=GL_TRIANGLES)

        ammoType = self.game.playerWeapon.type.ammoType
        ammoText = str(player.ammo.get(ammoType, 0)) if ammoType else "-"
        self.text.draw(self.textShader, self.orthoMatrix, f"체력 {player.health}", 120, y0 - 2)
        self.text.draw(self.textShader, self.orthoMatrix, f"방어구 {player.armor}", 120, y0 + 26)
        self.text.draw(self.textShader, self.orthoMatrix, player.currentWeapon, keyX + 90, y0 + 12)
        self.text.draw(self.textShader, self.orthoMatrix, f"탄약 {ammoText}", keyX + 90, y0 + 36)
        self.text.draw(
            self.textShader, self.orthoMatrix,
            f"처치 {self.game.killCount}/{self.game.totalKills}  아이템 {self.game.itemCount}/{self.game.totalItems}",
            keyX + 220, y0 + 20,
        )
        self.text.draw(self.textShader, self.orthoMatrix, f"tic {self.game.tic}", SCREEN_W - 110, y0 - 20)
        self.text.draw(self.textShader, self.orthoMatrix, "Esc 메뉴  Tab 지도", SCREEN_W - 200, SCREEN_H - 24)
        glEnable(GL_DEPTH_TEST)

    def _render_menu(self):
        menu = self.game.menuStack.current
        boxW, boxH = 300, 60 + 40 * len(menu.items)
        x0 = (SCREEN_W - boxW) / 2
        y0 = (SCREEN_H - 90 - boxH) / 2

        verts = rect(x0, y0, x0 + boxW, y0 + boxH, (0.06, 0.06, 0.1))
        verts += thick_line(x0, y0, x0 + boxW, y0, 2, (0.4, 0.4, 0.5))
        for i, item in enumerate(menu.items):
            iy = y0 + 56 + i * 40
            selected = i == menu.selectedIndex
            color = (1.0, 0.8, 0.0) if selected else (0.7, 0.7, 0.7)
            verts += rect(x0 + 24, iy - 10, x0 + boxW - 24, iy + 10,
                           (0.15, 0.15, 0.2) if selected else (0.06, 0.06, 0.1))
            verts += thick_line(x0 + 24, iy, x0 + 24 + (200 if selected else 0), iy, 4, color)

        glUseProgram(self.uiShader)
        set_uniform_mat4(self.uiShader, "uOrtho", self.orthoMatrix)
        glDisable(GL_DEPTH_TEST)
        self.ui.draw(verts, primitive=GL_TRIANGLES)

        self.text.draw(self.textShader, self.orthoMatrix, menu.title, x0 + boxW / 2 - 20, y0 + 10,
                        color255=(255, 204, 0))
        for i, item in enumerate(menu.items):
            iy = y0 + 56 + i * 40
            selected = i == menu.selectedIndex
            color255 = (255, 204, 0) if selected else (200, 200, 200)
            self.text.draw(self.textShader, self.orthoMatrix, item.label, x0 + 40, iy - 12, color255=color255)
        glEnable(GL_DEPTH_TEST)


def main():
    import os
    import random
    from doom_wad import WadFile

    wadPath = os.path.join(os.path.dirname(__file__), "..", "examples", "doom", "assets", "doom1.wad")
    wad = WadFile(wadPath)
    game = Game.Start(wad, "E1M1", rng=random.Random(1).random)
    app = DoomGlApp(game)
    app.run()


if __name__ == "__main__":
    main()
