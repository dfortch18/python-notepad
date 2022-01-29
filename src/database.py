import sqlite3

def _get_connection():
    with sqlite3.connect("data.sqlite") as conn:
        return conn

def create_tables():
    conn = _get_connection()
    cur = conn.cursor()

    query = """CREATE TABLE IF NOT EXISTS recently_used (
        name TEXT NOT NULL,
        modifield DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )"""

    cur.execute(query)

    conn.commit()

def get_recently_files():
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM recently_used")
    data = cur.fetchall()

    return data

def add_file(name):
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM recently_used WHERE name == '{name}'")
    exists = cur.fetchone()

    if exists:
        cur.execute(f"DELETE FROM recently_used WHERE name == '{name}'")
        conn.commit()
    
    cur.execute(f"INSERT INTO recently_used (name) VALUES ('{name}')")
    conn.commit()

def delete_files():
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM recently_used")

    conn.commit()