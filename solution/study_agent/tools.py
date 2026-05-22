from datetime import datetime
from google.adk.tools import ToolContext

SUBJECT_DEADLINES = {
    "NLP": "2026-05-25",
    "Machine Learning": "2026-05-28",
    "Data Structures and Algorithms": "2026-06-01",
    "Artificial Intelligence": "2026-06-09",
}


def get_current_time() -> dict:
    """Returns the current date and time."""
    now = datetime.now()
    return {"current_time": now.strftime("%Y-%m-%d %H:%M:%S"), "date": now.strftime("%Y-%m-%d")}


def get_all_subjects() -> dict:
    """Returns the list of all subjects that have deadlines tracked.
    Always call this first when the user mentions a subject, to get the exact canonical name.
    """
    return {"subjects": list(SUBJECT_DEADLINES.keys())}


def get_subject_deadline(subject: str) -> dict:
    """Gets the assignment or exam deadline for a given subject.

    Args:
        subject: The exact subject name from get_all_subjects().
    """
    subject_key = next((k for k in SUBJECT_DEADLINES if k.lower() == subject.lower()), None)
    if subject_key:
        return {"subject": subject_key, "deadline": SUBJECT_DEADLINES[subject_key], "found": True}
    return {"subject": subject, "deadline": None, "found": False, "available_subjects": list(SUBJECT_DEADLINES.keys())}


def calculate_days_remaining(deadline_date: str) -> dict:
    """Calculates how many days remain until a given deadline date.

    Args:
        deadline_date: The deadline in YYYY-MM-DD format.
    """
    try:
        deadline = datetime.strptime(deadline_date, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days = (deadline - today).days
        if days < 0:
            status = "overdue"
        elif days == 0:
            status = "due_today"
        elif days <= 3:
            status = "critical"
        elif days <= 7:
            status = "urgent"
        else:
            status = "normal"
        return {"days_remaining": days, "deadline": deadline_date, "status": status}
    except ValueError:
        return {"error": f"Invalid date format: {deadline_date}. Use YYYY-MM-DD."}


def save_priority_subject(subject: str, tool_context: ToolContext) -> dict:
    """Saves the student's most important/priority subject to remember for this session.

    Args:
        subject: The subject name the student is most concerned about.
    """
    tool_context.state["priority_subject"] = subject
    return {"saved": True, "priority_subject": subject, "message": f"Got it! I'll remember that {subject} is your priority."}


def get_priority_subject(tool_context: ToolContext) -> dict:
    """Retrieves the student's previously saved priority subject from session memory."""
    subject = tool_context.state.get("priority_subject")
    if subject:
        return {"priority_subject": subject, "found": True}
    return {"priority_subject": None, "found": False, "message": "No priority subject saved yet. Please tell me which subject you're most concerned about."}


def create_study_plan(subject: str, days_remaining: int, tool_context: ToolContext) -> dict:
    """Creates a personalized study plan based on the subject and days remaining until deadline.

    Args:
        subject: The subject to create a plan for.
        days_remaining: Number of days until the deadline.
    """
    if days_remaining < 0:
        urgency = "OVERDUE"
        sessions = [
            "Contact your professor immediately about the missed deadline",
            "Complete the work as soon as possible",
        ]
    elif days_remaining == 0:
        urgency = "DUE TODAY"
        sessions = [
            "Focus entirely on this subject right now",
            "Aim to finish within the next few hours",
        ]
    elif days_remaining <= 3:
        urgency = "CRITICAL"
        sessions = [
            f"Tonight: 3h deep focus on {subject} core concepts",
            "Tomorrow: 2h practice problems + review notes",
            "Day before deadline: 1h final review, no new material",
        ]
    elif days_remaining <= 7:
        urgency = "HIGH"
        sessions = [
            f"Tonight: 2h study {subject} fundamentals",
            "Next 2 days: 1.5h/day on practice problems",
            "Day 4-5: 1h/day review and consolidation",
            "Day before deadline: Light review only",
        ]
    else:
        sessions_per_day = max(1, round(10 / days_remaining, 1))
        urgency = "NORMAL"
        sessions = [
            f"Daily: {sessions_per_day}h study sessions",
            "Week 1: Cover all main topics",
            "Week 2: Practice and review",
            "Final days: Mock tests and revision",
        ]

    plan = {
        "subject": subject,
        "days_remaining": days_remaining,
        "urgency": urgency,
        "study_sessions": sessions,
        "tip": "Take a 10-minute break every 50 minutes (Pomodoro technique).",
    }
    tool_context.state["last_study_plan"] = plan
    return plan
