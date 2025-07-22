"""
This test file verifies the Habit class functionality of the Habit Tracker application.
All tests are performed in memory, independently of the database, to ensure correctness
of data normalization, formatting, and class methods.

Covered features:
- Creating Habit instances using the class constructor (`__init__`)
- Normalizing habit names to lowercase for internal consistency
- Preserving original casing via `habit_name_display` for display purposes
- Exporting class data using `to_db_tuple` for SQLite insertion
- Generating human-readable string output via `__str__`
- Capturing and printing outputs for manual inspection
"""

import sys
import os
from habit import Habit

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


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