"""
This test file verifies the analytics functions of the Habit Tracker application.
Tests are run using an in-memory SQLite database to ensure isolated and non-destructive test environments.

Covered features:
- Listing all tracked habits:
    - test_list_tracked_habits_no_data: user has no habits and declines to create one
    - test_list_tracked_habits_with_data: user has existing habits, verifies display
    - test_list_tracked_habits_create_prompt_yes: user has no habits and chooses to create one

- Listing habits by frequency:
    - test_list_habits_by_frequency_no_data: user selects frequency with no habits and declines to create
    - test_list_habits_by_frequency_with_data: user selects frequency with matching habits
    - test_list_habits_by_frequency_create_prompt_yes: user selects frequency with no habits and chooses to create one

- Viewing longest overall streak:
    - test_get_longest_overall_streak_no_data: no habits exist, user declines creation
    - test_get_longest_overall_streak_with_data: multiple habits share the longest streak

- Viewing longest streak for a specific habit:
    - test_get_longest_streak_for_habit_no_data: user has no habits and declines to create one
    - test_get_longest_streak_for_habit_selects_valid: user selects a habit and sees its streak

- Viewing habits due today:
    - test_list_habits_due_today_no_data_creates_none: no due habits, user declines to create one
    - test_list_habits_due_today_with_data: habits are due today and are correctly listed

"""


import sys
import os
import analytics
from habit_flow import create_habit
from unittest.mock import MagicMock

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)



# --------------------------- TEST: list_tracked_habits with no data ----------------------------

def test_list_tracked_habits_no_data(monkeypatch, test_db, capfd):
    """
    Simulates the user having no habits and choosing not to create one.
    Verifies appropriate message and graceful return.
    """
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display)
        VALUES (?, ?)
    """, ("tester", "Tester"))
    test_db.commit()
    user_id = cursor.lastrowid

    # Simulate user declining to create a habit
    monkeypatch.setattr(analytics, "get_yes_no_numbered", lambda _: False)

    cursor.execute("SELECT * FROM habits")
    existing = cursor.fetchall()
    print(f"HABITS IN DB BEFORE TEST: {existing}")

    # Run the function
    analytics.list_tracked_habits(user_id, "Tester")

    # Capture output
    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_list_tracked_habits_no_data ---")
    print(out)

    # Assertions
    assert "not currently tracking any habits" in out
    assert "Returning to Habit Tracker Overview" in out

    cursor.execute("SELECT COUNT(*) FROM habits")
    assert cursor.fetchone()[0] == 0  # Sanity check



# --------------------------- TEST: list_tracked_habits with data ----------------------------

def test_list_tracked_habits_with_data(test_db, capfd):
    """
    Simulates the user having habits and verifies they are correctly listed.
    """
    cursor = test_db.cursor()

    # Insert user
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display)
        VALUES (?, ?)
    """, ("tester", "Tester"))
    user_id = cursor.lastrowid

    # Insert habits
    habits = [
        ("read", "Read", "daily", "2025-07-20T08:00:00"),
        ("run", "Run", "weekly", "2025-07-18T10:00:00")
    ]
    for habit_name, habit_name_display, freq, created_at in habits:
        cursor.execute("""
            INSERT INTO habits (user_id, habit_name, habit_name_display, frequency, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, habit_name, habit_name_display, freq, created_at))
    test_db.commit()

    # Run the function
    analytics.list_tracked_habits(user_id, "Tester")

    # Capture and assert output
    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_list_tracked_habits_with_data ---")
    print(out)

    assert "Currently Tracked Habits" in out
    assert "1. Read (daily)" in out
    assert "2. Run (weekly)" in out


# --------------------------- TEST: list_tracked_habits - user agrees to create a habit ----------------------------

def test_list_tracked_habits_create_prompt_yes(monkeypatch, test_db, capfd):
    """
    Simulates the user having no habits and choosing to create one.
    Verifies that create_habit() is called.
    """
    cursor = test_db.cursor()

    # Insert user
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display)
        VALUES (?, ?)
    """, ("tester", "Tester"))
    user_id = cursor.lastrowid
    test_db.commit()

    # Simulate user selecting 'Yes'
    monkeypatch.setattr(analytics, "get_yes_no_numbered", lambda _: True)

    # Mock create_habit so it doesn't actually run
    mock_create = MagicMock()
    monkeypatch.setattr(analytics, "create_habit", mock_create)

    # Run the function
    analytics.list_tracked_habits(user_id, "Tester")

    # Capture output
    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_list_tracked_habits_create_prompt_yes ---")
    print(out)

    # Assertions
    assert "not currently tracking any habits" in out
    mock_create.assert_called_once_with(user_id, "Tester")


def test_list_habits_by_frequency_no_data(monkeypatch, test_db, capfd):
    """
    Simulates user selecting a frequency with no matching habits,
    and declining to create a new one.
    """
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display)
        VALUES (?, ?)
    """, ("tester", "Tester"))
    user_id = cursor.lastrowid
    test_db.commit()

    # Simulate user selecting 'daily' and then declining habit creation
    monkeypatch.setattr(analytics, "select_frequency", lambda: "daily")
    monkeypatch.setattr(analytics, "get_yes_no_numbered", lambda _: False)

    analytics.list_habits_by_frequency(user_id, "Tester")

    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_list_habits_by_frequency_no_data ---")
    print(out)

    assert "no habits with 'daily' frequency" in out.lower()
    assert "Returning to Habit Tracker Overview" in out


# --------------------------- TEST: list_habits_by_frequency - habits exist ----------------------------

def test_list_habits_by_frequency_with_data(monkeypatch, test_db, capfd):
    """
    Simulates user selecting a frequency with matching habits.
    Verifies the habits are listed correctly.
    """
    cursor = test_db.cursor()

    # Insert user
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display)
        VALUES (?, ?)
    """, ("tester", "Tester"))
    user_id = cursor.lastrowid

    # Insert daily habits
    habits = [
        ("read", "Read", "daily", "2025-07-15T09:00:00"),
        ("walk", "Walk", "daily", "2025-07-16T07:30:00")
    ]
    for habit_name, display_name, freq, created_at in habits:
        cursor.execute("""
            INSERT INTO habits (user_id, habit_name, habit_name_display, frequency, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, habit_name, display_name, freq, created_at))
    test_db.commit()

    # Simulate user selecting 'daily'
    monkeypatch.setattr(analytics, "select_frequency", lambda: "daily")

    # Run function
    analytics.list_habits_by_frequency(user_id, "Tester")

    # Capture output
    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_list_habits_by_frequency_with_data ---")
    print(out)

    # Assertions
    assert "Habits with 'daily' frequency" in out
    assert "1. Walk - Created on Jul 16, 2025" in out
    assert "2. Read - Created on Jul 15, 2025" in out



# --------------------------- TEST: list_habits_by_frequency - no data, user agrees to create ----------------------------

def test_list_habits_by_frequency_create_prompt_yes(monkeypatch, test_db, capfd):
    """
    Simulates user selecting a frequency with no habits, and choosing to create one.
    Verifies that create_habit() is called.
    """
    cursor = test_db.cursor()

    # Insert user
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display)
        VALUES (?, ?)
    """, ("tester", "Tester"))
    user_id = cursor.lastrowid
    test_db.commit()

    # Simulate selecting 'weekly' and user saying 'Yes'
    monkeypatch.setattr(analytics, "select_frequency", lambda: "weekly")
    monkeypatch.setattr(analytics, "get_yes_no_numbered", lambda _: True)

    # Mock create_habit to avoid actual logic
    mock_create = MagicMock()
    monkeypatch.setattr(analytics, "create_habit", mock_create)

    # Run the function
    analytics.list_habits_by_frequency(user_id, "Tester")

    # Capture output
    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_list_habits_by_frequency_create_prompt_yes ---")
    print(out)

    # Assertions
    assert "no habits with 'weekly' frequency" in out.lower()
    mock_create.assert_called_once_with(user_id, "Tester")


# --------------------------- TEST: get_longest_overall_streak - no habits, user declines ----------------------------

def test_get_longest_overall_streak_no_data(monkeypatch, test_db, capfd):
    """
    Simulates the user having no habits with streaks and choosing not to create one.
    Verifies graceful message and exit.
    """
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display)
        VALUES (?, ?)
    """, ("tester", "Tester"))
    user_id = cursor.lastrowid
    test_db.commit()

    monkeypatch.setattr(analytics, "get_yes_no_numbered", lambda _: False)

    analytics.get_longest_overall_streak(user_id, "Tester")

    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_get_longest_overall_streak_no_data ---")
    print(out)

    assert "No habits found to evaluate longest streak" in out
    assert "Returning to Habit Tracker Overview" in out


# --------------------------- TEST: get_longest_overall_streak - multiple habits share max streak ----------------------------

def test_get_longest_overall_streak_with_data(test_db, capfd):
    """
    Inserts habits with various longest_streaks and verifies that those sharing the max are listed.
    """
    cursor = test_db.cursor()

    # Insert user
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display)
        VALUES (?, ?)
    """, ("tester", "Tester"))
    user_id = cursor.lastrowid

    # Insert habits with streaks: 1, 4, 4
    habits = [
        ("stretch", "Stretch", "daily", 1),
        ("run", "Run", "weekly", 4),
        ("read", "Read", "daily", 4),
    ]
    for habit_name, display_name, freq, streak in habits:
        cursor.execute("""
            INSERT INTO habits (user_id, habit_name, habit_name_display, frequency, longest_streak)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, habit_name, display_name, freq, streak))
    test_db.commit()

    # Run function
    analytics.get_longest_overall_streak(user_id, "Tester")

    # Capture output
    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_get_longest_overall_streak_with_data ---")
    print(out)

    assert "Longest Streak: 4" in out
    assert "- Run (4)" in out
    assert "- Read (4)" in out
    assert "Stretch" not in out  # Should not appear



# --------------------------- TEST: get_longest_streak_for_habit - no habits, user declines to create a new one ----------------------------

def test_get_longest_streak_for_habit_no_data(monkeypatch, test_db, capfd):
    """
    Simulates a user with no habits who declines to create one.
    Verifies proper messaging and no crash.
    """
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display)
        VALUES (?, ?)
    """, ("tester", "Tester"))
    user_id = cursor.lastrowid
    test_db.commit()

    monkeypatch.setattr(analytics, "get_yes_no_numbered", lambda _: False)

    analytics.get_longest_streak_for_habit(user_id, "Tester")

    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_get_longest_streak_for_habit_no_data ---")
    print(out)

    assert "don't have any habits to analyze" in out.lower()
    assert "Returning to Habit Tracker Overview" in out


# --------------------------- TEST: get_longest_streak_for_habit - user selects habit ----------------------------

def test_get_longest_streak_for_habit_selects_valid(monkeypatch, test_db, capfd):
    """
    Simulates a user selecting a habit from the list and viewing its longest streak.
    """
    cursor = test_db.cursor()

    # Insert user
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display)
        VALUES (?, ?)
    """, ("tester", "Tester"))
    user_id = cursor.lastrowid

    # Insert two habits
    habits = [
        ("read", "Read", "daily", 3),
        ("meditate", "Meditate", "daily", 5)
    ]
    for habit_name, display_name, freq, streak in habits:
        cursor.execute("""
            INSERT INTO habits (user_id, habit_name, habit_name_display, frequency, longest_streak)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, habit_name, display_name, freq, streak))
    test_db.commit()

    # Simulate user selecting "Meditate", which appears first alphabetically
    monkeypatch.setattr(analytics, "get_valid_index_input", lambda *args, **kwargs: 0)
    
    #Print to debug:
    monkeypatch.setattr(analytics, "get_valid_index_input", lambda prompt, options, **kwargs: print("OPTIONS:", options) or 0)

    analytics.get_longest_streak_for_habit(user_id, "Tester")

    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_get_longest_streak_for_habit_selects_valid ---")
    print(out)

    assert "Longest streak for 'Meditate': 5 completion(s)" in out


# --------------------------- TEST: test_list_habits_due_today - no due habits, Unser selects NO ----------------------------


def test_list_habits_due_today_no_data_creates_none(monkeypatch, test_db, capfd):
    """
    Simulates user with no habits due today and choosing NOT to create one.
    Verifies appropriate message and graceful return.
    """

    # Insert user
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display)
        VALUES (?, ?)
    """, ("tester", "Tester"))
    test_db.commit()
    user_id = cursor.lastrowid

    # Monkeypatch: simulate user saying "no" to creating a habit
    monkeypatch.setattr(analytics, "get_yes_no_numbered", lambda _: False)

    # Call the function
    analytics.list_habits_due_today(user_id, "Tester")

    # Capture and verify output
    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_list_habits_due_today_no_data_creates_none ---")
    print(out)

    assert "No habits due right now" in out
    assert "Great work!" in out


# --------------------------- TEST: test_list_habits_due_today - no habits, User selects YES  ----------------------------

def test_list_habits_due_today_with_data(test_db, capfd):
    """
    Inserts habits that are due today and verifies that they are listed.
    """
    from datetime import datetime, timedelta
    cursor = test_db.cursor()

    # Insert user
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display) VALUES (?, ?)
    """, ("tester", "Tester"))
    user_id = cursor.lastrowid

    # Insert a habit that is due (created 3 days ago, daily)
    created_at = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO habits (user_id, habit_name, habit_name_display, frequency, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, "read", "Read", "daily", created_at))
    test_db.commit()

    # Run the function
    analytics.list_habits_due_today(user_id, "Tester")

    # Capture output
    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_list_habits_due_today_with_data ---")
    print(out)

    assert "Habits Due Today" in out
    assert "Read" in out
    assert "create_habit" not in out  # <-- Optional: confirm it wasn't called


# --------------------------- TEST: test_list_habits_due_today - with habits due today ----------------------------

def test_list_habits_due_today_with_data(test_db,capfd):
    """
    Inserts habits that are due today and verifies that they are listed.
    """
    # Insert user
    cursor = test_db.cursor()
    cursor.execute("""
        INSERT INTO users (user_name, user_name_display) VALUES (?, ?)
    """, ("tester", "Tester"))
    test_db.commit()
    user_id = cursor.lastrowid

    # Insert a habit due today (e.g. daily, created 2 days ago)
    from datetime import datetime, timedelta
    created_at = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO habits (user_id, habit_name, habit_name_display, frequency, created_at, longest_streak)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, "stretch", "Stretch", "daily", created_at, 0))
    test_db.commit()

    # Call the function
    analytics.list_habits_due_today(user_id, "Tester")

    # Capture output
    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_list_habits_due_today_with_data ---")
    print(out)

    # Assertions
    assert "Stretch" in out
    assert "Habits Due Today" in out


