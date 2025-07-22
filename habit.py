"""
Habit class module for the Habit Tracker application.

Defines the Habit class, representing a user-associated habit with core attributes
and behaviors for creation and database interaction.

Class:
- Habit:
    Encapsulates habit details such as name, frequency, streaks, and timestamps.

Methods:
- __init__:
    Initializes a Habit instance with fields including name, frequency, user association, and streak data.

- to_db_tuple():
    Returns a tuple of habit attributes formatted for insertion into the SQLite database.

- __str__:
    Provides a readable string representation for display and debugging purposes.
"""

from typing import Optional

class Habit:
    def __init__(
        self,
        habit_name: str,
        frequency: str,
        user_id: int,
        streak: int = 0,
        longest_streak: int = 0,
        created_at: Optional[str] = None,
        habit_id: Optional[int] = None
    ) -> None:
        self.habit_id = habit_id
        self.user_id = user_id
        self.habit_name = habit_name.lower()             # stored lowercase for uniqueness
        self.habit_name_display = habit_name.strip()     # original casing for display
        self.frequency = frequency
        self.streak = streak
        self.longest_streak = longest_streak
        self.created_at = created_at  # assigned by database

    def to_db_tuple(self) -> tuple:
        """Return a tuple representation suitable for database insertion."""
        return (
            self.user_id,
            self.habit_name,
            self.habit_name_display,
            self.frequency,
            self.streak,
            self.longest_streak
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the habit."""
        return (
            f"Habit(id={self.habit_id}, name='{self.habit_name_display}', "
            f"frequency='{self.frequency}', streak={self.streak}, "
            f"longest={self.longest_streak})"
        )