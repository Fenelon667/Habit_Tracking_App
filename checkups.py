"""
This module is for checkup reasons only

"""

import sqlite3
import os

from create_db import DB_FILE


def list_tables(database=DB_FILE):
    """Prints all tables in the SQLite database (for debugging)."""
    try:
        with sqlite3.connect(database) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("Tables found in DB:", tables)
    except sqlite3.Error as e:
        print(f"Error listing tables: {e}")
    print("Tables found in DB:", [t[0] for t in tables])


def show_table_schema(table_name):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print(f"Schema for table '{table_name}':")
        for col in columns:
            print(col)


# Entry point to execute functions
if __name__ == "__main__":
    list_tables()
    show_table_schema("users")
    show_table_schema("habits")




def view_all_data():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        print("\n=== Users Table ===")
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        user_columns = [desc[0] for desc in cursor.description]
        print(" | ".join(user_columns))
        for row in users:
            print(" | ".join(str(item) for item in row))

        print("\n=== Habits Table ===")
        cursor.execute("SELECT * FROM habits")
        habits = cursor.fetchall()
        habit_columns = [desc[0] for desc in cursor.description]
        print(" | ".join(habit_columns))
        for row in habits:
            print(" | ".join(str(item) for item in row))

        print("\n=== Habit Completions Table ===")
        cursor.execute("SELECT * FROM habit_completions")
        completions = cursor.fetchall()
        completion_columns = [desc[0] for desc in cursor.description]
        print(" | ".join(completion_columns))
        for row in completions:
            print(" | ".join(str(item) for item in row))

def view_user_data(username):
    import sqlite3
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM habit_tracker WHERE user_name = ?", (username,))
        habits = cursor.fetchall()

        if not habits:
            print(f"\nNo habits found for user '{username}'.")
            return

        habit_columns = [desc[0] for desc in cursor.description]
        print(f"\n Habits for user '{username}':")
        print(" | ".join(habit_columns))  # print headers
        for row in habits:
            print(" | ".join(str(item) for item in row))

