# synthesis/mbti.py
# MBTI 合成逻辑，限制为三级物品，恢复固定比例失败机制，保留保底机制

from data import third, mbti_targets, item_entries, easter_eggs
from utils import normalize_elements, apply_disturbance, generate_hint
from synthesis.synthesis import apply_interactions
import random
import copy
import json
import math


def synthesize_mbti(inventory, selected_items):
    """MBTI 随机合成，限制为三级物品，范围匹配，保底机制"""
    if not selected_items:
        return None, None, None, None, "请至少选择一个物品！"

    # 检查是否只有单一物品
    if len(selected_items) == 1:
        return None, None, None, None, "MBTI 合成需至少两种物品！"

    if any(item['item_type'] != 'third' for item in selected_items):
        return None, None, None, None, "MBTI 合成仅限三级物品！"

    # 失败概率：35% (可调整，范围 0.0-1.0)
    FAILURE_PROBABILITY = 0.35
    # 彩蛋生成概率：5% (可调整，范围 0.0-1.0)
    EASTER_EGG_PROBABILITY = 0.05

    # 计算元素比例
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

    # 移除选中的三级物品（无论成功或失败，物品都消耗）
    new_inventory = copy.deepcopy(inventory)
    selected_ids = {id(item) for item in selected_items}
    selected_items_json = [
        {
            'name': item['name'],
            'elements': json.dumps(item['elements']),
            'entries': json.dumps(item.get('entries', [])),
            'item_type': item['item_type']
        }
        for item in selected_items
    ]

    items_to_remove = []
    for inv_item in new_inventory:
        inv_item_json = {
            'name': inv_item['name'],
            'elements': json.dumps(inv_item['elements']),
            'entries': json.dumps(inv_item.get('entries', [])),
            'item_type': inv_item['item_type']
        }
        if id(inv_item) in selected_ids or any(
                inv_item_json['name'] == sel_item['name'] and
                inv_item_json['elements'] == sel_item['elements'] and
                inv_item_json['entries'] == sel_item['entries'] and
                inv_item_json['item_type'] == sel_item['item_type']
                for sel_item in selected_items_json
        ):
            items_to_remove.append(inv_item)

    # 检查失败
    if random.random() < FAILURE_PROBABILITY:
        # 返还 50% 物品
        num_return = max(1, len(items_to_remove) // 2)
        returned_items = random.sample(items_to_remove, num_return)
        for item in items_to_remove:
            new_inventory.remove(item)

        # 彩蛋物品（从 easter_eggs 选择三级）
        easter_egg = None
        if random.random() < EASTER_EGG_PROBABILITY:
            third_eggs = [egg for egg in easter_eggs if egg['item_type'] == 'third']
            if third_eggs:
                egg = random.choice(third_eggs)
                easter_egg = {
                    'name': egg['name'],
                    'elements': {'water': 0.25, 'fire': 0.25, 'earth': 0.25, 'air': 0.25},
                    'entries': [],
                    'item_type': 'third'
                }

        # 触发保底 MBTI
        dominant_elem = max(ratios.items(), key=lambda x: x[1])[0]
        candidates = sorted(
            mbti_targets.items(),
            key=lambda x: x[1]['ranges'][dominant_elem][1],
            reverse=True
        )[:4]
        candidate_mbti = [mbti for mbti, _ in candidates]
        reality_percent = {
            'ISFJ': 13.8, 'ESFJ': 12.0, 'ISTJ': 11.6, 'ISFP': 8.8, 'ESTJ': 8.7,
            'ESFP': 8.5, 'ENFP': 8.1, 'ISTP': 5.4, 'INFP': 4.4, 'ESTP': 4.3,
            'INTP': 3.3, 'ENTP': 3.2, 'ENFJ': 2.5, 'INTJ': 2.1, 'ENTJ': 1.8, 'INFJ': 1.5
        }
        best_mbti = max(candidate_mbti, key=lambda x: reality_percent.get(x, 0))

        result = {
            'mbti': best_mbti,
            'ratios': ratios,
            'success': False,
            'entries': entries
        }

        hint = f"MBTI 合成失败，触发保底！"
        return result, new_inventory, returned_items, easter_egg, hint

    # 正常合成
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

    for item in items_to_remove:
        new_inventory.remove(item)

    # 副产物生成
    byproduct_prob = 0.1
    for entry in entries:
        if entry in item_entries and 'byproduct' in item_entries[entry]['effect']:
            byproduct_prob += item_entries[entry]['effect']['byproduct']

    byproduct = None
    if random.random() < byproduct_prob:
        byproduct_item = random.choice(list(third.keys()))
        byproduct = {
            'name': byproduct_item,
            'elements': ratios,
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

    return result, new_inventory, [], byproduct, hint