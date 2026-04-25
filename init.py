"""
Initialize the database with empty tables.
Usage: python init.py
"""
from app import create_app, db

def init_database():
    app = create_app()
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database initialized successfully!")
        print("   Tables created: schedule_events, tasks, habits, habit_entries,")
        print("   journal_entries, routines, daily_metrics")
        print("\n(Optional) Run 'python seed.py' to populate with sample data.")

if __name__ == "__main__":
    init_database()
