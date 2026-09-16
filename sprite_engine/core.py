# -*- coding: utf-8 -*-
"""sprite_engine.core — 通用像素画布与图元库（与角色无关）

提供：
  Canvas      像素画布（带边界钳制、镜像、bbox）
  ell/rect/tri/bez/limb/seg2   图元（返回像素坐标列表，纯函数）
  stamp       画部件并自动加 1px 外描边（8 邻域）
  decal       无描边贴花（条纹/五官/高光等）
"""
import math


class Canvas:
    """单帧像素画布，格子大小由调用方指定（艺术像素）。"""
    __slots__ = ('w', 'h', 'g')

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.g = [[None] * w for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = c

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.g[y][x]
        return None

    def mirror(self):
        """水平镜像，返回新 Canvas（用于 running-left 等）。"""
        out = Canvas(self.w, self.h)
        out.g = [[self.g[y][self.w - 1 - x] for x in range(self.w)]
                 for y in range(self.h)]
        return out

    def bbox(self):
        xs, ys = [], []
        for y in range(self.h):
            for x in range(self.w):
                if self.g[y][x]:
                    xs.append(x); ys.append(y)
        if not xs:
            return None
        return (min(xs), min(ys), max(xs), max(ys))


# ---------------- 图元（纯函数，返回 [(x,y), ...]） ----------------
def ell(cx, cy, rx, ry):
    pts = []
    if rx <= 0 or ry <= 0:
        return [(cx, cy)]
    for dy in range(-ry, ry + 1):
        t = 1.0 - (dy / ry) ** 2
        dx = int(math.floor(rx * math.sqrt(max(0.0, t)) + 0.5))
        for x in range(cx - dx, cx + dx + 1):
            pts.append((x, cy + dy))
    return pts


def rect(x0, y0, x1, y1):
    return [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]


def tri(tip, bl, br):
    pts = []
    ty = tip[1]
    by = max(bl[1], br[1])
    for y in range(ty, by + 1):
        t = 0.0 if by == ty else (y - ty) / (by - ty)
        xl = tip[0] + (bl[0] - tip[0]) * t
        xr = tip[0] + (br[0] - tip[0]) * t
        for x in range(int(math.floor(min(xl, xr) + 0.5)),
                       int(math.floor(max(xl, xr) + 0.5)) + 1):
            pts.append((x, y))
    return pts


def bez(p0, p1, p2, n=14):
    out = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 2
        b = 2 * (1 - t) * t
        c = t ** 2
        out.append((a * p0[0] + b * p1[0] + c * p2[0],
                    a * p0[1] + b * p1[1] + c * p2[1]))
    return out


def limb(p0, p1, p2, r):
    """沿二次贝塞尔曲线的粗 limb（尾巴/手臂）。"""
    pts = []
    for (x, y) in bez(p0, p1, p2):
        pts += ell(int(round(x)), int(round(y)), r, r)
    return pts


def seg2(x0, y0, x1, y1):
    """2px 宽的 limb 段（腿）。"""
    pts = []
    n = int(max(abs(x1 - x0), abs(y1 - y0))) or 1
    for i in range(n + 1):
        t = i / n
        x = int(round(x0 + (x1 - x0) * t))
        y = int(round(y0 + (y1 - y0) * t))
        pts += [(x, y), (x + 1, y)]
    return pts


# ---------------- 绘制 ----------------
def stamp(cv, pts, color, outline):
    """画部件：先铺 8 邻域外描边，再铺填充（后画者自然覆盖先画者 => 内部轮廓线）。"""
    S = set(pts)
    if outline:
        O = set()
        for (x, y) in S:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q not in S:
                        O.add(q)
        for q in O:
            cv.set(q[0], q[1], outline)
    for q in S:
        cv.set(q[0], q[1], color)


def decal(cv, pts, color):
    """无描边贴花。"""
    for q in pts:
        cv.set(q[0], q[1], color)
