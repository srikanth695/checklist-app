# Checklist App (Flask)

A comprehensive Python + Flask app for productivity management. Track daily schedules, habits, journal entries, and goals with built-in analytics, dark mode, and multi-page interface.

## Features

### Core Modules
- **📅 Schedule**: Daily event planning and time blocking
- **🔄 Habits**: Streak tracking, completion rates, categorized habits
- **📝 Journal**: Mood tracking, reflection-based journaling, tags
- **🎯 Goals & AI**: Goal-based suggestions and planning (static suggestions)
- **📊 Analytics**: Daily metrics, productivity tracking, mood correlation
- **⏰ Routines**: Morning/evening/custom routine templates
- **✅ Task Management**: Priority, deadline, effort estimation, recurring tasks, tags

### UI/UX
- 🌙 **Dark Mode Toggle**: Persistent theme with localStorage
- 📱 **Responsive Design**: Mobile-friendly multi-page app
- 🎨 **Modern Styling**: Bootstrap 5 with custom gradient cards and smooth transitions
- ⚡ **HTMX Integration**: Fast, reactive form submissions without page reload

## Quick Start

### 1. Create and activate a virtual environment

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r "requrments.txt"
```

### 3. (Optional) Seed sample data

Populate the database with demo data for testing:

```bash
python seed.py
```

This creates:
- 7 sample tasks with various priorities
- 6 habits with tracking history
- 4 schedule events
- 3 routine templates
- 4 journal entries with mood tracking
- 7 days of daily metrics

### 4. Run the app

```bash
python run.py
```

Open http://127.0.0.1:5000 in your browser.

## Running Tests

### Run all tests

```bash
pytest test_app.py -v
```

### Run specific test class

```bash
pytest test_app.py::TestTaskModel -v
```

### Run with coverage report

```bash
pytest test_app.py --cov=app --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`.

### Test Results

- **24 tests total** - All passing ✅
- **Test Categories:**
  - Task model and workflow (3)
  - Habit tracking and metrics (4)
  - Journal and mood tracking (3)
  - Routine templates (2)
  - Daily analytics (2)
  - Route integration tests (6)
  - AI suggestion API (2)

## Database

The app uses **SQLite** (`data.db` in project root) with the following tables:

- `schedule_events` - Daily calendar events
- `tasks` - To-do items with priority/deadline/effort
- `habits` - Habit definitions with streak tracking
- `habit_entries` - Daily habit completion log
- `journal_entries` - Journal entries with mood tracking
- `routines` - Routine templates
- `daily_metrics` - Daily productivity metrics

## Project Structure

```
.
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models
│   ├── routes.py            # Flask routes
│   ├── ai.py                # Static suggestion engine
│   └── static/
│       ├── styles.css       # Main stylesheet + dark mode
│       └── favicon.svg      # App icon
├── templates/
│   ├── base.html            # Base layout with navbar & dark mode toggle
│   ├── index.html           # Schedule page
│   ├── habits.html          # Habits tracker
│   ├── journal.html         # Journal entries
│   ├── ai.html              # Goals & suggestions
│   └── partials/            # HTMX components
├── run.py                   # Flask development server
├── seed.py                  # Database seeding script
├── test_app.py              # Unit & integration tests
├── requrments.txt           # Python dependencies
└── README.md                # This file
```

## Navigation

Click the navbar links to navigate between pages:
- **Schedule** - Add/view daily events
- **Habits** - Create and track habits
- **Journal** - Write entries and track mood
- **Goals & AI** - Get suggestions for goals
- **🌙 Dark Mode** - Toggle theme (persists in browser)

## Key Pages

### Schedule
Organize your day with time-blocked events. Add title, date, time, duration, and notes.

### Habits
Build consistency by tracking daily/weekly habits. View streak, completion %, and frequency.

### Journal
Reflect on your day with mood tracking. Choose reflection type: gratitude, brain dump, or free form.

### Goals & AI
Select a goal type (Get Healthy, Complete Course, Finish Project) and get personalized suggestions.

## Customization

### Change database location
Edit `app/__init__.py` and modify the `db_file` path or `SQLALCHEMY_DATABASE_URI`.

### Add custom CSS
Modify `app/static/styles.css` to customize colors, fonts, and layouts.

### Add more suggestion templates
Edit the `get_ai_suggestions()` function in `app/ai.py` to add new goal types.

## Notes

- The app uses **built-in static suggestions** (no external AI required)
- Database is created automatically on first run
- Dark mode preference is saved to browser localStorage
- All routes support HTMX for reactive updates

## Tech Stack

- **Backend**: Flask 3.1.3, SQLAlchemy ORM
- **Database**: SQLite
- **Frontend**: Bootstrap 5, HTMX, JavaScript (dark mode)
- **Testing**: Pytest, Pytest-Flask

## License

MIT License - Feel free to use and modify!
