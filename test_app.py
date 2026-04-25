"""
Unit and integration tests for the Checklist App.
Usage: pytest test_app.py -v
"""
import unittest
from datetime import datetime, date, timedelta
from app import create_app, db
from app.models import (
    Task, Habit, HabitEntry, ScheduleEvent, JournalEntry,
    Routine, DailyMetric
)


class BaseTestCase(unittest.TestCase):
    """Base test case with setup and teardown."""

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


class TestTaskModel(BaseTestCase):
    """Test Task model."""

    def test_create_task(self):
        """Test creating a task."""
        with self.app.app_context():
            task = Task(
                title="Test task",
                priority="high",
                deadline=date.today() + timedelta(days=1),
                effort_minutes=60
            )
            db.session.add(task)
            db.session.commit()
            
            fetched = Task.query.filter_by(title="Test task").first()
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.priority, "high")
            self.assertEqual(fetched.status, "inbox")

    def test_task_status_transitions(self):
        """Test task status workflow."""
        with self.app.app_context():
            task = Task(title="Status test")
            db.session.add(task)
            db.session.commit()
            
            fetched = Task.query.first()
            self.assertEqual(fetched.status, "inbox")
            
            fetched.status = "todo"
            fetched.status = "in_progress"
            fetched.completed = True
            fetched.completion_date = datetime.utcnow()
            db.session.commit()
            
            refreshed = Task.query.first()
            self.assertTrue(refreshed.completed)
            self.assertIsNotNone(refreshed.completion_date)

    def test_task_tags(self):
        """Test task tagging."""
        with self.app.app_context():
            task = Task(
                title="Tagged task",
                tags="work,urgent,project"
            )
            db.session.add(task)
            db.session.commit()
            
            fetched = Task.query.first()
            self.assertIn("work", fetched.tags)


class TestHabitModel(BaseTestCase):
    """Test Habit model and tracking."""

    def test_create_habit(self):
        """Test creating a habit."""
        with self.app.app_context():
            habit = Habit(
                name="Morning run",
                category="fitness",
                frequency="daily",
                difficulty="hard"
            )
            db.session.add(habit)
            db.session.commit()
            
            fetched = Habit.query.filter_by(name="Morning run").first()
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.category, "fitness")

    def test_habit_streak_tracking(self):
        """Test habit streak system."""
        with self.app.app_context():
            habit = Habit(name="Meditate", streak=5, longest_streak=10)
            db.session.add(habit)
            db.session.commit()
            
            fetched = Habit.query.first()
            self.assertEqual(fetched.streak, 5)
            self.assertEqual(fetched.longest_streak, 10)

    def test_habit_entries(self):
        """Test habit completion tracking."""
        with self.app.app_context():
            habit = Habit(name="Exercise")
            db.session.add(habit)
            db.session.commit()
            
            today = date.today()
            for i in range(7):
                entry = HabitEntry(
                    habit_id=habit.id,
                    date=today - timedelta(days=i),
                    completed=(i % 2 == 0)
                )
                db.session.add(entry)
            db.session.commit()
            
            entries = HabitEntry.query.filter_by(habit_id=habit.id).all()
            completed = [e for e in entries if e.completed]
            self.assertEqual(len(entries), 7)
            self.assertEqual(len(completed), 4)

    def test_completion_percentage(self):
        """Test habit completion percentage calculation."""
        with self.app.app_context():
            habit = Habit(name="Yoga", completion_pct=75.0)
            db.session.add(habit)
            db.session.commit()
            
            fetched = Habit.query.first()
            self.assertEqual(fetched.completion_pct, 75.0)


class TestJournalModel(BaseTestCase):
    """Test Journal model."""

    def test_create_journal_entry(self):
        """Test creating a journal entry."""
        with self.app.app_context():
            entry = JournalEntry(
                title="Today's reflection",
                content="Had a productive day.",
                mood="good",
                mood_score=4,
                reflection_type="reflection"
            )
            db.session.add(entry)
            db.session.commit()
            
            fetched = JournalEntry.query.first()
            self.assertEqual(fetched.mood, "good")
            self.assertEqual(fetched.mood_score, 4)

    def test_journal_mood_tracking(self):
        """Test mood tracking across entries."""
        with self.app.app_context():
            moods = [
                ("Day 1", "excellent", 5),
                ("Day 2", "good", 4),
                ("Day 3", "bad", 2),
            ]
            
            for title, mood, score in moods:
                entry = JournalEntry(
                    title=title,
                    content=f"{title} content",
                    mood=mood,
                    mood_score=score
                )
                db.session.add(entry)
            db.session.commit()
            
            entries = JournalEntry.query.all()
            avg_mood = sum(e.mood_score for e in entries) / len(entries)
            self.assertAlmostEqual(avg_mood, 3.67, places=1)

    def test_journal_tags(self):
        """Test journal entry tagging."""
        with self.app.app_context():
            entry = JournalEntry(
                title="Work day",
                content="Great progress",
                tags="work,productivity,team"
            )
            db.session.add(entry)
            db.session.commit()
            
            fetched = JournalEntry.query.first()
            self.assertIn("work", fetched.tags)


class TestRoutineModel(BaseTestCase):
    """Test Routine model."""

    def test_create_routine(self):
        """Test creating a routine."""
        with self.app.app_context():
            routine = Routine(
                name="Morning routine",
                routine_type="morning",
                day_type="weekday",
                items='["Meditate", "Shower", "Breakfast"]'
            )
            db.session.add(routine)
            db.session.commit()
            
            fetched = Routine.query.first()
            self.assertEqual(fetched.routine_type, "morning")
            self.assertIn("Meditate", fetched.items)

    def test_routine_types(self):
        """Test different routine types."""
        with self.app.app_context():
            routine_types = ["morning", "evening", "workout"]
            for rt in routine_types:
                routine = Routine(
                    name=f"{rt.capitalize()} routine",
                    routine_type=rt
                )
                db.session.add(routine)
            db.session.commit()
            
            routines = Routine.query.all()
            self.assertEqual(len(routines), 3)


class TestDailyMetricsModel(BaseTestCase):
    """Test DailyMetric model."""

    def test_create_daily_metric(self):
        """Test creating daily metrics."""
        with self.app.app_context():
            metric = DailyMetric(
                date=date.today(),
                tasks_completed=5,
                tasks_total=10,
                habits_completed=4,
                habits_total=6,
                avg_mood=4.0,
                focus_minutes=300
            )
            db.session.add(metric)
            db.session.commit()
            
            fetched = DailyMetric.query.filter_by(date=date.today()).first()
            self.assertEqual(fetched.tasks_completed, 5)
            self.assertEqual(fetched.focus_minutes, 300)

    def test_productivity_metrics(self):
        """Test calculating productivity metrics."""
        with self.app.app_context():
            today = date.today()
            metrics = []
            
            for i in range(7):
                metric = DailyMetric(
                    date=today - timedelta(days=i),
                    tasks_completed=6 - i,
                    tasks_total=10,
                    habits_completed=5,
                    habits_total=6,
                    avg_mood=4 - (i % 2)
                )
                metrics.append(metric)
                db.session.add(metric)
            db.session.commit()
            
            all_metrics = DailyMetric.query.all()
            avg_tasks_completed = sum(m.tasks_completed for m in all_metrics) / len(all_metrics)
            self.assertGreater(avg_tasks_completed, 0)


class TestRoutesIntegration(BaseTestCase):
    """Integration tests for Flask routes."""

    def test_index_page(self):
        """Test index page loads."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_habits_page(self):
        """Test habits page loads."""
        response = self.client.get('/habits')
        self.assertEqual(response.status_code, 200)

    def test_journal_page(self):
        """Test journal page loads."""
        response = self.client.get('/journal')
        self.assertEqual(response.status_code, 200)

    def test_ai_page(self):
        """Test AI/goals page loads."""
        response = self.client.get('/goals')
        self.assertEqual(response.status_code, 200)

    def test_favicon_redirect(self):
        """Test favicon redirects."""
        response = self.client.get('/favicon.ico', follow_redirects=False)
        self.assertIn(response.status_code, [301, 302, 303, 307, 308])

    def test_add_schedule_event(self):
        """Test adding a schedule event."""
        with self.app.app_context():
            data = {
                'title': 'Test event',
                'date': date.today().isoformat(),
                'time': '14:00',
                'duration': '60'
            }
            response = self.client.post('/schedule/add', data=data)
            self.assertIn(response.status_code, [200, 302])

    def test_add_habit(self):
        """Test adding a habit."""
        with self.app.app_context():
            data = {
                'name': 'Test habit',
                'frequency': 'daily'
            }
            response = self.client.post('/habit/add', data=data)
            self.assertIn(response.status_code, [200, 204, 302])

    def test_add_journal(self):
        """Test adding a journal entry."""
        with self.app.app_context():
            data = {
                'title': 'Test entry',
                'content': 'Test content'
            }
            response = self.client.post('/journal/add', data=data)
            self.assertIn(response.status_code, [200, 302])


class TestAISuggestions(BaseTestCase):
    """Test AI suggestion functionality."""

    def test_ai_suggestions_endpoint(self):
        """Test AI suggestions API."""
        response = self.client.post('/api/ai_suggest', json={
            'goal_type': 'get_healthy',
            'details': 'Want to build a fitness routine'
        })
        self.assertEqual(response.status_code, 200)

    def test_all_goal_types(self):
        """Test all goal types return suggestions."""
        goals = ['get_healthy', 'complete_course', 'finish_project']
        
        for goal in goals:
            response = self.client.post('/api/ai_suggest', json={
                'goal_type': goal,
                'details': 'Sample details'
            })
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIn('summary', data)
            self.assertIn('tasks', data)


if __name__ == '__main__':
    unittest.main()
