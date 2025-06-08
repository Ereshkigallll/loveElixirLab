# database.py
# SQLite 数据库操作：保存和加载元素、物品库存、MBTI历史，支持词条属性

import sqlite3
import json


def init_db():
    """初始化数据库，创建 elements、inventory 和 mbti_history 表，支持 entries 列"""
    conn = sqlite3.connect('mbti_synthesis.db')
    cursor = conn.cursor()

    # 创建 elements 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS elements (
            element TEXT PRIMARY KEY,
            amount REAL
        )
    ''')

    # 创建 inventory 表，新增 entries 列
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            elements TEXT,
            traits TEXT,
            entries TEXT,
            item_type TEXT
        )
    ''')

    # 创建 mbti_history 表，新增 entries 列
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mbti_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mbti TEXT,
            ratios TEXT,
            success INTEGER,
            trait TEXT,
            entries TEXT
        )
    ''')

    conn.commit()
    conn.close()


def save_to_db(elements, inventory, mbti_history):
    """保存元素、物品库存和 MBTI 历史到数据库，包括词条"""
    conn = sqlite3.connect('mbti_synthesis.db')
    cursor = conn.cursor()

    # 清空表
    cursor.execute('DELETE FROM elements')
    cursor.execute('DELETE FROM inventory')
    cursor.execute('DELETE FROM mbti_history')

    # 保存 elements
    for element, amount in elements.items():
        cursor.execute('INSERT INTO elements (element, amount) VALUES (?, ?)', (element, amount))

    # 保存 inventory
    for item in inventory:
        elements_json = json.dumps(item['elements'])
        traits_json = json.dumps(item.get('traits', []))
        entries_json = json.dumps(item.get('entries', []))
        cursor.execute('INSERT INTO inventory (name, elements, traits, entries, item_type) VALUES (?, ?, ?, ?, ?)',
                       (item['name'], elements_json, traits_json, entries_json, item['item_type']))

    # 保存 mbti_history
    for record in mbti_history:
        ratios_json = json.dumps(record['ratios'])
        entries_json = json.dumps(record.get('entries', []))
        cursor.execute('INSERT INTO mbti_history (mbti, ratios, success, trait, entries) VALUES (?, ?, ?, ?, ?)',
                       (record['mbti'], ratios_json, 1 if record['success'] else 0, record['trait'], entries_json))

    conn.commit()
    conn.close()


def load_from_db():
    """从数据库加载元素、物品库存和 MBTI 历史，包括词条"""
    try:
        conn = sqlite3.connect('mbti_synthesis.db')
        cursor = conn.cursor()

        # 加载 elements
        cursor.execute('SELECT element, amount FROM elements')
        elements = {row[0]: row[1] for row in cursor.fetchall()}

        # 加载 inventory
        cursor.execute('SELECT name, elements, traits, entries, item_type FROM inventory')
        inventory = []
        for row in cursor.fetchall():
            name, elements_json, traits_json, entries_json, item_type = row
            elements = json.loads(elements_json)
            traits = json.loads(traits_json) if traits_json else []
            entries = json.loads(entries_json) if entries_json else []
            inventory.append({
                'name': name,
                'elements': elements,
                'traits': traits,
                'entries': entries,
                'item_type': item_type
            })

        # 加载 mbti_history
        cursor.execute('SELECT mbti, ratios, success, trait, entries FROM mbti_history')
        mbti_history = []
        for row in cursor.fetchall():
            mbti, ratios_json, success, trait, entries_json = row
            ratios = json.loads(ratios_json)
            entries = json.loads(entries_json) if entries_json else []
            mbti_history.append({
                'mbti': mbti,
                'ratios': ratios,
                'success': bool(success),
                'trait': trait,
                'entries': entries
            })

        conn.close()
        return elements, inventory, mbti_history
    except (sqlite3.OperationalError, json.JSONDecodeError):
        # 数据库不存在或损坏，返回默认值
        return {'water': 10, 'fire': 10, 'earth': 0, 'air': 0}, [], []