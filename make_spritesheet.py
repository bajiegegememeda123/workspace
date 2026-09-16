#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex Pet 雪碧图构建入口（engine + pet 插件 + spec 配置 三层架构）

用法：
  python3 make_spritesheet.py                          # 默认 specs/v1.json（猫 v1）
  python3 make_spritesheet.py --spec specs/blob_demo.json
  python3 make_spritesheet.py --pet cat_v1 --spec specs/v1.json --out x.webp --preview x.png
"""
import argparse
import importlib
import sys

from sprite_engine import sheet as SH


def main(argv=None):
    ap = argparse.ArgumentParser(description='Codex Pet sprite sheet builder')
    ap.add_argument('--spec', default='specs/v1.json', help='规格 JSON 路径')
    ap.add_argument('--pet', default=None, help='pets/ 下的宠物模块名（默认取 spec["pet"]）')
    ap.add_argument('--out', default=None, help='输出 webp 路径（默认取 spec["out"]）')
    ap.add_argument('--preview', default=None, help='棋盘格预览路径（默认取 spec["preview"]）')
    a = ap.parse_args()

    spec = SH.Spec.load(a.spec)
    pet_name = a.pet or spec.pet
    assert pet_name, 'spec missing "pet" and --pet not given'
    pet = importlib.import_module('pets.' + pet_name)
    assert (pet.ART_SIZE[0], pet.ART_SIZE[1]) == (spec.art_w, spec.art_h), \
        f'pet ART_SIZE {pet.ART_SIZE} != spec art cell {(spec.art_w, spec.art_h)}'
    missing = [s for s in spec.row_states if s not in pet.ROW_BUILDERS]
    assert not missing, f'pet {pet_name} lacks states: {missing}'

    frames = [pet.ROW_BUILDERS[state](spec.cols) for state in spec.row_states]
    art = SH.assemble(frames, spec)
    sh = SH.upscale(art, spec)

    out = a.out or spec.out or (spec.name + '_spritesheet.webp')
    prev = a.preview or spec.preview or (spec.name + '_preview.png')
    SH.export_webp(sh, out)
    SH.checker_preview(sh, prev)

    rep = SH.validate(sh, spec)
    print(f'pet={pet_name} spec={a.spec}')
    print('sheet size:', rep['size'], '| mode RGBA:', rep['mode_ok'])
    print('colors:', rep['colors'], '| crisp(no-AA):', rep['crisp_ok'],
          '| alpha:', rep['alpha_ok'], '| row bbox in-cell:', rep['bbox_ok'])
    print('row bboxes (art px):')
    for i, bb in enumerate(rep['row_bboxes']):
        print(f'  row {i + 1} [{spec.row_states[i]}]: {bb}')
    print('out:', out, '| preview:', prev)
    if not rep['ok']:
        print('VALIDATION FAILED')
        return 1
    print('VALIDATION OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
