import sqlite3

def read_from_db():
    final_list = []
    try:
        conn = sqlite3.connect('screentime.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM window_time")

        rows = cursor.fetchall()

        for row in rows:
            modded_row = []
            modded_row.append(row[1])
            modded_row.append(row[2])
            modded_row.append(row[3])
            final_list.append(modded_row)

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        for entry in final_list:
            print(entry)
        
        
        if conn:
            conn.close()

read_from_db()