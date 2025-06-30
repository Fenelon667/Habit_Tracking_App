"""
Habit class module for the Habit Tracker application.

This module defines the Habit class, which represents the structure and core attributes
of a habit associated with a user. It serves as a blueprint for creating and managing
habit objects within the application.

Methods:
- __init__: 
    Initializes a Habit instance with relevant fields like name, frequency, and streaks.

- to_db_tuple(): 
    Returns the habit data as a tuple, formatted for SQLite insertion.
    
- __str__: 
    Provides a readable string representation of the habit for display and debugging.
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