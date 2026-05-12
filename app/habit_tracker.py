"""
Habit tracking and analytics module.
Handles streak calculation, completion tracking, and habit statistics.
"""
from datetime import datetime, timedelta, date
from sqlalchemy import func
from . import db
from .models import Habit, HabitEntry


class HabitTracker:
    """Centralized habit tracking logic."""
    
    @staticmethod
    def log_habit_completion(habit_id, log_date=None, completed=True, notes=None):
        """
        Log a habit completion for a specific date.
        
        Args:
            habit_id: ID of the habit
            log_date: Date to log (defaults to today)
            completed: Whether habit was completed (default True)
            notes: Optional notes for the entry
            
        Returns:
            HabitEntry object or None if error
        """
        try:
            habit = Habit.query.get(habit_id)
            if not habit:
                return None
            
            if log_date is None:
                log_date = date.today()
            
            # Check if entry already exists for this date
            entry = HabitEntry.query.filter_by(
                habit_id=habit_id,
                date=log_date
            ).first()
            
            if entry:
                entry.completed = completed
                entry.notes = notes
            else:
                entry = HabitEntry(
                    habit_id=habit_id,
                    date=log_date,
                    completed=completed,
                    notes=notes
                )
                db.session.add(entry)
            
            db.session.commit()
            
            # Update habit metrics after logging
            HabitTracker.update_habit_metrics(habit_id)
            
            return entry
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def calculate_current_streak(habit_id):
        """
        Calculate the current streak for a habit.
        Streak breaks if a daily habit is missed for a day, or weekly habit misses its week.
        
        Args:
            habit_id: ID of the habit
            
        Returns:
            Integer streak count
        """
        try:
            habit = Habit.query.get(habit_id)
            if not habit:
                return 0
            
            today = date.today()
            streak = 0
            
            if habit.frequency == 'daily':
                # For daily habits, check consecutive days
                for i in range(365):  # Max 1 year lookback
                    check_date = today - timedelta(days=i)
                    entry = HabitEntry.query.filter_by(
                        habit_id=habit_id,
                        date=check_date,
                        completed=True
                    ).first()
                    
                    if entry:
                        streak += 1
                    else:
                        break
                        
            elif habit.frequency == 'weekly':
                # For weekly habits, check consecutive weeks
                current_week = today.isocalendar()[1]
                year = today.isocalendar()[0]
                
                for i in range(52):  # Max 1 year of weeks
                    check_date = today - timedelta(weeks=i)
                    entries = HabitEntry.query.filter(
                        HabitEntry.habit_id == habit_id,
                        HabitEntry.completed == True,
                        HabitEntry.date >= (check_date - timedelta(days=7)),
                        HabitEntry.date <= check_date
                    ).count()
                    
                    if entries > 0:
                        streak += 1
                    else:
                        break
                        
            elif habit.frequency == 'every_other_day':
                # For every other day habits
                for i in range(730):  # Max 2 years
                    check_date = today - timedelta(days=i*2)
                    entry = HabitEntry.query.filter_by(
                        habit_id=habit_id,
                        date=check_date,
                        completed=True
                    ).first()
                    
                    if entry:
                        streak += 1
                    else:
                        break
            
            return streak
        except Exception as e:
            raise e
    
    @staticmethod
    def calculate_longest_streak(habit_id):
        """
        Calculate the longest streak ever achieved for a habit.
        
        Args:
            habit_id: ID of the habit
            
        Returns:
            Integer longest streak count
        """
        try:
            habit = Habit.query.get(habit_id)
            if not habit:
                return 0
            
            entries = HabitEntry.query.filter_by(
                habit_id=habit_id,
                completed=True
            ).order_by(HabitEntry.date).all()
            
            if not entries:
                return 0
            
            longest_streak = 1
            current_streak = 1
            
            if habit.frequency == 'daily':
                for i in range(1, len(entries)):
                    if entries[i].date == entries[i-1].date + timedelta(days=1):
                        current_streak += 1
                        longest_streak = max(longest_streak, current_streak)
                    else:
                        current_streak = 1
                        
            elif habit.frequency == 'weekly':
                for i in range(1, len(entries)):
                    weeks_diff = (entries[i].date.isocalendar()[1] - 
                                entries[i-1].date.isocalendar()[1]) % 52
                    if weeks_diff <= 1:
                        current_streak += 1
                        longest_streak = max(longest_streak, current_streak)
                    else:
                        current_streak = 1
            
            return longest_streak
        except Exception as e:
            raise e
    
    @staticmethod
    def calculate_completion_percentage(habit_id, days=30):
        """
        Calculate completion percentage for a habit over a period.
        
        Args:
            habit_id: ID of the habit
            days: Number of days to look back (default 30)
            
        Returns:
            Float completion percentage (0-100)
        """
        try:
            habit = Habit.query.get(habit_id)
            if not habit:
                return 0.0
            
            start_date = date.today() - timedelta(days=days)
            
            if habit.frequency == 'daily':
                expected_completions = days
            elif habit.frequency == 'weekly':
                expected_completions = max(1, days // 7)
            elif habit.frequency == 'every_other_day':
                expected_completions = max(1, days // 2)
            else:
                expected_completions = days
            
            completed_count = HabitEntry.query.filter(
                HabitEntry.habit_id == habit_id,
                HabitEntry.completed == True,
                HabitEntry.date >= start_date,
                HabitEntry.date <= date.today()
            ).count()
            
            if expected_completions == 0:
                return 0.0
            
            percentage = (completed_count / expected_completions) * 100
            return min(100.0, percentage)
        except Exception as e:
            raise e
    
    @staticmethod
    def update_habit_metrics(habit_id):
        """
        Update all metrics for a habit (streak, longest_streak, completion_pct, last_completed).
        Call this after logging a habit completion.
        
        Args:
            habit_id: ID of the habit
        """
        try:
            habit = Habit.query.get(habit_id)
            if not habit:
                return
            
            # Calculate and update all metrics
            habit.streak = HabitTracker.calculate_current_streak(habit_id)
            habit.longest_streak = HabitTracker.calculate_longest_streak(habit_id)
            habit.completion_pct = HabitTracker.calculate_completion_percentage(habit_id)
            
            # Update last_completed
            last_entry = HabitEntry.query.filter_by(
                habit_id=habit_id,
                completed=True
            ).order_by(HabitEntry.date.desc()).first()
            
            if last_entry:
                habit.last_completed = last_entry.date
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_habit_statistics(habit_id, days=30):
        """
        Get comprehensive statistics for a habit.
        
        Args:
            habit_id: ID of the habit
            days: Number of days to analyze (default 30)
            
        Returns:
            Dictionary with statistics
        """
        try:
            habit = Habit.query.get(habit_id)
            if not habit:
                return {}
            
            start_date = date.today() - timedelta(days=days)
            
            entries = HabitEntry.query.filter(
                HabitEntry.habit_id == habit_id,
                HabitEntry.date >= start_date,
                HabitEntry.date <= date.today()
            ).all()
            
            completed_count = sum(1 for e in entries if e.completed)
            total_count = len(entries)
            
            return {
                'habit_id': habit_id,
                'name': habit.name,
                'frequency': habit.frequency,
                'category': habit.category,
                'difficulty': habit.difficulty,
                'current_streak': habit.streak,
                'longest_streak': habit.longest_streak,
                'completion_percentage': habit.completion_pct,
                'last_completed': habit.last_completed,
                'created_at': habit.created_at,
                'total_completions': completed_count,
                'total_tracked_days': total_count,
                'average_daily_completion': (completed_count / total_count * 100) if total_count > 0 else 0,
                'entries': entries
            }
        except Exception as e:
            raise e
    
    @staticmethod
    def get_habit_history(habit_id, days=30):
        """
        Get daily history entries for a habit.
        
        Args:
            habit_id: ID of the habit
            days: Number of days to retrieve (default 30)
            
        Returns:
            List of HabitEntry objects sorted by date (most recent first)
        """
        try:
            start_date = date.today() - timedelta(days=days)
            
            entries = HabitEntry.query.filter(
                HabitEntry.habit_id == habit_id,
                HabitEntry.date >= start_date,
                HabitEntry.date <= date.today()
            ).order_by(HabitEntry.date.desc()).all()
            
            return entries
        except Exception as e:
            raise e
    
    @staticmethod
    def is_habit_completed_today(habit_id):
        """
        Check if a habit has been completed today.
        
        Args:
            habit_id: ID of the habit
            
        Returns:
            Boolean
        """
        try:
            entry = HabitEntry.query.filter_by(
                habit_id=habit_id,
                date=date.today(),
                completed=True
            ).first()
            
            return entry is not None
        except Exception as e:
            raise e
    
    @staticmethod
    def get_today_habits_status():
        """
        Get all habits and their completion status for today.
        
        Returns:
            List of dictionaries with habit info and today's status
        """
        try:
            habits = Habit.query.all()
            today = date.today()
            
            habits_status = []
            for habit in habits:
                entry = HabitEntry.query.filter_by(
                    habit_id=habit.id,
                    date=today
                ).first()
                
                habits_status.append({
                    'habit': habit,
                    'completed_today': entry.completed if entry else False,
                    'entry_id': entry.id if entry else None,
                    'entry': entry
                })
            
            return habits_status
        except Exception as e:
            raise e
    
    @staticmethod
    def get_habits_by_category(category):
        """
        Get all habits in a specific category with their current stats.
        
        Args:
            category: Category name
            
        Returns:
            List of Habit objects
        """
        try:
            habits = Habit.query.filter_by(category=category).all()
            return habits
        except Exception as e:
            raise e
    
    @staticmethod
    def generate_habit_insights(habit_id):
        """
        Generate insights and recommendations for a habit.
        
        Args:
            habit_id: ID of the habit
            
        Returns:
            Dictionary with insights
        """
        try:
            stats = HabitTracker.get_habit_statistics(habit_id, days=90)
            if not stats:
                return {}
            
            insights = {
                'habit_id': habit_id,
                'insights': []
            }
            
            # Streak insights
            if stats['current_streak'] >= 30:
                insights['insights'].append({
                    'type': 'positive',
                    'message': f"🔥 Excellent! You've maintained a {stats['current_streak']}-day streak!"
                })
            elif stats['current_streak'] >= 7:
                insights['insights'].append({
                    'type': 'positive',
                    'message': f"👏 Great job! {stats['current_streak']}-day streak going strong."
                })
            elif stats['current_streak'] == 0:
                insights['insights'].append({
                    'type': 'warning',
                    'message': "⚠️ Your streak is at 0. Complete this habit today to start a new streak!"
                })
            
            # Completion rate insights
            completion_pct = stats['completion_percentage']
            if completion_pct >= 80:
                insights['insights'].append({
                    'type': 'positive',
                    'message': f"📈 You're maintaining {completion_pct:.0f}% completion rate. Keep it up!"
                })
            elif completion_pct >= 50:
                insights['insights'].append({
                    'type': 'info',
                    'message': f"📊 Your completion rate is {completion_pct:.0f}%. Try to be more consistent."
                })
            else:
                insights['insights'].append({
                    'type': 'warning',
                    'message': f"⚠️ Low completion rate ({completion_pct:.0f}%). This habit needs attention."
                })
            
            # Personal best
            if stats['longest_streak'] > stats['current_streak']:
                insights['insights'].append({
                    'type': 'info',
                    'message': f"🏆 Your personal best streak is {stats['longest_streak']} days. You can do it again!"
                })
            
            # Consistency
            if stats['average_daily_completion'] > 75:
                insights['insights'].append({
                    'type': 'positive',
                    'message': "⭐ You're very consistent with this habit. This is becoming a real lifestyle change!"
                })
            
            return insights
        except Exception as e:
            raise e
