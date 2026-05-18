from datetime import datetime

# TODO (Step 3): Import ToolContext when you reach Step 4
# from google.adk.tools import ToolContext


# Step 3 — Basic Tools

def get_current_time() -> dict:
    """Returns the current date and time."""
    # TODO: Use datetime.now() and strftime to format the result.
    # Return: {"current_time": "YYYY-MM-DD HH:MM:SS", "date": "YYYY-MM-DD"}
    pass


def get_subject_deadline(subject: str) -> dict:
    """Gets the assignment or exam deadline for a given subject.

    Args:
        subject: The name of the subject (e.g., 'NLP', 'Machine Learning').
    """
    deadlines = {
        "NLP": "2026-05-25",
        "Machine Learning": "2026-05-28",
        "Data Structures and Algorithms": "2026-06-01",
        "Artificial Intelligence": "2026-06-09",
    }
    # TODO: Case-insensitive lookup. Return {"subject": ..., "deadline": ..., "found": True/False}
    pass


def calculate_days_remaining(deadline_date: str) -> dict:
    """Calculates how many days remain until a given deadline date.

    Args:
        deadline_date: The deadline in YYYY-MM-DD format.
    """
    # TODO: Calculate (deadline - today).days
    # Return {"days_remaining": int, "deadline": str, "status": str}
    # Status: "overdue" (<0), "due_today" (0), "critical" (<=3), "urgent" (<=7), "normal"
    pass


# Step 4 — State Tools (uncomment when you reach Step 4)

# def save_priority_subject(subject: str, tool_context: ToolContext) -> dict:
#     """Saves the student's priority subject to session state.
#
#     Args:
#         subject: The subject the student is most concerned about.
#     """
#     # TODO: tool_context.state is a dict — store subject in it
#     pass


# def get_priority_subject(tool_context: ToolContext) -> dict:
#     """Retrieves the student's saved priority subject from session state."""
#     # TODO: Read from tool_context.state and return the saved subject
#     pass


# Step 5 — Workflow Tool (uncomment when you reach Step 5)

# def create_study_plan(subject: str, days_remaining: int, tool_context: ToolContext) -> dict:
#     """Creates a personalized study plan based on subject and days until deadline.
#
#     Args:
#         subject: The subject to plan for.
#         days_remaining: Days until the deadline.
#     """
#     # TODO: Return a plan dict based on urgency:
#     # OVERDUE (<0), DUE TODAY (0), CRITICAL (<=3), HIGH (<=7), NORMAL (>7)
#     # Also save the plan: tool_context.state["last_study_plan"] = plan
#     pass
