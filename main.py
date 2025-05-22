# main.py
# 主程序：UI 和玩家输入，支持随机初级、中级和MBTI合成，选择具体物品，区分初级/中级颜色，数据库保存，中文名称，修复输入框，MBTI保底机制，MBTI历史存储与查看

import tkinter as tk
from tkinter import messagebox
import random
from synthesis import synthesize_initial, synthesize_intermediate, synthesize_mbti
from data import initial_items, intermediate_recipes, mbti_targets, item_traits
from database import init_db, save_to_db, load_from_db
import os


class MBTISynthesisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MBTI 元素合成系统")

        # 初始化数据库
        init_db()

        # 检查旧数据库（英文名称）
        if os.path.exists('mbti_synthesis.db'):
            response = messagebox.askyesno(
                "数据库更新提示",
                "物品名称已更新为中文，建议清空旧数据库（mbti_synthesis.db）以避免冲突！是否清空？"
            )
            if response:
                os.remove('mbti_synthesis.db')
                init_db()

        # 加载数据
        self.elements, self.inventory, self.mbti_history = load_from_db()

        # 主框架
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill='both', expand=True)

        # 元素库存显示
        self.elements_label = tk.Label(self.main_frame, text="元素库存：加载中...", font=("Arial", 12))
        self.elements_label.pack(anchor='w', pady=5)

        # 物品库存显示
        self.inventory_frame = tk.Frame(self.main_frame)
        self.inventory_frame.pack(anchor='w', pady=5)

        # 获取元素按钮
        tk.Button(self.main_frame, text="获取元素", command=self.add_elements, font=("Arial", 12)).pack(pady=5)

        # 查看库存详情按钮
        tk.Button(self.main_frame, text="查看库存详情", command=self.view_inventory_details, font=("Arial", 12)).pack(
            pady=5)

        # 查看 MBTI 历史按钮
        tk.Button(self.main_frame, text="查看 MBTI 历史", command=self.view_mbti_history, font=("Arial", 12)).pack(
            pady=5)

        # 合成选择
        tk.Label(self.main_frame, text="选择合成类型：", font=("Arial", 12)).pack(anchor='w', pady=5)
        self.synth_type = tk.StringVar(value="initial")
        tk.Radiobutton(self.main_frame, text="初级物品（随机）", variable=self.synth_type, value="initial",
                       command=self.update_inputs).pack(anchor='w')
        tk.Radiobutton(self.main_frame, text="中级物品（随机）", variable=self.synth_type, value="intermediate",
                       command=self.update_inputs).pack(anchor='w')
        tk.Radiobutton(self.main_frame, text="MBTI（随机）", variable=self.synth_type, value="mbti",
                       command=self.update_inputs).pack(anchor='w')

        # 元素输入（初级合成）
        self.element_inputs = {}
        tk.Label(self.main_frame, text="输入元素数量（初级合成）：", font=("Arial", 12)).pack(anchor='w', pady=5)
        for elem in ['water', 'fire', 'earth', 'air']:
            frame = tk.Frame(self.main_frame)
            frame.pack(anchor='w', fill='x', pady=2)
            tk.Label(frame, text=f"{elem}：", width=10).pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=5, state='normal', takefocus=True)  # 确保可接受焦点
            entry.pack(side=tk.LEFT, padx=5)
            self.element_inputs[elem] = entry

        # 物品选择（中级和MBTI合成）
        tk.Label(self.main_frame, text="选择物品（中级/MBTI合成）：", font=("Arial", 12)).pack(anchor='w', pady=5)
        self.item_selection_frame = tk.Frame(self.main_frame)
        self.item_selection_frame.pack(fill='both', expand=True, pady=5)
        self.item_checkboxes = {}  # 复选框变量
        self.item_vars = {}  # 复选框状态

        # 合成按钮
        tk.Button(self.main_frame, text="合成！", command=self.synthesize, font=("Arial", 12)).pack(pady=10)

        # 结果显示
        self.result_text = tk.Text(self.main_frame, height=8, width=60, font=("Arial", 12))
        self.result_text.pack(anchor='w', pady=5)

        # 配置文本颜色
        self.result_text.tag_configure("initial", foreground="#0000FF")  # 蓝色
        self.result_text.tag_configure("intermediate", foreground="#800080")  # 紫色
        self.result_text.tag_configure("error", foreground="#FF0000")  # 红色

        # 初始更新
        self.update_display()
        self.update_inputs()
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "数据加载成功，蓝色水晶与紫色灵液就位！\n")

    def add_elements(self):
        """模拟获取元素，反映现实分布"""
        rewards = {
            'earth': random.randint(5, 7),
            'water': random.randint(4, 6),
            'fire': random.randint(2, 4),
            'air': random.randint(2, 3)
        }
        for elem, amount in rewards.items():
            self.elements[elem] = self.elements.get(elem, 0) + amount
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"获取元素：{rewards}\n")
        self.update_display()
        save_to_db(self.elements, self.inventory, self.mbti_history)
        self.result_text.insert(tk.END, "数据已保存！\n")

    def update_display(self):
        """更新元素和物品库存显示，区分初级/中级颜色"""
        elements_str = "元素库存：" + ", ".join(f"{k}: {v}" for k, v in self.elements.items())
        self.elements_label.config(text=elements_str)

        # 清理旧库存显示
        for widget in self.inventory_frame.winfo_children():
            widget.destroy()

        # 显示库存
        item_counts = {'initial': {}, 'intermediate': {}}
        for item in self.inventory:
            item_type = item['item_type']
            name = item['name']
            item_counts[item_type][name] = item_counts[item_type].get(name, 0) + 1

        inventory_str = []
        if item_counts['initial']:
            initial_str = ", ".join(f"{k}: {v}" for k, v in item_counts['initial'].items())
            tk.Label(self.inventory_frame, text=f"初级库存：{initial_str}", font=("Arial", 12), fg="#0000FF").pack(
                anchor='w')
        if item_counts['intermediate']:
            intermediate_str = ", ".join(f"{k}: {v}" for k, v in item_counts['intermediate'].items())
            tk.Label(self.inventory_frame, text=f"中级库存：{intermediate_str}", font=("Arial", 12), fg="#800080").pack(
                anchor='w')
        if not item_counts['initial'] and not item_counts['intermediate']:
            tk.Label(self.inventory_frame, text="物品库存：空", font=("Arial", 12)).pack(anchor='w')

    def update_inputs(self, *args):
        """动态更新输入框状态，区分初级/中级颜色"""
        synth_type = self.synth_type.get()

        # 元素输入框
        for elem in self.element_inputs:
            self.element_inputs[elem].config(state='normal' if synth_type == "initial" else 'disabled')
            self.element_inputs[elem].delete(0, tk.END)

        # 强制焦点（初级合成时）
        if synth_type == "initial":
            self.element_inputs['water'].focus_set()

        # 清理旧复选框
        for widget in self.item_selection_frame.winfo_children():
            widget.destroy()
        self.item_checkboxes = {}
        self.item_vars = {}

        # 物品选择框（中级和MBTI合成）
        if synth_type in ["intermediate", "mbti"]:
            if not self.inventory:
                tk.Label(self.item_selection_frame, text="库存为空，请先合成初级物品！", font=("Arial", 12),
                         fg="red").pack(anchor='w')
            elif synth_type == "mbti" and not any(item['item_type'] == 'intermediate' for item in self.inventory):
                tk.Label(self.item_selection_frame, text="库存无中级物品，请先进行中级合成！", font=("Arial", 12),
                         fg="red").pack(anchor='w')
            else:
                # 滚动框
                canvas = tk.Canvas(self.item_selection_frame)
                scrollbar = tk.Scrollbar(self.item_selection_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = tk.Frame(canvas)

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")

                tk.Label(scrollable_frame, text="选择具体物品：", font=("Arial", 12)).pack(anchor='w')
                item_indices = {}
                for i, item in enumerate(self.inventory, 1):
                    if synth_type == "mbti" and item['item_type'] != 'intermediate':
                        continue  # MBTI 合成仅显示中级物品
                    name = item['name']
                    index = item_indices.get(name, 0) + 1
                    item_indices[name] = index
                    elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
                    traits = item.get('traits', [])
                    traits_str = ", ".join(
                        f"{t} ({item_traits[t]['description']})" for t in traits) if traits else "无属性"
                    label = f"{name}{index}: {elements_str}, 属性：{traits_str}"
                    var = tk.BooleanVar()
                    self.item_vars[id(item)] = var
                    self.item_checkboxes[id(item)] = tk.Checkbutton(
                        scrollable_frame,
                        text=label,
                        variable=var,
                        font=("Arial", 10),
                        foreground="#0000FF" if item['item_type'] == 'initial' else "#800080"
                    )
                    self.item_checkboxes[id(item)].pack(anchor='w')

        # 强制刷新 UI
        self.root.update()
        self.root.update_idletasks()

    def view_inventory_details(self):
        """查看库存物品的元素属性和随机属性作用，区分初级/中级颜色"""
        if not self.inventory:
            messagebox.showinfo("库存详情", "库存为空！快去合成吧！")
            return

        # 创建弹窗
        details_window = tk.Toplevel(self.root)
        details_window.title("库存详情")
        details_window.geometry("600x300")

        # 文本区域
        text = tk.Text(details_window, height=10, width=70, font=("Arial", 12))
        text.pack(padx=10, pady=10)

        # 配置颜色
        text.tag_configure("initial", foreground="#0000FF")
        text.tag_configure("intermediate", foreground="#800080")

        # 按物品名称分组并编号
        item_indices = {}
        for i, item in enumerate(self.inventory, 1):
            name = item['name']
            index = item_indices.get(name, 0) + 1
            item_indices[name] = index
            elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
            traits = item.get('traits', [])
            traits_str = ", ".join(f"{t} ({item_traits[t]['description']})" for t in traits) if traits else "无属性"
            tag = "initial" if item['item_type'] == 'initial' else "intermediate"
            text.insert(tk.END, f"物品{i} (", None)
            text.insert(tk.END, f"{name}{index}", tag)
            text.insert(tk.END, f"): {elements_str}, 属性：{traits_str}\n", None)

        text.config(state='disabled')
        tk.Button(details_window, text="关闭", command=details_window.destroy, font=("Arial", 12)).pack(pady=5)

        # 提示
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "库存如墨，紫色中级物品尽显，查看详情吧！\n")

    def view_mbti_history(self):
        """查看 MBTI 历史记录"""
        if not self.mbti_history:
            messagebox.showinfo("MBTI 历史", "暂无 MBTI 合成记录！快去合成吧！")
            return

        # 创建弹窗
        history_window = tk.Toplevel(self.root)
        history_window.title("MBTI 历史")
        history_window.geometry("600x400")

        # 滚动框
        canvas = tk.Canvas(history_window)
        scrollbar = tk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        # 文本区域
        text = tk.Text(scrollable_frame, height=15, width=70, font=("Arial", 12))
        text.pack(padx=10, pady=10)

        # 配置颜色
        text.tag_configure("intermediate", foreground="#800080")

        # 显示 MBTI 历史
        reality_percent = {
            'ISFJ': 13.8, 'ESFJ': 12.0, 'ISTJ': 11.6, 'ISFP': 8.8, 'ESTJ': 8.7,
            'ESFP': 8.5, 'ENFP': 8.1, 'ISTP': 5.4, 'INFP': 4.4, 'ESTP': 4.3,
            'INTP': 3.3, 'ENTP': 3.2, 'ENFJ': 2.5, 'INTJ': 2.1, 'ENTJ': 1.8, 'INFJ': 1.5
        }
        for i, record in enumerate(self.mbti_history, 1):
            mbti = record['mbti']
            ratios = record['ratios']
            success = record['success']
            trait = record['trait']
            ratios_str = ", ".join(f"{k}: {v:.2f}" for k, v in ratios.items())
            status = "成功合成" if success else "保底合成"
            trait_str = f"，属性：{trait} ({item_traits[trait]['description']})" if trait else ""
            text.insert(tk.END, f"MBTI {i}: ", None)
            text.insert(tk.END, f"{mbti}", "intermediate")
            text.insert(tk.END, f" (现实占比：{reality_percent.get(mbti, 0)}%)，比例：{ratios_str}，{status}{trait_str}\n",
                        None)

        text.config(state='disabled')
        tk.Button(history_window, text="关闭", command=history_window.destroy, font=("Arial", 12)).pack(pady=5)

        # 提示
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "水墨流转，MBTI 历史如卷轴展开，查看你的性格收藏！\n")

    def synthesize(self):
        """执行合成"""
        self.result_text.delete(1.0, tk.END)
        synth_type = self.synth_type.get()

        if synth_type == "initial":
            input_elements = {}
            for elem in self.element_inputs:
                try:
                    value = float(self.element_inputs[elem].get() or 0)
                    if value < 0 or value > self.elements.get(elem, 0):
                        messagebox.showerror("错误", f"{elem}数量无效！")
                        return
                    input_elements[elem] = value
                except ValueError:
                    messagebox.showerror("错误", f"请输入有效的{elem}数量！")
                    return
            item, new_elements, msg = synthesize_initial(self.elements, input_elements)
            if item:
                self.elements = new_elements
                self.inventory.append(item)
                elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
                traits = item.get('traits', [])
                traits_str = ", ".join(f"{t} ({item_traits[t]['description']})" for t in traits) if traits else "无属性"
                self.result_text.insert(tk.END, f"{msg}\n", None)
                self.result_text.insert(tk.END, f"元素组成：{elements_str}\n属性：{traits_str}\n", None)
                self.result_text.insert(tk.END, f"获得：", None)
                self.result_text.insert(tk.END, f"{item['name']}", "initial")
                self.result_text.insert(tk.END, "\n", None)
                save_to_db(self.elements, self.inventory, self.mbti_history)
                self.result_text.insert(tk.END, "数据已保存！\n")
            else:
                self.result_text.insert(tk.END, f"{msg}\n", "error")

        elif synth_type == "intermediate":
            selected_items = []
            for item_id, var in self.item_vars.items():
                if var.get():
                    for item in self.inventory:
                        if id(item) == item_id:
                            selected_items.append(item)
                            break
            if not selected_items:
                messagebox.showerror("错误", "请至少选择一个物品！")
                return

            item, new_inventory, msg = synthesize_intermediate(self.inventory, selected_items)
            if item:
                self.inventory = new_inventory
                self.inventory.append(item)
                elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
                traits = item.get('traits', [])
                traits_str = ", ".join(f"{t} ({item_traits[t]['description']})" for t in traits) if traits else "无属性"
                self.result_text.insert(tk.END, f"{msg}\n", None)
                self.result_text.insert(tk.END, f"元素组成：{elements_str}\n属性：{traits_str}\n", None)
                self.result_text.insert(tk.END, f"获得：", None)
                self.result_text.insert(tk.END, f"{item['name']}", "intermediate")
                self.result_text.insert(tk.END, "\n", None)
                save_to_db(self.elements, self.inventory, self.mbti_history)
                self.result_text.insert(tk.END, "数据已保存！\n")
            else:
                self.result_text.insert(tk.END, f"{msg}\n", "error")

        elif synth_type == "mbti":
            selected_items = []
            for item_id, var in self.item_vars.items():
                if var.get():
                    for item in self.inventory:
                        if id(item) == item_id:
                            selected_items.append(item)
                            break
            if not selected_items:
                messagebox.showerror("错误", "请至少选择一个物品！")
                return

            result, new_inventory, hint = synthesize_mbti(self.inventory, selected_items)
            if result:
                self.inventory = new_inventory
                # 存储 MBTI 历史
                self.mbti_history.append({
                    'mbti': result['mbti'],
                    'ratios': result['ratios'],
                    'success': result['success'],
                    'trait': result['trait']
                })
                reality_percent = {
                    'ISFJ': 13.8, 'ESFJ': 12.0, 'ISTJ': 11.6, 'ISFP': 8.8, 'ESTJ': 8.7,
                    'ESFP': 8.5, 'ENFP': 8.1, 'ISTP': 5.4, 'INFP': 4.4, 'ESTP': 4.3,
                    'INTP': 3.3, 'ENTP': 3.2, 'ENFJ': 2.5, 'INTJ': 2.1, 'ENTJ': 1.8, 'INFJ': 1.5
                }
                if result['success']:
                    self.result_text.insert(tk.END, f"MBTI 合成成功！结果：", None)
                    self.result_text.insert(tk.END, f"{result['mbti']}", "intermediate")
                    self.result_text.insert(tk.END, f" (现实占比：{reality_percent.get(result['mbti'], 0)}%)\n", None)
                    self.result_text.insert(tk.END,
                                            f"元素比例：{ {k: f'{v:.2f}' for k, v in result['ratios'].items()} }\n",
                                            None)
                    self.result_text.insert(tk.END, f"{hint}\n", None)
                    self.result_text.insert(tk.END, f"已存入 MBTI 历史！\n")
                else:
                    # 保底机制
                    self.result_text.insert(tk.END, f"MBTI 合成触发保底！结果：", None)
                    self.result_text.insert(tk.END, f"{result['mbti']}", "intermediate")
                    self.result_text.insert(tk.END, f" (现实占比：{reality_percent.get(result['mbti'], 0)}%)\n", None)
                    self.result_text.insert(tk.END,
                                            f"元素比例：{ {k: f'{v:.2f}' for k, v in result['ratios'].items()} }\n",
                                            None)
                    self.result_text.insert(tk.END,
                                            f"属性：{result['trait']} ({item_traits[result['trait']]['description']})\n",
                                            None)
                    self.result_text.insert(tk.END, f"{hint}\n", None)
                    self.result_text.insert(tk.END, f"已存入 MBTI 历史！\n")
                save_to_db(self.elements, self.inventory, self.mbti_history)
                self.result_text.insert(tk.END, "数据已保存！\n")
            else:
                self.result_text.insert(tk.END, f"{hint}\n", "error")

        self.update_display()
        self.update_inputs()


if __name__ == "__main__":
    root = tk.Tk()
    app = MBTISynthesisApp(root)
    root.mainloop()