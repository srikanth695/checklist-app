from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from . import db
from .models import ScheduleEvent, Habit, JournalEntry, Goal, DailyChecklistItem, Task, DailyMetric
from .ai import get_ai_suggestions
from datetime import datetime, timedelta
import json

bp = Blueprint('main', __name__)

@bp.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.svg'))

@bp.route('/')
def index():
    try:
        schedules = ScheduleEvent.query.order_by(ScheduleEvent.date).all()
        habits = Habit.query.order_by(Habit.id).all()
        journals = JournalEntry.query.order_by(JournalEntry.created_at.desc()).limit(20).all()
    except Exception:
        schedules = habits = journals = []
    return render_template('index.html', schedules=schedules, habits=habits, journals=journals)

@bp.route('/habits')
def habits_page():
    try:
        habits = Habit.query.order_by(Habit.id).all()
    except Exception:
        habits = []
    return render_template('habits.html', habits=habits)

@bp.route('/journal')
def journal_page():
    try:
        journals = JournalEntry.query.order_by(JournalEntry.created_at.desc()).all()
    except Exception:
        journals = []
    return render_template('journal.html', journals=journals)

@bp.route('/goals')
def ai_page():
    return render_template('ai.html')

@bp.route('/schedule/add', methods=['POST'])
def add_schedule():
    title = request.form.get('title', 'Untitled')
    date_str = request.form.get('date')
    time = request.form.get('time')
    duration = request.form.get('duration') or 0
    notes = request.form.get('notes')
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        date_obj = datetime.utcnow().date()
    ev = ScheduleEvent(title=title, date=date_obj, time=time, duration_minutes=int(duration), notes=notes)
    db.session.add(ev)
    db.session.commit()
    flash('Event added', 'success')
    if request.headers.get('HX-Request'):
        schedules = ScheduleEvent.query.order_by(ScheduleEvent.date).all()
        return render_template('partials/schedule_list.html', schedules=schedules)
    return redirect(url_for('main.index'))

@bp.route('/habit/add', methods=['POST'])
def add_habit():
    name = request.form.get('name')
    frequency = request.form.get('frequency', 'daily')
    if not name:
        return ('', 204)
    h = Habit(name=name, frequency=frequency)
    db.session.add(h)
    db.session.commit()
    flash('Habit added', 'success')
    if request.headers.get('HX-Request'):
        habits = Habit.query.order_by(Habit.id).all()
        return render_template('partials/habits_list.html', habits=habits)
    return redirect(url_for('main.habits_page'))

@bp.route('/journal/add', methods=['POST'])
def add_journal():
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    j = JournalEntry(title=title, content=content)
    db.session.add(j)
    db.session.commit()
    flash('Journal saved', 'success')
    if request.headers.get('HX-Request'):
        journals = JournalEntry.query.order_by(JournalEntry.created_at.desc()).limit(20).all()
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

# Daily Checklist Routes
@bp.route('/daily-checklist')
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
        checklist_items = []
        daily_metric = None
        completed_count = total_count = 0
    
    # Get past 7 days trends
    try:
        past_7_days = DailyMetric.query.filter(
            DailyMetric.date >= today - timedelta(days=7)
        ).order_by(DailyMetric.date).all()
    except:
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
            return ({'error': 'Item not found'}, 404)
        
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
        return ({'error': str(e)}, 500)

# Goal Setup Routes
@bp.route('/goal-setup')
def goal_setup():
    return render_template('goal_setup.html')

@bp.route('/goal-setup/confirm', methods=['POST'])
def goal_setup_confirm():
    try:
        category = request.form.get('category')
        timeframe = request.form.get('timeframe')
        current_situation = request.form.get('current_situation')
        desired_outcome = request.form.get('desired_outcome')
        
        # Generate goal title and description based on inputs
        goal_title = f"{desired_outcome} ({timeframe})"
        goal_description = f"Current: {current_situation}\nDesired: {desired_outcome}"
        
        # Create Goal
        goal = Goal(
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
        flash(f'Error creating goal: {str(e)}', 'error')
        return redirect(url_for('main.goal_setup'))

@bp.route('/my-goals')
def my_goals():
    try:
        goals = Goal.query.order_by(Goal.status, Goal.created_at.desc()).all()
        # Get completion stats for each goal
        goal_stats = []
        for goal in goals:
            items = DailyChecklistItem.query.filter_by(source_type='goal', source_id=goal.id).all()
            completed = sum(1 for item in items if item.completed)
            total = len(items)
            completion_pct = (completed / total * 100) if total > 0 else 0
            goal_stats.append({
                'goal': goal,
                'total_items': total,
                'completed_items': completed,
                'completion_pct': completion_pct
            })
    except Exception:
        goal_stats = []
    
    return render_template('my_goals.html', goal_stats=goal_stats)
