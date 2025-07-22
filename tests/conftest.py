"""
This file defines shared pytest fixtures for the Habit Tracker application.
These fixtures ensure test isolation, in-memory database operations, and schema consistency
across all test modules.

Defined fixtures:

- test_db:
    Provides an in-memory SQLite database with the full production schema
    (users, habits, habit_completions), used for all DB-related tests.

- clean_test_db:
    Automatically clears all tables and resets auto-increment counters before each test
    to ensure a clean and isolated environment.

- mock_db_file:
    Replaces the DB_FILE path in key modules with an in-memory database URI
    to prevent writing to the real `habit_tracker.db` during tests.
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
import analytics
import habit_flow


@pytest.fixture
def test_db():
    """Provide an in-memory SQLite database with required tables."""
    conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create tables with schema matching production
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT UNIQUE NOT NULL,
            user_name_display TEXT NOT NULL
        )
    """)
    cursor.execute("""
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
    """)
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
    """Clear all tables and reset autoincrement before each test for isolation."""
    cursor = test_db.cursor()

    # Clear in order respecting foreign key constraints
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

    # Patch get_db_file in the create_db module itself
    monkeypatch.setattr(create_db, "get_db_file", lambda: memory_uri)
    
    # Patch get_db_file inside habit_flow module (because it imports create_db)
    monkeypatch.setattr(habit_flow.create_db, "get_db_file", lambda: memory_uri)

    # Patch get_db_file inside user_flow module (because it imports create_db)
    monkeypatch.setattr(user_flow.create_db, "get_db_file", lambda: memory_uri)

    # Patch DB_FILE in analytics if used directly
    monkeypatch.setattr(analytics, "DB_FILE", memory_uri)