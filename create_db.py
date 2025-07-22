"""
Database setup module for the Habit Tracker application.

Handles the initialization and schema setup of the SQLite database (habit_tracker.db),
including creation of the core tables: 'users', 'habits', and 'habit_completions'.

Tables:
- users: Stores user accounts with unique, case-insensitive usernames and their display versions.
- habits: Stores user habits linked by foreign key to users, including frequency and streak data.
- habit_completions: Records timestamps of when habits are completed, linked by foreign key to habits.

Functions:
- initialize_database(): Creates the database file (if not present) and ensures all required tables
  exist with appropriate constraints and foreign key enforcement.
- get_db_file(): Returns the path or filename of the database file (constant).
- (Optional) list_tables(): Prints existing tables in the database for inspection (if implemented).
"""

import sqlite3

DB_FILE = "habit_tracker.db" #database filename (constant)
def get_db_file():
    """
    Returns the path or filename of the SQLite database file used by the application.

    Returns:
        str: The filename or path of the SQLite database (e.g., 'habit_tracker.db').
    """
    return DB_FILE


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
    
    """
    Creates and initializes the SQLite database with required tables.

    This function connects to the SQLite database file specified by `DB_FILE`.
    It enables foreign key constraints and creates the following tables if they
    do not already exist:

    - users: stores user account information with unique usernames.
    - habits: stores habits linked to users with frequency and streak information.
    - habit_completions: stores timestamps of habit completions linked to habits.

    Any SQL operational errors during creation are caught and printed.

    Side effects:
        Creates the database file and tables if missing.
        Prints status messages regarding database initialization.

    Raises:
        sqlite3.OperationalError: If there is an error executing SQL commands.
    """
    
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

if __name__ == "__main__":
    initialize_database()




