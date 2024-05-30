from datetime import datetime
import sqlite3
from database import create_connection, create_table, close_connection
from current_time import get_current_time


current_date = get_current_time()
#current_date = "31-05-2024"
db_file = "screentime.db"
conn = create_connection(db_file)

if conn is not None:
    create_table(conn)
else:
    print("Error: Unable to connect to the database.")
    exit(1)

def add_to_db(data, date):
    if conn is None:
        print("Error: Database connection is not established.")
        return
    current_date = date
    try:
        cursor = conn.cursor()
        for title, time_spent in data.items():
            cursor.execute("SELECT * FROM window_time WHERE (title) = (?) AND (date) = (?);", (title,current_date))
            rows = cursor.fetchall()
            if rows != []:
                cursor.execute("UPDATE window_time SET (time_spent) = (?) WHERE (title) = (?) AND (date) = (?);", (time_spent, title, current_date))
            else:
                cursor.execute("INSERT INTO window_time (title, time_spent, date) VALUES (?, ?, ?);", (title, time_spent, current_date))
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

        cursor.execute("SELECT * FROM window_time;")

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

def read_from_db_date(date):
    final_list = []
    try:
        conn = sqlite3.connect('screentime.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM window_time WHERE date = (?);", (date,))

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