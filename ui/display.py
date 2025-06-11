# ui/display.py
# 更新显示逻辑，适应统一物品选择框，三级物品橘色

import tkinter as tk


def update_display(app):
    """更新元素和物品库存显示，区分初级/中级/三级颜色"""
    elements_str = "元素库存：" + ", ".join(f"{k}: {v}" for k, v in app.elements.items())
    app.elements_label.config(text=elements_str)

    for widget in app.inventory_frame.winfo_children():
        widget.destroy()

    item_counts = {'initial': {}, 'intermediate': {}, 'third': {}}
    for item in app.inventory:
        item_type = item['item_type']
        name = item['name']
        item_counts[item_type][name] = item_counts[item_type].get(name, 0) + 1

    if item_counts['initial']:
        initial_str = ", ".join(f"{k}: {v}" for k, v in item_counts['initial'].items())
        tk.Label(app.inventory_frame, text=f"初级库存：{initial_str}", font=("Arial", 12), fg="#0000FF").pack(anchor='w')
    if item_counts['intermediate']:
        intermediate_str = ", ".join(f"{k}: {v}" for k, v in item_counts['intermediate'].items())
        tk.Label(app.inventory_frame, text=f"中级库存：{intermediate_str}", font=("Arial", 12), fg="#800080").pack(
            anchor='w')
    if item_counts['third']:
        third_str = ", ".join(f"{k}: {v}" for k, v in item_counts['third'].items())
        tk.Label(app.inventory_frame, text=f"三级库存：{third_str}", font=("Arial", 12), fg="#FFA500").pack(anchor='w')
    if not any(item_counts.values()):
        tk.Label(app.inventory_frame, text="物品库存：空", font=("Arial", 12)).pack(anchor='w')