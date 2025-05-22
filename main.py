# main.py
# 主程序：UI 和玩家输入，支持随机初级和中级合成，选择具体物品

import tkinter as tk
from tkinter import messagebox
import random
from synthesis import synthesize_initial, synthesize_intermediate, synthesize_mbti
from data import initial_items, intermediate_recipes, mbti_targets, item_traits


class MBTISynthesisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MBTI 元素合成系统")
        self.elements = {'water': 10, 'fire': 10, 'earth': 0, 'air': 0}  # 初始元素
        self.inventory = []  # 物品库存

        # 主框架
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill='both', expand=True)

        # 元素库存显示
        self.elements_label = tk.Label(self.main_frame, text="元素库存：加载中...", font=("Arial", 12))
        self.elements_label.pack(anchor='w')

        # 物品库存显示
        self.inventory_label = tk.Label(self.main_frame, text="物品库存：空", font=("Arial", 12))
        self.inventory_label.pack(anchor='w')

        # 获取元素按钮
        tk.Button(self.main_frame, text="获取元素", command=self.add_elements, font=("Arial", 12)).pack(pady=5)

        # 查看库存详情按钮
        tk.Button(self.main_frame, text="查看库存详情", command=self.view_inventory_details, font=("Arial", 12)).pack(
            pady=5)

        # 合成选择
        tk.Label(self.main_frame, text="选择合成类型：", font=("Arial", 12)).pack(anchor='w')
        self.synth_type = tk.StringVar(value="initial")
        tk.Radiobutton(self.main_frame, text="初级物品（随机）", variable=self.synth_type, value="initial",
                       command=self.update_inputs).pack(anchor='w')
        tk.Radiobutton(self.main_frame, text="中级物品（随机）", variable=self.synth_type, value="intermediate",
                       command=self.update_inputs).pack(anchor='w')
        tk.Radiobutton(self.main_frame, text="MBTI", variable=self.synth_type, value="mbti",
                       command=self.update_inputs).pack(anchor='w')

        # 元素输入（初级合成）
        self.element_inputs = {}
        tk.Label(self.main_frame, text="输入元素数量（初级合成）：", font=("Arial", 12)).pack(anchor='w')
        for elem in ['water', 'fire', 'earth', 'air']:
            frame = tk.Frame(self.main_frame)
            frame.pack(anchor='w')
            tk.Label(frame, text=f"{elem}：").pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=5)
            entry.pack(side=tk.LEFT)
            self.element_inputs[elem] = entry

        # 物品选择（中级合成）
        tk.Label(self.main_frame, text="选择物品（中级合成）：", font=("Arial", 12)).pack(anchor='w')
        self.item_selection_frame = tk.Frame(self.main_frame)
        self.item_selection_frame.pack(fill='both', expand=True)
        self.item_checkboxes = {}  # 复选框变量
        self.item_vars = {}  # 复选框状态

        # 合成按钮
        tk.Button(self.main_frame, text="合成！", command=self.synthesize, font=("Arial", 12)).pack(pady=10)

        # 结果显示
        self.result_text = tk.Text(self.main_frame, height=8, width=60, font=("Arial", 12))
        self.result_text.pack(anchor='w')

        # 初始更新
        self.update_display()
        self.update_inputs()

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

    def update_display(self):
        """更新元素和物品库存显示"""
        elements_str = "元素库存：" + ", ".join(f"{k}: {v}" for k, v in self.elements.items())
        self.elements_label.config(text=elements_str)

        item_counts = {}
        for item in self.inventory:
            item_counts[item['name']] = item_counts.get(item['name'], 0) + 1
        inventory_str = "物品库存：" + (", ".join(f"{k}: {v}" for k, v in item_counts.items()) if item_counts else "空")
        self.inventory_label.config(text=inventory_str)

    def update_inputs(self, *args):
        """动态更新输入框状态"""
        synth_type = self.synth_type.get()

        # 元素输入框
        for elem in self.element_inputs:
            self.element_inputs[elem].config(state='normal' if synth_type == "initial" else 'disabled')
            self.element_inputs[elem].delete(0, tk.END)

        # 清理旧复选框
        for widget in self.item_selection_frame.winfo_children():
            widget.destroy()
        self.item_checkboxes = {}
        self.item_vars = {}

        # 物品选择框（中级合成）
        if synth_type == "intermediate":
            if not self.inventory:
                tk.Label(self.item_selection_frame, text="库存为空，请先合成初级物品！", font=("Arial", 12),
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
                        font=("Arial", 10)
                    )
                    self.item_checkboxes[id(item)].pack(anchor='w')

    def view_inventory_details(self):
        """查看库存物品的元素属性和随机属性作用"""
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

        # 按物品名称分组并编号
        item_indices = {}
        for i, item in enumerate(self.inventory, 1):
            name = item['name']
            index = item_indices.get(name, 0) + 1
            item_indices[name] = index
            elements_str = ", ".join(f"{k}: {v:.2f}" for k, v in item['elements'].items())
            traits = item.get('traits', [])
            traits_str = ", ".join(f"{t} ({item_traits[t]['description']})" for t in traits) if traits else "无属性"
            text.insert(tk.END, f"物品{i} ({name}{index}): {elements_str}, 属性：{traits_str}\n")

        text.config(state='disabled')
        tk.Button(details_window, text="关闭", command=details_window.destroy, font=("Arial", 12)).pack(pady=5)

        # 提示
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "库存如墨，激情泥浆尽显，查看详情吧！\n")

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
                self.result_text.insert(tk.END, f"{msg}\n元素组成：{elements_str}\n属性：{traits_str}\n")
            else:
                self.result_text.insert(tk.END, f"{msg}\n")

        elif synth_type == "intermediate":
            # 收集勾选物品
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
                self.result_text.insert(tk.END, f"{msg}\n元素组成：{elements_str}\n属性：{traits_str}\n")
            else:
                self.result_text.insert(tk.END, f"{msg}\n")

        elif synth_type == "mbti":
            result, hint = synthesize_mbti(self.inventory)
            if result and result['success']:
                reality_percent = {
                    'ISFJ': 13.8, 'ESFJ': 12.0, 'ISTJ': 11.6, 'ISFP': 8.8, 'ESTJ': 8.7,
                    'ESFP': 8.5, 'ENFP': 8.1, 'ISTP': 5.4, 'INFP': 4.4, 'ESTP': 4.3,
                    'INTP': 3.3, 'ENTP': 3.2, 'ENFJ': 2.5, 'INTJ': 2.1, 'ENTJ': 1.8, 'INFJ': 1.5
                }
                self.result_text.insert(tk.END,
                                        f"合成结果：{result['mbti']} (现实占比：{reality_percent.get(result['mbti'], 0)}%)\n")
                self.result_text.insert(tk.END, f"元素比例：{ {k: f'{v:.2f}' for k, v in result['ratios'].items()} }\n")
                self.result_text.insert(tk.END,
                                        f"属性贡献：E/I={result['contributions']['E']:.2f}/{result['contributions']['I']:.2f}, "
                                        f"S/N={result['contributions']['S']:.2f}/{result['contributions']['N']:.2f}, "
                                        f"T/F={result['contributions']['T']:.2f}/{result['contributions']['F']:.2f}, "
                                        f"J/P={result['contributions']['J']:.2f}/{result['contributions']['P']:.2f}\n")
                self.result_text.insert(tk.END, f"{hint}\n")
            else:
                self.result_text.insert(tk.END, f"合成失败！{hint}\n")

        self.update_display()
        self.update_inputs()


if __name__ == "__main__":
    root = tk.Tk()
    app = MBTISynthesisApp(root)
    root.mainloop()