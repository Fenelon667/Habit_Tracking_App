"""
This test file verifies the habit-related flow functions of the Habit Tracker application.
Tests are performed using an in-memory SQLite database and monkeypatched input to simulate user interactions.

Covered features:
- Creating habits:
    - test_create_habit_success: user enters a valid name and selects a frequency
    - test_create_habit_duplicate_name: user tries to create a habit with a duplicate name
    - test_create_habit_cancel: user types 'back' to cancel the process
- Selecting habit frequency:
    - test_select_frequency_valid: user selects a valid frequency from the list
    - test_select_frequency_cancel: user chooses to go back or exit
- Deleting habits:
    - test_delete_habit_confirm_yes: user confirms deletion
    - test_delete_habit_confirm_no: user declines deletion
- Completing habits:
    - test_mark_habit_completed_new_streak: user completes an eligible habit
    - test_mark_habit_completed_too_early: user tries to complete before interval
    - test_mark_habit_completed_due_today_filter: user views and completes only habits due today

Notes:
- User inputs are mocked via monkeypatch to avoid interactive prompts.
- All database actions run on a temporary in-memory instance to avoid affecting production data.
"""

import pytest
import os
import sys
from habit_flow import create_habit, select_frequency
import habit_flow
from datetime import datetime


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# -------------------------------- TEST: create_habit: Successfully create a habit ---------------------------------------

def test_create_habit_success(monkeypatch, test_db, capfd):
    """
    Simulates a successful habit creation with valid input.
    Verifies the habit is added to the database.
    """
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("tester", "Tester"))
    user_id = cursor.lastrowid
    test_db.commit()

    inputs = iter(["Read", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("sqlite3.connect", lambda *a, **kw: test_db)

    create_habit(user_id, "Tester")

    out, err = capfd.readouterr()
    print("--- OUTPUT for test_create_habit_success ---")
    print(out)
    assert "✅ Habit 'Read' (daily) created for user Tester." in out

    cursor.execute("SELECT habit_name, habit_name_display, frequency FROM habits WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    assert result is not None
    assert result[0] == "read"
    assert result[1] == "Read"
    assert result[2] == "daily"


# -------------------------------- TEST: create_habit: User uses duplicate name ---------------------------------------

def test_create_habit_duplicate_name(monkeypatch, test_db, capfd):
    """
    Tests that duplicate habit names for the same user are not allowed.
    The user tries to create a duplicate, gets rejected, and then enters a new name.
    """
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("tester", "Tester"))
    user_id = cursor.lastrowid
    cursor.execute("""
        INSERT INTO habits (user_id, habit_name, habit_name_display, frequency)
        VALUES (?, ?, ?, ?)
    """, (user_id, "read", "Read", "daily"))
    test_db.commit()

    inputs = iter(["Read", "Read", "Walk", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("sqlite3.connect", lambda *a, **kw: test_db)

    create_habit(user_id, "Tester")

    out, err = capfd.readouterr()
    print("--- OUTPUT for test_create_habit_duplicate_name ---")
    print(out)
    assert "❌ You already have a habit named 'Read'. Choose a different name." in out
    assert "✅ Habit 'Walk' (daily) created for user Tester." in out

    cursor.execute("SELECT habit_name, habit_name_display FROM habits WHERE user_id = ? ORDER BY habit_id", (user_id,))
    rows = cursor.fetchall()
    assert len(rows) == 2
    assert rows[0][0] == "read"
    assert rows[1][0] == "walk"
    assert rows[1][1] == "Walk"


# -------------------------------- TEST: create_habit: User cancels habit creation ---------------------------------------

def test_create_habit_cancel(monkeypatch, test_db, capfd):
    """
    Simulates a user canceling the habit creation by typing 'back'.
    Verifies that no habit is added to the database.
    """
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("tester", "Tester"))
    user_id = cursor.lastrowid
    test_db.commit()

    inputs = iter(["back"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("sqlite3.connect", lambda *a, **kw: test_db)

    create_habit(user_id, "Tester")

    out, err = capfd.readouterr()
    print("--- OUTPUT for test_create_habit_cancel ---")
    print(out)
    assert "↩️ Habit creation cancelled." in out

    cursor.execute("SELECT * FROM habits WHERE user_id = ?", (user_id,))
    results = cursor.fetchall()
    assert results == []


# -------------------------------- TEST: Select Frequency: User selects a valid frequency ---------------------------------------

def test_select_frequency_valid(monkeypatch, capfd):
    """
    Simulates a user selecting 'daily' frequency.
    Verifies that the correct string 'daily' is returned.
    """
    monkeypatch.setattr(habit_flow, "get_valid_index_input", lambda *a, **kw: 0)
    result = select_frequency()
    out, _ = capfd.readouterr()
    print("--- OUTPUT for test_select_frequency_valid ---")
    print(f"Selected frequency: {result}")
    assert result == "daily"


# -------------------------------- TEST: Select Frequency: User chooses to go back ---------------------------------------

def test_select_frequency_cancel_go_back(monkeypatch):
    """
    Simulates user choosing 'Go back' during frequency selection.
    Verifies that the function returns None.
    """
    monkeypatch.setattr(habit_flow, "get_valid_index_input", lambda *a, **kw: None)
    result = select_frequency()
    assert result is None


# -------------------------------- TEST: Select Frequency: User chooses to exit application ---------------------------------------

def test_select_frequency_cancel_exit(monkeypatch):
    """
    Simulates user choosing 'Exit Application' during frequency selection.
    Verifies that the function raises SystemExit.
    """
    monkeypatch.setattr(habit_flow, "get_valid_index_input", lambda *a, **kw: "exit")
    with pytest.raises(SystemExit):
        select_frequency()


# -------------------------------- TEST: Delete Habit: User confirms deletion -----------------------------------------------

def test_delete_habit_confirm_yes(monkeypatch, test_db, capfd):
    """
    Simulates a user confirming deletion of a habit.
    Verifies that the habit is deleted from the database.
    """
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("tester", "Tester"))
    user_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO habits (user_id, habit_name, habit_name_display, frequency) VALUES (?, ?, ?, ?)",
        (user_id, "read", "Read", "daily")
    )
    test_db.commit()

    monkeypatch.setattr(habit_flow, "get_valid_index_input", lambda *a, **kw: 0)
    monkeypatch.setattr(habit_flow, "get_yes_no_numbered", lambda prompt: True)

    habit_flow.delete_habit(user_id)

    out, _ = capfd.readouterr()
    print("--- OUTPUT for test_delete_habit_confirm_yes ---")
    print(out)

    cursor.execute("SELECT COUNT(*) FROM habits WHERE user_id = ?", (user_id,))
    assert cursor.fetchone()[0] == 0


# -------------------------------- TEST: Delete Habit: User cancels deletion -------------------------------------------

def test_delete_habit_confirm_no(monkeypatch, test_db, capfd):
    """
    Simulates a user declining the deletion of a habit.
    Verifies that the habit remains in the database.
    """
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("tester", "Tester"))
    user_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO habits (user_id, habit_name, habit_name_display, frequency) VALUES (?, ?, ?, ?)",
        (user_id, "read", "Read", "daily")
    )
    test_db.commit()

    monkeypatch.setattr(habit_flow, "get_valid_index_input", lambda *a, **kw: 0)
    monkeypatch.setattr(habit_flow, "get_yes_no_numbered", lambda prompt: False)

    habit_flow.delete_habit(user_id)

    out, _ = capfd.readouterr()
    print("--- OUTPUT for test_delete_habit_confirm_no ---")
    print(out)

    cursor.execute("SELECT COUNT(*) FROM habits WHERE user_id = ?", (user_id,))
    assert cursor.fetchone()[0] == 1


# -------------------------------- TEST: Complete Habit: Successfully completed (New streak) ----------------------------------------

def test_mark_habit_completed_new_streak(monkeypatch, test_db, capfd):
    """
    Simulates marking a habit as completed when eligible.
    Verifies the streak is updated and completion is recorded.
    """
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("tester", "Tester"))
    user_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO habits (user_id, habit_name, habit_name_display, frequency, streak, longest_streak)
        VALUES (?, ?, ?, ?, 0, 0)
    """, (user_id, "read", "Read", "daily"))
    test_db.commit()

    monkeypatch.setattr(habit_flow, "get_valid_index_input", lambda *a, **kw: 0)
    monkeypatch.setattr(habit_flow, "get_yes_no_numbered", lambda prompt: False)

    habit_flow.mark_habit_completed(user_id, "Tester")

    out, _ = capfd.readouterr()
    print("--- OUTPUT for test_mark_habit_completed_new_streak ---")
    print(out)

    assert "marked as completed" in out
    assert "Current streak:" in out

    cursor.execute("SELECT COUNT(*) FROM habit_completions")
    count = cursor.fetchone()[0]
    assert count == 1


# -------------------------------- TEST: Complete Habit: Completion too early ----------------------------------------

def test_mark_habit_completed_too_early(monkeypatch, test_db, capfd):
    """
    Simulates trying to complete a habit too early.
    Verifies user is informed and no new completion recorded.
    """
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("tester", "Tester"))
    user_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO habits (user_id, habit_name, habit_name_display, frequency, streak, longest_streak)
        VALUES (?, ?, ?, ?, 1, 3)
    """, (user_id, "read", "Read", "daily"))
    habit_id = cursor.lastrowid

    now = datetime.now()
    cursor.execute("""
        INSERT INTO habit_completions (habit_id, completed_at) VALUES (?, ?)
    """, (habit_id, now.isoformat()))
    test_db.commit()

    monkeypatch.setattr(habit_flow, "get_valid_index_input", lambda *a, **kw: 0)
    monkeypatch.setattr(habit_flow, "get_yes_no_numbered", lambda prompt: False)

    habit_flow.mark_habit_completed(user_id, "Tester")

    out, _ = capfd.readouterr()
    print("--- OUTPUT for test_mark_habit_completed_too_early ---")
    print(out)

    assert "already completed this day" in out or "already completed this week" in out

    cursor.execute("SELECT COUNT(*) FROM habit_completions WHERE habit_id = ?", (habit_id,))
    assert cursor.fetchone()[0] == 1


# -------------------------------- TEST: Complete Habit: Show list of due habits and complete one -------------------------------

def test_mark_habit_completed_due_today_filter(monkeypatch, test_db, capfd):
    """
    Simulates user choosing to show only habits due today and completes one.
    """
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("tester", "Tester"))
    user_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO habits (user_id, habit_name, habit_name_display, frequency)
        VALUES (?, ?, ?, ?)
    """, (user_id, "due", "Due", "daily"))
    habit_due_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO habits (user_id, habit_name, habit_name_display, frequency)
        VALUES (?, ?, ?, ?)
    """, (user_id, "notdue", "NotDue", "daily"))
    habit_not_due_id = cursor.lastrowid

    now = datetime.now()
    cursor.execute("""
        INSERT INTO habit_completions (habit_id, completed_at) VALUES (?, ?)
    """, (habit_not_due_id, now.isoformat()))

    test_db.commit()

    inputs = iter([1, 0])
    monkeypatch.setattr(habit_flow, "get_valid_index_input", lambda *a, **kw: next(inputs))
    monkeypatch.setattr(habit_flow, "get_yes_no_numbered", lambda prompt: False)

    habit_flow.mark_habit_completed(user_id, "Tester")

    out, _ = capfd.readouterr()
    print("--- OUTPUT for test_mark_habit_completed_due_today_filter ---")
    print(out)

    assert "marked as completed" in out
    assert "Due" in out