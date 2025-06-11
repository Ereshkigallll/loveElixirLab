# ui/history.py
# 查看 MBTI 历史逻辑，MBTI绿色

import tkinter as tk


def view_mbti_history(app):
    """查看 MBTI 历史记录"""
    if not app.mbti_history:
        tk.messagebox.showinfo("MBTI 历史", "暂无 MBTI 合成记录！快去合成吧！")
        return

    history_window = tk.Toplevel(app.root)
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

    text.tag_configure("mbti", foreground="#008000")  # MBTI：绿色

    reality_percent = {
        'ISFJ': 13.8, 'ESFJ': 12.0, 'ISTJ': 11.6, 'ISFP': 8.8, 'ESTJ': 8.7,
        'ESFP': 8.5, 'ENFP': 8.1, 'ISTP': 5.4, 'INFP': 4.4, 'ESTP': 4.3,
        'INTP': 3.3, 'ENTP': 3.2, 'ENFJ': 2.5, 'INTJ': 2.1, 'ENTJ': 1.8, 'INFJ': 1.5
    }
    for i, record in enumerate(app.mbti_history, 1):
        mbti = record['mbti']
        ratios = record['ratios']
        success = record['success']
        entries = record.get('entries', [])
        ratios_str = ", ".join(f"{k}: {v:.2f}" for k, v in ratios.items())
        status = "成功合成" if success else "保底合成"
        entries_str = f"，词条：{', '.join(e for e in entries)}" if entries else ""
        text.insert(tk.END, f"MBTI {i}: ", None)
        text.insert(tk.END, f"{mbti}", "mbti")
        text.insert(tk.END, f" (现实占比：{reality_percent.get(mbti, 0)}%)，比例：{ratios_str}，{status}{entries_str}\n",
                    None)

    text.config(state='disabled')
    tk.Button(history_window, text="关闭", command=history_window.destroy, font=("Arial", 12)).pack(pady=5)

    app.result_text.delete(1.0, tk.END)
    app.result_text.insert(tk.END, "水墨流转，MBTI 历史如卷轴展开，查看你的性格收藏！\n")