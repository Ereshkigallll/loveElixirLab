# data.py
# 存储配方、权重、MBTI目标，新增中级配方、削弱属性、item_type，物品名称改为中文

import random

# 默认权重
default_weights = {
    'water': {'F': 0.55, 'I': 0.25, 'N': 0.15, 'J': 0.05},
    'fire': {'E': 0.55, 'S': 0.25, 'N': 0.15, 'T': 0.05},
    'earth': {'S': 0.55, 'J': 0.25, 'F': 0.15, 'I': 0.05},
    'air': {'T': 0.55, 'P': 0.25, 'S': 0.15, 'N': 0.05}
}

# 初级物品范围
initial_items = {
    '水晶': {
        'main': ['water'],
        'ranges': {'water': (0.7, 0.9), 'fire': (0, 0.3), 'earth': (0, 0.3), 'air': (0, 0.3)},
        'item_type': 'initial'
    },
    '火焰': {
        'main': ['fire'],
        'ranges': {'fire': (0.7, 0.9), 'water': (0, 0.3), 'earth': (0, 0.3), 'air': (0, 0.3)},
        'item_type': 'initial'
    },
    '泥浆': {
        'main': ['earth', 'water'],
        'ranges': {'earth': (0.4, 0.6), 'water': (0.3, 0.5), 'fire': (0, 0.2), 'air': (0, 0.2)},
        'item_type': 'initial'
    },
    '气流': {
        'main': ['air'],
        'ranges': {'air': (0.7, 0.9), 'water': (0, 0.3), 'fire': (0, 0.3), 'earth': (0, 0.3)},
        'item_type': 'initial'
    },
    '矿石': {
        'main': ['earth'],
        'ranges': {'earth': (0.7, 0.9), 'water': (0, 0.3), 'fire': (0, 0.3), 'air': (0, 0.3)},
        'item_type': 'initial'
    },
    '火花': {
        'main': ['fire', 'air'],
        'ranges': {'fire': (0.4, 0.6), 'air': (0.3, 0.5), 'water': (0, 0.2), 'earth': (0, 0.2)},
        'item_type': 'initial'
    }
}

# 属性定义（增强和削弱）
item_traits = {
    '激情': {
        'mbti': 'E',
        'elements': ['fire'],
        'weight': 0.8,
        'effect': {'fire': {'E': 0.05}},
        'description': '火元素 外向 属性增加 5%'
    },
    '内省': {
        'mbti': 'I',
        'elements': ['water'],
        'weight': 0.8,
        'effect': {'water': {'I': 0.05}},
        'description': '水元素 内向 属性增加 5%'
    },
    '稳定': {
        'mbti': 'S',
        'elements': ['earth'],
        'weight': 0.8,
        'effect': {'earth': {'S': 0.05}},
        'description': '土元素 感觉 属性增加 5%'
    },
    '创造': {
        'mbti': 'N',
        'elements': ['fire', 'water'],
        'weight': 0.4,
        'effect': {'fire': {'N': 0.05}, 'water': {'N': 0.05}},
        'description': '火、水元素 直觉 属性增加 5%'
    },
    '理性': {
        'mbti': 'T',
        'elements': ['air'],
        'weight': 0.8,
        'effect': {'air': {'T': 0.05}},
        'description': '风元素 思维 属性增加 5%'
    },
    '情感': {
        'mbti': 'F',
        'elements': ['water', 'earth'],
        'weight': 0.4,
        'effect': {'water': {'F': 0.05}, 'earth': {'F': 0.05}},
        'description': '水、土元素 情感 属性增加 5%'
    },
    '责任': {
        'mbti': 'J',
        'elements': ['earth'],
        'weight': 0.8,
        'effect': {'earth': {'J': 0.05}},
        'description': '土元素 判断 属性增加 5%'
    },
    '自由': {
        'mbti': 'P',
        'elements': ['air'],
        'weight': 0.8,
        'effect': {'air': {'P': 0.05}},
        'description': '风元素 感知 属性增加 5%'
    },
    '疲惫': {
        'mbti': 'E',
        'elements': ['fire'],
        'weight': 0.4,
        'effect': {'fire': {'E': -0.05}},
        'description': '火元素 外向 属性减少 5%'
    },
    '迷茫': {
        'mbti': 'I',
        'elements': ['water'],
        'weight': 0.4,
        'effect': {'water': {'I': -0.05}},
        'description': '水元素 内向 属性减少 5%'
    },
    '固执': {
        'mbti': 'S',
        'elements': ['earth'],
        'weight': 0.4,
        'effect': {'earth': {'S': -0.05}},
        'description': '土元素 感觉 属性减少 5%'
    },
    '浮躁': {
        'mbti': 'N',
        'elements': ['fire', 'water'],
        'weight': 0.2,
        'effect': {'fire': {'N': -0.05}, 'water': {'N': -0.05}},
        'description': '火、水元素 直觉 属性减少 5%'
    },
    '冷漠': {
        'mbti': 'T',
        'elements': ['air'],
        'weight': 0.4,
        'effect': {'air': {'T': -0.05}},
        'description': '风元素 思维 属性减少 5%'
    },
    '混乱': {
        'mbti': 'F',
        'elements': ['water', 'earth'],
        'weight': 0.2,
        'effect': {'water': {'F': -0.05}, 'earth': {'F': -0.05}},
        'description': '水、土元素 情感 属性减少 5%'
    },
    '拖延': {
        'mbti': 'J',
        'elements': ['earth'],
        'weight': 0.4,
        'effect': {'earth': {'J': -0.05}},
        'description': '土元素 判断 属性减少 5%'
    },
    '散漫': {
        'mbti': 'P',
        'elements': ['air'],
        'weight': 0.4,
        'effect': {'air': {'P': -0.05}},
        'description': '风元素 感知 属性减少 5%'
    }
}

# 中级物品配方（15种）
intermediate_recipes = {
    '深海之心': {
        'items': {'水晶': 2, '火焰': 1},
        'elements': {'water': 0.7, 'earth': 0.2, 'fire': 0.1},
        'trait': 'emotional_resonance',
        'ranges': {'water': (0.6, 0.8), 'earth': (0.1, 0.3), 'fire': (0, 0.2), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '烈焰水晶': {
        'items': {'火焰': 2, '水晶': 1},
        'elements': {'fire': 0.6, 'water': 0.2, 'air': 0.2},
        'trait': 'intuitive_spark',
        'ranges': {'fire': (0.5, 0.7), 'water': (0.1, 0.3), 'air': (0.1, 0.3), 'earth': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '星火精华': {
        'items': {'火花': 1, '火焰': 1, '气流': 1},
        'elements': {'fire': 0.5, 'air': 0.3, 'water': 0.1, 'earth': 0.1},
        'trait': 'creative_flare',
        'ranges': {'fire': (0.4, 0.6), 'air': (0.2, 0.4), 'water': (0, 0.2), 'earth': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '月影之水': {
        'items': {'泥浆': 2, '水晶': 1},
        'elements': {'water': 0.5, 'earth': 0.3, 'fire': 0.1, 'air': 0.1},
        'trait': 'empathic_flow',
        'ranges': {'water': (0.4, 0.6), 'earth': (0.2, 0.4), 'fire': (0, 0.2), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '地心矿核': {
        'items': {'矿石': 2, '泥浆': 1},
        'elements': {'earth': 0.6, 'water': 0.2, 'fire': 0.1, 'air': 0.1},
        'trait': 'steadfast_duty',
        'ranges': {'earth': (0.5, 0.7), 'water': (0.1, 0.3), 'fire': (0, 0.2), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '风之精魄': {
        'items': {'气流': 2, '火花': 1},
        'elements': {'air': 0.5, 'fire': 0.3, 'water': 0.1, 'earth': 0.1},
        'trait': 'freedom_breeze',
        'ranges': {'air': (0.4, 0.6), 'fire': (0.2, 0.4), 'water': (0, 0.2), 'earth': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '碧波灵液': {
        'items': {'水晶': 2, '泥浆': 1},
        'elements': {'water': 0.6, 'earth': 0.2, 'fire': 0.1, 'air': 0.1},
        'trait': 'empathic_tide',
        'ranges': {'water': (0.5, 0.7), 'earth': (0.1, 0.3), 'fire': (0, 0.2), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '炽焰核心': {
        'items': {'火焰': 2, '火花': 1},
        'elements': {'fire': 0.6, 'air': 0.2, 'water': 0.1, 'earth': 0.1},
        'trait': 'passionate_flare',
        'ranges': {'fire': (0.5, 0.7), 'air': (0.1, 0.3), 'water': (0, 0.2), 'earth': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '岩脉精华': {
        'items': {'矿石': 2, '火焰': 1},
        'elements': {'earth': 0.5, 'fire': 0.3, 'water': 0.1, 'air': 0.1},
        'trait': 'dutiful_rock',
        'ranges': {'earth': (0.4, 0.6), 'fire': (0.2, 0.4), 'water': (0, 0.2), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '星辉碎片': {
        'items': {'水晶': 1, '火花': 1, '气流': 1},
        'elements': {'water': 0.3, 'fire': 0.3, 'air': 0.3, 'earth': 0.1},
        'trait': 'creative_glow',
        'ranges': {'water': (0.2, 0.4), 'fire': (0.2, 0.4), 'air': (0.2, 0.4), 'earth': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '幽泉之息': {
        'items': {'泥浆': 2, '气流': 1},
        'elements': {'water': 0.4, 'earth': 0.3, 'air': 0.2, 'fire': 0.1},
        'trait': 'introspective_mist',
        'ranges': {'water': (0.3, 0.5), 'earth': (0.2, 0.4), 'air': (0.1, 0.3), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '熔岩晶核': {
        'items': {'火焰': 2, '矿石': 1},
        'elements': {'fire': 0.5, 'earth': 0.3, 'water': 0.1, 'air': 0.1},
        'trait': 'stable_heat',
        'ranges': {'fire': (0.4, 0.6), 'earth': (0.2, 0.4), 'water': (0, 0.2), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '雾隐精华': {
        'items': {'水晶': 2, '气流': 1},
        'elements': {'water': 0.5, 'air': 0.3, 'earth': 0.1, 'fire': 0.1},
        'trait': 'rational_mist',
        'ranges': {'water': (0.4, 0.6), 'air': (0.2, 0.4), 'earth': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '地焰之种': {
        'items': {'矿石': 1, '火焰': 1, '泥浆': 1},
        'elements': {'earth': 0.4, 'fire': 0.3, 'water': 0.2, 'air': 0.1},
        'trait': 'empathic_earth',
        'ranges': {'earth': (0.3, 0.5), 'fire': (0.2, 0.4), 'water': (0.1, 0.3), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '灵风结晶': {
        'items': {'火花': 2, '气流': 1},
        'elements': {'air': 0.4, 'fire': 0.3, 'water': 0.1, 'earth': 0.2},
        'trait': 'free_spirit',
        'ranges': {'air': (0.3, 0.5), 'fire': (0.2, 0.4), 'water': (0, 0.2), 'earth': (0.1, 0.3)},
        'item_type': 'intermediate'
    }
}

# MBTI 目标比例
mbti_targets = {
    'ISFJ': {'earth': 0.5, 'water': 0.4, 'fire': 0.05, 'air': 0.05},
    'ESFJ': {'water': 0.45, 'earth': 0.4, 'fire': 0.1, 'air': 0.05},
    'ISTJ': {'earth': 0.55, 'air': 0.3, 'water': 0.1, 'fire': 0.05},
    'ISFP': {'water': 0.4, 'earth': 0.35, 'air': 0.2, 'fire': 0.05},
    'ESTJ': {'earth': 0.4, 'air': 0.3, 'fire': 0.2, 'water': 0.1},
    'ESFP': {'water': 0.35, 'fire': 0.3, 'air': 0.25, 'earth': 0.1},
    'ENFP': {'fire': 0.4, 'water': 0.3, 'air': 0.2, 'earth': 0.1},
    'ISTP': {'air': 0.4, 'earth': 0.35, 'fire': 0.15, 'water': 0.1},
    'INFP': {'water': 0.45, 'fire': 0.25, 'air': 0.2, 'earth': 0.1},
    'ESTP': {'air': 0.35, 'fire': 0.3, 'earth': 0.25, 'water': 0.1},
    'INTP': {'air': 0.45, 'fire': 0.25, 'earth': 0.2, 'water': 0.1},
    'ENTP': {'fire': 0.35, 'air': 0.3, 'water': 0.2, 'earth': 0.15},
    'ENFJ': {'water': 0.4, 'fire': 0.3, 'earth': 0.15, 'air': 0.15},
    'INTJ': {'air': 0.4, 'fire': 0.25, 'water': 0.2, 'earth': 0.15},
    'ENTJ': {'fire': 0.4, 'air': 0.3, 'earth': 0.15, 'water': 0.15},
    'INFJ': {'water': 0.45, 'fire': 0.25, 'air': 0.2, 'earth': 0.1}
}

# 元素交互
interactions = {
    ('air', 'fire'): 0.1,
    ('water', 'fire'): -0.1
}