# Partial utils.py
# 更新 generate_hint，支持 MBTI 失败时的保底提示

from data import mbti_targets
import random

def generate_hint(ratios, success, mbti, trait, entries, has_byproduct):
    """生成 MBTI 合成提示，包含失败原因和建议"""
    if not success:
        target = mbti_targets[mbti]['ranges']
        issues = []
        for elem in ['water', 'fire', 'earth', 'air']:
            if ratios.get(elem, 0) < target[elem][0]:
                issues.append(f"{elem} 比例过低 ({ratios.get(elem, 0):.2f} < {target[elem][0]:.2f})")
            elif ratios.get(elem, 0) > target[elem][1]:
                issues.append(f"{elem} 比例过高 ({ratios.get(elem, 0):.2f} > {target[elem][1]:.2f})")
        hint = f"元素交融未达预期，触发保底！问题：{'; '.join(issues) if issues else '比例未完全匹配'}。"
    else:
        hint = f"元素交融，水墨成韵，{mbti} 如画卷展开！"
    if has_byproduct:
        hint += " 意外之喜，获得额外副产物！"
    return hint

def normalize_elements(elements):
    """归一化元素比例"""
    total = sum(elements.values())
    if total == 0:
        return {elem: 0 for elem in ['water', 'fire', 'earth', 'air']}
    return {elem: value / total for elem, value in elements.items()}

def apply_disturbance(elements):
    """应用随机扰动"""
    disturbed = elements.copy()
    for elem in disturbed:
        disturbance = random.uniform(-0.05, 0.05)
        disturbed[elem] = max(0, disturbed[elem] + disturbance)
    return disturbed