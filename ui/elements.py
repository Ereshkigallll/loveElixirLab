# ui/elements.py
# 获取元素逻辑

import random
from database import save_to_db
import tkinter as tk

def add_elements(app):
    """模拟获取元素，反映现实分布"""
    rewards = {
        'earth': random.randint(5, 7),
        'water': random.randint(4, 6),
        'fire': random.randint(2, 4),
        'air': random.randint(2, 3)
    }
    for elem, amount in rewards.items():
        app.elements[elem] = app.elements.get(elem, 0) + amount
    app.result_text.delete(1.0, tk.END)
    app.result_text.insert(tk.END, f"获取元素：{rewards}\n")
    app.update_display()  # 调用绑定到实例的 update_display
    save_to_db(app.elements, app.inventory, app.mbti_history)
    app.result_text.insert(tk.END, "数据已保存！\n")