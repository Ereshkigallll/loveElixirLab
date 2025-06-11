# synthesis/third.py
# 三级物品合成逻辑，限制为二级物品输入，恢复固定比例失败机制

from data import third, intermediate_recipes, item_entries, easter_eggs
from utils import normalize_elements
from synthesis.synthesis import apply_interactions
import random
import numpy as np
import math


def synthesize_third(inventory, selected_items):
    """三级物品随机合成，限制为二级物品输入，生成三级物品输出"""
    if not selected_items:
        return None, None, None, None, "请至少选择一个物品！"

    # 失败概率：30% (可调整，范围 0.0-1.0)
    FAILURE_PROBABILITY = 0.30
    # 彩蛋生成概率：5% (可调整，范围 0.0-1.0)
    EASTER_EGG_PROBABILITY = 0.05

    # 检查是否只有单一物品
    if len(selected_items) == 1:
        return None, None, None, None, "三级合成需至少两种物品！"

    # 检查输入物品等级
    if any(item['item_type'] != 'intermediate' for item in selected_items):
        return None, None, None, None, "三级合成仅限中级物品！"

    # 检查失败
    if random.random() < FAILURE_PROBABILITY:
        # 返还 50% 物品
        new_inventory = inventory.copy()
        num_return = max(1, len(selected_items) // 2)
        returned_items = random.sample(selected_items, num_return)

        # 彩蛋物品（从 easter_eggs 选择中级或三级）
        easter_egg = None
        if random.random() < EASTER_EGG_PROBABILITY:
            valid_eggs = [egg for egg in easter_eggs if egg['item_type'] in ['intermediate', 'third']]
            if valid_eggs:
                egg = random.choice(valid_eggs)
                easter_egg = {
                    'name': egg['name'],
                    'elements': {'water': 0.25, 'fire': 0.25, 'earth': 0.25, 'air': 0.25},
                    'entries': [],
                    'item_type': egg['item_type']
                }

        return None, new_inventory, returned_items, easter_egg, "三级合成失败！"

    # 正常合成
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
        return None, None, None, None, "无法合成任何物品！"
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

    byproduct = None
    if random.random() < byproduct_prob:
        byproduct = {
            'name': item_name,
            'elements': input_ratios,
            'entries': [],
            'item_type': 'third'
        }

    result = {
        'name': item_name,
        'elements': input_ratios,
        'entries': entries,
        'item_type': 'third'
    }

    return result, new_inventory, [], byproduct, f"三级物品合成成功！获得：{item_name}" + (
        f"，额外生成副产物：{item_name}" if byproduct else "")