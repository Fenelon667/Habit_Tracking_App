
"""
This test file verifies the Habit class functionality of the Habit Tracker application.
Tests are performed entirely in memory to ensure logic and formatting work independently of database state.

Covered features:
- Creating Habit instances using the class constructor (`__init__`)
- Verifying proper normalization of habit names to lowercase
- Preserving original casing via habit_name_display
- Exporting data as tuples using `to_db_tuple` for SQLite insertion
- Generating human-readable output using `__str__`
- Capturing and printing output for visual confirmation of class behavior
"""

import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from habit import Habit


def test_habit_initialization():
    habit = Habit(
        habit_name="Reading",
        frequency="daily",
        user_id=1,
        streak=5,
        longest_streak=10,
        habit_id=42
    )

    print("--- Habit Initialization ---")
    print(habit)  # triggers __str__ method

    assert habit.habit_id == 42
    assert habit.user_id == 1
    assert habit.habit_name == "reading"
    assert habit.habit_name_display == "Reading"
    assert habit.frequency == "daily"
    assert habit.streak == 5
    assert habit.longest_streak == 10
    assert habit.created_at is None


def test_to_db_tuple():
    habit = Habit("Workout", "weekly", 2, 1, 3)
    db_tuple = habit.to_db_tuple()
    expected = (2, "workout", "Workout", "weekly", 1, 3)

    print("--- DB Tuple ---")
    print(db_tuple)

    assert db_tuple == expected