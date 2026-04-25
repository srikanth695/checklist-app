def get_ai_suggestions(goal_type, details):
    """Return canned suggestions for a few goal types (no external AI)."""
    suggestions = {
        'get_healthy': {
            'summary': 'Small daily habits: sleep, movement, nutrition.',
            'tasks': ['Walk 30 minutes', 'Prepare a healthy meal', 'Sleep 7-8 hours', 'Drink 2L water', 'Do 15 minutes stretching']
        },
        'complete_course': {
            'summary': 'Break course into weekly modules and scheduled study sessions.',
            'tasks': ['List course modules', 'Schedule 3 study sessions per week', 'Complete one assignment per week', 'Review notes weekly', 'Practice with exercises']
        },
        'finish_project': {
            'summary': 'Define milestones, allocate time blocks, and remove blockers.',
            'tasks': ['Define project milestones', 'Break milestone into tasks', 'Assign time blocks', 'Remove top 3 blockers', 'Review progress weekly']
        }
    }
    base = suggestions.get(goal_type, {'summary': 'Try breaking the goal into small tasks.', 'tasks': []})
    if details:
        base = base.copy()
        base['summary'] = base['summary'] + ' Context: ' + details
    return base
