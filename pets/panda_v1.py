# -*- coding: utf-8 -*-
"""pets.panda_v1 — 角色插件：大熊猫幼崽（参考 uploads/panda.png）

形象要点：奶油白身+头、圆黑耳、黑眼圈(微倾)、黑鼻、黑四肢与肩带、白尾 stub。
道具：竹绿笔记本（working/review 状态语义需要）。
接口契约（docs/HOWTO_new_pet.md）：ART_SIZE / PALETTE / ROW_BUILDERS
"""
import math
from sprite_engine import core as C

ART_SIZE = (48, 52)

PALETTE = dict(
    outline=(40, 40, 44, 255),
    black=(58, 60, 68, 255),        # 黑毛
    black_dark=(44, 46, 52, 255),   # 远侧黑毛
    white=(247, 244, 238, 255),     # 奶油白毛
    white_shade=(226, 220, 208, 255),
    eye=(22, 22, 26, 255),          # 瞳孔
    glint=(255, 255, 255, 255),     # 高光/闭眼线
    nose=(30, 30, 34, 255),
    blush=(240, 178, 178, 255),
    lid=(118, 158, 102, 255),       # 竹绿笔记本
    lid_dark=(88, 124, 78, 255),
    glow=(214, 240, 200, 255),
)
OUTLINE = PALETTE['outline']
BLACK = PALETTE['black']
BLACK_D = PALETTE['black_dark']
WHITE = PALETTE['white']
SHADE = PALETTE['white_shade']
EYE = PALETTE['eye']
GLINT = PALETTE['glint']
NOSE = PALETTE['nose']
BLUSH = PALETTE['blush']
LID = PALETTE['lid']
LID_DARK = PALETTE['lid_dark']
GLOW = PALETTE['glow']


def _stamp(cv, pts, color, outline=None):
    C.stamp(cv, pts, color, outline if outline is not None else OUTLINE)


def _decal(cv, pts, color):
    C.decal(cv, pts, color)


ell, rect, tri, limb, seg2 = C.ell, C.rect, C.tri, C.limb, C.seg2

# ---------------- 正面熊猫 rig ----------------
BASE = dict(gx=0, gy=0, body_ry=0, hdx=0, hdy=0, ear_l=0, ear_r=0,
            tail=(33, 41), fl_lift=0, fr_lift=0, fl_dx=0, fr_dx=0,
            arm_l='side', arm_r='side', paw_l_lift=0, paw_r_lift=0, wave_ang=25,
            eyes='open', edx=0, edy=0, mouth='smile', laptop=None)

EAR_OFF = {0: (0, 0), 1: (-2, 2), 2: (-3, 4)}   # 圆耳下垂档位（左耳；右耳镜像）


def draw_front(P):
    p = dict(BASE); p.update(P)
    g = C.Canvas(*ART_SIZE)
    gx, gy = p['gx'], p['gy']
    bx, by = 24 + gx, 36 + gy
    bry = 8 + p['body_ry']
    hx, hy = 24 + p['hdx'], 19 + p['hdy'] + gy

    # tail stub（白尾，身后）
    tx, ty = p['tail']
    _stamp(g, ell(tx, ty, 2, 2), WHITE)
    _decal(g, [(tx + 1, ty - 1), (tx, ty - 1)], SHADE)

    # feet（黑脚）
    _stamp(g, ell(bx - 5 + p['fl_dx'], 45 + gy - p['fl_lift'], 3, 2), BLACK)
    _stamp(g, ell(bx + 5 + p['fr_dx'], 45 + gy - p['fr_lift'], 3, 2), BLACK)

    # body（白身）
    _stamp(g, ell(bx, by, 8, bry), WHITE)
    _decal(g, ell(bx, by + 3, 4, 4), SHADE)

    # ears（圆黑耳，头后）
    lo = EAR_OFF[p['ear_l']]; ro = EAR_OFF[p['ear_r']]
    _stamp(g, ell(16 + lo[0] + p['hdx'], hy - 9 + lo[1], 3, 3), BLACK)
    _stamp(g, ell(32 - ro[0] + p['hdx'], hy - 9 + ro[1], 3, 3), BLACK)

    # head（白头）
    _stamp(g, ell(hx, hy, 10, 9), WHITE)
    # 黑眼圈（小斜椭圆：外上倾斜像素并入 stamp 保证描边完整）
    patchL = ell(hx - 5, hy + 2, 2, 3) + [(hx - 6, hy - 1), (hx - 7, hy)]
    patchR = ell(hx + 5, hy + 2, 2, 3) + [(hx + 6, hy - 1), (hx + 7, hy)]
    _stamp(g, patchL, BLACK)
    _stamp(g, patchR, BLACK)
    # （正面脸部元素已密集：黑眼圈+鼻嘴，不加腮红保持干净）
    # 鼻 + 嘴
    _decal(g, [(hx - 1, hy + 5), (hx, hy + 5), (hx + 1, hy + 5), (hx, hy + 6)], NOSE)
    m = p['mouth']
    if m == 'smile':
        _decal(g, [(hx - 2, hy + 7), (hx + 1, hy + 7), (hx - 1, hy + 8), (hx, hy + 8)], OUTLINE)
    elif m == 'open':
        _decal(g, rect(hx - 1, hy + 7, hx, hy + 8), OUTLINE)
        _decal(g, [(hx - 1, hy + 8), (hx, hy + 8)], BLUSH)
    elif m == 'frown':
        _decal(g, [(hx - 1, hy + 7), (hx, hy + 7), (hx - 2, hy + 8), (hx + 1, hy + 8)], OUTLINE)
    elif m == 'flat':
        _decal(g, [(hx - 1, hy + 7), (hx, hy + 7)], OUTLINE)

    # eyes（黑眼圈内）
    ex = [hx - 6 + p['edx'], hx + 4 + p['edx']]
    ey = hy + 1 + p['edy']
    for x0 in ex:
        if p['eyes'] == 'open':
            _decal(g, rect(x0 + 1, ey, x0 + 2, ey + 1), EYE)
            _decal(g, [(x0 + 2, ey)], GLINT)
        elif p['eyes'] == 'blink':
            _decal(g, [(x0 + 1, ey + 1), (x0 + 2, ey + 1)], GLINT)
        elif p['eyes'] == 'half':
            _decal(g, rect(x0 + 1, ey + 1, x0 + 2, ey + 2), EYE)
            _decal(g, [(x0 + 2, ey + 1)], GLINT)
        elif p['eyes'] == 'sad':
            if x0 < hx:
                _decal(g, [(x0 + 1, ey), (x0 + 2, ey + 1)], GLINT)
            else:
                _decal(g, [(x0 + 1, ey + 1), (x0 + 2, ey)], GLINT)
        elif p['eyes'] == 'down':
            _decal(g, rect(x0 + 1, ey + 1, x0 + 2, ey + 2), EYE)

    # laptop（竹绿）
    if p['laptop'] == 'work':
        _stamp(g, rect(bx - 10, 42, bx + 10, 43), LID_DARK)
        _stamp(g, rect(bx - 9, 34, bx + 9, 41), LID)
        _decal(g, rect(bx - 2, 36, bx + 1, 39), GLINT)
        _decal(g, [(bx - 3, 37), (bx - 3, 38), (bx + 2, 37), (bx + 2, 38)], GLINT)
    elif p['laptop'] == 'review':
        _stamp(g, rect(bx - 17, 42, bx + 1, 43), LID_DARK)
        _stamp(g, rect(bx - 16, 34, bx, 41), LID)
        _decal(g, [(bx, y) for y in range(35, 41)], GLOW)
        _decal(g, rect(bx - 10, 36, bx - 7, 39), GLINT)

    # arms（黑臂）
    sh_l, sh_r = (bx - 7, by - 4), (bx + 7, by - 4)
    if p['arm_l'] == 'side':
        _stamp(g, ell(bx - 8, by - 2, 2, 3), BLACK)
    elif p['arm_l'] == 'none':
        pass
    elif p['arm_l'] == 'type':
        _stamp(g, rect(bx - 6, 32 - p['paw_l_lift'], bx - 3, 33 - p['paw_l_lift']), BLACK)
    elif p['arm_l'] == 'rest':
        _stamp(g, rect(bx - 9, 32, bx - 6, 33), BLACK)
    elif p['arm_l'] == 'up':
        _stamp(g, limb(sh_l, (bx - 11, by - 7), (bx - 13, by - 11), 2), BLACK)
        _stamp(g, ell(bx - 13, by - 11, 2, 2), BLACK)
    if p['arm_r'] == 'side':
        _stamp(g, ell(bx + 8, by - 2, 2, 3), BLACK)
    elif p['arm_r'] == 'none':
        pass
    elif p['arm_r'] == 'type':
        _stamp(g, rect(bx + 3, 32 - p['paw_r_lift'], bx + 6, 33 - p['paw_r_lift']), BLACK)
    elif p['arm_r'] == 'wave':
        a = math.radians(p['wave_ang'])
        paw = (int(round(sh_r[0] + 14 * math.sin(a))), int(round(sh_r[1] - 14 * math.cos(a))))
        mid = (sh_r[0] + 8 * math.sin(a) + 1, sh_r[1] - 8 * math.cos(a))
        _stamp(g, limb(sh_r, mid, paw, 2), BLACK)
        _stamp(g, ell(paw[0], paw[1], 2, 2), BLACK)
    elif p['arm_r'] == 'cheek':
        paw = (hx + 7, hy + 6)
        _stamp(g, limb(sh_r, (bx + 9, by - 6), paw, 2), BLACK)
        _stamp(g, ell(paw[0], paw[1], 2, 2), BLACK)
    elif p['arm_r'] == 'up':
        _stamp(g, limb(sh_r, (bx + 11, by - 7), (bx + 13, by - 11), 2), BLACK)
        _stamp(g, ell(bx + 13, by - 11, 2, 2), BLACK)
    return g


# ---------------- 侧视熊猫 rig（跑动） ----------------
LEGCycle = [(4, 0), (3, 0), (0, 0), (-3, 2), (-4, 2), (-2, 3), (1, 2), (4, 1)]


def draw_side(i, gy, sway):
    g = C.Canvas(*ART_SIZE)
    i8 = i % 8
    fdx, fl = LEGCycle[(i8 + 4) % 8]
    bdx, bl = LEGCycle[i8]
    _stamp(g, seg2(25, 34 + gy, 25 + fdx, 41 + gy - fl), BLACK_D)   # far front
    _stamp(g, seg2(13, 34 + gy, 13 + bdx, 41 + gy - bl), BLACK_D)   # far back
    # tail stub
    _stamp(g, ell(10 + sway, 28 + gy, 2, 2), WHITE)
    # body
    _stamp(g, ell(20, 31 + gy, 10, 7), WHITE)
    _decal(g, ell(21, 33 + gy, 5, 3), SHADE)
    _stamp(g, ell(26, 30 + gy, 3, 3), BLACK)     # 肩带（近侧肩）
    # ears + head
    _stamp(g, ell(27, 11 + gy, 3, 3), BLACK)
    _stamp(g, ell(33, 11 + gy, 3, 3), BLACK)
    _stamp(g, ell(30, 20 + gy, 8, 8), WHITE)
    _stamp(g, ell(33, 21 + gy, 2, 3), BLACK)     # 黑眼圈
    _decal(g, rect(33, 20 + gy, 34, 21 + gy), EYE)
    _decal(g, [(34, 20 + gy)], GLINT)
    _decal(g, [(36, 21 + gy), (37, 21 + gy), (36, 22 + gy)], NOSE)
    _decal(g, [(35, 24 + gy), (35, 25 + gy), (36, 25 + gy)], OUTLINE)
    _decal(g, [(29, 23 + gy), (30, 23 + gy)], BLUSH)
    # near legs（黑）
    ndx, nl = LEGCycle[i8]
    hdx2, hl = LEGCycle[(i8 + 4) % 8]
    _stamp(g, seg2(26, 35 + gy, 26 + ndx, 43 + gy - nl), BLACK)    # near front
    _stamp(g, seg2(14, 35 + gy, 14 + hdx2, 43 + gy - hl), BLACK)   # near back
    return g


# ---------------- 状态行构建器 ----------------
def row_idle(n=8):
    frames = []
    breath = [0, 0, 1, 1, 1, 1, 0, 0]
    sway = [0, 1, 1, 1, 0, -1, -1, 0]
    for i in range(n):
        i8 = i % 8
        P = dict(gy=breath[i8], tail=(33 + sway[i8], 41))
        if i8 in (3, 4):
            P['eyes'] = 'blink'
        frames.append(draw_front(P))
    return frames


def row_run(n=8, right=True):
    frames = []
    bounce = [0, -1, -2, -1, 0, -1, -2, -1]
    sway = [0, 1, 1, 0, -1, -1, 0, 1]
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
                 tail=(33 + (1 if i8 % 4 < 2 else -1), 41))
        if i8 == 5:
            P['eyes'] = 'blink'
        frames.append(draw_front(P))
    return frames


def row_jumping(n=8):
    frames = []
    spec = [
        dict(gy=0),
        dict(gy=1, body_ry=1, hdy=2, mouth='flat'),
        dict(gy=-2, mouth='open', tail=(34, 38)),
        dict(gy=-4, fl_lift=2, fr_lift=2, fl_dx=1, fr_dx=-1, mouth='open', tail=(35, 35)),
        dict(gy=-4, fl_lift=2, fr_lift=2, fl_dx=1, fr_dx=-1, mouth='open', tail=(34, 36)),
        dict(gy=-2, fl_lift=1, fr_lift=1, mouth='open', tail=(34, 38)),
        dict(gy=0, body_ry=1, hdy=2, mouth='flat', tail=(33, 42)),
        dict(gy=-1, mouth='smile', tail=(33, 41)),
    ]
    for i in range(n):
        i8 = i % 8
        P = dict(BASE); P.update(spec[i8])
        if i8 in (2, 3, 4, 5):
            P['arm_l'] = 'up'; P['arm_r'] = 'up'
        frames.append(draw_front(P))
    return frames


def row_failed(n=8):
    frames = []
    sway = [0, -1, -1, -1, 0, 0, 1, 1]
    nod = [3, 3, 4, 4, 4, 4, 3, 3]
    for i in range(n):
        i8 = i % 8
        P = dict(gy=1, body_ry=1, hdy=nod[i8], ear_l=1, ear_r=1,
                 tail=(34 + sway[i8] // 2, 44),
                 eyes='sad', mouth='frown')
        if i8 == 5:
            P['ear_r'] = 2
        frames.append(draw_front(P))
    return frames


def row_waiting(n=8):
    frames = []
    gx = [0, 1, 1, 0, 0, -1, -1, 0]
    sway = [0, 1, 1, 0, -1, -1, 0, 1]
    for i in range(n):
        i8 = i % 8
        P = dict(gx=gx[i8], tail=(33 + sway[i8], 41), eyes='half', mouth='smile')
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
                 hdy=hdy[i8], edy=1, tail=(33 + sway[i8], 41))
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
                 mouth='flat', tail=(33 + sway[i8], 41))
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
