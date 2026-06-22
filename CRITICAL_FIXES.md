# Critical Issues & Quick Fixes

## 🔴 CRITICAL BUG #1: Missing User Context in Routes

### Issue
Several routes expose data across all users instead of filtering by `current_user.id`.

### Affected Code Locations

**1. `/journal` route** - Line 53 in `routes.py`
```python
# CURRENT (INSECURE)
@bp.route('/journal')
def journal_page():
    try:
        journals = JournalEntry.query.order_by(JournalEntry.created_at.desc()).all()  # ❌ ALL USERS
```

**2. Other potential issues**
- `/schedule/add`, `/habits` endpoints may not be filtering by user
- Need to audit all endpoints that query user-specific data

### Fix Applied

**For `/journal` route:**
```python
# FIXED (SECURE)
@bp.route('/journal')
@login_required  # Ensure user is logged in
def journal_page():
    try:
        journals = JournalEntry.query.filter_by(user_id=current_user.id)\
            .order_by(JournalEntry.created_at.desc()).all()  # ✅ ONLY CURRENT USER
```

---

## 🔴 CRITICAL BUG #2: Missing user_id in Database Models

### Issue
Three important models DON'T have `user_id` field:
- ScheduleEvent
- Task  
- Routine

### Current Model Definitions

**ScheduleEvent** (models.py):
```python
class ScheduleEvent(db.Model):
    __tablename__ = 'schedule_events'
    id = db.Column(db.Integer, primary_key=True)
    # ❌ NO user_id - Missing!
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
```

**Task** (models.py):
```python
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    # ❌ NO user_id - Missing!
    title = db.Column(db.String(300), nullable=False)
```

**Routine** (models.py):
```python
class Routine(db.Model):
    __tablename__ = 'routines'
    id = db.Column(db.Integer, primary_key=True)
    # ❌ NO user_id - Missing!
    name = db.Column(db.String(200), nullable=False)
```

### Required Fixes

Add this field to each model:
```python
user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                     nullable=False, index=True)
```

### Full Fixed Models

**ScheduleEvent - FIXED:**
```python
class ScheduleEvent(db.Model):
    __tablename__ = 'schedule_events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                        nullable=False, index=True)  # ✅ ADDED
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.String(20))
    duration_minutes = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
```

**Task - FIXED:**
```python
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                        nullable=False, index=True)  # ✅ ADDED
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')
    deadline = db.Column(db.Date, index=True)
    effort_minutes = db.Column(db.Integer)
    tags = db.Column(db.String(500))
    status = db.Column(db.String(20), default='inbox', index=True)
    recurring = db.Column(db.String(20))
    completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Routine - FIXED:**
```python
class Routine(db.Model):
    __tablename__ = 'routines'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), 
                        nullable=False, index=True)  # ✅ ADDED
    name = db.Column(db.String(200), nullable=False)
    routine_type = db.Column(db.String(50), index=True)
    day_type = db.Column(db.String(20), default='weekday')
    items = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Database Migration Steps

If you already have data in these tables:

```sql
-- Add user_id column (nullable first)
ALTER TABLE schedule_events ADD COLUMN user_id INTEGER;
ALTER TABLE tasks ADD COLUMN user_id INTEGER;
ALTER TABLE routines ADD COLUMN user_id INTEGER;

-- Backfill with admin user (ID 1) or delete test data
UPDATE schedule_events SET user_id = 1;
UPDATE tasks SET user_id = 1;
UPDATE routines SET user_id = 1;

-- Add foreign key constraint
ALTER TABLE schedule_events 
  ADD CONSTRAINT fk_schedule_user 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE tasks 
  ADD CONSTRAINT fk_tasks_user 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE routines 
  ADD CONSTRAINT fk_routines_user 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Add index
CREATE INDEX idx_schedule_user ON schedule_events(user_id);
CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_routines_user ON routines(user_id);
```

---

## 🟠 HIGH PRIORITY: Update All Routes to Filter by User

### Audit Checklist

Every route that queries these models MUST filter by `current_user.id`:

- [ ] `/habits` - queries Habit model
- [ ] `/journal` - queries JournalEntry model (KNOWN ISSUE)
- [ ] `/schedule/add` - creates ScheduleEvent
- [ ] `/goals` - queries Goal model
- [ ] `/daily-checklist` - queries DailyChecklistItem

### Example Fix Pattern

**BEFORE:**
```python
@bp.route('/habits')
@login_required
def habits_page():
    habits = Habit.query.order_by(Habit.id).all()  # ❌ No filter
    return render_template('habits.html', habits=habits)
```

**AFTER:**
```python
@bp.route('/habits')
@login_required
def habits_page():
    habits = Habit.query.filter_by(user_id=current_user.id)\
        .order_by(Habit.id).all()  # ✅ Filtered
    return render_template('habits.html', habits=habits)
```

### Routes Needing Review

1. **routes.py - `/` (index)**
   - ScheduleEvent query - needs filter
   
2. **routes.py - `/journal`**
   - JournalEntry query - needs filter (**CONFIRMED BUG**)

3. **routes.py - `/habits`**
   - Habit query - verify filtering

4. **routes.py - `/goals`**
   - Goal query - verify filtering

5. **Any POST/PUT/DELETE routes**
   - Verify ownership before modifications

---

## 🟡 MODERATE: File System Issues

### Issue: Duplicate requirements.txt

**Files Found:**
- `requirements.txt` ✅ (correct)
- `requrments.txt` ❌ (typo, should be deleted)

**Action:**
```bash
# Delete the typo file
rm requrments.txt

# Verify only one remains
ls -la requirements.txt
```

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Critical Security Fixes (DO FIRST)
- [ ] Add user_id to ScheduleEvent model
- [ ] Add user_id to Task model  
- [ ] Add user_id to Routine model
- [ ] Run database migration
- [ ] Update `/journal` route with user filter
- [ ] Audit all routes for user context
- [ ] Add @login_required to routes missing it
- [ ] Delete requrments.txt

### Phase 2: Testing
- [ ] Test multi-user isolation
- [ ] Run existing test suite
- [ ] Add tests for user isolation
- [ ] Verify no data leakage

### Phase 3: Code Quality
- [ ] Add error page handlers (404, 500)
- [ ] Improve logging
- [ ] Add security headers

---

## 🔍 SECURITY AUDIT SCRIPT

Run this to find potential issues:

```python
# audit_routes.py
import re
import os

def audit_routes():
    """Find routes that might be missing user filters."""
    
    issues = []
    
    with open('app/routes.py', 'r') as f:
        content = f.read()
        
    # Find all Query operations
    queries = re.findall(r'(\w+)\.query\..*?\.all\(\)', content)
    
    for query in queries:
        if query not in ['current_user']:  # These are OK
            issues.append(f"Potential unfiltered query: {query}.query")
    
    print("\n=== Audit Results ===")
    for issue in issues:
        print(f"⚠️  {issue}")

if __name__ == '__main__':
    audit_routes()
```

---

## 🎯 ESTIMATED EFFORT

| Task | Effort | Risk | Time |
|------|--------|------|------|
| Add user_id fields | Low | Low | 30 min |
| Database migration | Low | Medium | 1 hour |
| Update routes | Low | Low | 2 hours |
| Testing | Low | Low | 2 hours |
| **TOTAL** | **Low** | **Medium** | **5.5 hours** |

---

## ✅ SUCCESS CRITERIA

After fixes:
1. ✅ Each user only sees their own data
2. ✅ No data leakage between users
3. ✅ All tests pass
4. ✅ User isolation verified manually
5. ✅ No duplicate files in repo
