# database.py
# 数据库操作，移除 trait 字段，支持三级物品存储

import sqlite3
import json
import os


def init_db():
    """初始化数据库，移除 trait 字段"""
    conn = sqlite3.connect('mbti_synthesis.db')
    c = conn.cursor()

    # 创建元素库存表
    c.execute('''CREATE TABLE IF NOT EXISTS elements
                 (element TEXT PRIMARY KEY, amount REAL)''')

    # 创建物品库存表
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  elements TEXT,
                  entries TEXT,
                  item_type TEXT)''')

    # 创建 MBTI 历史表，移除 trait 字段
    c.execute('''CREATE TABLE IF NOT EXISTS mbti_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  mbti TEXT,
                  ratios TEXT,
                  success INTEGER,
                  entries TEXT)''')

    conn.commit()
    conn.close()


def save_to_db(elements, inventory, mbti_history):
    """保存数据到数据库，移除 trait 存储"""
    conn = sqlite3.connect('mbti_synthesis.db')
    c = conn.cursor()

    # 保存元素库存
    c.execute('DELETE FROM elements')
    for element, amount in elements.items():
        c.execute('INSERT INTO elements (element, amount) VALUES (?, ?)', (element, amount))

    # 保存物品库存
    c.execute('DELETE FROM inventory')
    for item in inventory:
        elements_json = json.dumps(item['elements'])
        entries_json = json.dumps(item.get('entries', []))
        c.execute('INSERT INTO inventory (name, elements, entries, item_type) VALUES (?, ?, ?, ?)',
                  (item['name'], elements_json, entries_json, item['item_type']))

    # 保存 MBTI 历史，移除 trait
    c.execute('DELETE FROM mbti_history')
    for record in mbti_history:
        ratios_json = json.dumps(record['ratios'])
        entries_json = json.dumps(record.get('entries', []))
        c.execute('INSERT INTO mbti_history (mbti, ratios, success, entries) VALUES (?, ?, ?, ?)',
                  (record['mbti'], ratios_json, 1 if record['success'] else 0, entries_json))

    conn.commit()
    conn.close()


def load_from_db():
    """从数据库加载数据，兼容无 trait 的旧数据库"""
    elements = {'water': 0, 'fire': 0, 'earth': 0, 'air': 0}
    inventory = []
    mbti_history = []

    if not os.path.exists('mbti_synthesis.db'):
        return elements, inventory, mbti_history

    conn = sqlite3.connect('mbti_synthesis.db')
    c = conn.cursor()

    # 加载元素库存
    c.execute('SELECT element, amount FROM elements')
    for row in c.fetchall():
        elements[row[0]] = row[1]

    # 加载物品库存
    c.execute('SELECT name, elements, entries, item_type FROM inventory')
    for row in c.fetchall():
        item = {
            'name': row[0],
            'elements': json.loads(row[1]),
            'entries': json.loads(row[2]),
            'item_type': row[3]
        }
        inventory.append(item)

    # 加载 MBTI 历史，兼容旧数据库
    c.execute('PRAGMA table_info(mbti_history)')
    columns = [info[1] for info in c.fetchall()]
    has_trait = 'trait' in columns

    query = 'SELECT mbti, ratios, success, entries'
    if has_trait:
        query += ', trait'
    query += ' FROM mbti_history'

    c.execute(query)
    for row in c.fetchall():
        record = {
            'mbti': row[0],
            'ratios': json.loads(row[1]),
            'success': bool(row[2]),
            'entries': json.loads(row[3])
        }
        # 忽略旧数据库中的 trait
        mbti_history.append(record)

    conn.close()
    return elements, inventory, mbti_history