"""
Streak Calculation Module for the Habit Tracker application.

Provides functionality to calculate and update current and longest streaks
for user habits based on the timing and frequency of their completions.

Functions:
- calculate_streaks(habit_id, cursor): Analyzes completion timestamps for the given habit,
  returning the current and longest streak counts.
- update_streaks(habit_id, cursor): Computes streaks using calculate_streaks and updates
  the corresponding habit record in the database.

Streak Rules:
- 'daily' habits require completions exactly 1 day apart to maintain a streak.
- 'weekly' habits require completions exactly 7 days apart.
- Multiple completions within the same day/week interval are ignored (do not increase streak).
- Streak is reset if the last completion is beyond the expected interval.

Database Interaction:
- Reads completion timestamps from 'habit_completions' table.
- Updates 'streak' and 'longest_streak' fields in the 'habits' table.
- Relies on foreign key constraints for data integrity.

Note:
- The caller must provide a cursor with an active database connection.
"""

from datetime import datetime, timedelta
from create_db import DB_FILE


def calculate_streaks(habit_id, cursor):
    cursor.execute("SELECT frequency FROM habits WHERE habit_id = ?", (habit_id,))
    result = cursor.fetchone()
    if not result or result[0] is None:
        return (0, 0)

    frequency = result[0]

    cursor.execute("""
        SELECT completed_at FROM habit_completions
        WHERE habit_id = ?
        ORDER BY completed_at ASC
    """, (habit_id,))
    rows = cursor.fetchall()

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
    current_streak, longest_streak = calculate_streaks(habit_id, cursor)

    cursor.execute("""
        UPDATE habits
        SET streak = ?, longest_streak = ?
        WHERE habit_id = ?
    """, (current_streak, longest_streak, habit_id))