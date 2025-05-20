# main.py
# 主程序：UI 和玩家输入，支持随机初级合成

# main.py
# 主程序：UI 和玩家输入，支持随机初级合成，显示输入比例

import tkinter as tk
from tkinter import messagebox
import random
from synthesis import synthesize_initial, synthesize_intermediate, synthesize_mbti
from data import initial_items, intermediate_recipes, mbti_targets


class MBTISynthesisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MBTI 元素合成系统")
        self.elements = {'water': 10, 'fire': 10, 'earth': 0, 'air': 0}  # 初始元素
        self.inventory = []  # 物品库存

        # 主框架
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack()

        # 元素库存显示
        self.elements_label = tk.Label(self.main_frame, text="元素库存：加载中...", font=("Arial", 12))
        self.elements_label.pack()

        # 物品库存显示
        self.inventory_label = tk.Label(self.main_frame, text="物品库存：空", font=("Arial", 12))
        self.inventory_label.pack()

        # 获取元素按钮
        tk.Button(self.main_frame, text="获取元素", command=self.add_elements, font=("Arial", 12)).pack(pady=5)

        # 合成选择
        tk.Label(self.main_frame, text="选择合成类型：", font=("Arial", 12)).pack()
        self.synth_type = tk.StringVar(value="initial")
        tk.Radiobutton(self.main_frame, text="初级物品（随机）", variable=self.synth_type, value="initial").pack()
        tk.Radiobutton(self.main_frame, text="中级物品", variable=self.synth_type, value="intermediate").pack()
        tk.Radiobutton(self.main_frame, text="MBTI", variable=self.synth_type, value="mbti").pack()

        # 合成目标（中级和 MBTI）
        tk.Label(self.main_frame, text="合成目标（中级/MBTI）：", font=("Arial", 12)).pack()
        self.target_var = tk.StringVar(value=list(intermediate_recipes.keys())[0])
        self.target_menu = tk.OptionMenu(self.main_frame, self.target_var, *intermediate_recipes.keys())
        self.target_menu.pack()

        # 元素输入（初级合成）
        self.element_inputs = {}
        tk.Label(self.main_frame, text="输入元素数量（初级合成）：", font=("Arial", 12)).pack()
        for elem in ['water', 'fire', 'earth', 'air']:
            frame = tk.Frame(self.main_frame)
            frame.pack()
            tk.Label(frame, text=f"{elem}：").pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=5)
            entry.pack(side=tk.LEFT)
            self.element_inputs[elem] = entry

        # 物品选择（中级合成）
        tk.Label(self.main_frame, text="选择物品（中级合成）：", font=("Arial", 12)).pack()
        self.item_selections = {}
        for item in initial_items.keys() | intermediate_recipes.keys():
            frame = tk.Frame(self.main_frame)
            frame.pack()
            tk.Label(frame, text=f"{item}：").pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=5)
            entry.pack(side=tk.LEFT)
            self.item_selections[item] = entry

        # 合成按钮
        tk.Button(self.main_frame, text="合成！", command=self.synthesize, font=("Arial", 12)).pack(pady=10)

        # 结果显示
        self.result_text = tk.Text(self.main_frame, height=8, width=60, font=("Arial", 12))
        self.result_text.pack()

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

        # 更新下拉菜单
        menu = self.target_menu['menu']
        menu.delete(0, 'end')
        targets = (
            list(intermediate_recipes.keys()) if self.synth_type.get() == "intermediate" else
            list(mbti_targets.keys()) if self.synth_type.get() == "mbti" else
            []
        )
        for target in targets:
            menu.add_command(label=target, command=lambda t=target: self.target_var.set(t))
        if not self.target_var.get() in targets and targets:
            self.target_var.set(targets[0])

    def update_inputs(self, *args):
        """动态更新输入框状态"""
        synth_type = self.synth_type.get()

        # 元素输入框
        for elem in self.element_inputs:
            self.element_inputs[elem].config(state='normal' if synth_type == "initial" else 'disabled')
            self.element_inputs[elem].delete(0, tk.END)

        # 物品选择框
        for item in self.item_selections:
            self.item_selections[item].config(state='disabled')
            self.item_selections[item].delete(0, tk.END)
        if synth_type == "intermediate" and self.target_var.get() in intermediate_recipes:
            required = intermediate_recipes[self.target_var.get()]['items']
            for item in self.item_selections:
                if item in required:
                    self.item_selections[item].config(state='normal')

    def synthesize(self):
        """执行合成"""
        self.result_text.delete(1.0, tk.END)
        synth_type = self.synth_type.get()
        target = self.target_var.get()

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
                self.result_text.insert(tk.END, f"{msg}\n元素组成：{elements_str}\n")
            else:
                self.result_text.insert(tk.END, f"{msg}\n")

        elif synth_type == "intermediate":
            if target not in intermediate_recipes:
                messagebox.showerror("错误", "请选择有效配方！")
                return
            selected_items = {}
            for item in self.item_selections:
                try:
                    count = int(self.item_selections[item].get() or 0)
                    if count < 0:
                        raise ValueError
                    selected_items[item] = count
                except ValueError:
                    messagebox.showerror("错误", f"请输入有效的{item}数量！")
                    return
            required = intermediate_recipes[target]['items']
            for item in selected_items:
                if selected_items[item] > 0 and item not in required:
                    messagebox.showerror("错误", f"{target}无需{item}！")
                    return
            item_counts = {}
            for item in self.inventory:
                item_counts[item['name']] = item_counts.get(item['name'], 0) + 1
            for item, count in selected_items.items():
                if item_counts.get(item, 0) < count:
                    messagebox.showerror("错误", f"{item}库存不足！")
                    return
            input_inventory = []
            for item, count in selected_items.items():
                for _ in range(count):
                    for inv_item in self.inventory:
                        if inv_item['name'] == item:
                            input_inventory.append(inv_item)
                            break
            item, new_inventory, msg = synthesize_intermediate(input_inventory, target)
            if item:
                self.inventory = new_inventory
                self.inventory.append(item)
                self.result_text.insert(tk.END, f"{msg}\n获得：{item['name']}\n")
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


if __name__ == "__main__":
    root = tk.Tk()
    app = MBTISynthesisApp(root)
    root.mainloop()