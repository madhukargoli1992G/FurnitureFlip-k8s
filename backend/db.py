import sqlite3
import json
from typing import Dict, Any, List

DB_PATH = "furnitureflip.db"


def conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    c = conn()
    cur = c.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payload TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS comps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        payload TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )
    """)
    c.commit()
    c.close()


def insert_item(payload: Dict[str, Any]) -> int:
    c = conn()
    cur = c.cursor()
    cur.execute("INSERT INTO items(payload) VALUES (?)", (json.dumps(payload),))
    c.commit()
    item_id = cur.lastrowid
    c.close()
    return item_id


def insert_comps(item_id: int, comps: List[Dict[str, Any]]):
    c = conn()
    cur = c.cursor()
    cur.execute("DELETE FROM comps WHERE item_id=?", (item_id,))
    for comp in comps or []:
        cur.execute("INSERT INTO comps(item_id, payload) VALUES (?, ?)", (item_id, json.dumps(comp)))
    c.commit()
    c.close()


def get_item(item_id: int) -> Dict[str, Any]:
    c = conn()
    cur = c.cursor()
    cur.execute("SELECT payload FROM items WHERE id=?", (item_id,))
    row = cur.fetchone()
    c.close()
    return json.loads(row[0]) if row else {}


def get_comps(item_id: int) -> List[Dict[str, Any]]:
    c = conn()
    cur = c.cursor()
    cur.execute("SELECT payload FROM comps WHERE item_id=?", (item_id,))
    rows = cur.fetchall()
    c.close()
    return [json.loads(r[0]) for r in rows]
