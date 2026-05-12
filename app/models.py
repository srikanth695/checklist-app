from datetime import datetime, timedelta
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class ScheduleEvent(db.Model):
    __tablename__ = 'schedule_events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
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


# User and Authentication Models (GDPR Compliant)
class User(UserMixin, db.Model):
    """User model with GDPR compliance for EU norms."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth-only accounts
    
    # OAuth fields
    google_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    google_profile_pic = db.Column(db.String(500), nullable=True)
    
    # User profile data
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    
    # Privacy & GDPR compliance
    data_processing_consent = db.Column(db.Boolean, default=False)  # GDPR: explicit consent required
    marketing_consent = db.Column(db.Boolean, default=False)  # GDPR: marketing emails
    gdpr_consent_date = db.Column(db.DateTime, nullable=True)  # When user consented
    last_gdpr_review = db.Column(db.DateTime, nullable=True)  # Last GDPR policy review
    data_export_requested = db.Column(db.Boolean, default=False)
    data_deletion_requested = db.Column(db.Boolean, default=False)
    
    # Account management
    is_active = db.Column(db.Boolean, default=True, index=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    last_ip = db.Column(db.String(45), nullable=True)  # Supports IPv6
    
    # Relationships
    habits = db.relationship('Habit', backref='user', cascade='all, delete-orphan', foreign_keys='Habit.user_id')
    schedules = db.relationship('ScheduleEvent', backref='user', cascade='all, delete-orphan', foreign_keys='ScheduleEvent.user_id')
    journals = db.relationship('JournalEntry', backref='user', cascade='all, delete-orphan', foreign_keys='JournalEntry.user_id')
    goals = db.relationship('Goal', backref='user', cascade='all, delete-orphan', foreign_keys='Goal.user_id')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password is correct."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary (for GDPR data export)."""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_picture': self.google_profile_pic,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
        if include_sensitive:
            data.update({
                'email_verified': self.email_verified,
                'data_processing_consent': self.data_processing_consent,
                'marketing_consent': self.marketing_consent,
                'gdpr_consent_date': self.gdpr_consent_date.isoformat() if self.gdpr_consent_date else None,
            })
        return data


class AuditLog(db.Model):
    """GDPR compliance: Log all user data access and modifications."""
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)  # 'login', 'data_export', 'data_deletion', etc.
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
