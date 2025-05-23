# synthesis.py
# 核心合成逻辑：初级随机合成（100%元素规则，中文名称）、中级随机合成（自动配方匹配）、MBTI随机合成（仅中级物品，保底机制，存储历史）
# TODO 一个一级物品也可以合成中级物品，需要修改

from data import default_weights, initial_items, intermediate_recipes, mbti_targets, interactions, item_traits
from utils import normalize_elements, normalize_weights, apply_disturbance, generate_hint
import math
import random
import numpy as np


def adjust_weights(element, context):
    """动态调整情景权重，考虑物品属性"""
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
    if 'creative_flare' in context.get('traits', []) and element in ['fire', 'air']:
        weights['N'] = min(weights['N'] + 0.05, 0.2)
        weights['E'] -= 0.03 if element == 'fire' else 0
        weights['P'] -= 0.02 if element == 'air' else 0
    if 'empathic_flow' in context.get('traits', []) and element in ['water', 'earth']:
        weights['F'] = min(weights['F'] + 0.05, 0.3)
        weights['I'] -= 0.03 if element == 'water' else 0
        weights['J'] -= 0.02 if element == 'earth' else 0
    if 'steadfast_duty' in context.get('traits', []) and element == 'earth':
        weights['S'] = min(weights['S'] + 0.05, 0.3)
        weights['J'] -= 0.03
        weights['F'] -= 0.02
    if 'freedom_breeze' in context.get('traits', []) and element == 'air':
        weights['P'] = min(weights['P'] + 0.05, 0.3)
        weights['T'] -= 0.03
        weights['N'] -= 0.02
    if 'empathic_tide' in context.get('traits', []) and element == 'water':
        weights['F'] = min(weights['F'] + 0.05, 0.3)
        weights['I'] -= 0.03
        weights['N'] -= 0.02
    if 'passionate_flare' in context.get('traits', []) and element == 'fire':
        weights['E'] = min(weights['E'] + 0.05, 0.3)
        weights['N'] -= 0.03
        weights['S'] -= 0.02
    if 'dutiful_rock' in context.get('traits', []) and element == 'earth':
        weights['J'] = min(weights['J'] + 0.05, 0.3)
        weights['S'] -= 0.03
        weights['F'] -= 0.02
    if 'creative_glow' in context.get('traits', []) and element in ['fire', 'water', 'air']:
        weights['N'] = min(weights['N'] + 0.05, 0.2)
        weights['E'] -= 0.03 if element == 'fire' else 0
        weights['P'] -= 0.02 if element == 'air' else 0
        weights['I'] -= 0.02 if element == 'water' else 0
    if 'introspective_mist' in context.get('traits', []) and element == 'water':
        weights['I'] = min(weights['I'] + 0.05, 0.3)
        weights['F'] -= 0.03
        weights['N'] -= 0.02
    if 'stable_heat' in context.get('traits', []) and element == 'fire':
        weights['S'] = min(weights['S'] + 0.05, 0.3)
        weights['E'] -= 0.03
        weights['N'] -= 0.02
    if 'rational_mist' in context.get('traits', []) and element == 'air':
        weights['T'] = min(weights['T'] + 0.05, 0.3)
        weights['P'] -= 0.03
        weights['N'] -= 0.02
    if 'empathic_earth' in context.get('traits', []) and element == 'earth':
        weights['F'] = min(weights['F'] + 0.05, 0.3)
        weights['S'] -= 0.03
        weights['J'] -= 0.02
    if 'free_spirit' in context.get('traits', []) and element == 'air':
        weights['P'] = min(weights['P'] + 0.05, 0.3)
        weights['T'] -= 0.03
        weights['N'] -= 0.02

    # 物品属性影响（支持增强和削弱）
    for trait in context.get('traits', []):
        if trait in item_traits and element in item_traits[trait].get('effect', {}):
            for attr, boost in item_traits[trait]['effect'][element].items():
                weights[attr] = max(0.1, min(weights[attr] + boost, 0.9))  # 限制权重范围
                total = sum(weights.values())
                for k in weights:
                    if k != attr:
                        weights[k] *= (1 - weights[attr]) / (total - weights[attr])

    main_attr = 'E' if element == 'fire' else 'F' if element == 'water' else 'S' if element == 'earth' else 'T'
    if weights[main_attr] < 0.4:
        weights[main_attr] = 0.4
        total = sum(weights.values()) - 0.4
        for k in weights:
            if k != main_attr:
                weights[k] *= (1 - 0.4) / (total - weights[main_attr])
    return normalize_weights(weights)


def apply_interactions(elements):
    """元素交互：相生相克"""
    adjusted = elements.copy()
    for (elem1, elem2), effect in interactions.items():
        if adjusted.get(elem1, 0) > 0 and adjusted.get(elem2, 0) > 0:
            adjusted[elem2] *= (1 + effect)
    return normalize_elements(adjusted)


def synthesize_initial(elements, input_elements):
    """初级物品随机合成，记录输入比例，添加随机属性，支持100%元素规则"""
    total_input = sum(input_elements.values())
    if total_input == 0:
        return None, elements, "请输入至少一种元素！"
    for elem, amount in input_elements.items():
        if amount < 0 or amount > elements.get(elem, 0):
            return None, elements, f"{elem}数量无效！"

    input_ratios = normalize_elements(input_elements)

    # 检查100%元素规则
    item_name = None
    for elem, ratio in input_ratios.items():
        if ratio == 1.0:
            # 查找该元素比例最高的物品
            max_ratio = -1
            for name, data in initial_items.items():
                elem_range = data['ranges'].get(elem, (0, 0))
                max_elem_ratio = elem_range[1]  # 取范围最大值
                if max_elem_ratio > max_ratio:
                    max_ratio = max_elem_ratio
                    item_name = name
            break

    # 若无100%元素，使用随机选择
    if not item_name:
        probabilities = {}
        for item_name, item_data in initial_items.items():
            typical_ratios = {elem: (ranges[0] + ranges[1]) / 2 for elem, ranges in item_data['ranges'].items()}
            vec1 = np.array([input_ratios.get(elem, 0) for elem in ['water', 'fire', 'earth', 'air']])
            vec2 = np.array([typical_ratios.get(elem, 0) for elem in ['water', 'fire', 'earth', 'air']])
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-10)
            probabilities[item_name] = similarity

        total_prob = sum(probabilities.values())
        if total_prob == 0:
            return None, elements, "无法合成任何物品！"
        probabilities = {k: v / total_prob for k, v in probabilities.items()}

        item_name = random.choices(list(probabilities.keys()), weights=list(probabilities.values()), k=1)[0]

    item_elements = input_ratios

    # 随机赋予属性（0-2个）
    trait_probs = {}
    for trait, data in item_traits.items():
        prob = 0
        for elem in data['elements']:
            prob += input_ratios.get(elem, 0) * data['weight']
        trait_probs[trait] = prob
    num_traits = random.choices([0, 1, 2], weights=[0.1, 0.6, 0.3], k=1)[0]
    traits = []
    if num_traits > 0:
        available_traits = list(trait_probs.keys())
        trait_weights = [trait_probs[t] for t in available_traits]
        total_weight = sum(trait_weights)
        if total_weight > 0:
            trait_weights = [w / total_weight for w in trait_weights]
            selected_traits = random.choices(available_traits, weights=trait_weights,
                                             k=min(num_traits, len(available_traits)))
            selected_traits = list(dict.fromkeys(selected_traits))  # 避免重复
            mbti_attrs = set()
            for t in selected_traits:
                mbti = item_traits[t]['mbti']
                if mbti not in mbti_attrs:
                    traits.append(t)
                    mbti_attrs.add(mbti)

    new_elements = elements.copy()
    for elem, amount in input_elements.items():
        new_elements[elem] -= amount

    return {
        'name': item_name,
        'elements': item_elements,
        'traits': traits,
        'item_type': 'initial'
    }, new_elements, f"初级物品合成成功！获得：{item_name}"


def synthesize_intermediate(inventory, selected_items):
    """中级物品随机合成，自动匹配配方或随机生成"""
    if not selected_items:
        return None, None, "请至少选择一个物品！"

    # 计算物品数量
    item_counts = {}
    input_traits = []
    for item in selected_items:
        item_counts[item['name']] = item_counts.get(item['name'], 0) + 1
        input_traits.extend(item.get('traits', []))

    # 匹配配方
    possible_items = []
    for item_name, recipe in intermediate_recipes.items():
        required = recipe['items']
        if all(item_counts.get(item, 0) >= count for item, count in required.items()):
            possible_items.append(item_name)

    # 计算平均元素比例
    input_elements = {'water': 0, 'fire': 0, 'earth': 0, 'air': 0}
    for item in selected_items:
        for elem, ratio in item['elements'].items():
            input_elements[elem] += ratio
    input_ratios = normalize_elements(input_elements)

    # 随机选择物品
    if possible_items:
        # 匹配配方，随机选择
        probabilities = {}
        for item_name in possible_items:
            item_data = intermediate_recipes[item_name]
            typical_ratios = {elem: (ranges[0] + ranges[1]) / 2 for elem, ranges in item_data['ranges'].items()}
            vec1 = np.array([input_ratios.get(elem, 0) for elem in ['water', 'fire', 'earth', 'air']])
            vec2 = np.array([typical_ratios.get(elem, 0) for elem in ['water', 'fire', 'earth', 'air']])
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-10)
            probabilities[item_name] = similarity

        total_prob = sum(probabilities.values())
        if total_prob == 0:
            return None, None, "无法合成任何物品！"
        probabilities = {k: v / total_prob for k, v in probabilities.items()}

        item_name = random.choices(list(probabilities.keys()), weights=list(probabilities.values()), k=1)[0]
        item_data = intermediate_recipes[item_name]

        # 随机赋予属性（0-2个）
        trait_probs = {}
        for trait, data in item_traits.items():
            prob = 0
            for elem in data['elements']:
                prob += input_ratios.get(elem, 0) * data['weight']
            trait_probs[trait] = prob
        num_traits = random.choices([0, 1, 2], weights=[0.1, 0.6, 0.3], k=1)[0]
        traits = []
        if num_traits > 0:
            available_traits = list(trait_probs.keys())
            trait_weights = [trait_probs[t] for t in available_traits]
            total_weight = sum(trait_weights)
            if total_weight > 0:
                trait_weights = [w / total_weight for w in trait_weights]
                selected_traits = random.choices(available_traits, weights=trait_weights,
                                                 k=min(num_traits, len(available_traits)))
                selected_traits = list(dict.fromkeys(selected_traits))  # 避免重复
                mbti_attrs = set()
                for t in selected_traits:
                    mbti = item_traits[t]['mbti']
                    if mbti not in mbti_attrs:
                        traits.append(t)
                        mbti_attrs.add(mbti)
    else:
        # 不匹配配方，随机选择物品
        item_name = random.choice(list(intermediate_recipes.keys()))
        item_data = intermediate_recipes[item_name]

        # 强制赋予1个削弱属性
        negative_traits = ['疲惫', '迷茫', '固执', '浮躁', '冷漠', '混乱', '拖延', '散漫']
        traits = [random.choice(negative_traits)]

        # 可选：50% 概率赋予1个增强属性
        if random.random() < 0.5:
            positive_traits = [t for t in item_traits.keys() if t not in negative_traits]
            trait_probs = {}
            for trait in positive_traits:
                prob = 0
                for elem in item_traits[trait]['elements']:
                    prob += input_ratios.get(elem, 0) * item_traits[trait]['weight']
                trait_probs[trait] = prob
            if trait_probs:
                total_prob = sum(trait_probs.values())
                if total_prob > 0:
                    trait_weights = [trait_probs[t] / total_prob for t in positive_traits]
                    extra_trait = random.choices(positive_traits, weights=trait_weights, k=1)[0]
                    if item_traits[extra_trait]['mbti'] != item_traits[traits[0]]['mbti']:
                        traits.append(extra_trait)

    item_elements = input_ratios

    # 扣除物品
    new_inventory = inventory.copy()
    for item in selected_items:
        new_inventory.remove(item)

    return {
        'name': item_name,
        'elements': item_elements,
        'traits': traits,
        'item_type': 'intermediate'
    }, new_inventory, f"中级物品合成成功！获得：{item_name}"


def synthesize_mbti(inventory, selected_items):
    """MBTI 随机合成，基于选择的中级物品，支持保底机制"""
    if not selected_items:
        return None, None, "请至少选择一个物品！"

    # 检查是否均为中级物品
    if any(item['item_type'] != 'intermediate' for item in selected_items):
        return None, None, "MBTI 合成仅限中级物品！"

    # 计算平均元素比例
    total_elements = {'water': 0, 'fire': 0, 'earth': 0, 'air': 0}
    traits = []
    for item in selected_items:
        for elem, ratio in item['elements'].items():
            total_elements[elem] += ratio
        traits.extend(item.get('traits', []))

    total_elements = apply_interactions(total_elements)
    total_elements = apply_disturbance(total_elements)
    ratios = normalize_elements(total_elements)

    # 随机选择 MBTI
    probabilities = {}
    for mbti, target in mbti_targets.items():
        vec1 = np.array([ratios.get(elem, 0) for elem in ['water', 'fire', 'earth', 'air']])
        vec2 = np.array([target.get(elem, 0) for elem in ['water', 'fire', 'earth', 'air']])
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-10)
        probabilities[mbti] = similarity

    total_prob = sum(probabilities.values())
    if total_prob == 0:
        return None, None, generate_hint(ratios, False)
    probabilities = {k: v / total_prob for k, v in probabilities.items()}

    best_mbti = random.choices(list(probabilities.keys()), weights=list(probabilities.values()), k=1)[0]

    # 计算成功率
    target = mbti_targets[best_mbti]
    score = sum((ratios.get(elem, 0) - target.get(elem, 0)) ** 2 for elem in target)
    success_rate = max(0, 1 - score * 10) * 100
    success = success_rate > 80

    # 保底机制
    trait = None
    if not success:
        # 从现实比例最高的 4 个 MBTI 随机选择
        best_mbti = random.choice(['ISFJ', 'ESFJ', 'ISTJ', 'ISFP'])
        # 随机赋予削弱属性
        negative_traits = ['疲惫', '迷茫', '固执', '浮躁', '冷漠', '混乱', '拖延', '散漫']
        trait = random.choice(negative_traits)

    # 扣除物品
    new_inventory = inventory.copy()
    for item in selected_items:
        new_inventory.remove(item)

    hint = generate_hint(ratios, success, best_mbti, trait)
    result = {
        'mbti': best_mbti,
        'ratios': ratios,
        'success': success,
        'trait': trait  # 保底时包含削弱属性
    }

    return result, new_inventory, hint