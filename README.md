# Productivity Planner (Windows Desktop MVP)

A lightweight local-first productivity app built with **Python + PySide6 + SQLite**.

## Features
- Dashboard (today's tasks, overdue, upcoming, summaries)
- Pendings CRUD with priority/status/category, filters, search
- To-Do quick list with checkbox completion, reorder, clear completed, optional due date/category
- Calendar with monthly view, due-item list, and add-from-date actions
- Offline local storage in SQLite with auto-save

## Project Structure
```
productivity_app/
  app.py
  database.py
  models.py
  ui/
    main_window.py
    dashboard.py
    pendings_view.py
    todo_view.py
    calendar_view.py
    settings_view.py
  assets/
requirements.txt
README.md
```

## Setup
1. Install Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run app:
   ```bash
   cd productivity_app
   python app.py
   ```

## Data Storage
- SQLite DB file: `productivity.db` (created automatically in `productivity_app/`)
- Tables: `pendings`, `todos`
- Includes basic seed data on first run.

## UX Direction
- Light neutral theme
- Rounded cards and controls
- Sidebar navigation and focused content area
- Overdue items highlighted in red

## Error Handling / Validation
- Prevents empty pending title and empty quick-task text
- Confirms before deleting pending/todo

## Packaging for Windows (EXE)
This repository now includes:
- `packaging/productivity_planner.spec`
- `build_windows.bat`

On a **Windows machine** run:
```bat
build_windows.bat
```

Output:
- `dist\ProductivityPlanner.exe`

> Note: EXE generation must be done on Windows (or equivalent Windows build environment).

## Design Decisions
- **PySide6** selected for quick clean Windows-native desktop MVP.
- **SQLite** selected for reliable local persistence and future extensibility.
- Modular UI files to support future feature growth.
