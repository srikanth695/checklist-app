from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from . import db
from .models import ScheduleEvent, Habit, JournalEntry, Goal, DailyChecklistItem, Task, DailyMetric, HabitEntry
from .ai import get_ai_suggestions
from .validators import validate_schedule_event, validate_habit, validate_journal_entry, validate_goal_setup
from .habit_tracker import HabitTracker
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)

@bp.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.svg'))

@bp.route('/privacy')
def privacy_policy():
    """Display privacy policy and GDPR information."""
    return render_template('privacy_policy.html')

@bp.route('/')
@login_required
def index():
    try:
        schedules = ScheduleEvent.query.filter_by(user_id=current_user.id).order_by(ScheduleEvent.date).all()
        habits = Habit.query.filter_by(user_id=current_user.id).order_by(Habit.id).all()
        journals = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.created_at.desc()).limit(20).all()
    except Exception as e:
        logger.error(f"Error loading index page: {str(e)}")
        flash("Error loading data. Please try again.", "error")
        schedules = habits = journals = []
    return render_template('index.html', schedules=schedules, habits=habits, journals=journals)

@bp.route('/habits')
@login_required
def habits_page():
    try:
        page = request.args.get('page', 1, type=int)
        paginated = Habit.query.filter_by(user_id=current_user.id)\
            .order_by(Habit.id).paginate(page=page, per_page=20, error_out=False)
        habits = paginated.items
        total_pages = paginated.pages
        current_page = page
    except Exception as e:
        logger.error(f"Error loading habits page: {str(e)}")
        flash("Error loading habits. Please try again.", "error")
        habits = []
        total_pages = 1
        current_page = 1
    return render_template('habits.html', habits=habits, total_pages=total_pages, current_page=current_page)

@bp.route('/journal')
@login_required
def journal_page():
    try:
        page = request.args.get('page', 1, type=int)
        paginated = JournalEntry.query.filter_by(user_id=current_user.id)\
            .order_by(JournalEntry.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
        journals = paginated.items
        total_pages = paginated.pages
        current_page = page
    except Exception as e:
        logger.error(f"Error loading journal page: {str(e)}")
        flash("Error loading journal. Please try again.", "error")
        journals = []
        total_pages = 1
        current_page = 1
    return render_template('journal.html', journals=journals, total_pages=total_pages, current_page=current_page)

@bp.route('/goals')
@login_required
def ai_page():
    return render_template('ai.html')

@bp.route('/schedule/add', methods=['POST'])
@login_required
def add_schedule():
    title = request.form.get('title', '').strip()
    date_str = request.form.get('date')
    time = request.form.get('time')
    duration = request.form.get('duration')
    notes = request.form.get('notes', '').strip()
    
    # Validate input
    is_valid, errors = validate_schedule_event(title, date_str, time, duration)
    if not is_valid:
        for error in errors:
            flash(error, "error")
        if request.headers.get('HX-Request'):
            schedules = ScheduleEvent.query.filter_by(user_id=current_user.id).order_by(ScheduleEvent.date).all()
            return render_template('partials/schedule_list.html', schedules=schedules), 400
        return redirect(url_for('main.index'))
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        ev = ScheduleEvent(
            user_id=current_user.id,
            title=title, 
            date=date_obj, 
            time=time or None, 
            duration_minutes=int(duration or 0), 
            notes=notes or None
        )
        db.session.add(ev)
        db.session.commit()
        flash('Event added successfully', 'success')
    except ValueError as e:
        logger.error(f"Error parsing schedule date: {str(e)}")
        flash("Invalid date format", "error")
    except Exception as e:
        logger.error(f"Error adding schedule event: {str(e)}")
        db.session.rollback()
        flash("Error adding event. Please try again.", "error")
    
    if request.headers.get('HX-Request'):
        schedules = ScheduleEvent.query.filter_by(user_id=current_user.id).order_by(ScheduleEvent.date).all()
        return render_template('partials/schedule_list.html', schedules=schedules)
    return redirect(url_for('main.index'))

@bp.route('/habit/add', methods=['POST'])
@login_required
def add_habit():
    name = request.form.get('name', '').strip()
    frequency = request.form.get('frequency', 'daily')
    
    # Validate input
    is_valid, errors = validate_habit(name, frequency)
    if not is_valid:
        for error in errors:
            flash(error, "error")
        if request.headers.get('HX-Request'):
            habits = Habit.query.order_by(Habit.id).all()
            return render_template('partials/habits_list.html', habits=habits), 400
        return redirect(url_for('main.habits_page'))
    
    try:
        h = Habit(user_id=current_user.id, name=name, frequency=frequency)
        db.session.add(h)
        db.session.commit()
        flash('Habit added successfully', 'success')
    except Exception as e:
        logger.error(f"Error adding habit: {str(e)}")
        db.session.rollback()
        flash("Error adding habit. Please try again.", "error")
    
    if request.headers.get('HX-Request'):
        habits = Habit.query.order_by(Habit.id).all()
        return render_template('partials/habits_list.html', habits=habits)
    return redirect(url_for('main.habits_page'))

@bp.route('/api/habit/<int:habit_id>/log', methods=['POST'])
@login_required
def log_habit_completion(habit_id):
    """Log a habit completion for today or a specific date."""
    try:
        # Handle both form data and JSON payloads
        json_data = request.get_json(silent=True) or {}
        date_str = request.form.get('date') or json_data.get('date')
        completed_str = request.form.get('completed') or json_data.get('completed', 'true')
        completed = str(completed_str).lower() in ['true', '1', 'yes']
        notes = request.form.get('notes', '').strip() or None
        
        log_date = None
        if date_str:
            try:
                log_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                log_date = datetime.utcnow().date()
        else:
            log_date = datetime.utcnow().date()
        
        # Log the habit
        entry = HabitTracker.log_habit_completion(habit_id, log_date, completed, notes)
        
        if entry:
            flash('Habit logged successfully', 'success')
            
            # Return HTML for HTMX requests, JSON otherwise
            if request.headers.get('HX-Request'):
                habits = Habit.query.order_by(Habit.id).all()
                return render_template('partials/habits_list.html', habits=habits), 200
            else:
                return {'success': True, 'habit_id': habit_id, 'completed': completed}, 200
        else:
            if request.headers.get('HX-Request'):
                flash('Habit not found', 'error')
                habits = Habit.query.filter_by(user_id=current_user.id).order_by(Habit.id).all()
                return render_template('partials/habits_list.html', habits=habits), 404
            else:
                return {'error': 'Habit not found'}, 404
    except Exception as e:
        logger.error(f"Error logging habit {habit_id}: {str(e)}")
        if request.headers.get('HX-Request'):
            flash(f'Error: {str(e)}', 'error')
            habits = Habit.query.filter_by(user_id=current_user.id).order_by(Habit.id).all()
            return render_template('partials/habits_list.html', habits=habits), 500
        else:
            return {'error': str(e)}, 500

@bp.route('/api/habit/<int:habit_id>/stats')
@login_required
def get_habit_stats(habit_id):
    """Get detailed statistics for a habit."""
    try:
        days = request.args.get('days', 30, type=int)
        stats = HabitTracker.get_habit_statistics(habit_id, days)
        
        if not stats:
            return {'error': 'Habit not found'}, 404
        
        # Convert dates to strings for JSON serialization
        stats['last_completed'] = str(stats['last_completed']) if stats['last_completed'] else None
        stats['created_at'] = stats['created_at'].isoformat()
        stats['entries'] = [
            {
                'date': str(e.date),
                'completed': e.completed,
                'notes': e.notes
            } for e in stats['entries']
        ]
        
        return stats, 200
    except Exception as e:
        logger.error(f"Error getting habit stats {habit_id}: {str(e)}")
        return {'error': str(e)}, 500

@bp.route('/api/habit/<int:habit_id>/insights')
@login_required
def get_habit_insights(habit_id):
    """Get insights and recommendations for a habit."""
    try:
        insights = HabitTracker.generate_habit_insights(habit_id)
        
        if not insights:
            return {'error': 'Habit not found'}, 404
        
        return insights, 200
    except Exception as e:
        logger.error(f"Error getting habit insights {habit_id}: {str(e)}")
        return {'error': str(e)}, 500

@bp.route('/habit/<int:habit_id>/details')
@login_required
def habit_details(habit_id):
    """Display detailed view of a single habit with history and insights."""
    try:
        habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()
        if not habit:
            flash('Habit not found', 'error')
            return redirect(url_for('main.habits_page'))
        
        # Get statistics and history
        stats = HabitTracker.get_habit_statistics(habit_id, days=90)
        history = HabitTracker.get_habit_history(habit_id, days=30)
        insights = HabitTracker.generate_habit_insights(habit_id)
        is_completed_today = HabitTracker.is_habit_completed_today(habit_id)
        
        return render_template(
            'habit_details.html',
            habit=habit,
            stats=stats,
            history=history,
            insights=insights,
            is_completed_today=is_completed_today,
            now=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error loading habit details: {str(e)}")
        flash('Error loading habit details', 'error')
        return redirect(url_for('main.habits_page'))

@bp.route('/api/habit/<int:habit_id>/delete', methods=['POST'])
@login_required
def delete_habit(habit_id):
    """Delete a habit and all its entries."""
    try:
        habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first()
        if not habit:
            return {'error': 'Habit not found'}, 404
        
        db.session.delete(habit)
        db.session.commit()
        flash(f'Habit "{habit.name}" deleted', 'success')
        
        if request.headers.get('HX-Request'):
            habits = Habit.query.filter_by(user_id=current_user.id).order_by(Habit.id).all()
            return render_template('partials/habits_list.html', habits=habits)
        
        return redirect(url_for('main.habits_page'))
    except Exception as e:
        logger.error(f"Error deleting habit {habit_id}: {str(e)}")
        db.session.rollback()
        return {'error': str(e)}, 500

@bp.route('/journal/add', methods=['POST'])
@login_required
def add_journal():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    
    # Validate input
    is_valid, errors = validate_journal_entry(title, content)
    if not is_valid:
        for error in errors:
            flash(error, "error")
        if request.headers.get('HX-Request'):
            journals = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.created_at.desc()).limit(20).all()
            return render_template('partials/journal_list.html', journals=journals), 400
        return redirect(url_for('main.index'))
    
    try:
        j = JournalEntry(user_id=current_user.id, title=title or None, content=content or None)
        db.session.add(j)
        db.session.commit()
        flash('Journal entry saved successfully', 'success')
    except Exception as e:
        logger.error(f"Error adding journal entry: {str(e)}")
        db.session.rollback()
        flash("Error saving journal entry. Please try again.", "error")
    
    if request.headers.get('HX-Request'):
        journals = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.created_at.desc()).limit(20).all()
        return render_template('partials/journal_list.html', journals=journals)
    return redirect(url_for('main.index'))

@bp.route('/api/ai_suggest', methods=['POST'])
def ai_suggest():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    goal_type = data.get('goal_type')
    details = data.get('details', '')
    suggestions = get_ai_suggestions(goal_type, details)
    if request.headers.get('HX-Request'):
        return render_template('partials/ai_result.html', suggestions=suggestions)
    return current_app.response_class(
        response=json.dumps(suggestions),
        status=200,
        mimetype='application/json'
    )

@bp.route('/daily-checklist')
@login_required
def daily_checklist():
    today = datetime.utcnow().date()
    try:
        checklist_items = DailyChecklistItem.query.filter_by(date=today).order_by(
            DailyChecklistItem.priority.desc(),
            DailyChecklistItem.created_at
        ).all()
        daily_metric = DailyMetric.query.filter_by(date=today).first()
        if not daily_metric:
            daily_metric = DailyMetric(date=today)
        completed_count = sum(1 for item in checklist_items if item.completed)
        total_count = len(checklist_items)
    except Exception as e:
        logger.error(f"Error loading daily checklist: {str(e)}")
        flash("Error loading checklist. Please try again.", "error")
        checklist_items = []
        daily_metric = None
        completed_count = total_count = 0
    
    # Get past 7 days trends
    try:
        past_7_days = DailyMetric.query.filter(
            DailyMetric.date >= today - timedelta(days=7)
        ).order_by(DailyMetric.date).all()
    except Exception as e:
        logger.error(f"Error loading daily metrics: {str(e)}")
        past_7_days = []
    
    return render_template('daily_checklist.html', 
                         items=checklist_items,
                         daily_metric=daily_metric,
                         completed_count=completed_count,
                         total_count=total_count,
                         past_7_days=past_7_days,
                         now=datetime.utcnow())

@bp.route('/api/checklist-item/<int:item_id>/toggle', methods=['POST'])
def toggle_checklist_item(item_id):
    try:
        item = DailyChecklistItem.query.get(item_id)
        if not item:
            logger.warning(f"Checklist item {item_id} not found")
            return {'error': 'Item not found'}, 404
        
        item.completed = not item.completed
        if item.completed:
            item.completed_at = datetime.utcnow()
        else:
            item.completed_at = None
        
        db.session.commit()
        
        # Update daily metric
        today = item.date
        daily_metric = DailyMetric.query.filter_by(date=today).first()
        if daily_metric:
            completed_count = DailyChecklistItem.query.filter_by(
                date=today, completed=True
            ).count()
            total_count = DailyChecklistItem.query.filter_by(date=today).count()
            daily_metric.tasks_completed = completed_count
            daily_metric.tasks_total = total_count
            db.session.commit()
        
        return {'completed': item.completed, 'item_id': item_id}, 200
    except Exception as e:
        logger.error(f"Error toggling checklist item {item_id}: {str(e)}")
        db.session.rollback()
        return {'error': 'Error updating item. Please try again.'}, 500

# Goal Setup Routes
@bp.route('/goal-setup')
@login_required
def goal_setup():
    return render_template('goal_setup.html')

@bp.route('/goal-setup/confirm', methods=['POST'])
@login_required
def goal_setup_confirm():
    category = request.form.get('category')
    timeframe = request.form.get('timeframe')
    current_situation = request.form.get('current_situation', '').strip()
    desired_outcome = request.form.get('desired_outcome', '').strip()
    
    # Validate input
    is_valid, errors = validate_goal_setup(category, timeframe, current_situation, desired_outcome)
    if not is_valid:
        for error in errors:
            flash(error, "error")
        return redirect(url_for('main.goal_setup'))
    
    try:
        goal_title = f"{desired_outcome} ({timeframe})"
        goal_description = f"Current: {current_situation}\nDesired: {desired_outcome}"
        
        goal = Goal(
            user_id=current_user.id,
            title=goal_title,
            description=goal_description,
            category=category,
            timeframe=timeframe,
            target_metric=desired_outcome,
            status='active'
        )
        db.session.add(goal)
        db.session.flush()
        
        # Create daily checklist item for today
        today = datetime.utcnow().date()
        item = DailyChecklistItem(
            date=today,
            source_type='goal',
            source_id=goal.id,
            title=goal_title,
            description=f"Work on: {desired_outcome}",
            priority='high'
        )
        db.session.add(item)
        db.session.commit()
        
        flash(f'Goal "{goal_title}" created and added to today\'s checklist!', 'success')
        return redirect(url_for('main.daily_checklist'))
    except Exception as e:
        logger.error(f"Error creating goal: {str(e)}")
        db.session.rollback()
        flash('Error creating goal. Please try again.', 'error')
        return redirect(url_for('main.goal_setup'))

@bp.route('/my-goals')
@login_required
def my_goals():
    try:
        goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.status, Goal.created_at.desc()).all()
        
        # Get completion stats more efficiently using aggregation
        goal_stats = []
        for goal in goals:
            # Count items efficiently
            completed = DailyChecklistItem.query.filter_by(
                source_type='goal', source_id=goal.id, completed=True
            ).count()
            total = DailyChecklistItem.query.filter_by(
                source_type='goal', source_id=goal.id
            ).count()
            completion_pct = (completed / total * 100) if total > 0 else 0
            goal_stats.append({
                'goal': goal,
                'total_items': total,
                'completed_items': completed,
                'completion_pct': completion_pct
            })
    except Exception as e:
        logger.error(f"Error loading goals: {str(e)}")
        flash("Error loading goals. Please try again.", "error")
        goal_stats = []
    
    return render_template('my_goals.html', goal_stats=goal_stats)
