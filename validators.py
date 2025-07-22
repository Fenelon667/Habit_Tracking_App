"""
Validators Module for the Habit Tracker application.

Provides reusable input validation and CLI utility functions to ensure
consistent and user-friendly interactions throughout the application.

Functions:
- get_valid_index_input: Displays a numbered menu with optional 'Go back' and 'Exit Application' options.
  Validates and returns the user's choice as an index, 'exit', or None for go back.
- get_yes_no_numbered: Prompts for a Yes/No input using numbered choices (1 for Yes, 2 for No).
  Returns True for Yes and False for No.
- exit_application: Prints a goodbye message and exits the application cleanly.
"""

import sys

def get_valid_index_input(prompt: str, options: list[str], go_back: bool = False, allow_exit: bool = False) -> int | str | None:
    display_options = [f"🟢 {option}" for option in options]

    if go_back:
        display_options.append("🔙 Go back")
    if allow_exit:
        display_options.append("🚪 Exit Application")

    print(f"{prompt}")
    for i, option in enumerate(display_options, 1):
        print(f"{i}. {option}")

    while True:
        try:
            index = int(input("Enter the number: ")) - 1
            if 0 <= index < len(display_options):
                if allow_exit and index == len(display_options) - 1:
                    return "exit"
                if go_back and (
                    (allow_exit and index == len(display_options) - 2) or
                    (not allow_exit and index == len(display_options) - 1)
                ):
                    return None
                return index
            else:
                print("❌ Invalid selection. Try again.")
        except ValueError:
            print("❌ Invalid input. Enter a number.")


def get_yes_no_numbered(prompt: str) -> bool:
    print(f"{prompt}")
    print("1. 👍 Yes")
    print("2. 👎 No")

    while True:
        try:
            choice = int(input("Enter the number: ").strip())
            if choice == 1:
                return True
            elif choice == 2:
                return False
            else:
                print("❌ Invalid choice. Please enter 1 for Yes or 2 for No.\n")
        except ValueError:
            print("❌ Invalid input. Please enter a number (1 or 2).\n")


def exit_application():
    print("Goodbye!")
    sys.exit()