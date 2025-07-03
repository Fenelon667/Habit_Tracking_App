# Habit Tracking Application
## Project Description
A command-line based Habit Tracker that helps users build and maintain routines by tracking daily and weekly habit completions. 
This project was built to help users stay consistent with positive habits and routines. 
Users can create and delete habits, mark them as completed, and view progress over time including current and longest streaks. 
The app provides analytics and reminders for habits due today.
It also includes built-in user management, allowing multiple users to create and manage their own habit profiles. 
Each user account stores personalized habit data and tracking history, enabling secure and private usage for different individuals on the same system.
This tool is ideal for individuals who prefer a simple, local, terminal-based solution to monitor personal growth without relying on third-party apps or services. 


## Technologies Used
The application was built with Python and SQLite, and uses a modular code structure with support for unit testing via Pytest.

## Features
- ✅ **User Accounts**
  - Create multiple user profiles with individual login and habit data
  - Private and secure usage on the same system

- 📝 **Habit Management**
  - Create new habits with customizable frequency (daily or weekly)
  - Delete existing habits as needed

- 📅 **Completion Tracking**
  - Mark completions with automatic timestamp logging
  - Prevent duplicate completions on the same day (for daily habits) or week (for weekly habits)

- 🔁 **Streak Analytics**
  - Track your current and longest streaks to stay consistent

- 📊 **Data Visualization (Text-Based)**
  - See summaries of all your habits
  - Filter habits by frequency or completion status

- 🧪 **Testable and Modular Code**
  - Cleanly separated logic into modules (user flow, habit flow, analytics)
  - Pytest-enabled for unit testing key features
 
## Installation
Follow these steps to set up and run the Habit Tracking Application on your local machine.

### 1. Clone the repository:
   ```bash
   git clone https://github.com/Fenelon667/Habit_Tracking_App
   cd Habit_Tracking_App
   ```

### 2. Create and activate a virtual environment (Optional)
  ```bash
  python -m venv venv
  ```
  #### On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
  #### On Windows:
  ```bash
  venv\Scripts\activate
  ```
  
### 3. Install dependencies
  ```bash
  pip install -r requirements.txt
  ```
If you don't have a requirements.txt file, you can manually install needed packages like this:
pip install pytest

### 4. Run the application
  ```bash
  python main.py
  ```
  You will be prompted to log in or create a new user. Once logged in, you can:
- Create and track habits
- Mark completions
- View habits due today
- Check streaks

## Running Tests
This project uses **[Pytest](https://docs.pytest.org/)** for unit testing.
To run all tests, open your terminal and run:
```bash
pytest
```
Make sure you're in the root project directory where your test files (named like test_*.py) are located — typically in a test/ or tests/ folder.

Each test provides printed output to show what is being tested and whether it passed. This makes it easier to follow along when running tests manually.
To see detailed output in the terminal, run:
```bash
pytest -s
```
The -s flag allows print() statements inside tests to be shown in the console.


