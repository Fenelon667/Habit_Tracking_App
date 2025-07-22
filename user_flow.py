"""
User Flow Module for the Habit Tracker application.

Manages user account lifecycle including login, creation, selection, and deletion.

Functions:
- create_user: Prompts for a new username, validates uniqueness and format, then inserts into the database.
- delete_current_user: Confirms and deletes the current user and all their associated habits and completions.
- select_existing_user: Lists registered users for selection with support for going back or exiting.
- get_existing_usernames: Retrieves all usernames (display form) from the database.
- login_flow: Provides the main login menu to select or create users, with navigation support.

Notes:
- Usernames are stored in lowercase to ensure uniqueness, while preserving the original casing for display.
- Validation enforces alphanumeric usernames, length limits, and uniqueness.
- Foreign key constraints ensure cascading deletions of related habit data when a user is removed.
- All database connections enable foreign key enforcement.
"""

import sqlite3
import create_db
from validators import get_valid_index_input, get_yes_no_numbered, exit_application  


def create_user():
    MAX_LENGTH = 30

    while True:
        user_input = input("Enter a username (or type 'back' to cancel): ").strip()

        if user_input.lower() == "back":
            return None  # go back to login menu

        if len(user_input) == 0:
            print("❌ Username cannot be empty.\n")
            continue
        if len(user_input) > MAX_LENGTH:
            print(f"❌ Username too long. Please limit to {MAX_LENGTH} characters.\n")
            continue
        if not user_input.isalnum():
            print("❌ Username can only contain letters and numbers. Don't use spaces, symbols or special characters.\n")
            continue

        username_display = user_input.strip()
        username_lower = username_display.lower()

        try:
            with sqlite3.connect(create_db.get_db_file(), uri=True) as conn:
            #with sqlite3.connect(DB_FILE, uri=True) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE LOWER(user_name) = ?", (username_lower,))
                if cursor.fetchone():
                    print("❌ Username already exists. Please try another.\n")
                    continue

                cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", (username_lower, username_display))
                conn.commit()
                print(f"✅ User '{username_display}' created successfully.")
                return cursor.lastrowid, username_display
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return None


def delete_current_user(current_user_id, current_user_name):
    with sqlite3.connect(create_db.get_db_file(), uri=True) as conn:
    #with sqlite3.connect(DB_FILE, uri=True) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        confirm_message = f"❗ Are you sure you want to delete your account '{current_user_name}'? This will permanently remove your account and all associated habits! This action cannot be undone."

        if get_yes_no_numbered(confirm_message):
            cursor.execute("DELETE FROM users WHERE user_id = ?", (current_user_id,))
            conn.commit()
            print(f"✅ Your account '{current_user_name}' has been deleted.")
            return True
        else:
            print("❌ Account deletion canceled.")
            return False    


def select_existing_user():
    with sqlite3.connect(create_db.get_db_file(), uri=True) as conn:
    #with sqlite3.connect(DB_FILE, uri=True) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, user_name_display FROM users ORDER BY user_id")
        users = cursor.fetchall()

        if not users:
            return "NO_USERS"

        user_names = [uname for (_, uname) in users]
        selected_index = get_valid_index_input("Select a user:", user_names, go_back=True, allow_exit=True)

        if selected_index is None:
            return None
        elif selected_index == "exit":
            exit_application()
        return users[selected_index]


def get_existing_usernames():
    with sqlite3.connect(create_db.get_db_file(), uri=True) as conn:
    #with sqlite3.connect(DB_FILE, uri=True) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_name_display FROM users")
        rows = cursor.fetchall()
        return [row[0] for row in rows]


def login_flow():
    while True:
        options = ["Select from existing usernames", "Create a new user"]
        choice = get_valid_index_input("=== Login ===", options, allow_exit=True)

        if choice == "exit":
            exit_application()

        if choice == 0:
            result = select_existing_user()
            if result == "NO_USERS":
                print("No users found. Let's create one.")
                return create_user()
            elif result is None:
                continue
            else:
                return result

        elif choice == 1:
            result = create_user()
            if result is None:
                continue
            return result