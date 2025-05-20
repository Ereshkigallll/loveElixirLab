# data.py
# 存储配方、权重、MBTI目标

# 默认权重（元素对MBTI属性的贡献）
default_weights = {
    'fire': {'E': 0.6, 'N': 0.3, 'F': 0.1},
    'water': {'F': 0.6, 'I': 0.3, 'N': 0.1},
    'earth': {'S': 0.6, 'J': 0.3, 'F': 0.1},
    'air': {'T': 0.6, 'P': 0.3, 'S': 0.1}
}

# 初级物品配方
initial_recipes = {
    'crystal': {'water': 3},  # 水晶：3水
    'flame': {'fire': 3}      # 火焰：3火
}

# 中级物品配方与元素比例
intermediate_recipes = {
    'deep_sea_heart': {
        'items': {'crystal': 2, 'flame': 1},
        'elements': {'water': 0.7, 'earth': 0.2, 'fire': 0.1},
        'trait': 'emotional_resonance'  # 加F+10%
    },
    'blazing_crystal': {
        'items': {'flame': 2, 'crystal': 1},
        'elements': {'fire': 0.6, 'water': 0.2, 'air': 0.2},
        'trait': 'intuitive_spark'      # 加N+10%
    }
}

# MBTI目标比例
mbti_targets = {
    'INFJ': {'water': 0.5, 'fire': 0.2, 'air': 0.2, 'earth': 0.1},
    'ENFP': {'fire': 0.5, 'water': 0.2, 'air': 0.2, 'earth': 0.1}
}

# 元素交互（相生相克）
interactions = {
    ('air', 'fire'): 0.1,   # 风助火：火+10%
    ('water', 'fire'): -0.1 # 水克火：火-10%
}