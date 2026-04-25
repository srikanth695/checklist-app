from flask import Blueprint, render_template, request, redirect, url_for, current_app
from . import db
from .models import ScheduleEvent, Habit, JournalEntry
from .ai import get_ai_suggestions
from datetime import datetime
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
    if request.headers.get('HX-Request'):
        habits = Habit.query.order_by(Habit.id).all()
        return render_template('partials/habits_list.html', habits=habits)
    return redirect(url_for('main.index'))

@bp.route('/journal/add', methods=['POST'])
def add_journal():
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    j = JournalEntry(title=title, content=content)
    db.session.add(j)
    db.session.commit()
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
