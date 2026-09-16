# -*- coding: utf-8 -*-
"""sprite_engine.timing — 动画节奏工具（相位表生成器，与角色无关）

新宠物写状态动画时优先用这里生成节奏数组，避免手抄魔数：
  table(n, values)          循环取值表
  sine(n, amp, period, ...) 整数正弦摆动（尾摆/身摆/挥爪）
  arc(n, height)            抛物线腾空（跳跃）
  bounce(n, depth, period)  步态弹跳（跑动）
"""
import math


def table(n, values):
    return [values[i % len(values)] for i in range(n)]


def sine(n, amp, period=None, phase=0.0, offset=0):
    period = period or n
    return [offset + int(round(amp * math.sin(2 * math.pi * (i + phase) / period)))
            for i in range(n)]


def arc(n, height):
    """0 -> -height -> 0 的抛物线（负值=向上），首尾落地。"""
    if n < 2:
        return [0] * n
    return [-int(round(height * math.sin(math.pi * i / (n - 1)))) for i in range(n)]


def bounce(n, depth, period=4):
    """跑动弹跳：每 period 帧一个落地-腾空周期。"""
    pat = [0, -depth // 2, -depth, -depth // 2] if period == 4 else \
          [-int(round(depth * abs(math.sin(math.pi * i / period)))) for i in range(period)]
    return table(n, pat)
