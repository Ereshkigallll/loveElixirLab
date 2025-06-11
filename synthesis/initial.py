# synthesis/initial.py
# 初级物品合成逻辑，支持元素和初级物品，允许同种元素，恢复固定比例失败机制

from data import initial_items, item_entries, easter_eggs
from utils import normalize_elements
from synthesis.synthesis import apply_interactions
import random
import numpy as np
import math


def synthesize_initial(elements, input_elements, input_items=None):
    """初级物品随机合成，支持元素和初级物品，限制为初级物品输出，允许同种元素"""
    input_items = input_items or []

    # 失败概率：20% (可调整，范围 0.0-1.0)
    FAILURE_PROBABILITY = 0.20
    # 彩蛋生成概率：5% (可调整，范围 0.0-1.0)
    EASTER_EGG_PROBABILITY = 0.05

    # 检查输入物品等级
    if any(item['item_type'] == 'intermediate' or item['item_type'] == 'third' for item in input_items):
        return None, elements, None, None, "初级合成不可使用中级或三级物品！"

    total_input = sum(input_elements.values())
    if total_input == 0 and not input_items:
        return None, elements, None, None, "请输入至少一种元素或选择一个初级物品！"

    # 合并元素和物品比例
    combined_elements = input_elements.copy()
    for item in input_items:
        for elem, ratio in item['elements'].items():
            combined_elements[elem] = combined_elements.get(elem, 0) + ratio

    # 检查总输入数量（元素总数 + 物品数 ≥ 2）
    total_input_elements = sum(input_elements.values())
    if total_input_elements + len(input_items) < 2:
        return None, elements, None, None, "初级合成需至少两个元素或一个元素加一个物品！"

    # 验证元素数量
    adjusted_elements = input_elements.copy()
    for elem, amount in input_elements.items():
        if amount < 0 or amount > elements.get(elem, 0):
            return None, elements, None, None, f"{elem}数量无效！"
        adjusted_elements[elem] = amount

    # 检查失败
    if random.random() < FAILURE_PROBABILITY:
        # 返还 50% 材料
        returned_elements = elements.copy()
        returned_items = []

        if total_input_elements > 0:
            # 返还 50% 元素（随机选择非零元素）
            non_zero_elements = [(elem, amt) for elem, amt in input_elements.items() if amt > 0]
            if non_zero_elements:
                return_elem, return_amt = random.choice(non_zero_elements)
                return_qty = math.floor(return_amt * 0.5)
                if return_qty > 0:
                    returned_elements[return_elem] += return_qty
        else:
            # 返还 50% 物品（随机选择）
            if input_items:
                num_return = max(1, len(input_items) // 2)
                returned_items = random.sample(input_items, num_return)

        # 彩蛋物品（从 easter_eggs 选择初级）
        easter_egg = None
        if random.random() < EASTER_EGG_PROBABILITY:
            initial_eggs = [egg for egg in easter_eggs if egg['item_type'] == 'initial']
            if initial_eggs:
                egg = random.choice(initial_eggs)
                easter_egg = {
                    'name': egg['name'],
                    'elements': {'water': 0.25, 'fire': 0.25, 'earth': 0.25, 'air': 0.25},
                    'entries': [],
                    'item_type': 'initial'
                }

        return None, returned_elements, returned_items, easter_egg, "初级合成失败！"

    # 正常合成
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
            return None, elements, None, None, "无法合成任何物品！"
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

    byproduct = None
    if random.random() < byproduct_prob:
        byproduct = {
            'name': item_name,
            'elements': input_ratios,
            'entries': [],
            'item_type': 'initial'
        }

    result = {
        'name': item_name,
        'elements': input_ratios,
        'entries': entries,
        'item_type': 'initial'
    }

    return result, new_elements, input_items, byproduct, f"初级物品合成成功！获得：{item_name}" + (
        f"，额外生成副产物：{item_name}" if byproduct else "")