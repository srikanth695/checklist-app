"""
Seed script to populate the database with sample data for testing.
Usage: python seed.py
"""
from datetime import datetime, timedelta, date
from app import create_app, db
from app.models import (
    Task, Habit, HabitEntry, ScheduleEvent, JournalEntry, 
    Routine, DailyMetric, Goal, DailyChecklistItem
)

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        print("✓ Database cleared and recreated")

        # === TASKS ===
        today = date.today()
        tasks = [
            Task(
                title="Complete project proposal",
                description="Finish Q2 project proposal and send to manager",
                priority="high",
                deadline=today + timedelta(days=2),
                effort_minutes=120,
                tags="work,project",
                status="in_progress"
            ),
            Task(
                title="Call client about Q2 roadmap",
                description="Discuss timeline and deliverables",
                priority="high",
                deadline=today + timedelta(days=1),
                effort_minutes=30,
                tags="work,communication",
                status="todo"
            ),
            Task(
                title="Review pull requests",
                priority="medium",
                deadline=today,
                effort_minutes=60,
                tags="work,code",
                status="todo"
            ),
            Task(
                title="Workout session",
                priority="medium",
                deadline=today,
                effort_minutes=45,
                tags="health,fitness",
                status="done",
                completed=True,
                completion_date=datetime.now() - timedelta(hours=2)
            ),
            Task(
                title="Read 'Atomic Habits' chapter 3",
                priority="low",
                effort_minutes=30,
                tags="learning,personal",
                status="inbox"
            ),
            Task(
                title="Plan weekend trip",
                priority="low",
                deadline=today + timedelta(days=5),
                effort_minutes=90,
                tags="personal",
                status="inbox"
            ),
            Task(
                title="Team standup meeting",
                priority="high",
                deadline=today,
                effort_minutes=15,
                tags="work,meeting",
                status="done",
                completed=True,
                completion_date=datetime.now() - timedelta(hours=4)
            ),
        ]
        db.session.add_all(tasks)
        print(f"✓ Added {len(tasks)} tasks")

        # === HABITS ===
        habits = [
            Habit(
                name="Morning meditation",
                category="health",
                frequency="daily",
                difficulty="easy",
                streak=12,
                longest_streak=18,
                completion_pct=85.0,
                last_completed=today
            ),
            Habit(
                name="Exercise/Workout",
                category="fitness",
                frequency="daily",
                difficulty="hard",
                streak=5,
                longest_streak=21,
                completion_pct=70.0,
                last_completed=today
            ),
            Habit(
                name="Read for learning",
                category="learning",
                frequency="daily",
                difficulty="medium",
                streak=8,
                longest_streak=15,
                completion_pct=65.0,
                last_completed=today - timedelta(days=1)
            ),
            Habit(
                name="Drink 8 glasses of water",
                category="health",
                frequency="daily",
                difficulty="easy",
                streak=3,
                longest_streak=7,
                completion_pct=50.0,
                last_completed=today
            ),
            Habit(
                name="Weekly review",
                category="productivity",
                frequency="weekly",
                difficulty="medium",
                streak=2,
                longest_streak=4,
                completion_pct=60.0,
                last_completed=today - timedelta(days=1)
            ),
            Habit(
                name="Code review contributions",
                category="work",
                frequency="daily",
                difficulty="medium",
                streak=9,
                longest_streak=25,
                completion_pct=80.0,
                last_completed=today
            ),
        ]
        db.session.add_all(habits)
        db.session.flush()
        print(f"✓ Added {len(habits)} habits")

        # === HABIT ENTRIES ===
        habit_entries = []
        for h in habits:
            for i in range(7):
                entry_date = today - timedelta(days=i)
                completed = (i % 2 == 0) if h.frequency == "daily" else (i == 0)
                habit_entries.append(
                    HabitEntry(
                        habit_id=h.id,
                        date=entry_date,
                        completed=completed,
                        notes=f"Completed on {entry_date}" if completed else None
                    )
                )
        db.session.add_all(habit_entries)
        print(f"✓ Added {len(habit_entries)} habit entries (tracking log)")

        # === SCHEDULE EVENTS ===
        events = [
            ScheduleEvent(
                title="Team standup",
                date=today,
                time="09:30",
                duration_minutes=15,
                completed=True
            ),
            ScheduleEvent(
                title="Client meeting",
                date=today + timedelta(days=1),
                time="14:00",
                duration_minutes=60,
                notes="Discuss Q2 deliverables"
            ),
            ScheduleEvent(
                title="Project review",
                date=today + timedelta(days=2),
                time="16:00",
                duration_minutes=30,
                notes="Internal team sync"
            ),
            ScheduleEvent(
                title="Gym session",
                date=today,
                time="18:00",
                duration_minutes=60,
                completed=True
            ),
        ]
        db.session.add_all(events)
        print(f"✓ Added {len(events)} schedule events")

        # === ROUTINES ===
        routines = [
            Routine(
                name="Morning routine",
                routine_type="morning",
                day_type="weekday",
                items='["Meditate 10min", "Shower", "Breakfast", "Review daily goals", "Check email"]'
            ),
            Routine(
                name="Evening routine",
                routine_type="evening",
                day_type="daily",
                items='["Reflect on day", "Journal 10min", "Prepare for tomorrow", "Light stretching", "Sleep 11pm"]'
            ),
            Routine(
                name="Workout routine",
                routine_type="workout",
                day_type="weekday",
                items='["Warm up 5min", "Strength training 30min", "Cardio 15min", "Cool down 10min"]'
            ),
        ]
        db.session.add_all(routines)
        print(f"✓ Added {len(routines)} routines")

        # === JOURNAL ENTRIES ===
        moods = ["excellent", "good", "neutral", "bad"]
        reflections = ["gratitude", "brain_dump", "reflection", "free_form"]
        journal_entries = [
            JournalEntry(
                title="Productive day",
                content="Got a lot done today. Completed the project proposal and had a great client call.",
                mood="good",
                mood_score=4,
                reflection_type="reflection",
                tags="work,productivity",
                created_at=datetime.now() - timedelta(hours=2)
            ),
            JournalEntry(
                title="Grateful for my team",
                content="Really appreciate how supportive my team is. They helped me debug that tricky issue.",
                mood="excellent",
                mood_score=5,
                reflection_type="gratitude",
                tags="work,team",
                created_at=datetime.now() - timedelta(days=1, hours=6)
            ),
            JournalEntry(
                title="Feeling overwhelmed",
                content="Too many tasks in the inbox. Need to prioritize and delegate more.",
                mood="bad",
                mood_score=2,
                reflection_type="brain_dump",
                tags="stress,work",
                created_at=datetime.now() - timedelta(days=2, hours=4)
            ),
            JournalEntry(
                title="Learning moment",
                content="Tried a new time-blocking approach today. Really helped with focus.",
                mood="good",
                mood_score=4,
                reflection_type="reflection",
                tags="productivity,learning",
                created_at=datetime.now() - timedelta(days=3)
            ),
        ]
        db.session.add_all(journal_entries)
        print(f"✓ Added {len(journal_entries)} journal entries")

        # === DAILY METRICS ===
        metrics = []
        for i in range(7):
            metric_date = today - timedelta(days=i)
            metrics.append(
                DailyMetric(
                    date=metric_date,
                    tasks_completed=3 + (i % 4),
                    tasks_total=8,
                    habits_completed=4 + (i % 3),
                    habits_total=6,
                    avg_mood=3 + (i % 3) * 0.5,
                    focus_minutes=240 + (i * 15),
                    created_at=datetime.now() - timedelta(days=i)
                )
            )
        db.session.add_all(metrics)
        print(f"✓ Added {len(metrics)} daily metrics")

        # === GOALS ===
        goals = [
            Goal(
                title="Exercise 4 times per week (1 Month)",
                description="Current: I exercise occasionally, about 1-2 times per week\nDesired: Exercise 4 times per week consistently and build a strong fitness routine",
                category="fitness",
                timeframe="1_month",
                target_metric="Exercise 4 times per week consistently",
                current_progress=12,
                target_progress=100,
                status="active"
            ),
            Goal(
                title="Complete 2 online courses (3 Month)",
                description="Current: Haven't completed any online courses in the past year\nDesired: Complete 2 meaningful online courses to develop new skills",
                category="learning",
                timeframe="3_month",
                target_metric="2 courses completed",
                current_progress=0,
                target_progress=100,
                status="active"
            ),
            Goal(
                title="Write 3 blog posts (1 Month)",
                description="Current: Haven't written anything in months\nDesired: Share knowledge by writing 3 technical blog posts",
                category="career",
                timeframe="1_month",
                target_metric="3 blog posts published",
                current_progress=0,
                target_progress=100,
                status="active"
            ),
            Goal(
                title="Read one full book (1 Month)",
                description="Current: Reading sporadically\nDesired: Read one complete book from start to finish",
                category="learning",
                timeframe="1_month",
                target_metric="1 book completed",
                current_progress=40,
                target_progress=100,
                status="active"
            ),
        ]
        db.session.add_all(goals)
        db.session.flush()  # Flush to get goal IDs
        print(f"✓ Added {len(goals)} goals")

        # === DAILY CHECKLIST ITEMS ===
        checklist_items = []
        for goal in goals:
            item = DailyChecklistItem(
                date=today,
                source_type='goal',
                source_id=goal.id,
                title=goal.title,
                description=f"Work on: {goal.target_metric}",
                priority='high',
                completed=False
            )
            checklist_items.append(item)
        
        # Add some custom checklist items
        custom_items = [
            DailyChecklistItem(
                date=today,
                source_type='custom',
                title='Morning meditation',
                description='10 minutes meditation session',
                priority='medium',
                completed=False
            ),
            DailyChecklistItem(
                date=today,
                source_type='custom',
                title='Code review',
                description='Review pull requests from the team',
                priority='high',
                completed=True,
                completed_at=datetime.now() - timedelta(hours=2)
            ),
            DailyChecklistItem(
                date=today,
                source_type='custom',
                title='Team standup',
                description='9:30 AM sync with the team',
                priority='high',
                completed=True,
                completed_at=datetime.now() - timedelta(hours=3)
            ),
        ]
        checklist_items.extend(custom_items)
        db.session.add_all(checklist_items)
        print(f"✓ Added {len(checklist_items)} daily checklist items")

        # Commit all changes
        db.session.commit()
        print("\n✅ Database successfully seeded with sample data!")
        print("\nSample data summary:")
        print(f"  - {len(tasks)} tasks")
        print(f"  - {len(habits)} habits with {len(habit_entries)} tracking entries")
        print(f"  - {len(events)} schedule events")
        print(f"  - {len(routines)} routines")
        print(f"  - {len(journal_entries)} journal entries")
        print(f"  - {len(metrics)} daily metrics")
        print(f"  - {len(goals)} goals")
        print(f"  - {len(checklist_items)} daily checklist items")

if __name__ == "__main__":
    seed_database()
