# utils.py
# 工具函数：归一化、扰动、生成提示，支持保底机制

import random

def normalize_elements(elements):
    """归一化元素比例"""
    total = sum(elements.values())
    if total == 0:
        return {k: 0 for k in ['water', 'fire', 'earth', 'air']}
    return {k: v / total for k, v in elements.items()}

def normalize_weights(weights):
    """归一化权重"""
    total = sum(weights.values())
    if total == 0:
        return {k: 1/len(weights) for k in weights}
    return {k: v / total for k, v in weights}

def apply_disturbance(elements):
    """施加随机扰动"""
    disturbed = elements.copy()
    for elem in disturbed:
        disturbed[elem] += random.uniform(-0.03, 0.03)
        disturbed[elem] = max(0, disturbed[elem])
    return normalize_elements(disturbed)

def generate_hint(ratios, success, mbti=None, trait=None):
    """生成提示信息，支持保底机制"""
    if success:
        return f"水墨流转，{mbti} 性格觉醒！元素搭配完美，微博晒一下吧！"
    elif mbti and trait:
        return f"元素失衡，触发保底！凝结{mbti}，但{trait}稍显不足，调整物品再战！"
    else:
        primary = max(ratios.items(), key=lambda x: x[1])[0]
        if primary == 'water':
            return "水元素过多，玻璃心警告！试试加入火或土元素平衡比例！"
        elif primary == 'fire':
            return "火元素过盛，热情过头！试试加入水或风元素调和！"
        elif primary == 'earth':
            return "土元素太重，过于沉稳！加入风或火元素增添灵动！"
        else:
            return "风元素太强，飘忽不定！加入土或水元素稳定性格！"