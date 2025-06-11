# ui/inputs.py
# 更新输入框和复选框逻辑，统一物品选择框，三级物品橘色

import tkinter as tk
from data import item_entries


def update_inputs(app, *args):
    """动态更新输入框和统一物品选择框，显示所有库存物品"""
    # 清空元素输入框（避免残留无效输入）
    for elem in app.element_inputs:
        app.element_inputs[elem].delete(0, tk.END)

    # 清理物品选择框
    for widget in app.item_selection_frame.winfo_children():
        widget.destroy()

    app.item_checkboxes = {}
    app.item_vars = {}

    # 统一物品选择框
    if not app.inventory:
        tk.Label(app.item_selection_frame, text="库存为空，请先获取元素或合成物品！", font=("Arial", 12), fg="red").pack(
            anchor='w')
    else:
        canvas = tk.Canvas(app.item_selection_frame)
        scrollbar = tk.Scrollbar(app.item_selection_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scrollable_frame, text="选择物品：", font=("Arial", 12)).pack(anchor='w')
        item_indices = {}
        for i, item in enumerate(app.inventory, 1):
            name = item['name']
            index = item_indices.get(name, 0) + 1
            item_indices[name] = index
            elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
            entries = item.get('entries', [])
            entries_str = ", ".join(f"{e} ({item_entries[e]['description']})" for e in entries) if entries else "无词条"
            label = f"{name}{index}: {elements_str}，词条：{entries_str}"
            var = tk.BooleanVar()
            app.item_vars[id(item)] = var
            color = "#0000FF" if item['item_type'] == 'initial' else "#FFA500" if item[
                                                                                      'item_type'] == 'third' else "#800080"
            app.item_checkboxes[id(item)] = tk.Checkbutton(
                scrollable_frame,
                text=label,
                variable=var,
                font=("Arial", 10),
                foreground=color
            )
            app.item_checkboxes[id(item)].pack(anchor='w')

    app.root.update()
    app.root.update_idletasks()