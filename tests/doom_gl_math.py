"""render.md의 '뷰 행렬'/'투영 행렬' 계산을 위한 아주 작은 4x4 행렬 유틸리티.

numpy 없이 순수 파이썬으로 구현한다 — 이 프로젝트의 다른 파일들과 마찬가지로
표준 라이브러리만 쓴다는 관례를 따른다. 행렬은 컬럼 메이저(column-major)
16개 float 리스트로 표현한다(OpenGL의 glUniformMatrix4fv 기본 레이아웃과
같다).
"""
import math


def identity():
    return [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0]


def multiply(a, b):
    """a * b (둘 다 컬럼 메이저 4x4). 결과 = a를 먼저 적용한 뒤 b... 실제로는
    OpenGL 관례대로 result = a (column-major) 곱하기 b이며, 벡터에는
    result * v = a * (b * v) 순서로 적용된다(b가 먼저 적용됨)."""
    result = [0.0] * 16
    for col in range(4):
        for row in range(4):
            s = 0.0
            for k in range(4):
                s += a[k * 4 + row] * b[col * 4 + k]
            result[col * 4 + row] = s
    return result


def perspective(fovYDeg, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fovYDeg) / 2.0)
    m = [0.0] * 16
    m[0] = f / aspect
    m[5] = f
    m[10] = (far + near) / (near - far)
    m[11] = -1.0
    m[14] = (2 * far * near) / (near - far)
    return m


def ortho(left, right, bottom, top, near, far):
    m = identity()
    m[0] = 2.0 / (right - left)
    m[5] = 2.0 / (top - bottom)
    m[10] = -2.0 / (far - near)
    m[12] = -(right + left) / (right - left)
    m[13] = -(top + bottom) / (top - bottom)
    m[14] = -(far + near) / (far - near)
    return m


def _normalize(v):
    length = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if length < 1e-9:
        return (0.0, 0.0, 0.0)
    return (v[0] / length, v[1] / length, v[2] / length)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def look_at(eye, center, up):
    f = _normalize((center[0] - eye[0], center[1] - eye[1], center[2] - eye[2]))
    s = _normalize(_cross(f, up))
    u = _cross(s, f)
    m = identity()
    m[0], m[4], m[8] = s[0], s[1], s[2]
    m[1], m[5], m[9] = u[0], u[1], u[2]
    m[2], m[6], m[10] = -f[0], -f[1], -f[2]
    m[12] = -_dot(s, eye)
    m[13] = -_dot(u, eye)
    m[14] = _dot(f, eye)
    return m


def view_from_player(x, height, z, yawDeg):
    """DOOM의 (worldX, height, worldZ) 위치와 yaw(도, +x축 기준 반시계)로 뷰 행렬을 만든다."""
    yaw = math.radians(yawDeg)
    forward = (math.cos(yaw), 0.0, math.sin(yaw))
    eye = (x, height, z)
    center = (x + forward[0], height, z + forward[2])
    return look_at(eye, center, (0.0, 1.0, 0.0))


def right_and_up_from_view(viewMatrix):
    """뷰 행렬(월드->카메라)의 회전 부분에서 카메라의 오른쪽/위쪽 월드 벡터를 뽑는다
    (빌보드 스프라이트를 카메라 쪽으로 세우는 데 쓴다)."""
    right = (viewMatrix[0], viewMatrix[4], viewMatrix[8])
    up = (viewMatrix[1], viewMatrix[5], viewMatrix[9])
    return right, up
