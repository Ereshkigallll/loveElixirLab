# synthesis.py
# 核心合成逻辑：初级随机合成（记录输入比例）、中级、MBTI

from data import default_weights, initial_items, intermediate_recipes, mbti_targets, interactions
from utils import normalize_elements, normalize_weights, apply_disturbance, generate_hint
import math
import random
import numpy as np


def adjust_weights(element, context):
    """动态调整情景权重"""
    weights = default_weights[element].copy()
    ratios = context.get('ratios', {})
    balanced = all(0.2 <= v <= 0.3 for v in ratios.values())

    if balanced:
        return weights
    if element == 'fire' and ratios.get('water', 0) > 0.5:
        weights['F'] = min(weights['F'] + 0.05, 0.3)
        weights['E'] -= 0.03
        weights['N'] -= 0.02
    if element == 'water' and ratios.get('earth', 0) > 0.5:
        weights['J'] = min(weights['J'] + 0.05, 0.3)
        weights['F'] -= 0.03
        weights['I'] -= 0.02
    if 'emotional_resonance' in context.get('traits', []) and element == 'water':
        weights['F'] = min(weights['F'] + 0.05, 0.3)
        weights['I'] -= 0.03
        weights['N'] -= 0.02
    if 'intuitive_spark' in context.get('traits', []) and element == 'fire':
        weights['N'] = min(weights['N'] + 0.05, 0.2)
        weights['E'] -= 0.03
        weights['T'] -= 0.02
    main_attr = 'E' if element == 'fire' else 'F' if element == 'water' else 'S' if element == 'earth' else 'T'
    if weights[main_attr] < 0.4:
        weights[main_attr] = 0.4
        total = sum(weights.values()) - 0.4
        for k in weights:
            if k != main_attr:
                weights[k] *= (1 - 0.4) / total
    return normalize_weights(weights)


def apply_interactions(elements):
    """元素交互：相生相克"""
    adjusted = elements.copy()
    for (elem1, elem2), effect in interactions.items():
        if adjusted.get(elem1, 0) > 0 and adjusted.get(elem2, 0) > 0:
            adjusted[elem2] *= (1 + effect)
    return normalize_elements(adjusted)


def synthesize_initial(elements, input_elements):
    """初级物品随机合成，记录输入比例"""
    # 检查输入
    total_input = sum(input_elements.values())
    if total_input == 0:
        return None, elements, "请输入至少一种元素！"
    for elem, amount in input_elements.items():
        if amount < 0 or amount > elements.get(elem, 0):
            return None, elements, f"{elem}数量无效！"

    # 归一化输入比例
    input_ratios = normalize_elements(input_elements)

    # 计算合成概率（余弦相似度）
    probabilities = {}
    for item_name, item_data in initial_items.items():
        # 使用物品范围中点作为典型比例
        typical_ratios = {elem: (ranges[0] + ranges[1]) / 2 for elem, ranges in item_data['ranges'].items()}
        # 余弦相似度
        vec1 = np.array([input_ratios.get(elem, 0) for elem in ['water', 'fire', 'earth', 'air']])
        vec2 = np.array([typical_ratios.get(elem, 0) for elem in ['water', 'fire', 'earth', 'air']])
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-10)
        probabilities[item_name] = similarity

    # 归一化概率
    total_prob = sum(probabilities.values())
    if total_prob == 0:
        return None, elements, "无法合成任何物品！"
    probabilities = {k: v / total_prob for k, v in probabilities.items()}

    # 随机选择物品
    item_name = random.choices(list(probabilities.keys()), weights=list(probabilities.values()), k=1)[0]

    # 使用输入比例作为物品元素数值
    item_elements = input_ratios

    # 扣除输入元素
    new_elements = elements.copy()
    for elem, amount in input_elements.items():
        new_elements[elem] -= amount

    return {
        'name': item_name,
        'elements': item_elements
    }, new_elements, f"初级物品合成成功！获得：{item_name}"


def synthesize_intermediate(inventory, item_name):
    """中级物品合成"""
    recipe = intermediate_recipes.get(item_name)
    if not recipe:
        return None, None, "无此配方！"
    required = recipe['items']
    item_counts = {}
    for item in inventory:
        item_counts[item['name']] = item_counts.get(item['name'], 0) + 1
    for item, count in required.items():
        if item_counts.get(item, 0) < count:
            return None, None, f"{item}不足！"

    new_inventory = inventory.copy()
    for item, count in required.items():
        for _ in range(count):
            new_inventory.remove(next(i for i in new_inventory if i['name'] == item))

    return {
        'name': item_name,
        'elements': recipe['elements'],
        'trait': recipe['trait']
    }, new_inventory, "中级物品合成成功！"


def synthesize_mbti(items):
    """MBTI 合成"""
    if not items:
        return None, generate_hint({}, False)
    total_elements = {'water': 0, 'fire': 0, 'earth': 0, 'air': 0}
    traits = []

    for item in items:
        for elem, ratio in item['elements'].items():
            total_elements[elem] += ratio
        traits.append(item['trait'])

    total_elements = apply_interactions(total_elements)
    total_elements = apply_disturbance(total_elements)
    ratios = normalize_elements(total_elements)

    contributions = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
    for elem, amount in total_elements.items():
        weights = adjust_weights(elem, {'ratios': ratios, 'traits': traits})
        for attr, weight in weights.items():
            contributions[attr] += amount * weight

    pairs = [('E', 'I'), ('S', 'N'), ('T', 'F'), ('J', 'P')]
    for attr1, attr2 in pairs:
        total = contributions[attr1] + contributions[attr2]
        if total > 0:
            contributions[attr1] /= total
            contributions[attr2] /= total
        else:
            contributions[attr1] = contributions[attr2] = 0.5

    best_mbti, best_score = None, float('inf')
    for mbti, target in mbti_targets.items():
        score = sum((ratios.get(elem, 0) - target.get(elem, 0)) ** 2 for elem in target)
        if score < best_score:
            best_score = score
            best_mbti = mbti

    success_rate = max(0, 1 - best_score * 10) * 100
    success = success_rate > 80 and best_mbti in mbti_targets
    hint = generate_hint(ratios, success, best_mbti)
    return {
        'mbti': best_mbti,
        'success_rate': success_rate,
        'ratios': ratios,
        'contributions': contributions,
        'success': success
    }, hint