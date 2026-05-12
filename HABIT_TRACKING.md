# Habit Tracking System Documentation

## Overview

The habit tracking system monitors and analyzes user habits to help build consistency and track progress toward behavioral goals. It uses a combination of database models and analytics algorithms to provide real-time insights.

## Architecture

### Database Models

#### Habit Model
- **Fields**: 
  - `name`: Habit name (e.g., "Morning meditation")
  - `category`: Optional categorization (health, fitness, learning, productivity, work)
  - `frequency`: Tracking frequency (daily, weekly, every_other_day)
  - `difficulty`: Difficulty level (easy, medium, hard)
  - `streak`: Current consecutive completion streak
  - `longest_streak`: Personal best streak ever achieved
  - `completion_pct`: Completion percentage over last 30 days
  - `last_completed`: Date of last completion
  - `created_at`: When the habit was created

#### HabitEntry Model (Tracking Log)
- **Fields**:
  - `habit_id`: Foreign key to Habit
  - `date`: Date of the entry
  - `completed`: Boolean indicating if habit was completed
  - `notes`: Optional notes for that day

## Core Features

### 1. Streak Calculation
**Purpose**: Track consecutive days/weeks of completion

**Algorithm**:
- **Daily habits**: Counts consecutive days marked as completed
- **Weekly habits**: Counts consecutive weeks with at least one completion
- **Every other day**: Counts consecutive scheduled completions
- **Breaks when**: A scheduled day is missed

**Example**:
```
Habit: "Exercise"
Frequency: Daily
Mon ✓ Tue ✓ Wed ✓ Thu ✗ Fri ...
Streak: 0 (broke on Thursday)
```

### 2. Longest Streak
**Purpose**: Motivate by showing personal best achievement

**Calculation**: Scans entire history to find longest consecutive streak achieved

### 3. Completion Percentage
**Purpose**: Show overall consistency over a period

**Formula**:
```
Completion % = (Completed Days / Expected Days) × 100
```

**Time windows**: Defaults to 30 days, configurable

**Example for Daily Habit**:
- 30-day period
- 24 completions out of 30 days
- Completion %: 80%

### 4. Last Completed Tracking
**Purpose**: Show recency of habit completion

**Values**: 
- Date of most recent completion
- Used to detect if habit is being abandoned

## Core Functions (HabitTracker Class)

### `log_habit_completion(habit_id, log_date=None, completed=True, notes=None)`
**Purpose**: Record a habit completion

**Parameters**:
- `habit_id`: Habit to log
- `log_date`: Date to log for (default: today)
- `completed`: True/False
- `notes`: Optional notes

**Returns**: HabitEntry object

**Example**:
```python
from app.habit_tracker import HabitTracker

# Log today's completion
HabitTracker.log_habit_completion(habit_id=1, completed=True, notes="Felt great!")

# Log a past date
HabitTracker.log_habit_completion(
    habit_id=1, 
    log_date=date(2024, 5, 10),
    completed=True
)
```

### `calculate_current_streak(habit_id)`
**Purpose**: Get current streak count

**Returns**: Integer

```python
streak = HabitTracker.calculate_current_streak(1)  # Returns: 5
```

### `calculate_longest_streak(habit_id)`
**Purpose**: Get personal best streak

**Returns**: Integer

```python
best = HabitTracker.calculate_longest_streak(1)  # Returns: 23
```

### `calculate_completion_percentage(habit_id, days=30)`
**Purpose**: Get completion rate over period

**Returns**: Float (0-100)

```python
completion = HabitTracker.calculate_completion_percentage(1, days=30)  # Returns: 78.5
```

### `update_habit_metrics(habit_id)`
**Purpose**: Recalculate all metrics for a habit

**Call this after**: Logging a completion, deleting entries, or updating history

```python
HabitTracker.update_habit_metrics(1)
# Updates: streak, longest_streak, completion_pct, last_completed
```

### `get_habit_statistics(habit_id, days=30)`
**Purpose**: Get comprehensive statistics dictionary

**Returns**: Dictionary with all metrics

```python
stats = HabitTracker.get_habit_statistics(1, days=30)
# {
#     'habit_id': 1,
#     'name': 'Morning meditation',
#     'frequency': 'daily',
#     'category': 'health',
#     'current_streak': 5,
#     'longest_streak': 23,
#     'completion_percentage': 78.5,
#     'last_completed': date(2024, 5, 15),
#     'total_completions': 23,
#     'total_tracked_days': 30,
#     'average_daily_completion': 76.67,
#     'entries': [...]
# }
```

### `get_habit_history(habit_id, days=30)`
**Purpose**: Get all daily entries for a habit

**Returns**: List of HabitEntry objects

```python
history = HabitTracker.get_habit_history(1, days=30)
for entry in history:
    print(f"{entry.date}: {'✓' if entry.completed else '✗'}")
```

### `is_habit_completed_today(habit_id)`
**Purpose**: Quick check if today's completion is logged

**Returns**: Boolean

```python
if HabitTracker.is_habit_completed_today(1):
    print("Today's habit is done!")
```

### `get_today_habits_status()`
**Purpose**: Get all habits with today's status

**Returns**: List of dictionaries

```python
statuses = HabitTracker.get_today_habits_status()
# [
#     {
#         'habit': Habit object,
#         'completed_today': True/False,
#         'entry_id': int or None,
#         'entry': HabitEntry or None
#     },
#     ...
# ]
```

### `generate_habit_insights(habit_id)`
**Purpose**: Generate motivational insights and recommendations

**Returns**: Dictionary with insight messages

```python
insights = HabitTracker.generate_habit_insights(1)
# {
#     'habit_id': 1,
#     'insights': [
#         {
#             'type': 'positive',
#             'message': "🔥 Excellent! You've maintained a 5-day streak!"
#         },
#         {
#             'type': 'positive',
#             'message': "📈 You're maintaining 78.5% completion rate. Keep it up!"
#         },
#         ...
#     ]
# }
```

## API Endpoints

### POST `/api/habit/<habit_id>/log`
**Purpose**: Log a habit completion

**Parameters** (form or JSON):
- `date`: Optional YYYY-MM-DD format
- `completed`: "true" or "false" (default: "true")
- `notes`: Optional notes

**Response**:
```json
{
    "success": true,
    "habit_id": 1,
    "completed": true
}
```

### GET `/api/habit/<habit_id>/stats`
**Purpose**: Get habit statistics

**Query Parameters**:
- `days`: Number of days to analyze (default: 30)

**Response**: Habit statistics dictionary (JSON serialized)

### GET `/api/habit/<habit_id>/insights`
**Purpose**: Get habit insights

**Response**: Insights dictionary

### GET `/habit/<habit_id>/details`
**Purpose**: View comprehensive habit details page

**Returns**: HTML page with full statistics, history, and insights

## Web Interface Routes

### Habit Management Routes

#### `GET /habits`
Displays all habits with summary stats

#### `POST /habit/add`
Create a new habit

#### `POST /api/habit/<habit_id>/delete`
Delete a habit and all its entries

#### `GET /habit/<habit_id>/details`
View detailed habit page with full analytics

## Monitoring Metrics Explanation

### 🔥 Streak
- Current consecutive days/weeks of completion
- Resets to 0 if a day is missed
- Motivates consistency

### 🏆 Longest Streak
- Personal record for consecutive completions
- Never decreases
- Shows what you're capable of

### 📊 Completion Rate
- Percentage of scheduled days completed
- 30-day rolling window
- Key consistency indicator
- Target: 80%+ for habit formation

### ✓ Last Completed
- Most recent completion date
- Shows if habit is being maintained
- Red flag if too old

### 📈 Average Daily Completion
- Long-term consistency metric
- Over full history
- Shows overall reliability

## Habit Formation Insights

The system generates automatic insights based on:

1. **Streak Status**
   - 🔥 30+ days: Excellent habit formation
   - 👏 7-29 days: Good progress
   - ⚠️ 0 days: Needs attention

2. **Completion Rate**
   - ✅ 80%+: Habit is forming well
   - ⚠️ 50-79%: Needs more consistency
   - ❌ <50%: Habit not yet established

3. **Personal Best**
   - Compare current streak to longest
   - Shows if regressing

4. **Consistency**
   - 🟢 High (75%+): Becoming lifestyle
   - 🟡 Medium (50-74%): Still building
   - 🔴 Low (<50%): Early stage

## Example Usage Workflow

```python
from app.habit_tracker import HabitTracker
from datetime import date

# 1. User creates a habit
habit_id = 1  # Habit: "Morning meditation"

# 2. User logs completion
HabitTracker.log_habit_completion(habit_id, completed=True, notes="10 minutes")

# 3. System updates metrics automatically
HabitTracker.update_habit_metrics(habit_id)

# 4. View stats
stats = HabitTracker.get_habit_statistics(habit_id)
print(f"Streak: {stats['current_streak']} days")
print(f"Completion: {stats['completion_percentage']:.1f}%")

# 5. Get insights
insights = HabitTracker.generate_habit_insights(habit_id)
for insight in insights['insights']:
    print(f"{insight['message']}")

# 6. View history
history = HabitTracker.get_habit_history(habit_id, days=30)
for entry in history[:7]:  # Last 7 days
    print(f"{entry.date}: {'✓' if entry.completed else '✗'} {entry.notes or ''}")
```

## Performance Considerations

### Database Indexes
- `habit_id` in HabitEntry (foreign key)
- `date` in HabitEntry
- `completed` in HabitEntry
- `category` in Habit
- `status` in Habit

### Optimization Tips

1. **Caching**: Cache completion percentage calculations
   ```python
   # Good for read-heavy operations
   @cache.cached(timeout=3600)
   def get_completion_pct(habit_id):
       return HabitTracker.calculate_completion_percentage(habit_id)
   ```

2. **Batch Updates**: Update multiple habits efficiently
   ```python
   habits = Habit.query.all()
   for habit in habits:
       HabitTracker.update_habit_metrics(habit.id)
   ```

3. **Limit History Queries**: Use date ranges
   ```python
   # Good: Limited date range
   HabitTracker.get_habit_history(habit_id, days=30)
   
   # Avoid: Full history for large datasets
   # HabitTracker.get_habit_history(habit_id, days=3650)
   ```

## Future Enhancements

1. **Predictive Analytics**
   - Machine learning to predict streak breakage
   - Recommend optimal timing for habits

2. **Social Features**
   - Share streaks with friends
   - Group habit challenges

3. **Habit Stacking**
   - Link related habits
   - Build synergistic routines

4. **Advanced Insights**
   - Correlation with mood/productivity
   - Seasonal patterns
   - Habit difficulty adaptation

5. **Mobile Integration**
   - Push notifications for reminders
   - Quick-log via mobile

6. **Gamification**
   - Badges and achievements
   - Leaderboards
   - Challenges and rewards
