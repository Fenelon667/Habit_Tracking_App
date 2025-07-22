"""
load_dummy_data.py

Script to populate the Habit Tracker application's database with dummy data for development and testing.

Features:
- Creates 5 example users with unique usernames.
- Adds a variety of habits per user, including different frequencies (daily/weekly).
- Simulates 6 weeks of historical completion data per habit, including:
    - Mostly consistent completions
    - Some habits with intentionally broken streaks
- Sets each habit's `created_at` to a date earlier than its first completion.
- Automatically creates the database and required tables if they do not exist.

Modules Used:
- sqlite3: For interacting with the SQLite database.
- os, subprocess: For checking file existence and triggering setup.
- datetime, timedelta: For generating realistic timestamps.
- random: To introduce variability in completion behavior.
- create_db: Provides the `initialize_database()` function and DB file path.

How It Works:
1. Ensures the database file and tables are present using `ensure_database_is_ready()`.
2. Creates users with both lowercase `user_name` and capitalized `user_name_display`.
3. Assigns different habits to users, including:
    - One user with 5 habits
    - Others with 2 habits each
4. For each habit:
    - Inserts historical completions over a 6-week period
    - Randomly skips some completions to simulate broken streaks
5. Commits all data and prints a success message.

Note:
This script is meant for internal testing/demo purposes and should not be committed to production codebases or Git history if it contains static/test data.

Run from CLI:
    python load_dummy_data.py
"""


import sqlite3
import os
from datetime import datetime, timedelta
import random
from create_db import initialize_database

DB_FILE = "habit_tracker.db"
REQUIRED_TABLES = {"users", "habits", "habit_completions"}

def ensure_database_is_ready():
    if not os.path.exists(DB_FILE):
        print("🔧 Database file not found. Creating a new one...")
        initialize_database()
    else:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        missing_tables = REQUIRED_TABLES - existing_tables
        if missing_tables:
            print(f"⚠️ Missing tables detected: {missing_tables}. Re-initializing database...")
            initialize_database()
        else:
            print("✅ All required tables found.")

def create_dummy_users(cursor):
    user_names = ['alice', 'bob', 'charlie', 'diana', 'edward']
    user_ids = []
    for name in user_names:
        cursor.execute(
            "INSERT INTO users (user_name, user_name_display) VALUES (?, ?)",
            (name.lower(), name.capitalize())
        )
        user_ids.append(cursor.lastrowid)
    return user_ids

def create_dummy_habits(cursor, user_ids):
    all_habits = {
        "alice": [
            ("Morning Jog", "daily"),
            ("Meditate", "daily"),
            ("Read 10 Pages", "daily"),
            ("Call Grandma", "weekly"),
            ("Declutter Desk", "weekly")
        ],
        "bob": [("Evening Walk", "daily"), ("Guitar Practice", "weekly")],
        "charlie": [("Water Plants", "daily"), ("Clean Room", "weekly")],
        "diana": [("Write Journal", "daily"), ("Yoga", "weekly")],
        "edward": [("Stretching", "daily"), ("Grocery Shopping", "weekly")]
    }

    user_habits = []
    today = datetime.now()

    for idx, user_id in enumerate(user_ids):
        name_key = ["alice", "bob", "charlie", "diana", "edward"][idx]
        habits = all_habits[name_key.lower()]

        for habit_name_display, frequency in habits:
            habit_name = habit_name_display.lower().replace(" ", "_")
            created_days_ago = random.randint(49, 63)
            created_at = today - timedelta(days=created_days_ago)

            cursor.execute(
                "INSERT INTO habits (user_id, habit_name, habit_name_display, frequency, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, habit_name, habit_name_display, frequency, created_at.isoformat())
            )
            habit_id = cursor.lastrowid
            user_habits.append((habit_id, frequency, created_at))
    return user_habits

def create_dummy_completions(cursor, habits):
    today = datetime.now()

    for habit_id, freq, created_at in habits:
        is_broken_streak = random.random() < 0.4  # 40% of habits will have a broken streak
        completions = []

        if freq == "daily":
            start_date = today - timedelta(days=42)
            date = start_date

            while date <= today:
                if date >= created_at:
                    # Simulate a gap in week 3 to break the streak
                    if is_broken_streak and (today - date).days in range(18, 24):
                        date += timedelta(days=2)
                        continue
                    if (not is_broken_streak and random.random() < 0.85) or (is_broken_streak and random.random() < 0.6):
                        completions.append(date)
                date += timedelta(days=1)

        elif freq == "weekly":
            start_date = today - timedelta(weeks=6)
            date = start_date

            while date <= today:
                if date >= created_at:
                    if is_broken_streak and (today - date).days in range(21, 35):
                        date += timedelta(weeks=2)
                        continue
                    if (not is_broken_streak and random.random() < 0.9) or (is_broken_streak and random.random() < 0.6):
                        completions.append(date)
                date += timedelta(weeks=1)

        for completion_date in completions:
            cursor.execute(
                "INSERT INTO habit_completions (habit_id, completed_at) VALUES (?, ?)",
                (habit_id, completion_date.isoformat())
            )

def update_streaks(cursor, habits):
    for habit_id, freq, _ in habits:
        cursor.execute(
            "SELECT DATE(completed_at) FROM habit_completions WHERE habit_id = ? ORDER BY completed_at ASC",
            (habit_id,)
        )
        rows = cursor.fetchall()
        dates = [datetime.fromisoformat(row[0]) for row in rows]

        current_streak = 0
        longest_streak = 0
        today = datetime.now().date()
        expected_interval = timedelta(days=1) if freq == "daily" else timedelta(weeks=1)

        streak = 1
        for i in range(1, len(dates)):
            if (dates[i].date() - dates[i-1].date()) == expected_interval:
                streak += 1
            else:
                longest_streak = max(longest_streak, streak)
                streak = 1
        longest_streak = max(longest_streak, streak)

        if dates:
            last_completion = dates[-1].date()
            if (today - last_completion) <= expected_interval:
                current_streak = streak
            else:
                current_streak = 0

        cursor.execute(
            "UPDATE habits SET streak = ?, longest_streak = ? WHERE habit_id = ?",
            (current_streak, longest_streak, habit_id)
        )

def main():
    ensure_database_is_ready()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    try:
        user_ids = create_dummy_users(cursor)
        habits = create_dummy_habits(cursor, user_ids)
        create_dummy_completions(cursor, habits)
        update_streaks(cursor, habits)

        conn.commit()
        print("✅ Dummy data successfully loaded into the database.")
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()
    main()