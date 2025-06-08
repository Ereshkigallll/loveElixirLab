# utils.py
# 工具函数：归一化、扰动、生成提示，支持词条提示

import random


def normalize_elements(elements):
    """归一化元素比例"""
    total = sum(elements.values())
    if total == 0:
        return {k: 0 for k in ['water', 'fire', 'earth', 'air']}
    return {k: v / total for k, v in elements.items()}


def normalize_weights(weights):
    """归一化权重，确保输入是字典并返回归一化权重"""
    if not isinstance(weights, dict):
        # 防御性处理：若 weights 不是字典，返回默认均匀权重
        return {'E': 0.25, 'I': 0.25, 'S': 0.25, 'N': 0.25}

    total = sum(v for v in weights.values() if isinstance(v, (int, float)))
    if total == 0:
        return {k: 1 / len(weights) for k in weights}

    return {k: v / total for k, v in weights.items()}


def apply_disturbance(elements):
    """施加随机扰动"""
    disturbed = elements.copy()
    for elem in disturbed:
        disturbed[elem] += random.uniform(-0.03, 0.03)
        disturbed[elem] = max(0, disturbed[elem])
    return normalize_elements(disturbed)


def generate_hint(ratios, success, mbti=None, trait=None, entries=None, byproduct=False):
    """生成提示信息，支持词条和副产物"""
    entries = entries or []
    dominant_elem = max(ratios.items(), key=lambda x: x[1])[0]
    entries_str = f"，{'、'.join(entries)}助力" if entries else ""
    byproduct_str = f"，副产物增益触发，额外物品入手！" if byproduct else ""

    if success:
        return f"水墨流转，{mbti} 性格觉醒！元素搭配完美{entries_str}，微博晒一下吧！{byproduct_str}"
    elif mbti and trait:
        return f"元素失衡，触发保底！凝结{mbti}，但{trait}稍显不足{entries_str}，调整物品再战！{byproduct_str}"
    else:
        if dominant_elem == 'water':
            return f"水元素过多，玻璃心警告！试试加入火元素增幅或土元素平衡比例！{byproduct_str}"
        elif dominant_elem == 'fire':
            return f"火元素过盛，热情过头！试试加入水元素增幅或风元素调和！{byproduct_str}"
        elif dominant_elem == 'earth':
            return f"土元素太重，过于沉稳！加入风元素增幅或火元素增添灵动！{byproduct_str}"
        else:
            return f"风元素太强，飘忽不定！加入土元素增幅或水元素稳定性格！{byproduct_str}"