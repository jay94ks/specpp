"""examples/doom/render.md의 Doom.Renderer.Backend를
std/graphics/opengl3.md 스타일(셰이더/VBO/VAO/EBO, 인스턴스 드로우)로 구현한
아주 얇은 PyOpenGL 래퍼.

실제 WAD 텍스처 이미지는 디코딩하지 않는다(wad.md Open Points에 이미 적힌
범위 밖 항목) — uploadTextureArray 대신 정점 색(vertex color) 속성을 쓴다.
GPU/창이 있어야 동작하므로 단위 테스트 대상이 아니다(순수 로직인
doom_render_mesh.py/doom_gl_math.py가 테스트 대상이다) — 이 파일은
app_doom_gl.py에서 실제로 띄워서 눈으로 검증한다.
"""
import ctypes

import pygame
from OpenGL.GL import *  # noqa: F401,F403

TEXT_VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aUv;
uniform mat4 uOrtho;
out vec2 vUv;
void main() {
    gl_Position = uOrtho * vec4(aPos, 0.0, 1.0);
    vUv = aUv;
}
"""

TEXT_FRAGMENT_SHADER = """
#version 330 core
in vec2 vUv;
uniform sampler2D uTex;
out vec4 FragColor;
void main() {
    FragColor = texture(uTex, vUv);
}
"""

LEVEL_VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;
layout(location = 2) in float aLight;
uniform mat4 uViewProj;
uniform vec3 uCamPos;
out vec3 vColor;
out float vLight;
out float vDist;
void main() {
    gl_Position = uViewProj * vec4(aPos, 1.0);
    vColor = aColor;
    vLight = aLight;
    vDist = length(aPos - uCamPos);
}
"""

LEVEL_FRAGMENT_SHADER = """
#version 330 core
in vec3 vColor;
in float vLight;
in float vDist;
out vec4 FragColor;
void main() {
    float brightness = clamp(vLight / 255.0, 0.15, 1.0);
    float fog = clamp(1.0 - vDist / 1400.0, 0.25, 1.0);
    FragColor = vec4(vColor * brightness * fog, 1.0);
}
"""

SPRITE_VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec2 aLocal;
layout(location = 1) in vec3 iPos;
layout(location = 2) in vec2 iScale;
layout(location = 3) in vec3 iColor;
uniform mat4 uViewProj;
uniform vec3 uCamRight;
uniform vec3 uCamUp;
out vec3 vColor;
out vec2 vLocal;
void main() {
    vec3 worldPos = iPos + uCamRight * (aLocal.x * iScale.x) + uCamUp * (aLocal.y * iScale.y);
    gl_Position = uViewProj * vec4(worldPos, 1.0);
    vColor = iColor;
    vLocal = aLocal;
}
"""

SPRITE_FRAGMENT_SHADER = """
#version 330 core
in vec3 vColor;
in vec2 vLocal;
out vec4 FragColor;
void main() {
    if (length(vLocal) > 0.5) discard;
    FragColor = vec4(vColor, 1.0);
}
"""

UI_VERTEX_SHADER = """
#version 330 core
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec3 aColor;
uniform mat4 uOrtho;
out vec3 vColor;
void main() {
    gl_Position = uOrtho * vec4(aPos, 0.0, 1.0);
    vColor = aColor;
}
"""

UI_FRAGMENT_SHADER = """
#version 330 core
in vec3 vColor;
out vec4 FragColor;
void main() { FragColor = vec4(vColor, 1.0); }
"""


def compile_shader_program(vertexSrc, fragmentSrc):
    def compile_stage(src, stage):
        shader = glCreateShader(stage)
        glShaderSource(shader, src)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            raise RuntimeError(glGetShaderInfoLog(shader).decode())
        return shader

    vs = compile_stage(vertexSrc, GL_VERTEX_SHADER)
    fs = compile_stage(fragmentSrc, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(program).decode())
    glDeleteShader(vs)
    glDeleteShader(fs)
    return program


class LevelMeshGpu:
    """build_level_mesh()의 결과를 한 번 GPU에 올린 것 (VAO/VBO/EBO)."""

    def __init__(self, meshData):
        vertices = (ctypes.c_float * len(meshData.vertices))(*meshData.vertices)
        indices = (ctypes.c_uint32 * len(meshData.indices))(*meshData.indices)
        self.indexCount = len(meshData.indices)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(vertices), vertices, GL_STATIC_DRAW)

        stride = 7 * 4
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))
        glEnableVertexAttribArray(2)

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, ctypes.sizeof(indices), indices, GL_STATIC_DRAW)

        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, self.indexCount, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)


class SpriteBillboardGpu:
    """단위 사각형(로컬 좌표) VAO 하나 + 매 프레임 다시 채우는 인스턴스 VBO."""

    QUAD = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]
    QUAD_INDICES = [0, 1, 2, 0, 2, 3]

    def __init__(self):
        quad = (ctypes.c_float * (len(self.QUAD) * 2))(*[v for p in self.QUAD for v in p])
        indices = (ctypes.c_uint32 * len(self.QUAD_INDICES))(*self.QUAD_INDICES)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.quadVbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.quadVbo)
        glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(quad), quad, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        self.instanceVbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.instanceVbo)
        stride = 8 * 4  # pos(3) + scale(2) + color(3)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribDivisor(1, 1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(2)
        glVertexAttribDivisor(2, 1)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(5 * 4))
        glEnableVertexAttribArray(3)
        glVertexAttribDivisor(3, 1)

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, ctypes.sizeof(indices), indices, GL_STATIC_DRAW)

        glBindVertexArray(0)

    def draw_instances(self, instanceFloats, instanceCount):
        if instanceCount == 0:
            return
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.instanceVbo)
        data = (ctypes.c_float * len(instanceFloats))(*instanceFloats)
        glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(data), data, GL_DYNAMIC_DRAW)
        glDrawElementsInstanced(GL_TRIANGLES, len(self.QUAD_INDICES), GL_UNSIGNED_INT, None, instanceCount)
        glBindVertexArray(0)


class UiOverlayGpu:
    """HUD/메뉴/자동지도처럼 매 프레임 내용이 바뀌는 2D 오버레이용 동적 버퍼."""

    def __init__(self, maxVertices=8192):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, maxVertices * 5 * 4, None, GL_DYNAMIC_DRAW)
        stride = 5 * 4
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(2 * 4))
        glEnableVertexAttribArray(1)
        glBindVertexArray(0)

    def draw(self, vertexFloats, primitive=GL_TRIANGLES):
        if not vertexFloats:
            return
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        data = (ctypes.c_float * len(vertexFloats))(*vertexFloats)
        glBufferSubData(GL_ARRAY_BUFFER, 0, ctypes.sizeof(data), data)
        glDrawArrays(primitive, 0, len(vertexFloats) // 5)
        glBindVertexArray(0)


def set_uniform_mat4(program, name, matrix16):
    loc = glGetUniformLocation(program, name)
    glUniformMatrix4fv(loc, 1, GL_FALSE, (ctypes.c_float * 16)(*matrix16))


def set_uniform_vec3(program, name, xyz):
    loc = glGetUniformLocation(program, name)
    glUniform3f(loc, xyz[0], xyz[1], xyz[2])


class TextRenderer:
    """raw OpenGL에는 폰트가 없으므로, pygame.font(SDL_ttf)로 문자열을 비트맵
    Surface로 그린 뒤 텍스처로 올려 사각형 하나로 그린다. 같은 문자열/색을
    다시 요청하면 텍스처를 새로 만들지 않고 캐시를 재사용한다."""

    def __init__(self, fontSize=18):
        if not pygame.font.get_init():
            pygame.font.init()
        # Consolas 등 서구권 고정폭 폰트는 한글(Hangul) 글리프가 없어 깨져
        # 보인다 — 맑은 고딕처럼 한글을 실제로 담고 있는 폰트를 쓴다.
        self.font = pygame.font.SysFont("malgungothic", fontSize)
        self._cache = {}  # (text, color) -> (textureId, width, height)

        quad = (ctypes.c_float * 16)(
            0, 0, 0, 0,  1, 0, 1, 0,  1, 1, 1, 1,  0, 1, 0, 1,
        )
        indices = (ctypes.c_uint32 * 6)(0, 1, 2, 0, 2, 3)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(quad), quad, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))
        glEnableVertexAttribArray(1)
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, ctypes.sizeof(indices), indices, GL_STATIC_DRAW)
        glBindVertexArray(0)

    def _texture_for(self, text, color255):
        key = (text, color255)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        surface = self.font.render(text, True, color255).convert_alpha()
        width, height = surface.get_size()
        # flipped=False: 첫 바이트 행 = surface의 첫(맨 위) 행. 아래 draw()의
        # 사각형이 화면 좌상단(0,0)을 uv(0,0)에 그대로 대응시키므로, 여기서
        # 다시 뒤집으면 텍스트가 위아래·좌우로 뒤집혀 보인다(실제로 겪은 버그).
        raw = pygame.image.tostring(surface, "RGBA", False)
        texId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texId)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, raw)
        self._cache[key] = (texId, width, height)
        return self._cache[key]

    def draw(self, shader, orthoMatrix, text, x, y, color255=(224, 224, 224), scale=1.0):
        if not text:
            return
        texId, width, height = self._texture_for(text, color255)
        w, h = width * scale, height * scale
        quad = (ctypes.c_float * 16)(
            x, y, 0, 0,  x + w, y, 1, 0,  x + w, y + h, 1, 1,  x, y + h, 0, 1,
        )
        glUseProgram(shader)
        set_uniform_mat4(shader, "uOrtho", orthoMatrix)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texId)
        glUniform1i(glGetUniformLocation(shader, "uTex"), 0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, ctypes.sizeof(quad), quad)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        glDisable(GL_BLEND)
