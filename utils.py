# utils.py
# 工具函数：归一化、提示

import random

def normalize_elements(elements):
    """归一化元素比例，总和=1"""
    total = sum(elements.values())
    if total == 0:
        return {k: 0 for k in elements}
    return {k: v / total for k, v in elements.items()}

def normalize_weights(weights):
    """归一化权重，总和=1"""
    total = sum(weights.values())
    if total == 0:
        return {k: 0 for k in weights}
    return {k: v / total for k, v in weights.items()}

def generate_hint(ratios, success, mbti=None):
    """生成幽默提示"""
    if not ratios:
        return "元素不足，熔炉空荡！快去收集吧！"
    if not success:
        if ratios.get('water', 0) > 0.5:
            return "水太多，玻璃心警告！试试加点火，点燃热情！"
        if ratios.get('fire', 0) > 0.5:
            return "火太旺，冷静点！加点水，平衡一下！"
    if mbti == 'INFJ':
        return "元素如墨流转，稀有INFJ觉醒！先知上线！"
    if mbti == 'ENFP':
        return "火花四溅，ENFP灵感爆棚！计划？明天再说！"
    return "元素融合，性格初显！再试试吧！"

def apply_disturbance(elements):
    """随机扰动：±3%"""
    disturbed = elements.copy()
    for elem in disturbed:
        disturbed[elem] *= (1 + random.uniform(-0.03, 0.03))
    return normalize_elements(disturbed)