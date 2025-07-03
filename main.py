"""
Main Entry Point for the Habit Tracker Application.

This module initializes the database and manages the Command Line Interface (CLI)
navigation. It provides access to habit management, user account actions, and data
visualization, structured into nested menus for an improved user experience.

Features:
- Habit Management: Create, complete, and delete habits with cooldown logic.
- User Management: Switch or delete user accounts securely.
- Data Insights: View all or current user-specific habit and completion data.
- Modular CLI: Clean navigation with headers, go-back options, and exit points.

Functions:
- print_header: Displays the section title and logged-in user.
- CLI loop: Presents main and sub-menus with action handling using validated input.

Usage:
Run this script to launch the Habit Tracker's interactive interface.
"""

import sqlite3
from habit_flow import create_habit, delete_habit, mark_habit_completed
from create_db import DB_FILE, initialize_database
from user_flow import login_flow, delete_current_user
from validators import get_valid_index_input, get_yes_no_numbered, exit_application
from analytics import (
    list_tracked_habits,
    list_habits_due_today,
    list_habits_by_frequency,
    get_longest_overall_streak,
    get_longest_streak_for_habit
)


def print_header(current_username, title=""):
    print(f"\n=== {title} ===\nLogged in as: {current_username}")

if __name__ == "__main__":
    initialize_database()
    current_user_id, current_username = login_flow()

    while True:
        print_header(current_username, "Habit Tracker")
        main_options = ["Habit Management", "User Management", "Data & Insights"]
        main_choice = get_valid_index_input("Main Menu - Select a category:", main_options, allow_exit=True)

        if main_choice == "exit":
            exit_application()

        if main_choice == 0:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                habit_options = ["View all habits", "Create new habit", "Mark habit completed", "Delete a habit"]
                while True:
                    print_header(current_username, "Habit Management")
                    habit_choice = get_valid_index_input("Choose an action:", habit_options, go_back=True, allow_exit=True)

                    if habit_choice is None:
                        break
                    elif habit_choice == "exit":
                        exit_application()
                    elif habit_choice == 0:
                        list_tracked_habits(current_user_id, current_username)
                    elif habit_choice == 1:
                        #create_habit(current_user_id, current_username, conn, cursor)
                       create_habit(current_user_id, current_username)
                    elif habit_choice == 2:
                        mark_habit_completed(current_user_id, current_username)
                    elif habit_choice == 3:
                        delete_habit(current_user_id)

        elif main_choice == 1:
            # User Management runs outside any open connection block
            user_options = ["Change user", "Delete current user"]
            while True:
                print_header(current_username, "User Management")
                user_choice = get_valid_index_input("Choose a user option:", user_options, go_back=True, allow_exit=True)

                if user_choice is None:
                    break
                elif user_choice == "exit":
                    exit_application()
                elif user_choice == 0:
                    current_user_id, current_username = login_flow()
                    break
                elif user_choice == 1:
                    deleted = delete_current_user(current_user_id, current_username)
                    if deleted:
                        print("Returning to login...\n")
                        current_user_id, current_username = login_flow()
                        break

        elif main_choice == 2:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM habits WHERE user_id = ?", (current_user_id,))
                has_data = cursor.fetchone()

            if not has_data:
                print("❌ You don't have any habits to analyze.")
                if get_yes_no_numbered("Would you like to create one now?"):
                    with sqlite3.connect(DB_FILE) as conn:
                        cursor = conn.cursor()
                        #create_habit(current_user_id, current_username, conn, cursor)
                        create_habit(current_user_id, current_username)
                else:
                    print("↩️ Returning to Habit Tracker Overview.\n")
                    continue

            data_options = [
                "Show all your tracked habits",
                "List habits that are due today",
                "Filter habits by frequency (daily/weekly)",
                "View habit(s) with the longest streak",
                "Check the longest streak of a specific habit"
            ]
            while True:
                print_header(current_username, "Data & Insights")
                data_choice = get_valid_index_input("Choose a data option:", data_options, go_back=True, allow_exit=True)

                if data_choice is None:
                    break
                elif data_choice == "exit":
                    exit_application()
                elif data_choice == 0:
                    list_tracked_habits(current_user_id, current_username)
                elif data_choice == 1:
                    list_habits_due_today(current_user_id, current_username)
                elif data_choice == 2:
                    list_habits_by_frequency(current_user_id, current_username)
                elif data_choice == 3:
                    get_longest_overall_streak(current_user_id, current_username)
                elif data_choice == 4:
                    get_longest_streak_for_habit(current_user_id, current_username)