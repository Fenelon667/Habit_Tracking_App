"""
Database setup module for the Habit Tracker application.

This module handles the initialization of the SQLite database (habit_tracker.db),
including creation of the 'users', 'habits', and 'habit_completions' tables,
along with optional database inspection utilities.

Tables:
- users: Stores user accounts with unique usernames.
- habits: Stores habit entries linked to users via a foreign key relationship.
- habit_completions: Stores individual timestamps for when a habit was marked completed.

Functions:
- initialize_database(): Creates the database file (if it doesn't exist) and ensures
  all required tables are present with proper constraints.
- list_tables(): Prints all tables in the database (for debugging purposes).
"""

import sqlite3

DB_FILE = "habit_tracker.db" #database filename (constant)


# users DB table schema
create_users_table_sql = '''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT UNIQUE NOT NULL,
    user_name_display TEXT NOT NULL
)
'''


# Habit.Tracking DB table schema
create_habits_table_sql = '''
CREATE TABLE IF NOT EXISTS habits (
    habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    habit_name TEXT NOT NULL,
    habit_name_display TEXT NOT NULL,
    frequency TEXT CHECK(frequency IN ('daily', 'weekly')),
    streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, habit_name),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
'''

# Habit completions DB table schema
create_completions_table_sql = '''
CREATE TABLE IF NOT EXISTS habit_completions (
    completion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits(habit_id) ON DELETE CASCADE
)
'''




def initialize_database():
    """Creates the SQLite database and initializes the users, habits, and completions tables."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")  # enforce foreign key constraints
            cursor.execute(create_users_table_sql)
            cursor.execute(create_habits_table_sql)
            cursor.execute(create_completions_table_sql)
            conn.commit()
            print("Database initialized or already present.")  # -----------------------------REMOVE ----------------
    except sqlite3.OperationalError as e:
        print(f"SQL error during database initialization: {e}")




