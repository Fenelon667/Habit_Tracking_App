"""
User Flow Module for the Habit Tracker application.

Handles user login, account creation, selection, and deletion.

Functions:
- create_user: Prompts for a new username, validates it, and inserts it into the database if unique.
- delete_current_user: Confirms and deletes the current user along with all associated habits and completions.
- select_existing_user: Displays and allows selection from registered users.
- get_existing_usernames: Returns all usernames in the database.
- login_flow: Guides the user through login or account creation, with support for going back and exiting.

Notes:
- All usernames are stored in lowercase for uniqueness, but the original casing is preserved for display.
- Input validation ensures clean and consistent data.
- Foreign key constraints ensure that deleting a user also deletes related habits and habit completions.
"""

import sqlite3
from create_db import DB_FILE
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
            with sqlite3.connect(DB_FILE, uri=True) as conn:
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
    with sqlite3.connect(DB_FILE, uri=True) as conn:
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
    with sqlite3.connect(DB_FILE, uri=True) as conn:
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
    with sqlite3.connect(DB_FILE, uri=True) as conn:
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