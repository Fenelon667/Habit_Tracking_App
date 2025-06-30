"""
Streak Calculation Module for the Habit Tracker application.

This module provides logic for calculating and updating streaks for user habits,
based on the frequency and timing of recorded completions.

Functions:
- calculate_streaks(habit_id): Analyzes all completions for a given habit to compute the current and longest streaks.
- update_streaks(habit_id, cursor): Stores the calculated streaks in the 'habits' table after each valid completion.

Streak Logic:
- For 'daily' habits: Completions must be exactly 1 day apart to continue a streak.
- For 'weekly' habits: Completions must be exactly 7 days apart.
- Duplicate completions within the same interval (e.g. multiple times on the same day) are ignored.
- A streak is broken if the most recent completion is outside the valid interval.

Database Use:
- Uses the 'habit_completions' table to read completion timestamps.
- Updates the 'streak' and 'longest_streak' columns in the 'habits' table.
- Enforces foreign key constraints on each connection.
"""

import sqlite3
from datetime import datetime, timedelta
from create_db import DB_FILE


def calculate_streaks(habit_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("SELECT frequency FROM habits WHERE habit_id = ?", (habit_id,))
    result = cursor.fetchone()
    if not result or result[0] is None:
        conn.close()
        return (0, 0)

    frequency = result[0]

    cursor.execute("""
        SELECT completed_at FROM habit_completions
        WHERE habit_id = ?
        ORDER BY completed_at ASC
    """, (habit_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return (0, 0)

    dates = [datetime.fromisoformat(row[0]) for row in rows]

    habit_interval = timedelta(days=1) if frequency == 'daily' else timedelta(days=7)

    current_streak = 1
    longest_streak = 1

    for i in range(1, len(dates)):
        delta = dates[i].date() - dates[i - 1].date()
        if delta == habit_interval:
            current_streak += 1
        elif delta < habit_interval:
            continue
        else:
            longest_streak = max(longest_streak, current_streak)
            current_streak = 1

    longest_streak = max(longest_streak, current_streak)

    now = datetime.now().date()
    last_completion = dates[-1].date()
    if (frequency == 'daily' and now - last_completion > timedelta(days=1)) or \
       (frequency == 'weekly' and now - last_completion > timedelta(days=7)):
        current_streak = 0

    return current_streak, longest_streak


def update_streaks(habit_id, cursor):
    current_streak, longest_streak = calculate_streaks(habit_id)

    cursor.execute("""
        UPDATE habits
        SET streak = ?, longest_streak = ?
        WHERE habit_id = ?
    """, (current_streak, longest_streak, habit_id))