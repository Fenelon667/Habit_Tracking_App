"""
Validation Tests for the Habit Tracker application.

This test suite verifies the behavior of input validation and CLI utility functions
defined in the validators module. The tests simulate user input and ensure the functions
handle valid, invalid, and edge-case inputs correctly, providing expected output or
raising appropriate exceptions.

Covered functions:
- get_valid_index_input:
    - test_get_valid_index_input_valid_choice: Valid numeric choice is accepted.
    - test_get_valid_index_input_invalid_then_valid: Handles invalid inputs before valid choice.
- get_yes_no_numbered:
    - test_get_yes_no_numbered_yes: User inputs 'Yes'.
    - test_get_yes_no_numbered_invalid_then_no: Handles invalid inputs before user inputs 'No'.
- exit_application:
    - test_exit_application: Confirms system exit is triggered correctly.

Notes:
- Uses monkeypatching to mock user input and system exit calls.
- Captures standard output to verify error messages.
- Ensures the CLI input validation is robust and user-friendly.
"""

import pytest
import validators
import builtins
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_get_valid_index_input_valid_choice(monkeypatch):
    inputs = iter(['1'])
    monkeypatch.setattr(builtins, 'input', lambda _: next(inputs))
    choice = validators.get_valid_index_input("Choose option:", ["opt1", "opt2"])
    assert choice == 0

def test_get_valid_index_input_invalid_then_valid(monkeypatch, capsys):
    inputs = iter(['abc', '5', '2'])
    monkeypatch.setattr(builtins, 'input', lambda _: next(inputs))
    choice = validators.get_valid_index_input("Choose option:", ["opt1", "opt2"])
    captured = capsys.readouterr()
    assert "Invalid input" in captured.out
    assert "Invalid selection" in captured.out
    assert choice == 1

def test_get_yes_no_numbered_yes(monkeypatch):
    inputs = iter(['1'])
    monkeypatch.setattr(builtins, 'input', lambda _: next(inputs))
    assert validators.get_yes_no_numbered("Confirm?") is True

def test_get_yes_no_numbered_invalid_then_no(monkeypatch, capsys):
    inputs = iter(['x', '3', '2'])
    monkeypatch.setattr(builtins, 'input', lambda _: next(inputs))
    result = validators.get_yes_no_numbered("Confirm?")
    captured = capsys.readouterr()
    assert "Invalid input" in captured.out
    assert result is False

def test_exit_application(monkeypatch):
    called = {}

    def fake_exit():
        called['exit'] = True
        raise SystemExit

    # Monkeypatch sys.exit, which is called inside exit_application
    monkeypatch.setattr(sys, 'exit', fake_exit)

    with pytest.raises(SystemExit):
        validators.exit_application()

    assert 'exit' in called and called['exit'] is True