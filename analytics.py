"""
Analytics Module for the Habit Tracker application.

Provides insights into user habits by listing tracked habits, filtering by frequency,
and analyzing completion streaks. Integrates with habit creation prompts to ensure
a continuous user flow when no data is available.

Functions:
- list_tracked_habits: Displays all currently tracked habits for the user, including frequency and creation date.
- list_habits_by_frequency: Prompts the user to select a frequency and displays all matching habits.
- get_longest_overall_streak: Shows all habits that share the longest recorded streak for the user.
- get_longest_streak_for_habit: Allows the user to select a specific habit and view its longest recorded streak.

Notes:
- All functions automatically prompt the user to create a habit if none exist.
- Input selections use indexed menus with 'go back' and 'exit' navigation.
- Foreign key constraints are explicitly enabled for all database connections.
"""

import sqlite3
from datetime import datetime, timedelta
from create_db import DB_FILE
from validators import get_yes_no_numbered, get_valid_index_input
from habit_flow import create_habit
from habit_flow import select_frequency
from streaks import update_streaks


import sqlite3
from create_db import DB_FILE
from validators import get_yes_no_numbered, get_valid_index_input
from habit_flow import create_habit, select_frequency, exit_application


def list_tracked_habits(current_user_id: int, current_username: str) -> None:
    """
    Displays all currently tracked habits for the user.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("""
            SELECT habit_name_display, frequency, created_at
            FROM habits
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (current_user_id,))
        habits = cursor.fetchall()

        if not habits:
            print("📭 You are not currently tracking any habits.")
            if get_yes_no_numbered("Would you like to create one now?"):
                create_habit(current_user_id, current_username, conn, cursor)
            else:
                print("↩️ Returning to Habit Tracker Overview.\n")
            return

        print("\n📋 Currently Tracked Habits:\n")
        for idx, (name, frequency, created_at) in enumerate(habits, 1):
            print(f"{idx}. {name} ({frequency}) - Created on {created_at}")
        print()


def list_habits_by_frequency(current_user_id: int, current_username: str) -> None:
    """
    Prompts user to select a frequency and displays all matching habits.
    """
    frequency = select_frequency()
    if frequency is None:
        print("↩️ Frequency selection cancelled.\n")
        return

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("""
            SELECT habit_name_display, created_at
            FROM habits
            WHERE user_id = ? AND frequency = ?
            ORDER BY created_at DESC
        """, (current_user_id, frequency))
        habits = cursor.fetchall()

        if not habits:
            print(f"📭 You have no habits with '{frequency}' frequency.")
            if get_yes_no_numbered("Would you like to create one now?"):
                create_habit(current_user_id, current_username, conn, cursor)
            else:
                print("↩️ Returning to Habit Tracker Overview.\n")
            return

        print(f"\n📅 Habits with '{frequency}' frequency:\n")
        for idx, (name, created_at) in enumerate(habits, 1):
            print(f"{idx}. {name} - Created on {created_at}")
        print()


def get_longest_overall_streak(current_user_id: int, current_username: str) -> None:
    """
    Displays all habits that share the longest recorded streak for the current user.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        cursor.execute("""
            SELECT MAX(longest_streak)
            FROM habits
            WHERE user_id = ?
        """, (current_user_id,))
        max_result = cursor.fetchone()

        if not max_result or max_result[0] is None:
            print("📭 No habits found to evaluate longest streak.")
            if get_yes_no_numbered("Would you like to create one now?"):
                create_habit(current_user_id, current_username, conn, cursor)
            else:
                print("↩️ Returning to Habit Tracker Overview.\n")
            return

        max_streak = max_result[0]

        cursor.execute("""
            SELECT habit_name_display
            FROM habits
            WHERE user_id = ? AND longest_streak = ?
        """, (current_user_id, max_streak))
        habits = cursor.fetchall()

        print(f"\n🏆 Longest Streak: {max_streak} completion(s)")
        print("🎯 Habit(s) with this streak:\n")
        for name_tuple in habits:
            print(f"- {name_tuple[0]} ({max_streak})")
        print()


def get_longest_streak_for_habit(current_user_id: int, current_username: str) -> None:
    """
    Prompts the user to select one of their habits and displays its longest recorded streak.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        cursor.execute("""
            SELECT habit_id, habit_name_display, longest_streak
            FROM habits
            WHERE user_id = ?
            ORDER BY habit_name_display ASC
        """, (current_user_id,))
        habits = cursor.fetchall()

        if not habits:
            print("📭 You don't have any habits to analyze.")
            if get_yes_no_numbered("Would you like to create one now?"):
                create_habit(current_user_id, current_username, conn, cursor)
            else:
                print("↩️ Returning to Habit Tracker Overview.\n")
            return

        habit_names = [habit[1] for habit in habits]
        index = get_valid_index_input("📊 Select a habit to view its longest streak:", habit_names, go_back=True, allow_exit=True)

        if index is None:
            print("↩️ Streak check cancelled.\n")
            return
        if index == "exit":
           exit_application()

        selected_name = habits[index][1]
        selected_streak = habits[index][2]

        print(f"\n🏁 Longest streak for '{selected_name}': {selected_streak} completion(s)\n")



def list_habits_due_today(current_user_id: int, current_username: str) -> None:
    due_today = []

    with sqlite3.connect(DB_FILE, timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("""
            SELECT h.habit_name_display, h.frequency,
                   MAX(c.completed_at) AS last_completed
            FROM habits h
            LEFT JOIN habit_completions c ON h.habit_id = c.habit_id
            WHERE h.user_id = ?
            GROUP BY h.habit_id
        """, (current_user_id,))
        rows = cursor.fetchall()

    for name, frequency, last_completed in rows:
        last_dt = datetime.fromisoformat(last_completed) if last_completed else None
        interval = timedelta(days=1 if frequency == 'daily' else 7)
        if not last_dt or datetime.now() >= last_dt + interval:
            due_today.append((name, frequency))

    if not due_today:
        print("✅ No habits due right now. Great work!\n")
        return

    print("\n📆 Habits Due Today:\n")
    for idx, (name, frequency) in enumerate(due_today, 1):
        print(f"{idx}. {name} ({frequency})")
    print()