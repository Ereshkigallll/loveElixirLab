# ui/inventory.py
# 查看库存详情逻辑，三级物品橘色

import tkinter as tk
from data import item_entries


def view_inventory_details(app):
    """查看库存物品的元素比例和词条，区分初级/中级/三级颜色"""
    if not app.inventory:
        tk.messagebox.showinfo("库存详情", "库存为空！快去合成吧！")
        return

    details_window = tk.Toplevel(app.root)
    details_window.title("库存详情")
    details_window.geometry("600x300")

    text = tk.Text(details_window, height=10, width=70, font=("Arial", 12))
    text.pack(padx=10, pady=10)

    text.tag_configure("initial", foreground="#0000FF")
    text.tag_configure("intermediate", foreground="#800080")
    text.tag_configure("third", foreground="#FFA500")  # 三级物品：橘色

    item_indices = {}
    for i, item in enumerate(app.inventory, 1):
        name = item['name']
        index = item_indices.get(name, 0) + 1
        item_indices[name] = index
        elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
        entries = item.get('entries', [])
        entries_str = ", ".join(f"{e} ({item_entries[e]['description']})" for e in entries) if entries else "无词条"
        tag = item['item_type']
        text.insert(tk.END, f"物品{i} (", None)
        text.insert(tk.END, f"{name}{index}", tag)
        text.insert(tk.END, f"): {elements_str}，词条：{entries_str}\n", None)

    text.config(state='disabled')
    tk.Button(details_window, text="关闭", command=details_window.destroy, font=("Arial", 12)).pack(pady=5)

    app.result_text.delete(1.0, tk.END)
    app.result_text.insert(tk.END, "库存如墨，紫色高级物品尽显，查看详情吧！\n")