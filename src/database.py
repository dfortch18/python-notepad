from config import CONFIG_FILE, DATA_PATH
import json
import sqlite3
import os
import pathlib

def _get_connection():
    with sqlite3.connect("data.sqlite") as conn:
        return conn

def create_tables():
    conn = _get_connection()

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS recent_files (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    conn.commit()

def get_recent_files(only_name: bool=False):
    conn = _get_connection()

    cur = conn.cursor()

    cur.execute("""SELECT * FROM recent_files""")
    files = cur.fetchall()

    if only_name:
        return [file[1] for file in files]
    else:
        return files

def add_recent_file(name: str):
    conn = _get_connection()

    cur = conn.cursor()

    cur.execute(f"""SELECT * FROM recent_files WHERE name='{name}'""")
    file = cur.fetchone()

    if file:
        cur.execute(f"""DELETE FROM recent_files WHERE name='{name}'""")
        conn.commit()
    cur.execute(f"""INSERT INTO recent_files (name) VALUES ('{name}')""")
    conn.commit()

def clear_recent_files():
    conn = _get_connection()

    cur = conn.cursor()

    cur.execute(f"""DELETE FROM recent_files""")
    conn.commit()

def setup():
    create_tables()

    if not os.path.exists(CONFIG_FILE):
        if not os.path.exists(DATA_PATH):
            os.mkdir(DATA_PATH)
        file = pathlib.Path(CONFIG_FILE)
        file.write_text('{"current_theme": "Default1", "text_colors": {"background": "white", "text": "black"}}')

def _get_config():
    with open(CONFIG_FILE, "r+") as f:
        content = json.load(f)
        return content

def set_theme(theme: str):
    config = _get_config()
    config["current_theme"] = theme

    data = json.dumps(config)

    with open(CONFIG_FILE, "w+") as f:
        f.write(data)

def get_theme():
    data = _get_config()
    return data["current_theme"]

def get_text_colors():
    data = _get_config()
    return data["text_colors"]

def set_text_colors(colors: tuple):
    config = _get_config()
    
    if len(config) == 2:
        config["text_colors"]["background"] = colors[0]
        config["text_colors"]["text"] = colors[1]
    else:
        config["text_colors"]["background"] = colors[0]

    data = json.dumps(config)

    with open(CONFIG_FILE, "w+") as f:
        f.write(data)