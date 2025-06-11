# main.py
# 主程序：UI 初始化，调用 UI 模块，自动判断合成类型，简化界面，三级物品橘色，MBTI绿色

import tkinter as tk
from ui import add_elements, update_display, update_inputs, view_inventory_details, view_mbti_history, synthesize
from database import init_db, load_from_db
import os


class MBTISynthesisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MBTI 元素合成系统")

        # 初始化数据库
        init_db()

        # 检查旧数据库
        if os.path.exists('mbti_synthesis.db'):
            response = tk.messagebox.askyesno(
                "数据库更新提示",
                "物品名称已更新为中文，建议清空旧数据库（mbti_synthesis.db）以避免冲突！是否清空？"
            )
            if response:
                os.remove('mbti_synthesis.db')
                init_db()

        # 加载数据
        self.elements, self.inventory, self.mbti_history = load_from_db()

        # 绑定 UI 模块函数到类实例
        self.add_elements = lambda: add_elements(self)
        self.update_display = lambda: update_display(self)
        self.update_inputs = lambda: update_inputs(self)
        self.view_inventory_details = lambda: view_inventory_details(self)
        self.view_mbti_history = lambda: view_mbti_history(self)
        self.synthesize = lambda: synthesize(self)

        # 主框架
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill='both', expand=True)

        # 元素库存显示
        self.elements_label = tk.Label(self.main_frame, text="元素库存：加载中...", font=("Arial", 12))
        self.elements_label.pack(anchor='w', pady=5)

        # 物品库存显示
        self.inventory_frame = tk.Frame(self.main_frame)
        self.inventory_frame.pack(anchor='w', pady=5)

        # 元素输入
        tk.Label(self.main_frame, text="输入元素数量：", font=("Arial", 12)).pack(anchor='w', pady=5)
        self.element_inputs = {}
        for elem in ['water', 'fire', 'earth', 'air']:
            frame = tk.Frame(self.main_frame)
            frame.pack(anchor='w', fill='x', pady=2)
            tk.Label(frame, text=f"{elem}：", width=10).pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=5, state='normal', takefocus=True)
            entry.pack(side=tk.LEFT, padx=5)
            self.element_inputs[elem] = entry

        # 物品选择
        tk.Label(self.main_frame, text="选择物品：", font=("Arial", 12)).pack(anchor='w', pady=5)
        self.item_selection_frame = tk.Frame(self.main_frame)
        self.item_selection_frame.pack(fill='both', expand=True, pady=5)
        self.item_checkboxes = {}
        self.item_vars = {}

        # 按钮
        tk.Button(self.main_frame, text="获取元素", command=self.add_elements, font=("Arial", 12)).pack(pady=5)
        tk.Button(self.main_frame, text="查看库存详情", command=self.view_inventory_details, font=("Arial", 12)).pack(
            pady=5)
        tk.Button(self.main_frame, text="查看 MBTI 历史", command=self.view_mbti_history, font=("Arial", 12)).pack(
            pady=5)
        tk.Button(self.main_frame, text="合成！", command=self.synthesize, font=("Arial", 12)).pack(pady=10)

        # 结果显示
        self.result_text = tk.Text(self.main_frame, height=8, width=60, font=("Arial", 12))
        self.result_text.pack(anchor='w', pady=5)

        # 配置文本颜色
        self.result_text.tag_configure("initial", foreground="#0000FF")
        self.result_text.tag_configure("intermediate", foreground="#800080")
        self.result_text.tag_configure("third", foreground="#FFA500")  # 三级物品：橘色
        self.result_text.tag_configure("mbti", foreground="#008000")  # MBTI：绿色
        self.result_text.tag_configure("error", foreground="#FF0000")

        # 初始更新
        self.update_display()
        self.update_inputs()
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "数据加载成功，蓝色水晶与紫色灵液就位！\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = MBTISynthesisApp(root)
    root.mainloop()