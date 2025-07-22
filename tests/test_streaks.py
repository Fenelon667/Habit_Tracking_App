"""
This test file verifies the streak calculation and update logic for the Habit Tracker application.
Tests are run using an in-memory SQLite database to simulate habit completions and validate streak logic.

Covered features:
- calculate_streaks:
    - Correctly identifies current and longest streaks for daily and weekly habits
    - Handles gaps and resets in streaks
    - Ignores multiple completions in the same interval
    - Resets current streak if latest completion is too old
- update_streaks:
    - Persists calculated streak values into the database

Each test simulates a habit with custom completion timestamps and verifies expected outcomes.
"""

import os
import sys
import pytest
from datetime import datetime, timedelta

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from streaks import calculate_streaks, update_streaks



def setup_habit_with_completions(conn, frequency, days_ago_list):
    cursor = conn.cursor()

    # Insert user
    cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("tester", "Tester"))
    user_id = cursor.lastrowid

    # Insert habit
    cursor.execute("""
        INSERT INTO habits (user_id, habit_name, habit_name_display, frequency)
        VALUES (?, ?, ?, ?)
    """, (user_id, "testhabit", "TestHabit", frequency))
    habit_id = cursor.lastrowid

    # Insert completions
    now = datetime.now()
    for days in days_ago_list:
        completion_time = (now - timedelta(days=days)).isoformat()
        cursor.execute("""
            INSERT INTO habit_completions (habit_id, completed_at)
            VALUES (?, ?)
        """, (habit_id, completion_time))

    conn.commit()
    return habit_id


@pytest.mark.parametrize("frequency, completions, expected", [
    ("daily", [1, 2, 3], (3, 3)),
    ("daily", [1, 3, 4], (1, 2)),
    ("daily", [2, 3, 4], (0, 3)),
    ("daily", [5, 6, 7], (0, 3)),
    ("weekly", [7, 14, 21], (3, 3)),
    ("weekly", [8, 15, 22], (0, 3)),
])
def test_calculate_streaks(test_db, frequency, completions, expected):
    """
    Parametrized test for calculating streaks for different completion scenarios.
    """
    habit_id = setup_habit_with_completions(test_db, frequency, completions)
    cursor = test_db.cursor()
    assert calculate_streaks(habit_id, cursor) == expected



def test_update_streaks_updates_database(test_db):
    """
    Ensures update_streaks() persists calculated values into the database.
    """
    habit_id = setup_habit_with_completions(test_db, "daily", [1, 2, 3])
    cursor = test_db.cursor()
    update_streaks(habit_id, cursor)

    cursor.execute("SELECT streak, longest_streak FROM habits WHERE habit_id = ?", (habit_id,))
    result = cursor.fetchone()
    assert result == (3, 3)