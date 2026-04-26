"""Input validation utilities for the checklist app."""

def validate_schedule_event(title, date_str, time, duration):
    """Validate schedule event input. Returns (is_valid, error_message)."""
    errors = []
    
    if not title or not title.strip():
        errors.append("Title cannot be empty")
    elif len(title.strip()) > 200:
        errors.append("Title cannot exceed 200 characters")
    
    if not date_str:
        errors.append("Date is required")
    
    try:
        int_duration = int(duration or 0)
        if int_duration < 0:
            errors.append("Duration cannot be negative")
        elif int_duration > 1440:  # More than a day
            errors.append("Duration cannot exceed 1440 minutes")
    except (ValueError, TypeError):
        errors.append("Duration must be a valid number")
    
    return len(errors) == 0, errors


def validate_habit(name, frequency):
    """Validate habit input. Returns (is_valid, error_message)."""
    errors = []
    
    if not name or not name.strip():
        errors.append("Habit name cannot be empty")
    elif len(name.strip()) > 200:
        errors.append("Habit name cannot exceed 200 characters")
    
    valid_frequencies = ['daily', 'weekly', 'monthly', 'custom']
    if frequency not in valid_frequencies:
        errors.append(f"Frequency must be one of: {', '.join(valid_frequencies)}")
    
    return len(errors) == 0, errors


def validate_journal_entry(title, content):
    """Validate journal entry input. Returns (is_valid, error_message)."""
    errors = []
    
    # Both fields can be empty, but at least one should have some content
    if not (title or content) or (not (title or content).strip()):
        errors.append("Please provide either a title or content")
    
    if title and len(title) > 200:
        errors.append("Title cannot exceed 200 characters")
    
    if content and len(content) > 10000:
        errors.append("Content cannot exceed 10000 characters")
    
    return len(errors) == 0, errors


def validate_goal_setup(category, timeframe, current_situation, desired_outcome):
    """Validate goal setup input. Returns (is_valid, error_message)."""
    errors = []
    
    valid_categories = ['health', 'career', 'learning', 'fitness', 'personal', 'finance', 'other']
    if not category or category not in valid_categories:
        errors.append(f"Category must be one of: {', '.join(valid_categories)}")
    
    valid_timeframes = ['1_week', '2_week', '1_month', '3_month', '6_month', '1_year']
    if not timeframe or timeframe not in valid_timeframes:
        errors.append(f"Timeframe must be one of: {', '.join(valid_timeframes)}")
    
    if not current_situation or not current_situation.strip():
        errors.append("Current situation cannot be empty")
    elif len(current_situation) > 500:
        errors.append("Current situation cannot exceed 500 characters")
    
    if not desired_outcome or not desired_outcome.strip():
        errors.append("Desired outcome cannot be empty")
    elif len(desired_outcome) > 500:
        errors.append("Desired outcome cannot exceed 500 characters")
    
    return len(errors) == 0, errors
