# -*- coding: utf-8 -*-
"""pets.blob_template — 新宠物模板 + 框架演示角色（"果冻 Blob"）

★ 新宠物接入方法：复制本文件为 pets/<your_pet>_v1.py，然后：
  1. 改 PALETTE（<=16 色，含 outline）
  2. 改 draw_blob 里的骨架几何（或整体重写 draw，只要返回 Canvas(*ART_SIZE)）
  3. 保持 ROW_BUILDERS 覆盖 spec 里全部状态名
  4. 复制 specs/blob_demo.json 改 name/pet/out/preview，运行：
       python3 make_spritesheet.py --spec specs/<your_spec>.json
接口契约见 docs/HOWTO_new_pet.md。
"""
import math
from sprite_engine import core as C
from sprite_engine import timing as T

ART_SIZE = (48, 52)

PALETTE = dict(
    outline=(44, 62, 80, 255),
    body=(126, 200, 170, 255),
    body_light=(178, 232, 205, 255),
    body_dark=(88, 156, 132, 255),
    white=(250, 252, 250, 255),
    eye=(38, 48, 60, 255),
    blush=(242, 160, 168, 255),
    lid=(120, 132, 150, 255),
    lid_dark=(92, 102, 118, 255),
    glow=(186, 224, 238, 255),
)
OUTLINE = PALETTE['outline']


def _stamp(cv, pts, color, outline=None):
    C.stamp(cv, pts, color, outline if outline is not None else OUTLINE)


def _decal(cv, pts, color):
    C.decal(cv, pts, color)


ell, rect, limb = C.ell, C.rect, C.limb

BASE = dict(gx=0, gy=0, squash=0, edx=0, edy=0, eyes='open', mouth='smile',
            arm_l='side', arm_r='side', wave_ang=20, paw_l=0, paw_r=0,
            laptop=None, droop=0, fl_lift=0, fr_lift=0)


def draw_blob(P):
    p = dict(BASE); p.update(P)
    cv = C.Canvas(*ART_SIZE)
    bx, by = 24 + p['gx'], 36 + p['gy']
    ry = 10 + p['squash']

    # antenna（角色记忆点）
    tipx = bx + (2 if p['droop'] else 0)
    tipy = by - 12 + (4 if p['droop'] else 0)
    _stamp(cv, limb((bx, by - 8), (bx, by - 10), (tipx, tipy), 1), PALETTE['body_dark'])
    _decal(cv, ell(tipx, tipy, 1, 1), PALETTE['body_light'])

    # feet
    _stamp(cv, ell(bx - 5, 46 + p['gy'] - p['fl_lift'], 3, 2), PALETTE['white'])
    _stamp(cv, ell(bx + 5, 46 + p['gy'] - p['fr_lift'], 3, 2), PALETTE['white'])

    # body
    _stamp(cv, ell(bx, by, 10, ry), PALETTE['body'])
    _decal(cv, ell(bx, by + 2, 5, max(2, ry - 4)), PALETTE['body_light'])
    _decal(cv, [(bx - 8, by + 4), (bx - 7, by + 4), (bx + 7, by + 4), (bx + 8, by + 4)],
           PALETTE['blush'])

    # face
    ex = [bx - 5 + p['edx'], bx + 3 + p['edx']]
    ey = by - 4 + p['edy']
    for x0 in ex:
        if p['eyes'] == 'open':
            _decal(cv, rect(x0, ey, x0 + 1, ey + 2), PALETTE['eye'])
            _decal(cv, [(x0 + 1, ey)], PALETTE['white'])
        elif p['eyes'] == 'blink':
            _decal(cv, [(x0, ey + 1), (x0 + 1, ey + 1)], PALETTE['eye'])
        elif p['eyes'] == 'sad':
            if x0 < bx:
                _decal(cv, [(x0, ey), (x0 + 1, ey + 1)], PALETTE['eye'])
            else:
                _decal(cv, [(x0, ey + 1), (x0 + 1, ey)], PALETTE['eye'])
    m = p['mouth']
    if m == 'smile':
        _decal(cv, [(bx - 2, by + 1), (bx + 1, by + 1), (bx - 1, by + 2), (bx, by + 2)],
               PALETTE['eye'])
    elif m == 'open':
        _decal(cv, rect(bx - 1, by + 1, bx, by + 2), PALETTE['eye'])
        _decal(cv, [(bx - 1, by + 2), (bx, by + 2)], PALETTE['blush'])
    elif m == 'frown':
        _decal(cv, [(bx - 1, by + 1), (bx, by + 1), (bx - 2, by + 2), (bx + 1, by + 2)],
               PALETTE['eye'])
    elif m == 'flat':
        _decal(cv, [(bx - 1, by + 1), (bx, by + 1)], PALETTE['eye'])

    # laptop
    if p['laptop'] == 'work':
        _stamp(cv, rect(bx - 10, 44, bx + 10, 45), PALETTE['lid_dark'])
        _stamp(cv, rect(bx - 9, 36, bx + 9, 43), PALETTE['lid'])
        _decal(cv, rect(bx - 2, 38, bx + 1, 41), PALETTE['white'])
    elif p['laptop'] == 'review':
        _stamp(cv, rect(bx - 17, 44, bx + 1, 45), PALETTE['lid_dark'])
        _stamp(cv, rect(bx - 16, 36, bx, 43), PALETTE['lid'])
        _decal(cv, [(bx, y) for y in range(37, 43)], PALETTE['glow'])

    # arms
    sh_l, sh_r = (bx - 9, by - 2), (bx + 9, by - 2)
    if p['arm_l'] == 'side':
        _stamp(cv, ell(bx - 11, by, 2, 3), PALETTE['body'])
    elif p['arm_l'] == 'none':
        pass
    elif p['arm_l'] == 'type':
        _stamp(cv, rect(bx - 6, 34 - p['paw_l'], bx - 3, 35 - p['paw_l']), PALETTE['white'])
    elif p['arm_l'] == 'rest':
        _stamp(cv, rect(bx - 9, 34, bx - 6, 35), PALETTE['white'])
    elif p['arm_l'] == 'up':
        _stamp(cv, limb(sh_l, (bx - 11, by - 6), (bx - 12, by - 10), 2), PALETTE['body'])
        _stamp(cv, ell(bx - 12, by - 10, 2, 2), PALETTE['white'])
    if p['arm_r'] == 'side':
        _stamp(cv, ell(bx + 11, by, 2, 3), PALETTE['body'])
    elif p['arm_r'] == 'none':
        pass
    elif p['arm_r'] == 'type':
        _stamp(cv, rect(bx + 3, 34 - p['paw_r'], bx + 6, 35 - p['paw_r']), PALETTE['white'])
    elif p['arm_r'] == 'up':
        _stamp(cv, limb(sh_r, (bx + 11, by - 6), (bx + 12, by - 10), 2), PALETTE['body'])
        _stamp(cv, ell(bx + 12, by - 10, 2, 2), PALETTE['white'])
    elif p['arm_r'] == 'wave':
        a = math.radians(p['wave_ang'])
        paw = (int(round(sh_r[0] + 12 * math.sin(a))),
               int(round(sh_r[1] - 12 * math.cos(a))))
        mid = (sh_r[0] + 7 * math.sin(a) + 1, sh_r[1] - 7 * math.cos(a))
        _stamp(cv, limb(sh_r, mid, paw, 2), PALETTE['body'])
        _stamp(cv, ell(paw[0], paw[1], 2, 2), PALETTE['white'])
    elif p['arm_r'] == 'cheek':
        paw = (bx + 6, by - 7)
        _stamp(cv, limb(sh_r, (bx + 10, by - 4), paw, 2), PALETTE['body'])
        _stamp(cv, ell(paw[0], paw[1], 2, 2), PALETTE['white'])
    return cv


# ---------------- 状态行（节奏尽量用 timing 工具生成，示范用法） ----------------
def row_idle(n=8):
    fr = []
    breath = T.table(n, [0, 0, 1, 1, 1, 1, 0, 0])
    for i in range(n):
        P = dict(gy=breath[i])
        if i % 8 in (3, 4):
            P['eyes'] = 'blink'
        fr.append(draw_blob(P))
    return fr


def row_run(n=8, right=True):
    fr = []
    gy = T.bounce(n, 2)
    for i in range(n):
        P = dict(gy=gy[i], gx=1, edx=1,
                 fl_lift=1 if i % 4 < 2 else 0,
                 fr_lift=0 if i % 4 < 2 else 1,
                 mouth='open' if i % 4 == 2 else 'smile')
        cv = draw_blob(P)
        fr.append(cv if right else cv.mirror())
    return fr


def row_waving(n=8):
    fr = []
    ang = T.table(n, [15, 30, 45, 30, 15, 0, 15, 30])
    for i in range(n):
        P = dict(arm_r='wave', wave_ang=ang[i],
                 mouth='open' if i % 8 in (2, 3) else 'smile')
        if i % 8 == 5:
            P['eyes'] = 'blink'
        fr.append(draw_blob(P))
    return fr


def row_jumping(n=8):
    fr = []
    gy = T.table(n, [0, 1, -2, -4, -4, -2, 0, -1])
    sq = T.table(n, [0, 1, 0, -1, -1, 0, 1, 0])
    for i in range(n):
        i8 = i % 8
        P = dict(gy=gy[i], squash=sq[i],
                 mouth='open' if i8 in (2, 3, 4, 5) else ('flat' if i8 in (1, 6) else 'smile'))
        if i8 in (2, 3, 4, 5):
            P['arm_l'] = 'up'; P['arm_r'] = 'up'
        fr.append(draw_blob(P))
    return fr


def row_failed(n=8):
    fr = []
    nod = T.table(n, [1, 1, 2, 2, 2, 2, 1, 1])
    for i in range(n):
        fr.append(draw_blob(dict(gy=1, squash=1, droop=1, gy2=0,
                                 eyes='sad', mouth='frown',
                                 edy=nod[i] // 2)))
    return fr


def row_waiting(n=8):
    fr = []
    gx = T.sine(n, 1, 8)
    for i in range(n):
        i8 = i % 8
        P = dict(gx=gx[i],
                 fl_lift=2 if i8 < 4 else 0,
                 fr_lift=0 if i8 < 4 else 2,
                 edx=-1 if i8 in (2, 3) else (1 if i8 in (6, 7) else 0))
        if i8 == 4:
            P['eyes'] = 'blink'
        fr.append(draw_blob(P))
    return fr


def row_working(n=8):
    fr = []
    for i in range(n):
        i8 = i % 8
        P = dict(laptop='work', arm_l='type', arm_r='type',
                 paw_l=1 if i8 % 2 == 0 else 0,
                 paw_r=1 if i8 % 2 == 1 else 0,
                 edy=1, gy=1 if i8 in (2, 3, 6) else 0)
        if i8 == 5:
            P['eyes'] = 'blink'
        fr.append(draw_blob(P))
    return fr


def row_review(n=8):
    fr = []
    for i in range(n):
        i8 = i % 8
        P = dict(laptop='review', arm_l='rest', arm_r='cheek',
                 gx=1, edx=-1, edy=1,
                 mouth='smile' if i8 in (2, 3) else 'flat')
        if i8 == 6:
            P['eyes'] = 'blink'
        fr.append(draw_blob(P))
    return fr


ROW_BUILDERS = {
    'idle': row_idle,
    'running-right': lambda n: row_run(n, True),
    'running-left': lambda n: row_run(n, False),
    'waving': row_waving,
    'jumping': row_jumping,
    'failed': row_failed,
    'waiting': row_waiting,
    'working': row_working,
    'review': row_review,
}
