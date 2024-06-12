import sqlite3

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    sql_create_table = """
    CREATE TABLE IF NOT EXISTS window_time (
        id INTEGER PRIMARY KEY,
        title TEXT,
        time_spent INTEGER,
        date TEXT
    )
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql_create_table)
    except sqlite3.Error as e:
        print(e)

def close_connection(conn):
    if conn:
        conn.close()


