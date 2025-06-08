# main.py
# 主程序：UI 和玩家输入，支持初级（元素+一级→一级）、中级（一级+中级→中级）、三级（二级→三级）、MBTI（三级→MBTI）合成，选择具体物品，区分初级/中级/三级颜色，数据库保存，中文名称，修复输入框，MBTI保底机制，MBTI历史存储与查看，MBTI范围匹配，移除情感属性，支持词条属性，允许同种元素合成

import tkinter as tk
from tkinter import messagebox
import random
from synthesis import synthesize_initial, synthesize_intermediate, synthesize_third, synthesize_mbti
from data import initial_items, intermediate_recipes, third, item_entries
from database import init_db, save_to_db, load_from_db
import os


class MBTISynthesisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MBTI 元素合成系统")

        # 初始化数据库
        init_db()

        # 检查旧数据库
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
        tk.Radiobutton(self.main_frame, text="三级物品（随机）", variable=self.synth_type, value="third",
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
            entry = tk.Entry(frame, width=5, state='normal', takefocus=True)
            entry.pack(side=tk.LEFT, padx=5)
            self.element_inputs[elem] = entry

        # 初级物品选择（初级合成）
        tk.Label(self.main_frame, text="选择初级物品（初级合成，可选）：", font=("Arial", 12)).pack(anchor='w', pady=5)
        self.initial_item_selection_frame = tk.Frame(self.main_frame)
        self.initial_item_selection_frame.pack(fill='both', expand=True, pady=5)
        self.initial_item_checkboxes = {}
        self.initial_item_vars = {}

        # 中级物品选择（中级合成）
        tk.Label(self.main_frame, text="选择中级物品（中级合成）：", font=("Arial", 12)).pack(anchor='w', pady=5)
        self.intermediate_item_selection_frame = tk.Frame(self.main_frame)
        self.intermediate_item_selection_frame.pack(fill='both', expand=True, pady=5)
        self.intermediate_item_checkboxes = {}
        self.intermediate_item_vars = {}

        # 三级物品选择（三级和MBTI合成）
        tk.Label(self.main_frame, text="选择三级物品（三级/MBTI合成）：", font=("Arial", 12)).pack(anchor='w', pady=5)
        self.third_item_selection_frame = tk.Frame(self.main_frame)
        self.third_item_selection_frame.pack(fill='both', expand=True, pady=5)
        self.third_item_checkboxes = {}
        self.third_item_vars = {}

        # 合成按钮
        tk.Button(self.main_frame, text="合成！", command=self.synthesize, font=("Arial", 12)).pack(pady=10)

        # 结果显示
        self.result_text = tk.Text(self.main_frame, height=8, width=60, font=("Arial", 12))
        self.result_text.pack(anchor='w', pady=5)

        # 配置文本颜色
        self.result_text.tag_configure("initial", foreground="#0000FF")
        self.result_text.tag_configure("intermediate", foreground="#800080")
        self.result_text.tag_configure("third", foreground="#800080")
        self.result_text.tag_configure("error", foreground="#FF0000")

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
        """更新元素和物品库存显示，区分初级/中级/三级颜色"""
        elements_str = "元素库存：" + ", ".join(f"{k}: {v}" for k, v in self.elements.items())
        self.elements_label.config(text=elements_str)

        for widget in self.inventory_frame.winfo_children():
            widget.destroy()

        item_counts = {'initial': {}, 'intermediate': {}, 'third': {}}
        for item in self.inventory:
            item_type = item['item_type']
            name = item['name']
            item_counts[item_type][name] = item_counts[item_type].get(name, 0) + 1

        if item_counts['initial']:
            initial_str = ", ".join(f"{k}: {v}" for k, v in item_counts['initial'].items())
            tk.Label(self.inventory_frame, text=f"初级库存：{initial_str}", font=("Arial", 12), fg="#0000FF").pack(
                anchor='w')
        if item_counts['intermediate']:
            intermediate_str = ", ".join(f"{k}: {v}" for k, v in item_counts['intermediate'].items())
            tk.Label(self.inventory_frame, text=f"中级库存：{intermediate_str}", font=("Arial", 12), fg="#800080").pack(
                anchor='w')
        if item_counts['third']:
            third_str = ", ".join(f"{k}: {v}" for k, v in item_counts['third'].items())
            tk.Label(self.inventory_frame, text=f"三级库存：{third_str}", font=("Arial", 12), fg="#800080").pack(
                anchor='w')
        if not any(item_counts.values()):
            tk.Label(self.inventory_frame, text="物品库存：空", font=("Arial", 12)).pack(anchor='w')

    def update_inputs(self, *args):
        """动态更新输入框状态，区分初级/中级/三级颜色"""
        synth_type = self.synth_type.get()

        # 元素输入框
        for elem in self.element_inputs:
            self.element_inputs[elem].config(state='normal' if synth_type == "initial" else 'disabled')
            self.element_inputs[elem].delete(0, tk.END)

        if synth_type == "initial":
            self.element_inputs['water'].focus_set()

        # 清理选择框
        for frame in [self.initial_item_selection_frame, self.intermediate_item_selection_frame,
                      self.third_item_selection_frame]:
            for widget in frame.winfo_children():
                widget.destroy()

        self.initial_item_checkboxes = {}
        self.initial_item_vars = {}
        self.intermediate_item_checkboxes = {}
        self.intermediate_item_vars = {}
        self.third_item_checkboxes = {}
        self.third_item_vars = {}

        # 初级物品选择（初级合成）
        if synth_type == "initial":
            if not any(item['item_type'] == 'initial' for item in self.inventory):
                tk.Label(self.initial_item_selection_frame, text="无初级物品可用！", font=("Arial", 12), fg="red").pack(
                    anchor='w')
            else:
                canvas = tk.Canvas(self.initial_item_selection_frame)
                scrollbar = tk.Scrollbar(self.initial_item_selection_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = tk.Frame(canvas)

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")

                tk.Label(scrollable_frame, text="选择初级物品：", font=("Arial", 12)).pack(anchor='w')
                item_indices = {}
                for i, item in enumerate(self.inventory, 1):
                    if item['item_type'] != 'initial':
                        continue
                    name = item['name']
                    index = item_indices.get(name, 0) + 1
                    item_indices[name] = index
                    elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
                    entries = item.get('entries', [])
                    entries_str = ", ".join(
                        f"{e} ({item_entries[e]['description']})" for e in entries) if entries else "无词条"
                    label = f"{name}{index}: {elements_str}，词条：{entries_str}"
                    var = tk.BooleanVar()
                    self.initial_item_vars[id(item)] = var
                    self.initial_item_checkboxes[id(item)] = tk.Checkbutton(
                        scrollable_frame,
                        text=label,
                        variable=var,
                        font=("Arial", 10),
                        foreground="#0000FF"
                    )
                    self.initial_item_checkboxes[id(item)].pack(anchor='w')

        # 中级物品选择（中级合成）
        if synth_type == "intermediate":
            if not any(item['item_type'] in ['initial', 'intermediate'] for item in self.inventory):
                tk.Label(self.intermediate_item_selection_frame, text="无初级或中级物品可用！", font=("Arial", 12),
                         fg="red").pack(anchor='w')
            else:
                canvas = tk.Canvas(self.intermediate_item_selection_frame)
                scrollbar = tk.Scrollbar(self.intermediate_item_selection_frame, orient="vertical",
                                         command=canvas.yview)
                scrollable_frame = tk.Frame(canvas)

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")

                tk.Label(scrollable_frame, text="选择中级物品：", font=("Arial", 12)).pack(anchor='w')
                item_indices = {}
                for i, item in enumerate(self.inventory, 1):
                    if item['item_type'] not in ['initial', 'intermediate']:
                        continue
                    name = item['name']
                    index = item_indices.get(name, 0) + 1
                    item_indices[name] = index
                    elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
                    entries = item.get('entries', [])
                    entries_str = ", ".join(
                        f"{e} ({item_entries[e]['description']})" for e in entries) if entries else "无词条"
                    label = f"{name}{index}: {elements_str}，词条：{entries_str}"
                    var = tk.BooleanVar()
                    self.intermediate_item_vars[id(item)] = var
                    self.intermediate_item_checkboxes[id(item)] = tk.Checkbutton(
                        scrollable_frame,
                        text=label,
                        variable=var,
                        font=("Arial", 10),
                        foreground="#0000FF" if item['item_type'] == 'initial' else "#800080"
                    )
                    self.intermediate_item_checkboxes[id(item)].pack(anchor='w')

        # 三级物品选择（三级和MBTI合成）
        if synth_type in ["third", "mbti"]:
            if not self.inventory:
                tk.Label(self.third_item_selection_frame, text="库存为空，请先合成初级物品！", font=("Arial", 12),
                         fg="red").pack(anchor='w')
            elif synth_type == "third" and not any(item['item_type'] == 'intermediate' for item in self.inventory):
                tk.Label(self.third_item_selection_frame, text="库存无中级物品，请先进行中级合成！", font=("Arial", 12),
                         fg="red").pack(anchor='w')
            elif synth_type == "mbti" and not any(item['item_type'] == 'third' for item in self.inventory):
                tk.Label(self.third_item_selection_frame, text="库存无三级物品，请先进行三级合成！", font=("Arial", 12),
                         fg="red").pack(anchor='w')
            else:
                canvas = tk.Canvas(self.third_item_selection_frame)
                scrollbar = tk.Scrollbar(self.third_item_selection_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = tk.Frame(canvas)

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")

                tk.Label(scrollable_frame, text="选择三级物品：", font=("Arial", 12)).pack(anchor='w')
                item_indices = {}
                for i, item in enumerate(self.inventory, 1):
                    if synth_type == "third" and item['item_type'] != 'intermediate':
                        continue
                    if synth_type == "mbti" and item['item_type'] != 'third':
                        continue
                    name = item['name']
                    index = item_indices.get(name, 0) + 1
                    item_indices[name] = index
                    elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
                    entries = item.get('entries', [])
                    entries_str = ", ".join(
                        f"{e} ({item_entries[e]['description']})" for e in entries) if entries else "无词条"
                    label = f"{name}{index}: {elements_str}，词条：{entries_str}"
                    var = tk.BooleanVar()
                    self.third_item_vars[id(item)] = var
                    self.third_item_checkboxes[id(item)] = tk.Checkbutton(
                        scrollable_frame,
                        text=label,
                        variable=var,
                        font=("Arial", 10),
                        foreground="#800080"
                    )
                    self.third_item_checkboxes[id(item)].pack(anchor='w')

        self.root.update()
        self.root.update_idletasks()

    def view_inventory_details(self):
        """查看库存物品的元素比例和词条，区分初级/中级/三级颜色"""
        if not self.inventory:
            messagebox.showinfo("库存详情", "库存为空！快去合成吧！")
            return

        details_window = tk.Toplevel(self.root)
        details_window.title("库存详情")
        details_window.geometry("600x300")

        text = tk.Text(details_window, height=10, width=70, font=("Arial", 12))
        text.pack(padx=10, pady=10)

        text.tag_configure("initial", foreground="#0000FF")
        text.tag_configure("intermediate", foreground="#800080")
        text.tag_configure("third", foreground="#800080")

        item_indices = {}
        for i, item in enumerate(self.inventory, 1):
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

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "库存如墨，紫色高级物品尽显，查看详情吧！\n")

    def view_mbti_history(self):
        """查看 MBTI 历史记录"""
        if not self.mbti_history:
            messagebox.showinfo("MBTI 历史", "暂无 MBTI 合成记录！快去合成吧！")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("MBTI 历史")
        history_window.geometry("600x400")

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

        text = tk.Text(scrollable_frame, height=15, width=70, font=("Arial", 12))
        text.pack(padx=10, pady=10)

        text.tag_configure("third", foreground="#800080")

        reality_percent = {
            'ISFJ': 13.8, 'ESFJ': 12.0, 'ISTJ': 11.6, 'ISFP': 8.8, 'ESTJ': 8.7,
            'ESFP': 8.5, 'ENFP': 8.1, 'ISTP': 5.4, 'INFP': 4.4, 'ESTP': 4.3,
            'INTP': 3.3, 'ENTP': 3.2, 'ENFJ': 2.5, 'INTJ': 2.1, 'ENTJ': 1.8, 'INFJ': 1.5
        }
        for i, record in enumerate(self.mbti_history, 1):
            mbti = record['mbti']
            ratios = record['ratios']
            success = record['success']
            entries = record.get('entries', [])
            ratios_str = ", ".join(f"{k}: {v:.2f}" for k, v in ratios.items())
            status = "成功合成" if success else "保底合成"
            entries_str = f"，词条：{', '.join(e for e in entries)}" if entries else ""
            text.insert(tk.END, f"MBTI {i}: ", None)
            text.insert(tk.END, f"{mbti}", "third")
            text.insert(tk.END,
                        f" (现实占比：{reality_percent.get(mbti, 0)}%)，比例：{ratios_str}，{status}{entries_str}\n", None)

        text.config(state='disabled')
        tk.Button(history_window, text="关闭", command=history_window.destroy, font=("Arial", 12)).pack(pady=5)

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "水墨流转，MBTI 历史如卷轴展开，查看你的性格收藏！\n")

    def synthesize(self):
        """执行合成，移除情感属性，支持三级物品合成，允许同种元素合成"""
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

            input_items = []
            for item_id, var in self.initial_item_vars.items():
                if var.get():
                    for item in self.inventory:
                        if id(item) == item_id:
                            input_items.append(item)
                            break

            # 检查总输入数量（元素总数 + 物品数 ≥ 2）
            total_input_elements = sum(input_elements.values())
            if total_input_elements + len(input_items) < 2:
                messagebox.showerror("合成错误", "合成失败！请至少使用两个元素或一个元素加一个物品进行初级合成！")
                return

            (item, new_elements, msg), byproduct = synthesize_initial(self.elements, input_elements, input_items)
            if item:
                self.elements = new_elements
                self.inventory.append(item)
                if byproduct:
                    self.inventory.append(item.copy())
                elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
                entries = item.get('entries', [])
                entries_str = ", ".join(
                    f"{e} ({item_entries[e]['description']})" for e in entries) if entries else "无词条"
                self.result_text.insert(tk.END, f"{msg}\n", None)
                self.result_text.insert(tk.END, f"元素组成：{elements_str}\n词条：{entries_str}\n", None)
                self.result_text.insert(tk.END, f"获得：", None)
                self.result_text.insert(tk.END, f"{item['name']}", "initial")
                self.result_text.insert(tk.END, "\n", None)
                save_to_db(self.elements, self.inventory, self.mbti_history)
                self.result_text.insert(tk.END, "数据已保存！\n")
            else:
                self.result_text.insert(tk.END, f"{msg}\n", "error")

        elif synth_type == "intermediate":
            selected_items = []
            for item_id, var in self.intermediate_item_vars.items():
                if var.get():
                    for item in self.inventory:
                        if id(item) == item_id:
                            selected_items.append(item)
                            break
            if not selected_items:
                messagebox.showerror("错误", "请至少选择一个物品！")
                return

            if len(selected_items) == 1:
                messagebox.showerror("合成错误", "合成失败！请至少选择两种物品进行中级合成！")
                return

            (item, new_inventory, msg), byproduct = synthesize_intermediate(self.inventory, selected_items)
            if item:
                self.inventory = new_inventory
                self.inventory.append(item)
                if byproduct:
                    self.inventory.append(item.copy())
                elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
                entries = item.get('entries', [])
                entries_str = ", ".join(
                    f"{e} ({item_entries[e]['description']})" for e in entries) if entries else "无词条"
                self.result_text.insert(tk.END, f"{msg}\n", None)
                self.result_text.insert(tk.END, f"元素组成：{elements_str}\n词条：{entries_str}\n", None)
                self.result_text.insert(tk.END, f"获得：", None)
                self.result_text.insert(tk.END, f"{item['name']}", "intermediate")
                self.result_text.insert(tk.END, "\n", None)
                save_to_db(self.elements, self.inventory, self.mbti_history)
                self.result_text.insert(tk.END, "数据已保存！\n")
            else:
                self.result_text.insert(tk.END, f"{msg}\n", "error")

        elif synth_type == "third":
            selected_items = []
            for item_id, var in self.third_item_vars.items():
                if var.get():
                    for item in self.inventory:
                        if id(item) == item_id:
                            selected_items.append(item)
                            break
            if not selected_items:
                messagebox.showerror("错误", "请至少选择一个物品！")
                return

            if len(selected_items) == 1:
                messagebox.showerror("合成错误", "合成失败！请至少选择两种物品进行三级合成！")
                return

            (item, new_inventory, msg), byproduct = synthesize_third(self.inventory, selected_items)
            if item:
                self.inventory = new_inventory
                self.inventory.append(item)
                if byproduct:
                    self.inventory.append(item.copy())
                elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
                entries = item.get('entries', [])
                entries_str = ", ".join(
                    f"{e} ({item_entries[e]['description']})" for e in entries) if entries else "无词条"
                self.result_text.insert(tk.END, f"{msg}\n", None)
                self.result_text.insert(tk.END, f"元素组成：{elements_str}\n词条：{entries_str}\n", None)
                self.result_text.insert(tk.END, f"获得：", None)
                self.result_text.insert(tk.END, f"{item['name']}", "third")
                self.result_text.insert(tk.END, "\n", None)
                save_to_db(self.elements, self.inventory, self.mbti_history)
                self.result_text.insert(tk.END, "数据已保存！\n")
            else:
                self.result_text.insert(tk.END, f"{msg}\n", "error")

        elif synth_type == "mbti":
            selected_items = []
            selected_entries = []
            for item_id, var in self.third_item_vars.items():
                if var.get():
                    for item in self.inventory:
                        if id(item) == item_id:
                            selected_items.append(item)
                            selected_entries.extend(item.get('entries', []))
                            break
            if not selected_items:
                messagebox.showerror("错误", "请至少选择一个物品！")
                return

            if len(selected_items) == 1:
                messagebox.showerror("合成错误", "合成失败！请至少选择两种物品进行 MBTI 合成！")
                return

            (result, new_inventory, hint), byproduct = synthesize_mbti(self.inventory, selected_items)
            if result:
                self.inventory = new_inventory
                if byproduct:
                    self.inventory.append(byproduct)
                self.mbti_history.append({
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
                    self.result_text.insert(tk.END, f"MBTI 合成成功！结果：", None)
                    self.result_text.insert(tk.END, f"{result['mbti']}", "third")
                    self.result_text.insert(tk.END, f" (现实占比：{reality_percent.get(result['mbti'], 0)}%)\n", None)
                    self.result_text.insert(tk.END,
                                            f"元素比例：{ {k: f'{v:.2f}' for k, v in result['ratios'].items()} }\n",
                                            None)
                    self.result_text.insert(tk.END, f"{hint}{entries_str}\n", None)
                    self.result_text.insert(tk.END, f"已存入 MBTI 历史！\n")
                else:
                    self.result_text.insert(tk.END, f"MBTI 合成触发保底！结果：", None)
                    self.result_text.insert(tk.END, f"{result['mbti']}", "third")
                    self.result_text.insert(tk.END, f" (现实占比：{reality_percent.get(result['mbti'], 0)}%)\n", None)
                    self.result_text.insert(tk.END,
                                            f"元素比例：{ {k: f'{v:.2f}' for k, v in result['ratios'].items()} }\n",
                                            None)
                    self.result_text.insert(tk.END, f"{hint}{entries_str}\n", None)
                    self.result_text.insert(tk.END, f"已存入 MBTI 历史！\n")
                if byproduct:
                    self.result_text.insert(tk.END, f"额外生成副产物：{byproduct['name']}\n")
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