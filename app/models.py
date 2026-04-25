from datetime import datetime, timedelta
from . import db

class ScheduleEvent(db.Model):
    __tablename__ = 'schedule_events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(20))
    duration_minutes = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    deadline = db.Column(db.Date)
    effort_minutes = db.Column(db.Integer)  # estimated effort
    tags = db.Column(db.String(500))  # comma-separated
    status = db.Column(db.String(20), default='inbox')  # inbox, todo, in_progress, done
    recurring = db.Column(db.String(20))  # daily, weekly, monthly, or null
    completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HabitEntry(db.Model):
    __tablename__ = 'habit_entries'
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

class Habit(db.Model):
    __tablename__ = 'habits'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))  # fitness, learning, health, etc.
    frequency = db.Column(db.String(20), default='daily')
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    completion_pct = db.Column(db.Float, default=0.0)
    last_completed = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Routine(db.Model):
    __tablename__ = 'routines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    routine_type = db.Column(db.String(50))  # morning, evening, workout, etc.
    day_type = db.Column(db.String(20), default='weekday')  # weekday, weekend, daily
    items = db.Column(db.Text)  # JSON list of routine items
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    mood = db.Column(db.String(20))  # excellent, good, neutral, bad, terrible
    mood_score = db.Column(db.Integer)  # 1-5
    reflection_type = db.Column(db.String(50))  # gratitude, brain_dump, reflection, free_form
    tags = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DailyMetric(db.Model):
    __tablename__ = 'daily_metrics'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    tasks_completed = db.Column(db.Integer, default=0)
    tasks_total = db.Column(db.Integer, default=0)
    habits_completed = db.Column(db.Integer, default=0)
    habits_total = db.Column(db.Integer, default=0)
    avg_mood = db.Column(db.Float, default=0.0)
    focus_minutes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
