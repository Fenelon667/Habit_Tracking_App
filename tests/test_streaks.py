""" IN WORK """


import os
import sys
import pytest


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from datetime import datetime, timedelta
from streaks import calculate_streaks, update_streaks
from create_db import DB_FILE



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
    ("daily", [1, 3, 4], (2, 2)),
    ("daily", [2, 3, 4], (3, 3)),
    ("daily", [5, 6, 7], (0, 3)),
    ("weekly", [7, 14, 21], (3, 3)),
    ("weekly", [8, 15, 22], (1, 1)),
])
def test_calculate_streaks(test_db, frequency, completions, expected):
    habit_id = setup_habit_with_completions(test_db, frequency, completions)
    assert calculate_streaks(habit_id) == expected


def test_update_streaks_updates_database(test_db):
    habit_id = setup_habit_with_completions(test_db, "daily", [1, 2, 3])
    update_streaks(habit_id)

    cursor = test_db.cursor()
    cursor.execute("SELECT streak, longest_streak FROM habits WHERE habit_id = ?", (habit_id,))
    result = cursor.fetchone()

    assert result == (3, 3)