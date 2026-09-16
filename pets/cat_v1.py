# -*- coding: utf-8 -*-
"""pets.cat_v1 — Codex Pet v1 角色插件：奶油橘虎斑猫（参考 uploads/cat.webp）

接口契约（docs/HOWTO_new_pet.md）：
  ART_SIZE     艺术像素单帧尺寸
  PALETTE      角色色板（<=16 色建议）
  ROW_BUILDERS {状态名: fn(n_frames) -> [Canvas]}
状态词汇 v1：idle / running-right / running-left / waving / jumping /
            failed / waiting / working / review
"""
import math
from sprite_engine import core as C

ART_SIZE = (48, 52)

# ---------------- 色板（ref cat.webp: pale ginger tabby） ----------------
PALETTE = dict(
    outline=(101, 67, 33, 255),
    fur=(243, 206, 140, 255),
    fur_light=(252, 231, 182, 255),
    fur_dark=(214, 158, 90, 255),
    stripe=(203, 143, 74, 255),
    white=(255, 248, 236, 255),
    ear_pink=(240, 164, 140, 255),
    nose=(235, 140, 140, 255),
    blush=(246, 170, 150, 255),
    eye_dark=(58, 40, 28, 255),
    eye_iris=(126, 178, 106, 255),
    lid=(122, 138, 158, 255),
    lid_dark=(94, 108, 126, 255),
    glow=(188, 226, 240, 255),
    logo=(203, 214, 228, 255),
)
OUTLINE = PALETTE['outline']
FUR = PALETTE['fur']
FUR_LIGHT = PALETTE['fur_light']
FUR_DARK = PALETTE['fur_dark']
STRIPE = PALETTE['stripe']
WHITE = PALETTE['white']
EAR_PINK = PALETTE['ear_pink']
NOSE = PALETTE['nose']
BLUSH = PALETTE['blush']
EYE_DARK = PALETTE['eye_dark']
EYE_IRIS = PALETTE['eye_iris']
LID = PALETTE['lid']
LID_DARK = PALETTE['lid_dark']
GLOW = PALETTE['glow']
LOGO = PALETTE['logo']

# 角色本地包装：默认描边色 = 角色 outline
def _stamp(cv, pts, color, outline=None):
    C.stamp(cv, pts, color, outline if outline is not None else OUTLINE)

def _decal(cv, pts, color):
    C.decal(cv, pts, color)

ell, rect, tri, limb, seg2 = C.ell, C.rect, C.tri, C.limb, C.seg2

# ---------------- 正面猫 rig ----------------
BASE = dict(gx=0, gy=0, body_ry=0, hdx=0, hdy=0, ear_l=0, ear_r=0,
            tail_tip=(39, 29), tail_mid=(36, 38),
            fl_lift=0, fr_lift=0, fl_dx=0, fr_dx=0,
            arm_l='side', arm_r='side', paw_l_lift=0, paw_r_lift=0, wave_ang=25,
            eyes='open', edx=0, edy=0, mouth='smile', laptop=None)

def draw_front(P):
    p = dict(BASE); p.update(P)
    g = C.Canvas(*ART_SIZE)
    gx, gy = p['gx'], p['gy']
    bx, by = 24 + gx, 36 + gy
    bry = 8 + p['body_ry']
    hx, hy = 24 + p['hdx'], 19 + p['hdy']

    # tail (behind everything)
    if p.get('tail_side') == 'left':
        tb = (bx - 6, by + 3)
        tm = (2 * bx - p['tail_mid'][0], p['tail_mid'][1])
        tt = (2 * bx - p['tail_tip'][0], p['tail_tip'][1])
    else:
        tb = (bx + 6, by + 3)
        tm, tt = p['tail_mid'], p['tail_tip']
    _stamp(g, limb(tb, tm, tt, 2), FUR)
    _decal(g, ell(tt[0], tt[1], 2, 2), FUR_LIGHT)

    # feet (white socks)
    _stamp(g, ell(bx - 5 + p['fl_dx'], 45 + gy - p['fl_lift'], 3, 2), WHITE)
    _stamp(g, ell(bx + 5 + p['fr_dx'], 45 + gy - p['fr_lift'], 3, 2), WHITE)

    # body
    _stamp(g, ell(bx, by, 8, bry), FUR)
    _decal(g, ell(bx, by + 1, 4, 5), FUR_LIGHT)
    _decal(g, [(bx - 7, by - 3), (bx - 6, by - 3), (bx + 6, by - 3), (bx + 7, by - 3)], STRIPE)
    _decal(g, [(bx - 7, by + 1), (bx - 6, by + 1), (bx + 6, by + 1), (bx + 7, by + 1)], STRIPE)

    # ears (behind head)
    ear_tips = {0: (-8, -14), 1: (-11, -10), 2: (-12, -6)}
    lt = ear_tips[p['ear_l']]; rt = ear_tips[p['ear_r']]
    earL = tri((hx + lt[0], hy + lt[1]), (hx - 10, hy - 6), (hx - 4, hy - 8))
    earR = tri((hx - rt[0], hy + rt[1]), (hx + 4, hy - 8), (hx + 10, hy - 6))
    _stamp(g, earL, FUR); _stamp(g, earR, FUR)
    def shrink(tp, a, b, f=0.32):
        cx = (tp[0] + a[0] + b[0]) / 3.0; cy = (tp[1] + a[1] + b[1]) / 3.0
        m = lambda q: (q[0] + (cx - q[0]) * f, q[1] + (cy - q[1]) * f)
        return m(tp), m(a), m(b)
    t1, a1, b1 = shrink((hx + lt[0], hy + lt[1]), (hx - 10, hy - 6), (hx - 4, hy - 8))
    _decal(g, tri((int(t1[0]), int(t1[1])), (int(a1[0]), int(a1[1])), (int(b1[0]), int(b1[1]))), EAR_PINK)
    t2, a2, b2 = shrink((hx - rt[0], hy + rt[1]), (hx + 4, hy - 8), (hx + 10, hy - 6))
    _decal(g, tri((int(t2[0]), int(t2[1])), (int(a2[0]), int(a2[1])), (int(b2[0]), int(b2[1]))), EAR_PINK)

    # head
    _stamp(g, ell(hx, hy, 10, 9), FUR)
    _decal(g, [(hx - 4, hy - 8), (hx - 4, hy - 7), (hx - 4, hy - 6),
               (hx, hy - 9), (hx, hy - 8), (hx, hy - 7), (hx, hy - 6),
               (hx + 4, hy - 8), (hx + 4, hy - 7), (hx + 4, hy - 6)], STRIPE)
    _decal(g, [(hx - 10, hy - 1), (hx - 9, hy - 1), (hx + 9, hy - 1), (hx + 10, hy - 1)], STRIPE)
    _decal(g, ell(hx, hy + 5, 3, 2), WHITE)
    _decal(g, [(hx - 1, hy + 4), (hx, hy + 4)], NOSE)
    _decal(g, [(hx - 8, hy + 4), (hx - 7, hy + 4), (hx + 7, hy + 4), (hx + 8, hy + 4)], BLUSH)

    # eyes
    ex = [hx - 4 + p['edx'], hx + 3 + p['edx']]
    ey = hy + p['edy']
    for x0 in ex:
        if p['eyes'] == 'open':
            _decal(g, rect(x0, ey, x0 + 1, ey + 2), EYE_DARK)
            _decal(g, [(x0, ey + 1), (x0 + 1, ey + 1)], EYE_IRIS)
            _decal(g, [(x0 + 1, ey)], WHITE)
        elif p['eyes'] == 'blink':
            _decal(g, [(x0, ey + 1), (x0 + 1, ey + 1)], EYE_DARK)
        elif p['eyes'] == 'half':
            _decal(g, rect(x0, ey + 1, x0 + 1, ey + 2), EYE_DARK)
            _decal(g, [(x0, ey + 1), (x0 + 1, ey + 1)], EYE_IRIS)
        elif p['eyes'] == 'sad':
            if x0 < hx:
                _decal(g, [(x0, ey), (x0 + 1, ey + 1)], EYE_DARK)
            else:
                _decal(g, [(x0, ey + 1), (x0 + 1, ey)], EYE_DARK)
        elif p['eyes'] == 'down':
            if x0 < hx:
                _decal(g, [(x0, ey + 1), (x0 + 1, ey + 2)], EYE_DARK)
            else:
                _decal(g, [(x0, ey + 2), (x0 + 1, ey + 1)], EYE_DARK)

    # mouth
    m = p['mouth']
    if m == 'smile':
        _decal(g, [(hx - 2, hy + 6), (hx + 1, hy + 6), (hx - 1, hy + 7), (hx, hy + 7)], EYE_DARK)
    elif m == 'open':
        _decal(g, rect(hx - 1, hy + 6, hx, hy + 7), EYE_DARK)
        _decal(g, [(hx - 1, hy + 7), (hx, hy + 7)], NOSE)
    elif m == 'frown':
        _decal(g, [(hx - 1, hy + 6), (hx, hy + 6), (hx - 2, hy + 7), (hx + 1, hy + 7)], EYE_DARK)
    elif m == 'flat':
        _decal(g, [(hx - 1, hy + 6), (hx, hy + 6)], EYE_DARK)

    # laptop
    if p['laptop'] == 'work':
        _stamp(g, rect(bx - 10, 42, bx + 10, 43), LID_DARK)
        _stamp(g, rect(bx - 9, 34, bx + 9, 41), LID)
        _decal(g, rect(bx - 2, 36, bx + 1, 39), LOGO)
        _decal(g, [(bx - 3, 37), (bx - 3, 38), (bx + 2, 37), (bx + 2, 38)], LOGO)
    elif p['laptop'] == 'review':
        _stamp(g, rect(bx - 17, 42, bx + 1, 43), LID_DARK)
        _stamp(g, rect(bx - 16, 34, bx, 41), LID)
        _decal(g, [(bx, y) for y in range(35, 41)], GLOW)
        _decal(g, rect(bx - 10, 36, bx - 7, 39), LOGO)

    # arms
    sh_l, sh_r = (bx - 7, by - 4), (bx + 7, by - 4)
    if p['arm_l'] == 'side':
        _stamp(g, ell(bx - 8, by - 2, 2, 3), FUR)
    elif p['arm_l'] == 'none':
        pass
    elif p['arm_l'] == 'type':
        _stamp(g, rect(bx - 6, 32 - p['paw_l_lift'], bx - 3, 33 - p['paw_l_lift']), WHITE)
    elif p['arm_l'] == 'rest':
        _stamp(g, rect(bx - 9, 32, bx - 6, 33), WHITE)
    if p['arm_r'] == 'side':
        _stamp(g, ell(bx + 8, by - 2, 2, 3), FUR)
    elif p['arm_r'] == 'none':
        pass
    elif p['arm_r'] == 'type':
        _stamp(g, rect(bx + 3, 32 - p['paw_r_lift'], bx + 6, 33 - p['paw_r_lift']), WHITE)
    elif p['arm_r'] == 'wave':
        a = math.radians(p['wave_ang'])
        paw = (sh_r[0] + 14 * math.sin(a), sh_r[1] - 14 * math.cos(a))
        paw = (int(round(paw[0])), int(round(paw[1])))
        mid = (sh_r[0] + 8 * math.sin(a) + 1, sh_r[1] - 8 * math.cos(a))
        _stamp(g, limb(sh_r, mid, paw, 2), FUR)
        _stamp(g, ell(paw[0], paw[1], 2, 2), WHITE)
    elif p['arm_r'] == 'cheek':
        paw = (hx + 7, hy + 6)
        _stamp(g, limb(sh_r, (bx + 9, by - 6), paw, 2), FUR)
        _stamp(g, ell(paw[0], paw[1], 2, 2), WHITE)
    return g

# ---------------- 侧视猫 rig（跑动） ----------------
LEGCycle = [(4, 0), (3, 0), (0, 0), (-3, 2), (-4, 2), (-2, 3), (1, 2), (4, 1)]

def draw_side(i, gy, sway):
    g = C.Canvas(*ART_SIZE)
    i8 = i % 8
    fdx, fl = LEGCycle[(i8 + 4) % 8]
    bdx, bl = LEGCycle[i8]
    _stamp(g, seg2(25, 34 + gy, 25 + fdx, 41 + gy - fl), FUR_DARK)   # far front
    _stamp(g, seg2(13, 34 + gy, 13 + bdx, 41 + gy - bl), FUR_DARK)   # far back
    _decal(g, [(25 + fdx, 41 + gy - fl), (26 + fdx, 41 + gy - fl)], FUR_LIGHT)
    _decal(g, [(13 + bdx, 41 + gy - bl), (14 + bdx, 41 + gy - bl)], FUR_LIGHT)
    _stamp(g, limb((10, 28 + gy), (6, 25 + gy), (3 + sway, 19 + gy), 2), FUR)
    _decal(g, ell(3 + sway, 19 + gy, 2, 2), FUR_LIGHT)
    _stamp(g, ell(20, 31 + gy, 10, 7), FUR)
    _decal(g, ell(21, 33 + gy, 5, 3), FUR_LIGHT)
    _decal(g, [(11, 29 + gy), (12, 29 + gy), (11, 33 + gy), (12, 33 + gy)], STRIPE)
    _stamp(g, tri((25, 7 + gy), (23, 14 + gy), (30, 12 + gy)), FUR)
    _stamp(g, tri((33, 7 + gy), (30, 12 + gy), (36, 14 + gy)), FUR)
    _decal(g, tri((25, 9 + gy), (24, 13 + gy), (28, 12 + gy)), EAR_PINK)
    _decal(g, tri((32, 9 + gy), (30, 12 + gy), (34, 13 + gy)), EAR_PINK)
    _stamp(g, ell(30, 20 + gy, 8, 8), FUR)
    _decal(g, [(27, 13 + gy), (27, 14 + gy), (27, 15 + gy), (30, 12 + gy), (30, 13 + gy), (30, 14 + gy)], STRIPE)
    _decal(g, rect(32, 18 + gy, 33, 20 + gy), EYE_DARK)
    _decal(g, [(32, 19 + gy), (33, 19 + gy)], EYE_IRIS)
    _decal(g, [(33, 18 + gy)], WHITE)
    _decal(g, ell(35, 22 + gy, 2, 2), WHITE)
    _decal(g, [(35, 21 + gy), (36, 21 + gy)], NOSE)
    _decal(g, [(33, 23 + gy), (34, 24 + gy), (35, 24 + gy)], EYE_DARK)
    _decal(g, [(29, 23 + gy), (30, 23 + gy)], BLUSH)
    ndx, nl = LEGCycle[i8]
    hdx2, hl = LEGCycle[(i8 + 4) % 8]
    _stamp(g, seg2(26, 35 + gy, 26 + ndx, 43 + gy - nl), FUR)    # near front
    _stamp(g, seg2(14, 35 + gy, 14 + hdx2, 43 + gy - hl), FUR)   # near back
    _decal(g, [(26 + ndx, 43 + gy - nl), (27 + ndx, 43 + gy - nl)], WHITE)
    _decal(g, [(14 + hdx2, 43 + gy - hl), (15 + hdx2, 43 + gy - hl)], WHITE)
    return g

# ---------------- 状态行构建器 ----------------
def row_idle(n=8):
    frames = []
    breath = [0, 0, 1, 1, 1, 1, 0, 0]
    sway = [0, 1, 2, 2, 2, 1, 0, -1]
    for i in range(n):
        i8 = i % 8
        P = dict(gy=breath[i8], tail_tip=(40 + sway[i8] // 2, 27), tail_mid=(37, 37))
        if i8 in (3, 4):
            P['eyes'] = 'blink'
        frames.append(draw_front(P))
    return frames

def row_run(n=8, right=True):
    frames = []
    bounce = [0, -1, -2, -1, 0, -1, -2, -1]
    sway = [0, 1, 2, 1, 0, -1, -2, -1]
    for i in range(n):
        i8 = i % 8
        g = draw_side(i, bounce[i8], sway[i8])
        if not right:
            g = g.mirror()
        frames.append(g)
    return frames

def row_waving(n=8):
    frames = []
    ang = [15, 30, 45, 30, 15, 0, 15, 30]
    gy = [0, 0, -1, 0, 0, 0, -1, 0]
    for i in range(n):
        i8 = i % 8
        P = dict(arm_r='wave', wave_ang=ang[i8], gy=gy[i8],
                 mouth='open' if i8 in (2, 3) else 'smile',
                 tail_side='left', tail_tip=(39 + (1 if i8 % 4 < 2 else -1), 28),
                 tail_mid=(37, 37))
        if i8 == 5:
            P['eyes'] = 'blink'
        frames.append(draw_front(P))
    return frames

def row_jumping(n=8):
    frames = []
    spec = [
        dict(gy=0),
        dict(gy=1, body_ry=1, hdy=2, mouth='flat'),
        dict(gy=-2, mouth='open', tail_tip=(39, 25), tail_mid=(37, 34)),
        dict(gy=-4, fl_lift=2, fr_lift=2, fl_dx=1, fr_dx=-1, mouth='open', tail_tip=(40, 22), tail_mid=(38, 31)),
        dict(gy=-4, fl_lift=2, fr_lift=2, fl_dx=1, fr_dx=-1, mouth='open', tail_tip=(39, 23), tail_mid=(37, 32)),
        dict(gy=-2, fl_lift=1, fr_lift=1, mouth='open', tail_tip=(39, 27), tail_mid=(37, 35)),
        dict(gy=0, body_ry=1, hdy=2, mouth='flat', tail_tip=(39, 31)),
        dict(gy=-1, mouth='smile', tail_tip=(39, 29)),
    ]
    for i in range(n):
        i8 = i % 8
        s = spec[i8]
        P = dict(BASE); P.update(s)
        if i8 in (2, 3, 4, 5):
            P['arm_l'] = 'none'; P['arm_r'] = 'none'
        frames.append(draw_front(P))
    for i in range(n):
        i8 = i % 8
        if i8 in (2, 3, 4, 5):
            g = frames[i]
            gy = spec[i8]['gy']
            bx, by = 24, 36 + gy
            _stamp(g, limb((bx - 7, by - 4), (bx - 11, by - 7), (bx - 13, by - 11), 2), FUR)
            _stamp(g, ell(bx - 13, by - 11, 2, 2), WHITE)
            _stamp(g, limb((bx + 7, by - 4), (bx + 11, by - 7), (bx + 13, by - 11), 2), FUR)
            _stamp(g, ell(bx + 13, by - 11, 2, 2), WHITE)
    return frames

def row_failed(n=8):
    frames = []
    sway = [0, -1, -2, -2, -1, 0, 1, 1]
    nod = [3, 3, 4, 4, 4, 4, 3, 3]
    for i in range(n):
        i8 = i % 8
        P = dict(gy=1, body_ry=1, hdy=nod[i8], ear_l=1, ear_r=1,
                 tail_side='left', tail_tip=(38 - sway[i8] // 2, 45), tail_mid=(36, 42),
                 eyes='down', mouth='frown')
        if i8 == 5:
            P['ear_r'] = 2
        frames.append(draw_front(P))
    return frames

def row_waiting(n=8):
    frames = []
    gx = [0, 1, 1, 0, 0, -1, -1, 0]
    sway = [0, 1, 2, 1, 0, -1, -2, -1]
    for i in range(n):
        i8 = i % 8
        P = dict(gx=gx[i8], tail_tip=(39 + sway[i8], 29), eyes='half',
                 mouth='smile', tail_mid=(37, 37))
        if i8 < 4:
            P['fl_lift'] = 2; P['fl_dx'] = 1
        else:
            P['fr_lift'] = 2; P['fr_dx'] = -1
        if i8 in (2, 3):
            P['edx'] = -1
        if i8 in (6, 7):
            P['edx'] = 1
        if i8 == 4:
            P['eyes'] = 'blink'
        frames.append(draw_front(P))
    return frames

def row_working(n=8):
    frames = []
    hdy = [0, 0, 1, 1, 0, 0, 1, 0]
    sway = [0, 0, 1, 1, 0, 0, -1, -1]
    for i in range(n):
        i8 = i % 8
        P = dict(laptop='work', arm_l='type', arm_r='type',
                 paw_l_lift=1 if i8 % 2 == 0 else 0,
                 paw_r_lift=1 if i8 % 2 == 1 else 0,
                 hdy=hdy[i8], edy=1, tail_tip=(39 + sway[i8], 29))
        if i8 == 5:
            P['eyes'] = 'blink'
        if i8 == 3:
            P['ear_r'] = 1
        frames.append(draw_front(P))
    return frames

def row_review(n=8):
    frames = []
    sway = [0, 1, 1, 0, -1, -1, 0, 1]
    for i in range(n):
        i8 = i % 8
        P = dict(laptop='review', arm_l='rest', arm_r='cheek',
                 hdx=2, hdy=1, ear_r=1, edx=-1, edy=1,
                 mouth='flat', tail_tip=(39 + sway[i8], 29))
        if i8 == 6:
            P['eyes'] = 'blink'
        if i8 in (2, 3):
            P['mouth'] = 'smile'
        frames.append(draw_front(P))
    return frames

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
