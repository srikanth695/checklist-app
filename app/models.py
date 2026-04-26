from datetime import datetime, timedelta
from . import db

class ScheduleEvent(db.Model):
    __tablename__ = 'schedule_events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
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
    deadline = db.Column(db.Date, index=True)
    effort_minutes = db.Column(db.Integer)  # estimated effort
    tags = db.Column(db.String(500))  # comma-separated
    status = db.Column(db.String(20), default='inbox', index=True)  # inbox, todo, in_progress, done
    recurring = db.Column(db.String(20))  # daily, weekly, monthly, or null
    completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HabitEntry(db.Model):
    __tablename__ = 'habit_entries'
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id', ondelete='CASCADE'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

class Habit(db.Model):
    __tablename__ = 'habits'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), index=True)  # fitness, learning, health, etc.
    frequency = db.Column(db.String(20), default='daily')
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    completion_pct = db.Column(db.Float, default=0.0)
    last_completed = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with cascading deletes
    entries = db.relationship('HabitEntry', cascade='all, delete-orphan', backref='habit')

class Routine(db.Model):
    __tablename__ = 'routines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    routine_type = db.Column(db.String(50), index=True)  # morning, evening, workout, etc.
    day_type = db.Column(db.String(20), default='weekday')  # weekday, weekend, daily
    items = db.Column(db.Text)  # JSON list of routine items
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), index=True)
    content = db.Column(db.Text)
    mood = db.Column(db.String(20), index=True)  # excellent, good, neutral, bad, terrible
    mood_score = db.Column(db.Integer)  # 1-5
    reflection_type = db.Column(db.String(50))  # gratitude, brain_dump, reflection, free_form
    tags = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class DailyMetric(db.Model):
    __tablename__ = 'daily_metrics'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True, index=True)
    tasks_completed = db.Column(db.Integer, default=0)
    tasks_total = db.Column(db.Integer, default=0)
    habits_completed = db.Column(db.Integer, default=0)
    habits_total = db.Column(db.Integer, default=0)
    avg_mood = db.Column(db.Float, default=0.0)
    focus_minutes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), index=True)  # health, career, learning, fitness, etc.
    timeframe = db.Column(db.String(50))  # 1_week, 2_week, 1_month, 3_month, 6_month, 1_year
    target_metric = db.Column(db.String(200))  # e.g., "Exercise 30 min", "Read 20 pages"
    current_progress = db.Column(db.Integer, default=0)
    target_progress = db.Column(db.Integer, default=100)
    status = db.Column(db.String(20), default='active', index=True)  # active, paused, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with cascading deletes
    checklist_items = db.relationship('DailyChecklistItem', cascade='all, delete-orphan', 
                                     foreign_keys='DailyChecklistItem.source_id',
                                     primaryjoin='and_(Goal.id==DailyChecklistItem.source_id, DailyChecklistItem.source_type=="goal")')

class DailyChecklistItem(db.Model):
    __tablename__ = 'daily_checklist_items'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    source_type = db.Column(db.String(20), index=True)  # 'goal', 'habit', 'task', 'custom'
    source_id = db.Column(db.Integer, index=True)  # ID of the goal, habit, or task
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium', index=True)  # low, medium, high
    completed = db.Column(db.Boolean, default=False, index=True)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
