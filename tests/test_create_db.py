"""
This test file verifies the database initialization functionality of the Habit Tracker application.
Tests are executed using a temporary SQLite database file to ensure the real habit_tracker.db remains unaffected.

Covered features:
- Initializing the database using `initialize_database`
- Creating the 'users', 'habits', and 'habit_completions' tables
- Enabling and validating foreign key constraints
- Verifying table creation and schema structure using PRAGMA statements
- Capturing and printing database state and structure for visual confirmation
"""

import sqlite3
import pytest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from create_db import initialize_database

# --------------------------- TEST: Initiate Database ------------------------------
def test_initialize_database(tmp_path, monkeypatch, capfd):
    temp_db = tmp_path / "test_habit_tracker.db"
    monkeypatch.setattr("create_db.DB_FILE", str(temp_db))

    initialize_database()

    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        # Tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        print("Tables in DB:", tables)

        # Foreign Key enforcement status
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        print("Foreign keys enabled:", fk_status)

        # Schemas
        cursor.execute("PRAGMA table_info(users)")
        users_schema = cursor.fetchall()
        print("Users schema:", users_schema)

        cursor.execute("PRAGMA table_info(habits)")
        habits_schema = cursor.fetchall()
        print("Habits schema:", habits_schema)

        cursor.execute("PRAGMA table_info(habit_completions)")
        completions_schema = cursor.fetchall()
        print("Habit Completions schema:", completions_schema)

        # Foreign key structure checks
        cursor.execute("PRAGMA foreign_key_list(habits)")
        habit_fk = cursor.fetchall()
        print("Foreign keys in 'habits':", habit_fk)

        cursor.execute("PRAGMA foreign_key_list(habit_completions)")
        completions_fk = cursor.fetchall()
        print("Foreign keys in 'habit_completions':", completions_fk)

        # Assertions
        assert "users" in tables
        assert "habits" in tables
        assert "habit_completions" in tables
        assert fk_status == 1
        assert len(habit_fk) == 1
        assert len(completions_fk) == 1

        # Verify required fields in 'users'
        user_columns = {col[1] for col in users_schema}
        assert "user_name" in user_columns
        assert "user_name_display" in user_columns

        # Verify required fields in 'habits'
        habit_columns = {col[1] for col in habits_schema}
        assert "habit_name" in habit_columns
        assert "habit_name_display" in habit_columns
        assert "created_at" in habit_columns

    # Output check
    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_initialize_database ---")
    print(out)
    assert "Tables in DB:" in out
    assert "users" in out
    assert "habits" in out
    assert "habit_completions" in out
    assert "Foreign keys enabled: 1" in out


# --------------------------- TEST: Auto-population of created_at ------------------------------

def test_created_at_is_auto_populated(tmp_path, monkeypatch):
    temp_db = tmp_path / "test_created_at.db"
    monkeypatch.setattr("create_db.DB_FILE", str(temp_db))

    from create_db import initialize_database
    initialize_database()

    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()

        # Insert user with both required fields
        cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("testuser", "TestUser"))
        user_id = cursor.lastrowid

        # Insert habit with required display fields
        cursor.execute("""
            INSERT INTO habits (user_id, habit_name, habit_name_display, frequency, streak, longest_streak)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, "testhabit", "TestHabit", "daily", 0, 0))

        # Verify created_at was auto-populated
        cursor.execute("SELECT created_at FROM habits WHERE habit_name = ?", ("testhabit",))
        created_at = cursor.fetchone()[0]

        assert created_at is not None
        print("created_at timestamp:", created_at)