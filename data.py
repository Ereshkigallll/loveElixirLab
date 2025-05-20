# data.py
# 存储配方、权重、MBTI目标，添加初级物品范围

import random

# 默认权重
default_weights = {
    'fire': {'E': 0.55, 'S': 0.25, 'N': 0.15, 'T': 0.05},
    'water': {'F': 0.55, 'I': 0.25, 'N': 0.15, 'J': 0.05},
    'earth': {'S': 0.55, 'J': 0.25, 'F': 0.15, 'I': 0.05},
    'air': {'T': 0.55, 'P': 0.25, 'S': 0.15, 'N': 0.05}
}

# 初级物品范围
initial_items = {
    'crystal': {'main': ['water'], 'ranges': {'water': (0.7, 0.9), 'fire': (0, 0.3), 'earth': (0, 0.3), 'air': (0, 0.3)}},
    'flame': {'main': ['fire'], 'ranges': {'fire': (0.7, 0.9), 'water': (0, 0.3), 'earth': (0, 0.3), 'air': (0, 0.3)}},
    'mud': {'main': ['earth', 'water'], 'ranges': {'earth': (0.4, 0.6), 'water': (0.3, 0.5), 'fire': (0, 0.2), 'air': (0, 0.2)}},
    'gust': {'main': ['air'], 'ranges': {'air': (0.7, 0.9), 'water': (0, 0.3), 'fire': (0, 0.3), 'earth': (0, 0.3)}},
    'ore': {'main': ['earth'], 'ranges': {'earth': (0.7, 0.9), 'water': (0, 0.3), 'fire': (0, 0.3), 'air': (0, 0.3)}},
    'spark': {'main': ['fire', 'air'], 'ranges': {'fire': (0.4, 0.6), 'air': (0.3, 0.5), 'water': (0, 0.2), 'earth': (0, 0.2)}}
}

# 中级物品配方
intermediate_recipes = {
    'deep_sea_heart': {
        'items': {'crystal': 2, 'flame': 1},
        'elements': {'water': 0.7, 'earth': 0.2, 'fire': 0.1},
        'trait': 'emotional_resonance'
    },
    'blazing_crystal': {
        'items': {'flame': 2, 'crystal': 1},
        'elements': {'fire': 0.6, 'water': 0.2, 'air': 0.2},
        'trait': 'intuitive_spark'
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