import sqlite3
from database import create_connection, create_table, close_connection

db_file = "screentime.db"
conn = create_connection(db_file)

if conn is not None:
    create_table(conn)
else:
    print("Error: Unable to connect to the database.")
    exit(1)

def add_to_db(data):
    if conn is None:
        print("Error: Database connection is not established.")
        return

    try:
        cursor = conn.cursor()
        for title, time_spent in data.items():
            cursor.execute("SELECT * FROM window_time WHERE (title) = (?)", (title,))
            rows = cursor.fetchall()
            if rows != []:
                cursor.execute("UPDATE window_time SET (time_spent) = (?) WHERE (title) = (?)", (time_spent, title))
            else:
                cursor.execute("INSERT INTO window_time (title, time_spent) VALUES (?, ?)", (title, time_spent))
        conn.commit()
        print("Data added to the database successfully.")
        close_connection(conn)
    except sqlite3.Error as e:
        print(f"Error: {e}")
        close_connection(conn)


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
            final_list.append(modded_row)

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        if conn:
            conn.close()
        return final_list

