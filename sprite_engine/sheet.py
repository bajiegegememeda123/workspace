# -*- coding: utf-8 -*-
"""sprite_engine.sheet — 规格(Spec)、拼表、放大、导出、预览、校验（与角色无关）"""
import json
from PIL import Image


class Spec:
    """雪碧图规格。JSON 字段：
    {
      "name": 名称, "pet": 默认宠物模块名,
      "canvas": {"width": W, "height": H},
      "cell":   {"width": cw, "height": ch},
      "grid":   {"cols": C, "rows": R},
      "scale":  整数放大倍数（艺术像素 -> 最终像素）,
      "rows":   [状态名 x R]（与宠物模块 ROW_BUILDERS 的键对应）,
      "out":    输出 webp 路径, "preview": 棋盘格预览路径
    }
    """

    def __init__(self, d):
        self.raw = d
        self.name = d.get('name', 'sheet')
        self.pet = d.get('pet')
        self.canvas_w = int(d['canvas']['width'])
        self.canvas_h = int(d['canvas']['height'])
        self.cell_w = int(d['cell']['width'])
        self.cell_h = int(d['cell']['height'])
        self.cols = int(d['grid']['cols'])
        self.rows = int(d['grid']['rows'])
        self.scale = int(d.get('scale', 1))
        self.row_states = list(d['rows'])
        self.out = d.get('out')
        self.preview = d.get('preview')
        # 导出值
        self.art_w = self.cell_w // self.scale
        self.art_h = self.cell_h // self.scale
        self._check()

    def _check(self):
        assert self.cols * self.cell_w == self.canvas_w, 'grid.cols * cell.w != canvas.w'
        assert self.rows * self.cell_h == self.canvas_h, 'grid.rows * cell.h != canvas.h'
        assert self.cell_w % self.scale == 0 and self.cell_h % self.scale == 0, \
            'cell size must be divisible by scale (integer upscale, no AA)'
        assert len(self.row_states) == self.rows, 'len(rows) != grid.rows'

    @classmethod
    def load(cls, path):
        with open(path, 'r', encoding='utf-8') as f:
            return cls(json.load(f))


def assemble(frames, spec):
    """frames: [row][col] -> Canvas(art_w x art_h)。返回艺术分辨率 RGBA Image。"""
    assert len(frames) == spec.rows, 'frame rows != spec rows'
    W, H = spec.cols * spec.art_w, spec.rows * spec.art_h
    buf = bytearray(W * H * 4)
    for r, row in enumerate(frames):
        assert len(row) == spec.cols, 'frame cols != spec cols'
        for c, cv in enumerate(row):
            assert (cv.w, cv.h) == (spec.art_w, spec.art_h), \
                f'frame canvas {(cv.w, cv.h)} != art cell {(spec.art_w, spec.art_h)}'
            g = cv.g
            for y in range(cv.h):
                grow = g[y]
                base = ((r * spec.art_h + y) * W + c * spec.art_w) * 4
                for x in range(cv.w):
                    px = grow[x]
                    if px:
                        o = base + x * 4
                        buf[o:o + 4] = px
    return Image.frombytes('RGBA', (W, H), bytes(buf))


def upscale(art, spec):
    """整数倍 NEAREST 放大 = 关闭抗锯齿、保持清晰像素边缘。"""
    return art.resize((art.width * spec.scale, art.height * spec.scale), Image.NEAREST)


def export_webp(sheet, path, lossless=True):
    import os
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    sheet.save(path, lossless=lossless, quality=100, method=6)


def checker_preview(sheet, path, chk=24):
    """棋盘格底预览图（仅供人工核对透明区）。"""
    import os
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    sw, sh = sheet.size
    nw, nh = sw // chk, sh // chk
    sb = bytearray(nw * nh * 4)
    for y in range(nh):
        for x in range(nw):
            c = (222, 222, 226, 255) if (x + y) % 2 == 0 else (255, 255, 255, 255)
            o = (y * nw + x) * 4
            sb[o:o + 4] = c
    small = Image.frombytes('RGBA', (nw, nh), bytes(sb))
    prev = small.resize((sw, sh), Image.NEAREST)
    prev = Image.alpha_composite(prev, sheet)
    prev.convert('RGB').save(path)


def validate(sheet, spec):
    """交付前硬校验，返回报告 dict；rep['ok'] 为总判定。"""
    rep = {}
    rep['size'] = tuple(sheet.size)
    rep['size_ok'] = tuple(sheet.size) == (spec.canvas_w, spec.canvas_h)
    rep['mode_ok'] = sheet.mode == 'RGBA'
    small = sheet.resize((spec.cols * spec.art_w, spec.rows * spec.art_h), Image.NEAREST)
    rep['crisp_ok'] = small.resize(sheet.size, Image.NEAREST).tobytes() == sheet.tobytes()
    px = sheet.load()
    alphas = {px[x, y][3] for y in range(0, sheet.size[1], 7)
              for x in range(0, sheet.size[0], 7)}
    rep['alpha_ok'] = (0 in alphas and 255 in alphas)
    ap = small.load()
    bboxes, bbox_ok = [], True
    AW, AH = spec.art_w, spec.art_h
    for r in range(spec.rows):
        xs, ys = [], []
        for y in range(r * AH, (r + 1) * AH):
            for x in range(spec.cols * AW):
                if ap[x, y][3]:
                    xs.append(x % AW); ys.append(y % AH)
        if xs:
            bb = (min(xs), min(ys), max(xs), max(ys))
            bboxes.append(bb)
            if bb[2] >= AW or bb[3] >= AH:
                bbox_ok = False
        else:
            bboxes.append(None)
            bbox_ok = False
    rep['row_bboxes'] = bboxes
    rep['bbox_ok'] = bbox_ok
    rep['colors'] = len(sheet.getcolors(1000000))
    rep['ok'] = all([rep['size_ok'], rep['mode_ok'], rep['crisp_ok'],
                     rep['alpha_ok'], rep['bbox_ok']])
    return rep
