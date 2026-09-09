"""hud.md/menu.md/automap.md의 2D 오버레이를 위한 순수 지오메트리 생성기.

OpenGL에 의존하지 않는다 — 삼각형/선 정점 목록(플랫 float 리스트: x, y,
r, g, b)만 만든다. doom_render_gl_backend.py의 UiOverlayGpu가 이 목록을
그대로 GPU 동적 버퍼에 올려 그린다. GPU 없이도 이 모듈만으로 "표정이
바뀌면 정점 데이터도 그에 맞게 바뀌는지"를 테스트할 수 있다.
"""
import math


def rect(x0, y0, x1, y1, color):
    r, g, b = color
    return [
        x0, y0, r, g, b, x1, y0, r, g, b, x1, y1, r, g, b,
        x0, y0, r, g, b, x1, y1, r, g, b, x0, y1, r, g, b,
    ]


def circle_fan(cx, cy, radius, color, segments=20):
    r, g, b = color
    verts = []
    for i in range(segments):
        a0 = 2 * math.pi * i / segments
        a1 = 2 * math.pi * (i + 1) / segments
        verts.extend([cx, cy, r, g, b])
        verts.extend([cx + math.cos(a0) * radius, cy + math.sin(a0) * radius, r, g, b])
        verts.extend([cx + math.cos(a1) * radius, cy + math.sin(a1) * radius, r, g, b])
    return verts


def thick_line(x1, y1, x2, y2, width, color):
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return []
    nx, ny = -dy / length * width / 2, dx / length * width / 2
    r, g, b = color
    p1, p2, p3, p4 = (x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)
    return [
        p1[0], p1[1], r, g, b, p2[0], p2[1], r, g, b, p3[0], p3[1], r, g, b,
        p1[0], p1[1], r, g, b, p3[0], p3[1], r, g, b, p4[0], p4[1], r, g, b,
    ]


SKIN_COLORS = {
    "STFST": (0.89, 0.65, 0.44), "STFKILL": (0.89, 0.65, 0.44),
    "STFOUCH": (0.85, 0.56, 0.35), "STFEVL": (0.79, 0.42, 0.29),
    "STFDEAD0": (0.48, 0.48, 0.48),
}
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.05, 0.05, 0.05)


# spp-source: examples/doom/hud.md#Feature:_얼굴_표정_갱신 (2D 지오메트리로 옮긴 것)
def face_triangles(cx, cy, r, faceFrame):
    base = faceFrame.split("_")[0]
    grin = "GRIN" in faceFrame
    hit = "HIT" in faceFrame
    skin = SKIN_COLORS.get(base, SKIN_COLORS["STFST"])

    verts = circle_fan(cx, cy, r, skin, segments=24)

    eyeDx, eyeDy = r * 0.35, -r * 0.15
    eyeR = r * 0.16 if base != "STFEVL" else r * 0.22
    pupilShift = r * 0.06 if hit else 0.0
    mouthY = cy + r * 0.42

    if base == "STFDEAD0":
        for sign in (-1, 1):
            ex, ey = cx + sign * eyeDx, cy + eyeDy
            verts += thick_line(ex - 5, ey - 5, ex + 5, ey + 5, 2, BLACK)
            verts += thick_line(ex - 5, ey + 5, ex + 5, ey - 5, 2, BLACK)
        verts += thick_line(cx - r * 0.4, mouthY, cx + r * 0.4, mouthY, 2, BLACK)
        return verts

    for sign in (-1, 1):
        ex, ey = cx + sign * eyeDx, cy + eyeDy
        verts += circle_fan(ex, ey, eyeR, WHITE, segments=14)
        verts += circle_fan(ex + pupilShift, ey, eyeR * 0.45, BLACK, segments=10)

    if grin:
        verts += thick_line(cx - r * 0.3, mouthY - r * 0.05, cx + r * 0.3, mouthY - r * 0.05, 3, BLACK)
    elif base == "STFST":
        verts += thick_line(cx - r * 0.3, mouthY, cx + r * 0.3, mouthY, 2, BLACK)
    elif base == "STFKILL":
        verts += thick_line(cx - r * 0.3, mouthY - r * 0.05, cx + r * 0.3, mouthY + r * 0.1, 2, BLACK)
    else:  # STFOUCH / STFEVL — 입을 벌린 고통스러운 표정.
        verts += circle_fan(cx, mouthY, r * 0.18, (0.23, 0.06, 0.06), segments=12)

    return verts


def health_bar_color(ratio):
    if ratio > 0.66:
        return (0.22, 0.76, 0.35)
    if ratio > 0.33:
        return (0.82, 0.77, 0.23)
    return (0.82, 0.23, 0.23)


# spp-source: examples/doom/hud.md#Class:_Doom.Hud.render
def hud_bar_geometry(x, y, w, h, ratio, fillColor):
    verts = rect(x, y, x + w, y + h, (0.3, 0.3, 0.3))
    verts += rect(x + 2, y + 2, x + 2 + max(0.0, (w - 4) * ratio), y + h - 2, fillColor)
    return verts


KEY_COLORS = {"blue": (0.23, 0.44, 0.82), "yellow": (0.82, 0.77, 0.23), "red": (0.82, 0.23, 0.23)}


def key_icon_geometry(x, y, size, colorName, owned):
    color = KEY_COLORS[colorName] if owned else (0.2, 0.2, 0.2)
    return rect(x, y, x + size, y + size, color)
