"""
Habit Flow Module for the Habit Tracker application.

Handles creation, selection, and deletion of user habits, including input validation
and foreign key constraint enforcement.

Functions:
- create_habit: Prompts for a new habit name and frequency, validates input, and inserts it into the database.
- select_frequency: Displays frequency options ('daily', 'weekly') and returns the selected choice.
- delete_habit: Lists and deletes a selected habit for the current user after confirmation.
- mark_habit_completed: Marks a habit as completed if eligible, updates streaks, and provides feedback.

Notes:
- All habit names are stored in lowercase and must be unique per user.
- Input is validated for format, length, and duplication.
- Foreign key constraints are explicitly enabled for each connection to ensure cascading deletes.
"""

import re
import sqlite3
from habit import Habit
from create_db import DB_FILE
from datetime import datetime, timedelta
from validators import get_valid_index_input, get_yes_no_numbered, exit_application
from streaks import update_streaks


def create_habit(current_user_id: int, current_username: str, conn, cursor) -> None:
    MAX_LENGTH = 50
    pattern = re.compile(r'^[A-Za-z0-9 \-]+$')

    cursor.execute("PRAGMA foreign_keys = ON")

    while True:
        habit_name_input = input("Enter habit name (or type 'back' to cancel): ").strip()
        habit_name_lower = habit_name_input.lower()

        if habit_name_lower == "back":
            print("↩️ Habit creation cancelled.\n")
            return

        if len(habit_name_input) == 0:
            print("❌ Habit name cannot be empty.\n")
            continue

        if len(habit_name_input) > MAX_LENGTH:
            print(f"❌ Habit name too long. Please limit to {MAX_LENGTH} characters.\n")
            continue

        if not pattern.match(habit_name_input):
            print("❌ Habit name can only contain letters, numbers, spaces, and dashes.\n")
            continue

        cursor.execute(
            "SELECT 1 FROM habits WHERE user_id = ? AND habit_name = ?",
            (current_user_id, habit_name_lower)
        )
        if cursor.fetchone():
            print(f"❌ You already have a habit named '{habit_name_input}'. Choose a different name.\n")
        else:
            break

    frequency = select_frequency()
    if frequency is None:
        print("↩️ Habit creation cancelled.\n")
        return

    habit = Habit(habit_name=habit_name_input, frequency=frequency, user_id=current_user_id)

    try:
        cursor.execute(
            '''
            INSERT INTO habits (user_id, habit_name, habit_name_display, frequency, streak, longest_streak)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            habit.to_db_tuple()
        )
        conn.commit()
        print(f"✅ Habit '{habit_name_input}' ({frequency}) created for user {current_username}.")
    except sqlite3.IntegrityError:
        print("❌ Failed to create habit due to a database error.")



def select_frequency() -> str | None:
    options = ["daily", "weekly"]
    index = get_valid_index_input("Select a habit frequency:", options, go_back=True, allow_exit=True)

    if index is None:
        return None
    if index == "exit":
        exit_application()
    return options[index]


def delete_habit(user_id: int) -> None:
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        cursor.execute(
            "SELECT habit_id, habit_name_display FROM habits WHERE user_id = ?",
            (user_id,)
        )
        habits = cursor.fetchall()

        if not habits:
            print("❌ You don't have any habits to delete.")
            return

        habit_names = [row[1] for row in habits]
        index = get_valid_index_input("🗑️ Select a habit to delete:", habit_names, go_back=True, allow_exit=True)

        if index is None:
            print("↩️ Habit deletion cancelled.\n")
            return
        if index == "exit":
            exit_application()

        habit_id, habit_name = habits[index]

        prompt = f"❗ Are you sure you want to delete the habit '{habit_name}'? This cannot be undone."
        if get_yes_no_numbered(prompt):
            cursor.execute("DELETE FROM habits WHERE habit_id = ?", (habit_id,))
            conn.commit()
            print(f"✅ Habit '{habit_name}' deleted successfully.")
        else:
            print("❌ Habit deletion canceled.")



def mark_habit_completed(current_user_id: int, current_username: str):
    with sqlite3.connect(DB_FILE, timeout=10.0) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT habit_id, habit_name_display, frequency FROM habits WHERE user_id = ?",
            (current_user_id,)
        )
        all_habits = cursor.fetchall()

        if not all_habits:
            print("❌ You have no habits to complete.")
            if get_yes_no_numbered("Would you like to create one now?"):
                create_habit(current_user_id, current_username, conn, cursor)
            else:
                print("↩️ Returning to Habit Management.\n")
            return

        # Ask user which habits to show
        options = ["Show all habits", "Show only habits due today"]
        view_choice = get_valid_index_input(
            "Do you want to see all habits or only habits that are due today?",
            options,
            go_back=True,
            allow_exit=True
        )

        if view_choice is None:
            print("↩️ Returning to Habit Management.\n")
            return
        if view_choice == "exit":
            exit_application()

        habits = all_habits
        if view_choice == 1:  # Only show habits due today
            due_today = []
            for habit_id, name, frequency in all_habits:
                cursor.execute("""
                    SELECT completed_at FROM habit_completions
                    WHERE habit_id = ?
                    ORDER BY completed_at DESC
                    LIMIT 1
                """, (habit_id,))
                last_row = cursor.fetchone()
                last_completed = datetime.fromisoformat(last_row[0]) if last_row else None
                interval = timedelta(days=1) if frequency == 'daily' else timedelta(days=7)

                if last_completed is None or datetime.now() >= last_completed + interval:
                    due_today.append((habit_id, name, frequency))

            if not due_today:
                print("❌ No habits are due today.")
                if get_yes_no_numbered("Would you like to see all habits instead?"):
                    habits = all_habits
                else:
                    print("↩️ Returning to Habit Management.\n")
                    return
            else:
                habits = due_today

        # Prompt for habit selection
        habit_names = [row[1] for row in habits]
        index = get_valid_index_input(
            "Select a habit to mark as completed:",
            habit_names,
            go_back=True,
            allow_exit=True
        )

        if index is None:
            print("↩️ Habit completion cancelled.\n")
            return
        if index == "exit":
            exit_application()

        habit_id, name, frequency = habits[index]
        interval = timedelta(days=1) if frequency == "daily" else timedelta(days=7)

        cursor.execute("""
            SELECT completed_at FROM habit_completions
            WHERE habit_id = ? ORDER BY completed_at DESC LIMIT 1
        """, (habit_id,))
        last_row = cursor.fetchone()
        now = datetime.now()

        if last_row:
            last_completed = datetime.fromisoformat(last_row[0])
            next_eligible = last_completed + interval
            if now < next_eligible:
                wait = next_eligible - now
                hours = (wait.seconds % 86400) // 3600
                minutes = (wait.seconds % 3600) // 60
                if frequency == "daily":
                    print("⛔ You’ve already completed this day.")
                    print(f"⏳ You can complete it again in {hours} hour(s) and {minutes} minute(s).")
                else:
                    days = wait.days
                    print("⛔ You’ve already completed this week.")
                    print(f"⏳ You can complete it again in {days} day(s), {hours} hour(s), and {minutes} minute(s).")
                return

        # Mark as completed
        cursor.execute("""
            INSERT INTO habit_completions (habit_id, completed_at)
            VALUES (?, ?)
        """, (habit_id, now.isoformat()))
        update_streaks(habit_id, cursor)
        conn.commit()

        # Show result
        print(f"🎉 Habit '{name}' marked as completed!")
        cursor.execute("SELECT streak, longest_streak FROM habits WHERE habit_id = ?", (habit_id,))
        streak, longest = cursor.fetchone()
        unit = "day(s)" if frequency == "daily" else "week(s)"
        print(f"🔥 Current streak: {streak} {unit} | 🏆 Longest streak: {longest} {unit}")
        print(f"📅 Next streak window begins in 1 {unit[:-3]}")