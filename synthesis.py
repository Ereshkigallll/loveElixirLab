# synthesis.py
# 核心合成逻辑：初级（元素+一级→一级）、中级（一级+中级→中级）、三级（二级→三级）、MBTI（三级→MBTI），移除情感属性，支持词条属性，允许同种元素合成

from data import initial_items, intermediate_recipes, third, mbti_targets, interactions, item_entries
from utils import normalize_elements, apply_disturbance, generate_hint
import random
import numpy as np


def apply_interactions(elements):
    """元素交互：相生相克"""
    adjusted = elements.copy()
    for (elem1, elem2), effect in interactions.items():
        if adjusted.get(elem1, 0) > 0 and adjusted.get(elem2, 0) > 0:
            adjusted[elem2] *= (1 + effect)
    return normalize_elements(adjusted)


def synthesize_initial(elements, input_elements, input_items=None):
    """初级物品随机合成，支持元素和初级物品，限制为初级物品输出，允许同种元素"""
    input_items = input_items or []

    # 检查输入物品等级
    if any(item['item_type'] == 'intermediate' or item['item_type'] == 'third' for item in input_items):
        return None, elements, "初级合成不可使用中级或三级物品！"

    total_input = sum(input_elements.values())
    if total_input == 0 and not input_items:
        return None, elements, "请输入至少一种元素或选择一个初级物品！"

    # 合并元素和物品比例
    combined_elements = input_elements.copy()
    for item in input_items:
        for elem, ratio in item['elements'].items():
            combined_elements[elem] = combined_elements.get(elem, 0) + ratio

    # 检查总输入数量（元素总数 + 物品数 ≥ 2）
    total_input_elements = sum(input_elements.values())
    if total_input_elements + len(input_items) < 2:
        return None, elements, "初级合成需至少两个元素或一个元素加一个物品！"

    # 验证元素数量
    adjusted_elements = input_elements.copy()
    for elem, amount in input_elements.items():
        if amount < 0 or amount > elements.get(elem, 0):
            return None, elements, f"{elem}数量无效！"
        adjusted_elements[elem] = amount

    input_ratios = normalize_elements(combined_elements)

    # 检查100%元素规则
    item_name = None
    for elem, ratio in input_ratios.items():
        if ratio >= 0.999:
            max_ratio = -1
            for name, data in initial_items.items():
                elem_range = data['ranges'].get(elem, (0, 0))
                max_elem_ratio = elem_range[1]
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

    # 分配词条（entries）
    entry_probs = {}
    for entry, data in item_entries.items():
        prob = 0
        for elem in data['elements']:
            prob += input_ratios.get(elem, 0) * data['weight']
        entry_probs[entry] = prob

    num_entries = random.choices([0, 1], weights=[0.5, 0.5], k=1)[0]
    entries = []
    if num_entries > 0:
        available_entries = list(entry_probs.keys())
        entry_weights = [entry_probs.get(e, 0) for e in available_entries]
        total_weight = sum(entry_weights)
        if total_weight > 0:
            entry_weights = [w / total_weight for w in entry_weights]
            selected_entry = random.choices(available_entries, weights=entry_weights, k=1)[0]
            entries.append(selected_entry)

    # 扣除元素
    new_elements = elements.copy()
    for elem, amount in adjusted_elements.items():
        new_elements[elem] -= amount

    # 副产物生成
    byproduct_prob = 0.1
    for entry in entries:
        if entry in item_entries and 'byproduct' in item_entries[entry]['effect']:
            byproduct_prob += item_entries[entry]['effect']['byproduct']

    byproduct = random.random() < byproduct_prob
    result = {
        'name': item_name,
        'elements': input_ratios,
        'entries': entries,
        'item_type': 'initial'
    }

    return (result, new_elements,
            f"初级物品合成成功！获得：{item_name}" + (f"，额外生成副产物：{item_name}" if byproduct else "")), byproduct


def synthesize_intermediate(inventory, selected_items):
    """中级物品随机合成，支持一级和中级物品，限制为中级物品输出"""
    if not selected_items:
        return None, None, "请至少选择一个物品！"

    # 检查是否只有单一物品
    if len(selected_items) == 1:
        return None, None, "中级合成需至少两种物品！"

    # 检查输入物品等级
    if any(item['item_type'] == 'third' for item in selected_items):
        return None, None, "中级合成不可使用三级物品！"

    # 计算平均元素比例，应用词条效果
    input_elements = {'water': 0, 'fire': 0, 'earth': 0, 'air': 0}
    input_entries = []
    for item in selected_items:
        for elem, ratio in item['elements'].items():
            input_elements[elem] += ratio
        input_entries.extend(item.get('entries', []))

    # 应用词条效果：元素增幅
    for entry in input_entries:
        if entry in item_entries:
            for elem, boost in item_entries[entry]['effect'].items():
                if elem in input_elements:
                    input_elements[elem] += boost

    input_ratios = normalize_elements(input_elements)

    # 随机选择物品
    probabilities = {}
    for item_name, item_data in intermediate_recipes.items():
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

    # 分配词条
    entry_probs = {}
    for entry, data in item_entries.items():
        prob = 0
        for elem in data['elements']:
            prob += input_ratios.get(elem, 0) * data['weight']
        entry_probs[entry] = prob

    num_entries = random.choices([0, 1], weights=[0.5, 0.5], k=1)[0]
    entries = []
    if num_entries > 0:
        available_entries = list(entry_probs.keys())
        entry_weights = [entry_probs.get(e, 0) for e in available_entries]
        total_weight = sum(entry_weights)
        if total_weight > 0:
            entry_weights = [w / total_weight for w in entry_weights]
            selected_entry = random.choices(available_entries, weights=entry_weights, k=1)[0]
            entries.append(selected_entry)

    # 扣除物品
    new_inventory = inventory.copy()
    for item in selected_items:
        new_inventory.remove(item)

    # 副产物生成
    byproduct_prob = 0.1
    for entry in entries:
        if entry in item_entries and 'byproduct' in item_entries[entry]['effect']:
            byproduct_prob += item_entries[entry]['effect']['byproduct']

    byproduct = random.random() < byproduct_prob
    result = {
        'name': item_name,
        'elements': input_ratios,
        'entries': entries,
        'item_type': 'intermediate'
    }

    return (result, new_inventory,
            f"中级物品合成成功！获得：{item_name}" + (f"，额外生成副产物：{item_name}" if byproduct else "")), byproduct


def synthesize_third(inventory, selected_items):
    """三级物品随机合成，限制为二级物品输入，生成三级物品输出"""
    if not selected_items:
        return None, None, "请至少选择一个物品！"

    # 检查是否只有单一物品
    if len(selected_items) == 1:
        return None, None, "三级合成需至少两种物品！"

    # 检查输入物品等级
    if any(item['item_type'] != 'intermediate' for item in selected_items):
        return None, None, "三级合成仅限中级物品！"

    # 计算平均元素比例，应用词条效果
    input_elements = {'water': 0, 'fire': 0, 'earth': 0, 'air': 0}
    input_entries = []
    for item in selected_items:
        for elem, ratio in item['elements'].items():
            input_elements[elem] += ratio
        input_entries.extend(item.get('entries', []))

    # 应用词条效果：元素增幅
    for entry in input_entries:
        if entry in item_entries:
            for elem, boost in item_entries[entry]['effect'].items():
                if elem in input_elements:
                    input_elements[elem] += boost

    input_ratios = normalize_elements(input_elements)

    # 随机选择物品
    probabilities = {}
    for item_name, item_data in third.items():
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

    # 分配词条
    entry_probs = {}
    for entry, data in item_entries.items():
        prob = 0
        for elem in data['elements']:
            prob += input_ratios.get(elem, 0) * data['weight']
        entry_probs[entry] = prob

    num_entries = random.choices([0, 1], weights=[0.5, 0.5], k=1)[0]
    entries = []
    if num_entries > 0:
        available_entries = list(entry_probs.keys())
        entry_weights = [entry_probs.get(e, 0) for e in available_entries]
        total_weight = sum(entry_weights)
        if total_weight > 0:
            entry_weights = [w / total_weight for w in entry_weights]
            selected_entry = random.choices(available_entries, weights=entry_weights, k=1)[0]
            entries.append(selected_entry)

    # 扣除物品
    new_inventory = inventory.copy()
    for item in selected_items:
        new_inventory.remove(item)

    # 副产物生成
    byproduct_prob = 0.1
    for entry in entries:
        if entry in item_entries and 'byproduct' in item_entries[entry]['effect']:
            byproduct_prob += item_entries[entry]['effect']['byproduct']

    byproduct = random.random() < byproduct_prob
    result = {
        'name': item_name,
        'elements': input_ratios,
        'entries': entries,
        'item_type': 'third'
    }

    return (result, new_inventory,
            f"三级物品合成成功！获得：{item_name}" + (f"，额外生成副产物：{item_name}" if byproduct else "")), byproduct


def synthesize_mbti(inventory, selected_items):
    """MBTI 随机合成，限制为三级物品，范围匹配，保底机制"""
    if not selected_items:
        return None, None, "请至少选择一个物品！"

    # 检查是否只有单一物品
    if len(selected_items) == 1:
        return None, None, "MBTI 合成需至少两种物品！"

    if any(item['item_type'] != 'third' for item in selected_items):
        return None, None, "MBTI 合成仅限三级物品！"

    total_elements = {'water': 0, 'fire': 0, 'earth': 0, 'air': 0}
    entries = []
    for item in selected_items:
        for elem, ratio in item['elements'].items():
            total_elements[elem] += ratio
        entries.extend(item.get('entries', []))

    for entry in entries:
        if entry in item_entries:
            for elem, boost in item_entries[entry]['effect'].items():
                if elem in total_elements:
                    total_elements[elem] += boost

    total_elements = apply_interactions(total_elements)
    total_elements = apply_disturbance(total_elements)
    ratios = normalize_elements(total_elements)

    dominant_elem = max(ratios.items(), key=lambda x: x[1])[0]

    candidates = sorted(
        mbti_targets.items(),
        key=lambda x: x[1]['ranges'][dominant_elem][1],
        reverse=True
    )[:4]
    candidate_mbti = [mbti for mbti, _ in candidates]

    matched_mbti = []
    for mbti in candidate_mbti:
        ranges = mbti_targets[mbti]['ranges']
        if all(ranges[elem][0] <= ratios.get(elem, 0) <= ranges[elem][1] for elem in ['water', 'fire', 'earth', 'air']):
            matched_mbti.append(mbti)

    best_mbti = None
    success = False
    if matched_mbti:
        best_mbti = random.choice(matched_mbti)
        success = True
    else:
        reality_percent = {
            'ISFJ': 13.8, 'ESFJ': 12.0, 'ISTJ': 11.6, 'ISFP': 8.8, 'ESTJ': 8.7,
            'ESFP': 8.5, 'ENFP': 8.1, 'ISTP': 5.4, 'INFP': 4.4, 'ESTP': 4.3,
            'INTP': 3.3, 'ENTP': 3.2, 'ENFJ': 2.5, 'INTJ': 2.1, 'ENTJ': 1.8, 'INFJ': 1.5
        }
        best_mbti = max(candidate_mbti, key=lambda x: reality_percent.get(x, 0))

    new_inventory = inventory.copy()
    for item in selected_items:
        new_inventory.remove(item)

    byproduct_prob = 0.1
    for entry in entries:
        if entry in item_entries and 'byproduct' in item_entries[entry]['effect']:
            byproduct_prob += item_entries[entry]['effect']['byproduct']

    byproduct = None
    if random.random() < byproduct_prob:
        byproduct_item = random.choice(list(third.keys()))
        byproduct = {
            'name': byproduct_item,
            'elements': input_ratios,
            'entries': [],
            'item_type': 'third'
        }

    hint = generate_hint(ratios, success, best_mbti, None, entries, byproduct is not None)
    result = {
        'mbti': best_mbti,
        'ratios': ratios,
        'success': success,
        'entries': entries
    }

    return (result, new_inventory, hint), byproduct