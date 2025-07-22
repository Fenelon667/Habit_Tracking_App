'''
This test file verifies the user flow functions of the Habit Tracker application.
Tests are run using an in-memory SQLite database to avoid modifying the real habit_tracker.db database.

Covered features:
- Creating a user (test_create_user)
- Deleting the currently logged-in user:
    - test_delete_current_user_confirm_yes: user confirms deletion, account is removed
    - test_delete_current_user_confirm_no: user cancels deletion, account is preserved
- Selecting existing users (test_select_existing_user)
- Getting a list of all existing usernames (test_get_existing_usernames)
- Simulating login flow:
    - test_login_flow_enter_new_user: user selects option 2 and creates a new account
    - test_login_flow_select_existing_user: user selects an existing account from the list
    - test_login_flow_no_existing_users: user attempts to select from a list when no users exist
    - test_login_flow_exit: user chooses to exit the application
'''

import pytest
import os
import sys
import user_flow
from user_flow import create_user
import validators

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)



# --------------------------- TEST: Create a new user --------------------------------

def test_create_user(monkeypatch, test_db, capfd):
    monkeypatch.setattr("builtins.input", lambda _: "TestUser")

    test_db.commit()

    # Run the function
    user_id, user_name = create_user()

    cursor = test_db.cursor()
    cursor.execute("SELECT user_name_display FROM users ORDER BY user_id")
    result = cursor.fetchone()

    print("Created user in DB:", result[0])

    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_create_user---")
    print(out)

    assert result is not None
    assert user_name == "TestUser"
    assert result[0] == "TestUser"
    assert "TestUser" in out

# --------------------------- TEST: Delete the selected user --------------------------------

def test_delete_current_user_confirm_yes(monkeypatch, test_db, capfd):
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("deleteme", "Deleteme"))
    test_db.commit()
    user_id = cursor.lastrowid

    monkeypatch.setattr("builtins.input", lambda _: "1")

    result = user_flow.delete_current_user(user_id, "Deleteme")
    out, err = capfd.readouterr()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    print("--- CAPTURED OUTPUT FOR test_delete_current_user_confirm_yes ---")
    print(out)

    assert result is True
    assert "has been deleted" in out
    assert user is None

def test_delete_current_user_confirm_no(monkeypatch, test_db, capfd):
    cursor = test_db.cursor()
    cursor.execute("INSERT INTO users (user_name, user_name_display) VALUES (?, ?)", ("keeplease", "Keeplease"))
    test_db.commit()
    user_id = cursor.lastrowid

    monkeypatch.setattr("builtins.input", lambda _: "2")

    result = user_flow.delete_current_user(user_id, "Keeplease")
    out, err = capfd.readouterr()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    print("--- CAPTURED OUTPUT FOR test_delete_current_user_confirm_no ---")
    print(out)

    assert result is False
    assert "deletion canceled" in out.lower()
    assert user is not None

# --------------------------- TEST: Select existing users ------------------------------

def test_select_existing_user(monkeypatch, test_db, capfd):
    monkeypatch.setattr(validators, "get_valid_index_input", lambda prompt, opts, go_back=True: 2)

    cursor = test_db.cursor()
    cursor.executemany(
        "INSERT INTO users (user_name, user_name_display) VALUES (?, ?)",
        [("nicole", "Nicole"), ("simon", "Simon"), ("lilly", "Lilly")]
    )
    test_db.commit()

    monkeypatch.setattr("builtins.input", lambda _: "2")

    user_id, selected = user_flow.select_existing_user()
    assert selected == "Simon"

    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_select_existing_user---")
    print(out)
    print(repr(out))
    assert "Select a user:" in out
    assert "2. 🟢 Simon" in out.splitlines()[2]

# --------------------------- TEST: Select existing usernames ------------------------------

def test_get_existing_usernames(monkeypatch, test_db, capfd):
    cursor = test_db.cursor()
    cursor.executemany(
        "INSERT INTO users (user_name, user_name_display) VALUES (?, ?)",
        [("nicole", "Nicole"), ("simon", "Simon"), ("lilly", "Lilly")]
    )
    test_db.commit()

    usernames = user_flow.get_existing_usernames()

    print("Usernames found:", usernames)

    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_get_existing_usernames---")
    print(out)

    assert "Nicole" in usernames
    assert "Simon" in usernames
    assert "Lilly" in usernames

# --------------------------- TEST: User Login Flow ------------------------------

def test_login_flow_enter_new_user(monkeypatch, test_db, capfd):
    import create_db

    inputs = iter(["2", "TestUser"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    user_id, username = user_flow.login_flow()

    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_login_flow_enter_new_user ---")
    print(out)

    assert username == "TestUser"

def test_login_flow_select_existing_user(monkeypatch, test_db, capfd):
    monkeypatch.setattr(validators, "get_valid_index_input", lambda prompt, opts, go_back=True: 1)

    cursor = test_db.cursor()
    cursor.executemany(
        "INSERT INTO users (user_name, user_name_display) VALUES (?, ?)",
        [("nicole", "Nicole"), ("simon", "Simon"), ("lilly", "Lilly")]
    )
    test_db.commit()

    inputs = iter(["1", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    user_id, username = user_flow.login_flow()

    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_login_flow_select_existing_user ---")
    print(out)

    assert "=== Login ===" in out
    assert username == "Simon"

def test_login_flow_no_existing_users(monkeypatch, test_db, capfd):
    monkeypatch.setattr(validators, "get_valid_index_input", lambda prompt, opts, go_back=True: 1)

    inputs = iter(["1", "Nicole"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    user_id, username = user_flow.login_flow()

    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_login_flow_no_existing_users ---")
    print(out)

    assert "No users found" in out
    assert username == "Nicole"

def test_login_flow_exit(monkeypatch, test_db, capfd):
    monkeypatch.setattr("builtins.input", lambda _: "3")
    monkeypatch.setattr("builtins.exit", lambda: (_ for _ in ()).throw(SystemExit))

    with pytest.raises(SystemExit):
        user_flow.login_flow()

    out, err = capfd.readouterr()
    print("--- CAPTURED OUTPUT FOR test_login_flow_exit ---")
    print(out)

    assert "Goodbye!" in out