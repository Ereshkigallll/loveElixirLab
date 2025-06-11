# 通用合成逻辑：元素交互

from data import interactions
from utils import normalize_elements

def apply_interactions(elements):
    """元素交互：相生相克"""
    adjusted = elements.copy()
    for (elem1, elem2), effect in interactions.items():
        if adjusted.get(elem1, 0) > 0 and adjusted.get(elem2, 0) > 0:
            adjusted[elem2] *= (1 + effect)
    return normalize_elements(adjusted)