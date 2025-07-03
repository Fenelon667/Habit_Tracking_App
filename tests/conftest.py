"""
This file is used by pytest to define reusable fixtures shared across all test files
in the Habit Tracker application.

Defined fixtures:

- clean_test_db:
    Clears 'users', 'habits', and 'habit_completions' tables and resets auto-increment IDs
    before each test to ensure isolation and avoid test interference.

- test_db:
    Sets up an in-memory SQLite database with the production schema.
    Used for all database-related tests without affecting real data.

- mock_db_file:
    Replaces DB_FILE in all modules with an in-memory database ('file::memory:?cache=shared')
    to prevent changes to the real habit_tracker.db during tests.

These fixtures ensure a clean, reliable, and isolated environment for consistent test execution.
"""

import sqlite3
import pytest
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import user_flow
import create_db


@pytest.fixture
def test_db():
    """Provides an in-memory SQLite database with 'users', 'habits', and 'habit_completions' tables."""
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create users table (updated schema)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT UNIQUE NOT NULL,
            user_name_display TEXT NOT NULL
        )
    """)

    # Create habits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            habit_name TEXT NOT NULL,
            frequency TEXT CHECK(frequency IN ('daily', 'weekly')),
            streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, habit_name),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # Create habit_completions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit_completions (
            completion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(habit_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def clean_test_db(test_db):
    """Automatically clears all tables before each test."""
    cursor = test_db.cursor()

    # Clear child tables first due to foreign key constraints
    cursor.execute("DELETE FROM habit_completions")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='habit_completions'")

    cursor.execute("DELETE FROM habits")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='habits'")

    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='users'")

    test_db.commit()


@pytest.fixture(autouse=True)
def mock_db_file(monkeypatch):
    memory_uri = "file::memory:?cache=shared"
    monkeypatch.setattr(user_flow, "DB_FILE", memory_uri)
    monkeypatch.setattr(create_db, "DB_FILE", memory_uri)