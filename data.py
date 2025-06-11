# data.py
# 存储配方、权重、MBTI目标，新增中级配方、削弱属性、item_type，物品名称为中文，MBTI比例为范围，新增词条属性，更新一级物品比例

import random

# 默认权重：定义元素到 MBTI 属性的映射，用于情感属性（traits）分配
default_weights = {
    'water': {'F': 0.55, 'I': 0.25, 'N': 0.15, 'J': 0.05},
    'fire': {'E': 0.55, 'S': 0.25, 'N': 0.15, 'T': 0.05},
    'earth': {'S': 0.55, 'J': 0.25, 'F': 0.15, 'I': 0.05},
    'air': {'T': 0.55, 'P': 0.25, 'S': 0.15, 'N': 0.05}
}

# 一级物品（初级物品）
initial_items = {
    # 风系新物品
    '风茧丝': {
        'main': ['air'],
        'ranges': {'air': (0.75, 0.85), 'water': (0.1, 0.2), 'earth': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '干桑片': {
        'main': ['air', 'earth'],
        'ranges': {'air': (0.7, 0.8), 'earth': (0.15, 0.25), 'water': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '晨风露水': {
        'main': ['air', 'water'],
        'ranges': {'air': (0.65, 0.75), 'water': (0.2, 0.3), 'earth': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '风信子叶': {
        'main': ['air', 'water'],
        'ranges': {'air': (0.7, 0.8), 'water': (0.15, 0.25), 'earth': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '空石屑': {
        'main': ['air', 'earth'],
        'ranges': {'air': (0.65, 0.75), 'earth': (0.2, 0.3), 'water': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '鸣砂粒': {
        'main': ['air', 'earth'],
        'ranges': {'air': (0.7, 0.8), 'earth': (0.15, 0.25), 'water': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '螺纹叶片': {
        'main': ['air', 'water'],
        'ranges': {'air': (0.75, 0.85), 'water': (0.1, 0.2), 'earth': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '风引茎': {
        'main': ['air'],
        'ranges': {'air': (0.8, 0.9), 'water': (0.05, 0.15), 'earth': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    # 火系新物品
    '赤果皮': {
        'main': ['fire', 'earth'],
        'ranges': {'fire': (0.7, 0.8), 'earth': (0.15, 0.25), 'water': (0, 0.1), 'air': (0, 0.1)},
        'item_type': 'initial'
    },
    '焰藤须': {
        'main': ['fire', 'air'],
        'ranges': {'fire': (0.75, 0.85), 'air': (0.1, 0.2), 'water': (0, 0.1), 'earth': (0, 0.1)},
        'item_type': 'initial'
    },
    '火山碎晶': {
        'main': ['fire', 'earth'],
        'ranges': {'fire': (0.65, 0.75), 'earth': (0.2, 0.3), 'water': (0, 0.1), 'air': (0, 0.1)},
        'item_type': 'initial'
    },
    '熔岩砂': {
        'main': ['fire', 'earth'],
        'ranges': {'fire': (0.7, 0.8), 'earth': (0.15, 0.25), 'water': (0, 0.1), 'air': (0, 0.1)},
        'item_type': 'initial'
    },
    '火狐绒毛': {
        'main': ['fire', 'air'],
        'ranges': {'fire': (0.7, 0.8), 'air': (0.15, 0.25), 'water': (0, 0.1), 'earth': (0, 0.1)},
        'item_type': 'initial'
    },
    '狐焰脂': {
        'main': ['fire', 'water'],
        'ranges': {'fire': (0.75, 0.85), 'water': (0.1, 0.2), 'earth': (0, 0.1), 'air': (0, 0.1)},
        'item_type': 'initial'
    },
    '泉香片': {
        'main': ['fire', 'water'],
        'ranges': {'fire': (0.65, 0.75), 'water': (0.2, 0.3), 'earth': (0, 0.1), 'air': (0, 0.1)},
        'item_type': 'initial'
    },
    '温石露': {
        'main': ['fire', 'water'],
        'ranges': {'fire': (0.65, 0.75), 'water': (0.2, 0.3), 'earth': (0, 0.1), 'air': (0, 0.1)},
        'item_type': 'initial'
    },
    # 水系新物品
    '露心液': {
        'main': ['water', 'air'],
        'ranges': {'water': (0.75, 0.85), 'air': (0.1, 0.2), 'earth': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '雾瓣片': {
        'main': ['water', 'air'],
        'ranges': {'water': (0.7, 0.8), 'air': (0.15, 0.25), 'earth': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '潮音砂': {
        'main': ['water', 'earth'],
        'ranges': {'water': (0.7, 0.8), 'earth': (0.15, 0.25), 'air': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '旧贝母片': {
        'main': ['water', 'earth'],
        'ranges': {'water': (0.65, 0.75), 'earth': (0.2, 0.3), 'air': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '洗银水': {
        'main': ['water'],
        'ranges': {'water': (0.8, 0.9), 'air': (0.05, 0.15), 'earth': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '镜心银屑': {
        'main': ['water', 'earth'],
        'ranges': {'water': (0.65, 0.75), 'earth': (0.2, 0.3), 'air': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '龙鳞末': {
        'main': ['water', 'earth'],
        'ranges': {'water': (0.7, 0.8), 'earth': (0.15, 0.25), 'air': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '骨水渍': {
        'main': ['water', 'fire'],
        'ranges': {'water': (0.75, 0.85), 'fire': (0.1, 0.2), 'earth': (0, 0.1), 'air': (0, 0.1)},
        'item_type': 'initial'
    },
    # 土系新物品
    '眠砂粒': {
        'main': ['earth', 'air'],
        'ranges': {'earth': (0.7, 0.8), 'air': (0.15, 0.25), 'water': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '岩皮粉': {
        'main': ['earth', 'water'],
        'ranges': {'earth': (0.75, 0.85), 'water': (0.1, 0.2), 'air': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '古蕨叶脉': {
        'main': ['earth', 'water'],
        'ranges': {'earth': (0.65, 0.75), 'water': (0.2, 0.3), 'air': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '土香粉': {
        'main': ['earth', 'fire'],
        'ranges': {'earth': (0.7, 0.8), 'fire': (0.15, 0.25), 'water': (0, 0.1), 'air': (0, 0.1)},
        'item_type': 'initial'
    },
    '铜绿皮': {
        'main': ['earth', 'water'],
        'ranges': {'earth': (0.75, 0.85), 'water': (0.1, 0.2), 'air': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '星纹芯': {
        'main': ['earth', 'fire'],
        'ranges': {'earth': (0.8, 0.9), 'fire': (0.05, 0.15), 'water': (0, 0.1), 'air': (0, 0.1)},
        'item_type': 'initial'
    },
    '墨泥屑': {
        'main': ['earth', 'water'],
        'ranges': {'earth': (0.7, 0.8), 'water': (0.15, 0.25), 'air': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    },
    '蓝树根': {
        'main': ['earth', 'water'],
        'ranges': {'earth': (0.65, 0.75), 'water': (0.2, 0.3), 'air': (0, 0.1), 'fire': (0, 0.1)},
        'item_type': 'initial'
    }
}

# 词条定义（entries）：影响合成机制，如元素占比、副产物概率
item_entries = {
    '水元素增幅': {
        'elements': ['water'],
        'weight': 0.8,
        'effect': {'water': 0.10},
        'description': '下次合成水元素比例 +10%',
    },
    '火元素增幅': {
        'elements': ['fire'],
        'weight': 0.8,
        'effect': {'fire': 0.10},
        'description': '下次合成火元素比例 +10%',
    },
    '土元素增幅': {
        'elements': ['earth'],
        'weight': 0.8,
        'effect': {'earth': 0.10},
        'description': '下次合成土元素比例 +10%',
    },
    '风元素增幅': {
        'elements': ['air'],
        'weight': 0.8,
        'effect': {'air': 0.10},
        'description': '下次合成风元素比例 +10%',
    },
    '副产物增益': {
        'elements': ['water', 'fire', 'earth', 'air'],
        'weight': 0.4,
        'effect': {'byproduct': 0.20},
        'description': '下次合成副产物概率 +20%',
    },
    '水元素节约': {
        'elements': ['water'],
        'weight': 0.6,
        'effect': {'water_save': 0.10},
        'description': '下次合成水元素消耗 -10%',
    },
    '火元素节约': {
        'elements': ['fire'],
        'weight': 0.6,
        'effect': {'fire_save': 0.10},
        'description': '下次合成火元素消耗 -10%',
    },
    '土元素节约': {
        'elements': ['earth'],
        'weight': 0.6,
        'effect': {'earth_save': 0.10},
        'description': '下次合成土元素消耗 -10%',
    },
    '风元素节约': {
        'elements': ['air'],
        'weight': 0.6,
        'effect': {'air_save': 0.10},
        'description': '下次合成风元素消耗 -10%',
    }
}

# 中级物品配方（15种）
# 中级物品配方（二级物品）
intermediate_recipes = {
    # 风系
    '风茧纸': {
        'elements': {'air': 0.6, 'earth': 0.2, 'water': 0.1, 'fire': 0.1},
        'ranges': {'air': (0.5, 0.7), 'earth': (0.1, 0.3), 'water': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '羽叶香': {
        'elements': {'air': 0.5, 'water': 0.3, 'earth': 0.1, 'fire': 0.1},
        'ranges': {'air': (0.4, 0.6), 'water': (0.2, 0.4), 'earth': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '风琴石': {
        'elements': {'air': 0.5, 'earth': 0.3, 'water': 0.1, 'fire': 0.1},
        'ranges': {'air': (0.4, 0.6), 'earth': (0.2, 0.4), 'water': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '螺羽风叶': {
        'elements': {'air': 0.6, 'water': 0.2, 'earth': 0.1, 'fire': 0.1},
        'ranges': {'air': (0.5, 0.7), 'water': (0.1, 0.3), 'earth': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '银耳蘑孢': {
        'elements': {'air': 0.5, 'water': 0.2, 'earth': 0.2, 'fire': 0.1},
        'ranges': {'air': (0.4, 0.6), 'water': (0.1, 0.3), 'earth': (0.1, 0.3), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '云青矿': {
        'elements': {'air': 0.5, 'earth': 0.3, 'water': 0.1, 'fire': 0.1},
        'ranges': {'air': (0.4, 0.6), 'earth': (0.2, 0.4), 'water': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    # 火系
    '赤焰果': {
        'elements': {'fire': 0.6, 'earth': 0.2, 'water': 0.1, 'air': 0.1},
        'ranges': {'fire': (0.5, 0.7), 'earth': (0.1, 0.3), 'water': (0, 0.2), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '灰烬琉璃': {
        'elements': {'fire': 0.5, 'earth': 0.3, 'water': 0.1, 'air': 0.1},
        'ranges': {'fire': (0.4, 0.6), 'earth': (0.2, 0.4), 'water': (0, 0.2), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '星火绒': {
        'elements': {'fire': 0.5, 'air': 0.3, 'water': 0.1, 'earth': 0.1},
        'ranges': {'fire': (0.4, 0.6), 'air': (0.2, 0.4), 'water': (0, 0.2), 'earth': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '温泉叶': {
        'elements': {'fire': 0.5, 'water': 0.3, 'earth': 0.1, 'air': 0.1},
        'ranges': {'fire': (0.4, 0.6), 'water': (0.2, 0.4), 'earth': (0, 0.2), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '火霞绫': {
        'elements': {'fire': 0.6, 'water': 0.2, 'air': 0.1, 'earth': 0.1},
        'ranges': {'fire': (0.5, 0.7), 'water': (0.1, 0.3), 'air': (0, 0.2), 'earth': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '焰尾蠊': {
        'elements': {'fire': 0.5, 'earth': 0.2, 'air': 0.2, 'water': 0.1},
        'ranges': {'fire': (0.4, 0.6), 'earth': (0.1, 0.3), 'air': (0.1, 0.3), 'water': (0, 0.2)},
        'item_type': 'intermediate'
    },
    # 水系
    '蓝滴花': {
        'elements': {'water': 0.6, 'air': 0.2, 'earth': 0.1, 'fire': 0.1},
        'ranges': {'water': (0.5, 0.7), 'air': (0.1, 0.3), 'earth': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '潮声贝': {
        'elements': {'water': 0.5, 'earth': 0.3, 'air': 0.1, 'fire': 0.1},
        'ranges': {'water': (0.4, 0.6), 'earth': (0.2, 0.4), 'air': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '月水镜': {
        'elements': {'water': 0.5, 'earth': 0.2, 'air': 0.2, 'fire': 0.1},
        'ranges': {'water': (0.4, 0.6), 'earth': (0.1, 0.3), 'air': (0.1, 0.3), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '沉水龙鳞': {
        'elements': {'water': 0.5, 'earth': 0.2, 'fire': 0.2, 'air': 0.1},
        'ranges': {'water': (0.4, 0.6), 'earth': (0.1, 0.3), 'fire': (0.1, 0.3), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '潋青苔': {
        'elements': {'water': 0.5, 'earth': 0.2, 'air': 0.2, 'fire': 0.1},
        'ranges': {'water': (0.4, 0.6), 'earth': (0.1, 0.3), 'air': (0.1, 0.3), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '澄灵蜓': {
        'elements': {'water': 0.6, 'air': 0.2, 'earth': 0.1, 'fire': 0.1},
        'ranges': {'water': (0.5, 0.7), 'air': (0.1, 0.3), 'earth': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    # 土系
    '眠砂石': {
        'elements': {'earth': 0.6, 'air': 0.2, 'water': 0.1, 'fire': 0.1},
        'ranges': {'earth': (0.5, 0.7), 'air': (0.1, 0.3), 'water': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '蕨影纸': {
        'elements': {'earth': 0.5, 'water': 0.2, 'fire': 0.2, 'air': 0.1},
        'ranges': {'earth': (0.4, 0.6), 'water': (0.1, 0.3), 'fire': (0.1, 0.3), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '苔纹矿': {
        'elements': {'earth': 0.5, 'water': 0.3, 'air': 0.1, 'fire': 0.1},
        'ranges': {'earth': (0.4, 0.6), 'water': (0.2, 0.4), 'air': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '铜骨枝': {
        'elements': {'earth': 0.5, 'fire': 0.2, 'water': 0.2, 'air': 0.1},
        'ranges': {'earth': (0.4, 0.6), 'fire': (0.1, 0.3), 'water': (0.1, 0.3), 'air': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '墨根石': {
        'elements': {'earth': 0.5, 'water': 0.3, 'air': 0.1, 'fire': 0.1},
        'ranges': {'earth': (0.4, 0.6), 'water': (0.2, 0.4), 'air': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'intermediate'
    },
    '伏地蜚': {
        'elements': {'earth': 0.5, 'air': 0.2, 'fire': 0.2, 'water': 0.1},
        'ranges': {'earth': (0.4, 0.6), 'air': (0.1, 0.3), 'fire': (0.1, 0.3), 'water': (0, 0.2)},
        'item_type': 'intermediate'
    }
}

# 三级物品配方（由二级物品合成，用于 MBTI 合成）
third = {
    # 风系
    '风焰颂笛': {
        'elements': {'air': 0.5, 'fire': 0.3, 'water': 0.1, 'earth': 0.1},
        'ranges': {'air': (0.4, 0.6), 'fire': (0.2, 0.4), 'water': (0, 0.2), 'earth': (0, 0.2)},
        'item_type': 'third'
    },
    '飞信': {
        'elements': {'air': 0.5, 'water': 0.2, 'earth': 0.2, 'fire': 0.1},
        'ranges': {'air': (0.4, 0.6), 'water': (0.1, 0.3), 'earth': (0.1, 0.3), 'fire': (0, 0.2)},
        'item_type': 'third'
    },
    '螺簧录音片': {
        'elements': {'air': 0.4, 'earth': 0.3, 'water': 0.2, 'fire': 0.1},
        'ranges': {'air': (0.3, 0.5), 'earth': (0.2, 0.4), 'water': (0.1, 0.3), 'fire': (0, 0.2)},
        'item_type': 'third'
    },
    '灵岚结晶': {
        'elements': {'air': 0.5, 'earth': 0.2, 'water': 0.2, 'fire': 0.1},
        'ranges': {'air': (0.4, 0.6), 'earth': (0.1, 0.3), 'water': (0.1, 0.3), 'fire': (0, 0.2)},
        'item_type': 'third'
    },
    # 火系
    '烬露珠': {
        'elements': {'fire': 0.5, 'water': 0.2, 'earth': 0.2, 'air': 0.1},
        'ranges': {'fire': (0.4, 0.6), 'water': (0.1, 0.3), 'earth': (0.1, 0.3), 'air': (0, 0.2)},
        'item_type': 'third'
    },
    '炽羽砂钟': {
        'elements': {'fire': 0.4, 'air': 0.3, 'earth': 0.2, 'water': 0.1},
        'ranges': {'fire': (0.3, 0.5), 'air': (0.2, 0.4), 'earth': (0.1, 0.3), 'water': (0, 0.2)},
        'item_type': 'third'
    },
    '眠梦热砂枕': {
        'elements': {'fire': 0.4, 'earth': 0.3, 'air': 0.2, 'water': 0.1},
        'ranges': {'fire': (0.3, 0.5), 'earth': (0.2, 0.4), 'air': (0.1, 0.3), 'water': (0, 0.2)},
        'item_type': 'third'
    },
    '焰息披帛': {
        'elements': {'fire': 0.5, 'water': 0.2, 'air': 0.2, 'earth': 0.1},
        'ranges': {'fire': (0.4, 0.6), 'water': (0.1, 0.3), 'air': (0.1, 0.3), 'earth': (0, 0.2)},
        'item_type': 'third'
    },
    # 水系
    '晨雾诗笺': {
        'elements': {'water': 0.5, 'air': 0.3, 'earth': 0.1, 'fire': 0.1},
        'ranges': {'water': (0.4, 0.6), 'air': (0.2, 0.4), 'earth': (0, 0.2), 'fire': (0, 0.2)},
        'item_type': 'third'
    },
    '泪花幻镜': {
        'elements': {'water': 0.4, 'fire': 0.3, 'earth': 0.2, 'air': 0.1},
        'ranges': {'water': (0.3, 0.5), 'fire': (0.2, 0.4), 'earth': (0.1, 0.3), 'air': (0, 0.2)},
        'item_type': 'third'
    },
    '信歌风铃': {
        'elements': {'water': 0.5, 'air': 0.2, 'earth': 0.2, 'fire': 0.1},
        'ranges': {'water': (0.4, 0.6), 'air': (0.1, 0.3), 'earth': (0.1, 0.3), 'fire': (0, 0.2)},
        'item_type': 'third'
    },
    '梦睡莲': {
        'elements': {'water': 0.5, 'air': 0.2, 'earth': 0.2, 'fire': 0.1},
        'ranges': {'water': (0.4, 0.6), 'air': (0.1, 0.3), 'earth': (0.1, 0.3), 'fire': (0, 0.2)},
        'item_type': 'third'
    },
    # 土系
    '云岩灯': {
        'elements': {'earth': 0.5, 'air': 0.2, 'water': 0.2, 'fire': 0.1},
        'ranges': {'earth': (0.4, 0.6), 'air': (0.1, 0.3), 'water': (0.1, 0.3), 'fire': (0, 0.2)},
        'item_type': 'third'
    },
    '迷途引针': {
        'elements': {'earth': 0.4, 'air': 0.3, 'fire': 0.2, 'water': 0.1},
        'ranges': {'earth': (0.3, 0.5), 'air': (0.2, 0.4), 'fire': (0.1, 0.3), 'water': (0, 0.2)},
        'item_type': 'third'
    },
    '炉眠香': {
        'elements': {'earth': 0.5, 'fire': 0.3, 'water': 0.1, 'air': 0.1},
        'ranges': {'earth': (0.4, 0.6), 'fire': (0.2, 0.4), 'water': (0, 0.2), 'air': (0, 0.2)},
        'item_type': 'third'
    },
    '地纹巡记石': {
        'elements': {'earth': 0.5, 'water': 0.2, 'air': 0.2, 'fire': 0.1},
        'ranges': {'earth': (0.4, 0.6), 'water': (0.1, 0.3), 'air': (0.1, 0.3), 'fire': (0, 0.2)},
        'item_type': 'third'
    }
}

# MBTI 目标比例范围
mbti_targets = {
    'ISFJ': {
        'ranges': {
            'earth': (0.40, 0.60),
            'water': (0.30, 0.50),
            'fire': (0.0, 0.20),
            'air': (0.0, 0.20)
        }
    },
    'ESFJ': {
        'ranges': {
            'water': (0.35, 0.55),
            'earth': (0.30, 0.50),
            'fire': (0.05, 0.25),
            'air': (0.0, 0.20)
        }
    },
    'ISTJ': {
        'ranges': {
            'earth': (0.45, 0.65),
            'air': (0.20, 0.40),
            'water': (0.0, 0.20),
            'fire': (0.0, 0.20)
        }
    },
    'ISFP': {
        'ranges': {
            'water': (0.30, 0.50),
            'earth': (0.25, 0.45),
            'air': (0.10, 0.30),
            'fire': (0.0, 0.20)
        }
    },
    'ESTJ': {
        'ranges': {
            'earth': (0.30, 0.50),
            'air': (0.25, 0.45),
            'fire': (0.10, 0.30),
            'water': (0.0, 0.20)
        }
    },
    'ESFP': {
        'ranges': {
            'fire': (0.25, 0.45),
            'water': (0.25, 0.45),
            'air': (0.15, 0.35),
            'earth': (0.0, 0.20)
        }
    },
    'ENFP': {
        'ranges': {
            'fire': (0.30, 0.50),
            'water': (0.20, 0.40),
            'air': (0.15, 0.35),
            'earth': (0.0, 0.20)
        }
    },
    'ISTP': {
        'ranges': {
            'air': (0.30, 0.50),
            'earth': (0.25, 0.45),
            'fire': (0.10, 0.30),
            'water': (0.0, 0.20)
        }
    },
    'INFP': {
        'ranges': {
            'water': (0.35, 0.55),
            'air': (0.20, 0.40),
            'fire': (0.15, 0.35),
            'earth': (0.0, 0.20)
        }
    },
    'ESTP': {
        'ranges': {
            'air': (0.25, 0.45),
            'fire': (0.20, 0.40),
            'earth': (0.15, 0.35),
            'water': (0.0, 0.20)
        }
    },
    'INTP': {
        'ranges': {
            'air': (0.35, 0.55),
            'fire': (0.15, 0.35),
            'earth': (0.10, 0.30),
            'water': (0.0, 0.20)
        }
    },
    'ENTP': {
        'ranges': {
            'fire': (0.25, 0.45),
            'air': (0.20, 0.40),
            'water': (0.10, 0.30),
            'earth': (0.05, 0.25)
        }
    },
    'ENFJ': {
        'ranges': {
            'water': (0.30, 0.50),
            'fire': (0.20, 0.40),
            'earth': (0.10, 0.30),
            'air': (0.10, 0.30)
        }
    },
    'INTJ': {
        'ranges': {
            'air': (0.30, 0.50),
            'fire': (0.15, 0.35),
            'water': (0.10, 0.30),
            'earth': (0.05, 0.25)
        }
    },
    'ENTJ': {
        'ranges': {
            'fire': (0.30, 0.50),
            'air': (0.20, 0.40),
            'earth': (0.10, 0.30),
            'water': (0.05, 0.25)
        }
    },
    'INFJ': {
        'ranges': {
            'water': (0.35, 0.55),
            'fire': (0.20, 0.40),
            'air': (0.10, 0.30),
            'earth': (0.0, 0.20)
        }
    }
}

# 元素交互
interactions = {
    ('air', 'fire'): 0.1,
    ('water', 'fire'): -0.1
}

easter_eggs = [
    {'name': '彩蛋A', 'item_type': 'initial'},
    {'name': '彩蛋B', 'item_type': 'initial'},
    {'name': '彩蛋C', 'item_type': 'intermediate'},
    {'name': '彩蛋D', 'item_type': 'intermediate'},
    {'name': '彩蛋E', 'item_type': 'third'},
    {'name': '彩蛋F', 'item_type': 'third'}
]