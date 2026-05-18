from google.adk.agents import Agent

from .tools import (
    calculate_days_remaining,
    get_current_time,
    get_subject_deadline,
    # TODO (Step 4): Uncomment after adding state tools to tools.py
    # get_priority_subject,
    # save_priority_subject,
    # TODO (Step 5): Uncomment after adding create_study_plan to tools.py
    # create_study_plan,
)

# TODO (Step 5): Expand this instruction to guide multi-step workflow
INSTRUCTION = """You are a helpful study planning assistant for university students.

You have access to tools to check deadlines and calculate time remaining.
Always use tools to get accurate data — never guess dates or deadlines.
Be encouraging and specific in your responses.
"""

# TODO (Step 4 & 5): Add save_priority_subject, get_priority_subject, create_study_plan
root_agent = Agent(
    name="study_agent",
    model="gemini-2.0-flash",
    description="A student study planning assistant that tracks deadlines and creates personalized study plans.",
    instruction=INSTRUCTION,
    tools=[
        get_current_time,
        get_subject_deadline,
        calculate_days_remaining,
    ],
)
