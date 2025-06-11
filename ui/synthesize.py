# ui/synthesize.py
# 合成处理逻辑，自动判断合成类型，允许同种元素合成，三级物品橘色，MBTI绿色，恢复固定比例失败机制，简化失败提示

import tkinter as tk
from tkinter import messagebox
from synthesis import synthesize_initial, synthesize_intermediate, synthesize_third, synthesize_mbti
from data import item_entries
from database import save_to_db


def synthesize(app):
    """执行合成，自动判断合成类型，允许同种元素合成"""
    app.result_text.delete(1.0, tk.END)

    # 获取元素输入
    input_elements = {}
    for elem in app.element_inputs:
        try:
            value = float(app.element_inputs[elem].get() or 0)
            if value < 0 or value > app.elements.get(elem, 0):
                tk.messagebox.showerror("错误", f"{elem}数量无效！")
                return
            input_elements[elem] = value
        except ValueError:
            tk.messagebox.showerror("错误", f"请输入有效的{elem}数量！")
            return

    # 获取物品输入，确保从 app.inventory 引用
    selected_items = []
    selected_entries = []
    for item_id, var in app.item_vars.items():
        if var.get():
            for item in app.inventory:
                if id(item) == item_id:
                    selected_items.append(item)
                    selected_entries.extend(item.get('entries', []))
                    break

    # 检查输入有效性
    total_input_elements = sum(input_elements.values())
    if total_input_elements == 0 and not selected_items:
        tk.messagebox.showerror("错误", "请至少输入一种元素或选择一个物品！")
        return

    # 自动判断合成类型
    if total_input_elements > 0:
        # 初级合成：有元素输入
        if total_input_elements + len(selected_items) < 2:
            tk.messagebox.showerror("合成错误", "初级合成需至少两个元素或一个元素加一个物品！")
            return
        if any(item['item_type'] != 'initial' for item in selected_items):
            tk.messagebox.showerror("合成错误", "初级合成仅限初级物品！")
            return

        result, new_elements, returned_items, easter_egg, msg = synthesize_initial(app.elements, input_elements,
                                                                                   selected_items)
        if result:
            app.elements = new_elements
            app.inventory = [item for item in app.inventory if item not in selected_items]
            app.inventory.append(result)
            if easter_egg:
                app.inventory.append(easter_egg)
                app.result_text.insert(tk.END, f"意外之喜，获得彩蛋：", None)
                app.result_text.insert(tk.END, f"{easter_egg['name']}", easter_egg['item_type'])
                app.result_text.insert(tk.END, "\n", None)
            elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in result['elements'].items())
            entries = result.get('entries', [])
            entries_str = ", ".join(f"{e} ({item_entries[e]['description']})" for e in entries) if entries else "无词条"
            app.result_text.insert(tk.END, f"{msg}\n", None)
            app.result_text.insert(tk.END, f"元素组成：{elements_str}\n词条：{entries_str}\n", None)
            app.result_text.insert(tk.END, f"获得：", None)
            app.result_text.insert(tk.END, f"{result['name']}", "initial")
            app.result_text.insert(tk.END, "\n", None)
        else:
            app.elements = new_elements
            for item in returned_items:
                app.inventory.append(item)
            if easter_egg:
                app.inventory.append(easter_egg)
                app.result_text.insert(tk.END, f"意外之喜，获得彩蛋：", None)
                app.result_text.insert(tk.END, f"{easter_egg['name']}", easter_egg['item_type'])
                app.result_text.insert(tk.END, "\n", None)
            if returned_items:
                returned_str = ", ".join(item['name'] for item in returned_items)
                app.result_text.insert(tk.END, f"返还物品：{returned_str}\n", None)
            elif any(v > 0 for v in input_elements.values()):
                returned_elem = ", ".join(
                    f"{k}: {app.elements[k] - app.elements.get(k, 0)}" for k, v in input_elements.items() if
                    app.elements[k] > app.elements.get(k, 0))
                if returned_elem:
                    app.result_text.insert(tk.END, f"返还元素：{returned_elem}\n", None)
            app.result_text.insert(tk.END, f"{msg}\n", "error")
        save_to_db(app.elements, app.inventory, app.mbti_history)
        app.result_text.insert(tk.END, "数据已保存！\n")

    else:
        # 无元素输入，根据物品类型判断
        if len(selected_items) < 2:
            tk.messagebox.showerror("合成错误", "合成需至少选择两个物品！")
            return

        item_types = {item['item_type'] for item in selected_items}

        if item_types == {'intermediate'}:
            # 三级合成：仅中级物品
            result, new_inventory, returned_items, easter_egg, msg = synthesize_third(app.inventory, selected_items)
            if result:
                app.inventory = new_inventory
                app.inventory.append(result)
                if easter_egg:
                    app.inventory.append(easter_egg)
                    app.result_text.insert(tk.END, f"意外之喜，获得彩蛋：", None)
                    app.result_text.insert(tk.END, f"{easter_egg['name']}", easter_egg['item_type'])
                    app.result_text.insert(tk.END, "\n", None)
                elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in result['elements'].items())
                entries = result.get('entries', [])
                entries_str = ", ".join(
                    f"{e} ({item_entries[e]['description']})" for e in entries) if entries else "无词条"
                app.result_text.insert(tk.END, f"{msg}\n", None)
                app.result_text.insert(tk.END, f"元素组成：{elements_str}\n词条：{entries_str}\n", None)
                app.result_text.insert(tk.END, f"获得：", None)
                app.result_text.insert(tk.END, f"{result['name']}", "third")
                app.result_text.insert(tk.END, "\n", None)
            else:
                app.inventory = new_inventory
                for item in returned_items:
                    app.inventory.append(item)
                if easter_egg:
                    app.inventory.append(easter_egg)
                    app.result_text.insert(tk.END, f"意外之喜，获得彩蛋：", None)
                    app.result_text.insert(tk.END, f"{easter_egg['name']}", easter_egg['item_type'])
                    app.result_text.insert(tk.END, "\n", None)
                if returned_items:
                    returned_str = ", ".join(item['name'] for item in returned_items)
                    app.result_text.insert(tk.END, f"返还物品：{returned_str}\n", None)
                app.result_text.insert(tk.END, f"{msg}\n", "error")
            save_to_db(app.elements, app.inventory, app.mbti_history)
            app.result_text.insert(tk.END, "数据已保存！\n")

        elif 'initial' in item_types and item_types.issubset({'initial', 'intermediate'}):
            # 中级合成：包含初级物品
            if 'third' in item_types:
                tk.messagebox.showerror("合成错误", "中级合成不可使用三级物品！")
                return
            result, new_inventory, returned_items, easter_egg, msg = synthesize_intermediate(app.inventory,
                                                                                             selected_items)
            if result:
                app.inventory = new_inventory
                app.inventory.append(result)
                if easter_egg:
                    app.inventory.append(easter_egg)
                    app.result_text.insert(tk.END, f"意外之喜，获得彩蛋：", None)
                    app.result_text.insert(tk.END, f"{easter_egg['name']}", easter_egg['item_type'])
                    app.result_text.insert(tk.END, "\n", None)
                elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in result['elements'].items())
                entries = result.get('entries', [])
                entries_str = ", ".join(
                    f"{e} ({item_entries[e]['description']})" for e in entries) if entries else "无词条"
                app.result_text.insert(tk.END, f"{msg}\n", None)
                app.result_text.insert(tk.END, f"元素组成：{elements_str}\n词条：{entries_str}\n", None)
                app.result_text.insert(tk.END, f"获得：", None)
                app.result_text.insert(tk.END, f"{result['name']}", "intermediate")
                app.result_text.insert(tk.END, "\n", None)
            else:
                app.inventory = new_inventory
                for item in returned_items:
                    app.inventory.append(item)
                if easter_egg:
                    app.inventory.append(easter_egg)
                    app.result_text.insert(tk.END, f"意外之喜，获得彩蛋：", None)
                    app.result_text.insert(tk.END, f"{easter_egg['name']}", easter_egg['item_type'])
                    app.result_text.insert(tk.END, "\n", None)
                if returned_items:
                    returned_str = ", ".join(item['name'] for item in returned_items)
                    app.result_text.insert(tk.END, f"返还物品：{returned_str}\n", None)
                app.result_text.insert(tk.END, f"{msg}\n", "error")
            save_to_db(app.elements, app.inventory, app.mbti_history)
            app.result_text.insert(tk.END, "数据已保存！\n")

        elif item_types == {'third'}:
            # MBTI 合成：仅三级物品
            result, new_inventory, returned_items, easter_egg, hint = synthesize_mbti(app.inventory, selected_items)
            if result:
                app.inventory = new_inventory
                for item in returned_items:
                    app.inventory.append(item)
                if easter_egg:
                    app.inventory.append(easter_egg)
                    app.result_text.insert(tk.END, f"意外之喜，获得彩蛋：", None)
                    app.result_text.insert(tk.END, f"{easter_egg['name']}", easter_egg['item_type'])
                    app.result_text.insert(tk.END, "\n", None)
                app.mbti_history.append({
                    'mbti': result['mbti'],
                    'ratios': result['ratios'],
                    'success': result['success'],
                    'entries': selected_entries
                })
                reality_percent = {
                    'ISFJ': 13.8, 'ESFJ': 12.0, 'ISTJ': 11.6, 'ISFP': 8.8, 'ESTJ': 8.7,
                    'ESFP': 8.5, 'ENFP': 8.1, 'ISTP': 5.4, 'INFP': 4.4, 'ESTP': 4.3,
                    'INTP': 3.3, 'ENTP': 3.2, 'ENFJ': 2.5, 'INTJ': 2.1, 'ENTJ': 1.8, 'INFJ': 1.5
                }
                entries_str = f"，词条：{', '.join(e for e in selected_entries)}" if selected_entries else ""
                if result['success']:
                    app.result_text.insert(tk.END, f"MBTI 合成成功！结果：", None)
                    app.result_text.insert(tk.END, f"{result['mbti']}", "mbti")
                    app.result_text.insert(tk.END, f" (现实占比：{reality_percent.get(result['mbti'], 0)}%)\n", None)
                    app.result_text.insert(tk.END,
                                           f"元素比例：{ {k: f'{v:.2f}' for k, v in result['ratios'].items()} }\n", None)
                    app.result_text.insert(tk.END, f"{hint}{entries_str}\n", None)
                    app.result_text.insert(tk.END, f"已存入 MBTI 历史！\n")
                else:
                    app.result_text.insert(tk.END, f"{hint}\n", "error")
                    if returned_items:
                        returned_str = ", ".join(item['name'] for item in returned_items)
                        app.result_text.insert(tk.END, f"返还物品：{returned_str}\n", None)
                    if easter_egg:
                        app.result_text.insert(tk.END, f"意外之喜，获得彩蛋：", None)
                        app.result_text.insert(tk.END, f"{easter_egg['name']}", easter_egg['item_type'])
                        app.result_text.insert(tk.END, "\n", None)
                save_to_db(app.elements, app.inventory, app.mbti_history)
                app.result_text.insert(tk.END, "数据已保存！\n")
            else:
                app.result_text.insert(tk.END, f"{hint}\n", "error")

        else:
            tk.messagebox.showerror("合成错误", "无效的物品组合！请检查物品类型！")
            return

    app.update_display()
    app.update_inputs()