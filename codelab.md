---
id: student-study-planning-agent
name: Build a Student Study Planning Agent with Google ADK
summary: Learn to build a real AI Agent using Google ADK. You'll add tools, manage session state, and orchestrate a multi-step workflow — all powered by Gemini.
authors: GDGoC-UIT
categories: AI, Agentic AI, Google ADK
tags: google-adk, gemini, ai-agent, python, mcp
feedback link: https://github.com/eiyuumiru/student-study-agent-codelab/issues
status: Published
analytics account: UA-XXXXXXXX-X

---

# Build a Student Study Planning Agent with Google ADK

## Overview
Duration: 02:00

In this codelab, you will build a **Student Study Planning Agent** — a smart assistant that helps students manage their study schedule by checking deadlines, remembering context, and generating personalized study plans.

### What you'll learn

- The difference between a chatbot and an AI Agent
- How to build an agent with **Google ADK** and **Gemini**
- How to give your agent **Tools** to interact with real data
- How to use **Session State** to give your agent memory within a conversation
- How to design a **multi-step Workflow** for complex tasks
- (Bonus) How to connect your agent to **Google's MCP servers** (Calendar, Docs, Drive)

### What you'll build

By the end of this codelab, your agent will be able to handle a conversation like this:

```
You:   "I'm most worried about my NLP assignment."
Agent: "Got it! I'll keep NLP as your priority."

You:   "How many days do I have left?"
Agent: [calls get_priority_subject → NLP]
       [calls get_subject_deadline → 2026-05-25]
       [calls calculate_days_remaining → 2 days, status: critical]
       "You have 2 days until your NLP deadline. Let's make them count!"

You:   "Create a study plan for tonight."
Agent: [calls create_study_plan → HIGH urgency plan]
       "Here's your plan: Tonight: 2h on NLP fundamentals..."
```

### Architecture

```
+-----------------------------------------------+
|               AI Agent (ADK)                  |
|                                               |
|  +-----------+  +----------+  +------------+  |
|  |  Gemini   |  |  Tools   |  |  Session   |  |
|  |  Model    |  | (Python) |  |   State    |  |
|  +-----------+  +----------+  +------------+  |
+-----------------------------------------------+
       ^                  |
       | prompt           | tool calls
       |                  v
  +----------+     +-------------+
  |   User   |     |  Mock Data  |
  | (adk web)|     | (deadlines) |
  +----------+     +-------------+
```

### Prerequisites

- A Google account (for Gemini API key and Cloud Shell)
- Basic Python knowledge (functions, dicts, imports)
- A modern web browser — no local installation needed

---

## Step 1: Setup Your Environment
Duration: 10:00

Everything in this codelab runs in **Google Cloud Shell** — a free, browser-based Linux environment with Python pre-installed. No local setup needed.

### 1.1 Claim your Google Cloud credit

Your event organizer has provided Google Cloud credits. Claim them at:

```
https://trygcp.dev/claim/deveco-gdg-xxxxxxxx
```

> Replace `xxxxxxxx` with the code provided at the event. This gives you access to Google Cloud and the Gemini API.

### 1.2 Get a Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **Create API key** → select your Google Cloud project
3. Copy the key — you'll use it in step 1.4

<aside class="positive">
<strong>Free tier:</strong> The Gemini API has a generous free tier. You won't need to spend credits for this codelab.
</aside>

### 1.3 Open the starter code in Cloud Shell

Click the button below to open Google Cloud Shell with the starter code pre-loaded:

[![Open in Cloud Shell](open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/eiyuumiru/student-study-agent-codelab&cloudshell_git_branch=starter&cloudshell_tutorial=TUTORIAL.md&show=terminal)

This will:
1. Open Cloud Shell in your browser
2. Automatically clone the starter repo
3. Change into the `starter/` directory

<aside class="negative">
<strong>First time using Cloud Shell?</strong> It may take 30–60 seconds to provision. Accept any prompts to authorize Cloud Shell.
</aside>

### 1.4 Install dependencies and configure your API key

In the Cloud Shell terminal, run:

```bash
pip install -r requirements.txt
```

Then set your Gemini API key:

```bash
export GOOGLE_API_KEY="your_actual_api_key_here"
```

> Paste the key you copied from Google AI Studio. The quotes are important.

### 1.5 Verify your setup

Run the ADK web UI:

```bash
adk web
```

Cloud Shell will show a notification: **"Web Preview on port 8000"**. Click **"Open in new tab"** (or the web preview button in the Cloud Shell toolbar).

You should see the ADK interface. Select **study_agent** from the dropdown.

<aside class="negative">
<strong>Troubleshooting:</strong> If you see <code>ModuleNotFoundError: No module named 'study_agent'</code>, make sure you're in the repo root: run <code>cd ~/student-study-agent-codelab</code> then try again.
</aside>

<aside class="positive">
<strong>Keep Cloud Shell open</strong> throughout the codelab. Each time you edit a file, stop <code>adk web</code> with <code>Ctrl+C</code>, save your changes, then run <code>adk web</code> again to reload.
</aside>

---

## Step 2: Your First Agent
Duration: 05:00

Open `study_agent/agent.py`. You'll see the agent is already defined:

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="study_agent",
    model="gemini-2.0-flash",
    description="A student study planning assistant.",
    instruction="You are a helpful study assistant for students.",
)
```

### What each field does

| Field | Purpose |
|-------|---------|
| `name` | Identifier for the agent (used by ADK internally) |
| `model` | The Gemini model to use for reasoning |
| `description` | Helps ADK route requests in multi-agent setups |
| `instruction` | The system prompt — defines the agent's personality and behavior |

### Try it out

In the ADK web UI, type:

```
What subjects should I study for a computer science degree?
```

The agent responds using Gemini's knowledge. But notice — it can't tell you *your* actual deadlines. It's just a chatbot at this point.

### The key insight

```
LLM alone:  User asks → Model generates text → Done
AI Agent:   User asks → Model reasons → Calls tools → Uses state → Responds
```

In the next steps, we'll transform this chatbot into a real agent.

---

## Step 3: Adding Tools — The Agent Gains Abilities
Duration: 15:00

Tools are regular Python functions that your agent can call when it needs to perform an action or retrieve real data. The agent reads the **docstring** to decide when and how to use each tool.

Open `study_agent/tools.py`.

### 3.1 Implement `get_current_time`

```python
from datetime import datetime

def get_current_time() -> dict:
    """Returns the current date and time."""
    now = datetime.now()
    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
    }
```

### 3.2 Implement `get_subject_deadline`

```python
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
    subject_key = next((k for k in deadlines if k.lower() == subject.lower()), None)
    if subject_key:
        return {"subject": subject_key, "deadline": deadlines[subject_key], "found": True}
    return {
        "subject": subject,
        "deadline": None,
        "found": False,
        "available_subjects": list(deadlines.keys()),
    }
```

### 3.3 Implement `calculate_days_remaining`

```python
def calculate_days_remaining(deadline_date: str) -> dict:
    """Calculates how many days remain until a given deadline date.

    Args:
        deadline_date: The deadline in YYYY-MM-DD format.
    """
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
```

### 3.4 Register the tools with your agent

Update `agent.py` to import and use the tools:

```python
from google.adk.agents import Agent
from .tools import get_current_time, get_subject_deadline, calculate_days_remaining

root_agent = Agent(
    name="study_agent",
    model="gemini-2.0-flash",
    description="A student study planning assistant.",
    instruction="You are a helpful study assistant. Always use tools to get accurate data — never guess dates or deadlines.",
    tools=[
        get_current_time,
        get_subject_deadline,
        calculate_days_remaining,
    ],
)
```

### 3.5 Test your tools

Restart `adk web` and try these prompts:

```
What time is it right now?
```
```
When is the deadline for NLP?
```
```
How many days do I have until my Machine Learning deadline?
```

In the ADK web UI, you can expand each response to see exactly which tool was called and what it returned.

<aside class="positive">
<strong>Why docstrings matter:</strong> Gemini reads your function's docstring and type hints to decide when to call it. A clear, descriptive docstring = a smarter agent.
</aside>

### Checkpoint ✓

Your agent should now:
- Return the current time accurately
- Look up deadlines from mock data
- Calculate days remaining with a status label

---

## Step 4: Session State — The Agent Gets Memory
Duration: 15:00

Right now, if you tell the agent "I'm worried about NLP" and then ask "how many days do I have?", it won't know you meant NLP. Each message is processed independently.

**Session State** solves this. It's a dictionary that persists across all turns in a conversation session.

### 4.1 Understanding ToolContext

ADK passes a special `ToolContext` object to any tool that declares it as a parameter. Through `tool_context.state`, your tool can read and write to the session's persistent state.

```
Turn 1: "I'm worried about NLP"
         → save_priority_subject("NLP") writes to state["priority_subject"]

Turn 2: "How many days do I have?"
         → get_priority_subject() reads state["priority_subject"] → "NLP"
         → get_subject_deadline("NLP") → deadline
         → calculate_days_remaining(deadline) → 2 days
```

### 4.2 Add state tools to `tools.py`

Uncomment and implement the state tools:

```python
from google.adk.tools import ToolContext

def save_priority_subject(subject: str, tool_context: ToolContext) -> dict:
    """Saves the student's most important/priority subject to remember for this session.

    Args:
        subject: The subject name the student is most concerned about.
    """
    tool_context.state["priority_subject"] = subject
    return {
        "saved": True,
        "priority_subject": subject,
        "message": f"Got it! I'll remember that {subject} is your priority.",
    }


def get_priority_subject(tool_context: ToolContext) -> dict:
    """Retrieves the student's previously saved priority subject from session memory."""
    subject = tool_context.state.get("priority_subject")
    if subject:
        return {"priority_subject": subject, "found": True}
    return {
        "priority_subject": None,
        "found": False,
        "message": "No priority subject saved yet.",
    }
```

### 4.3 Register the state tools in `agent.py`

```python
from .tools import (
    calculate_days_remaining,
    get_current_time,
    get_priority_subject,
    get_subject_deadline,
    save_priority_subject,
)

root_agent = Agent(
    name="study_agent",
    model="gemini-2.0-flash",
    description="A student study planning assistant.",
    instruction="You are a helpful study assistant. When a student mentions they are worried about a subject, use save_priority_subject to remember it. Always use tools to get accurate data.",
    tools=[
        get_current_time,
        get_subject_deadline,
        calculate_days_remaining,
        save_priority_subject,
        get_priority_subject,
    ],
)
```

### 4.4 Test session state

Restart `adk web` and try this multi-turn conversation **in the same session**:

```
Turn 1: "I'm most worried about my NLP assignment."
Turn 2: "How many days do I have left for that subject?"
Turn 3: "What about Machine Learning?"
Turn 4: "Which subject did I say I was most worried about?"
```

Watch how the agent uses `save_priority_subject` on Turn 1, then `get_priority_subject` on Turn 2 to resolve "that subject" without you repeating yourself.

<aside class="positive">
<strong>Stateless vs Stateful:</strong><br>
A <strong>chatbot</strong> treats every message independently — it has no memory between turns.<br>
An <strong>AI Agent</strong> maintains state across turns — it builds context over the conversation.
</aside>

### Checkpoint ✓

Your agent should now:
- Remember which subject you're most worried about
- Use that memory to answer follow-up questions without you repeating yourself
- Correctly update the priority when you mention a new subject

---

## Step 5: Workflow — The Agent Orchestrates Multiple Steps
Duration: 10:00

So far, the agent answers one question at a time. But a real study planning request — "create a study plan for tonight" — requires multiple steps in sequence:

```
1. Check priority subject from state
2. Get the deadline for that subject
3. Calculate days remaining
4. Generate a plan based on urgency
```

This is a **workflow**: a task that the agent breaks down and executes across multiple tool calls.

### 5.1 Add the `create_study_plan` tool to `tools.py`

```python
def create_study_plan(subject: str, days_remaining: int, tool_context: ToolContext) -> dict:
    """Creates a personalized study plan based on the subject and days remaining until deadline.

    Args:
        subject: The subject to create a plan for.
        days_remaining: Number of days until the deadline.
    """
    if days_remaining < 0:
        urgency = "OVERDUE"
        sessions = [
            "Contact your professor immediately about the missed deadline.",
            "Complete the work as soon as possible.",
        ]
    elif days_remaining == 0:
        urgency = "DUE TODAY"
        sessions = ["Focus entirely on this subject right now."]
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
            "Day 4–5: 1h/day review and consolidation",
            "Day before deadline: Light review only",
        ]
    else:
        urgency = "NORMAL"
        sessions = [
            "Daily: 1h focused study sessions",
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
```

### 5.2 Update the agent instruction and tools in `agent.py`

The instruction is the agent's "system design" — it tells the agent *how* to orchestrate its tools:

```python
INSTRUCTION = """You are a helpful and encouraging study planning assistant for university students.

When a student mentions they are worried about or focused on a subject, use save_priority_subject to remember it.

When asked about deadlines or time remaining, always use tools to get accurate data — never guess dates.

When creating a study plan, follow these steps in order:
1. Check if there is a saved priority subject (use get_priority_subject)
2. If no priority subject is saved, ask the student which subject they need help with
3. Get the deadline for that subject (use get_subject_deadline)
4. Calculate days remaining (use calculate_days_remaining)
5. Create the study plan (use create_study_plan)

Always be encouraging, specific, and realistic in your recommendations.
"""

root_agent = Agent(
    name="study_agent",
    model="gemini-2.0-flash",
    description="A student study planning assistant.",
    instruction=INSTRUCTION,
    tools=[
        get_current_time,
        get_subject_deadline,
        calculate_days_remaining,
        save_priority_subject,
        get_priority_subject,
        create_study_plan,
    ],
)
```

### 5.3 Test the full workflow

Restart `adk web` and run this complete scenario:

```
Turn 1: "I'm most worried about NLP."
Turn 2: "Create a study plan for tonight."
```

Watch the ADK web UI — you should see the agent make **4 tool calls** automatically:
1. `get_priority_subject` → NLP
2. `get_subject_deadline("NLP")` → 2026-05-25
3. `calculate_days_remaining("2026-05-25")` → N days
4. `create_study_plan("NLP", N)` → personalized plan

<aside class="positive">
<strong>Why split into steps?</strong> Breaking complex tasks into discrete tool calls makes your agent more reliable, easier to debug, and easier to extend. Each tool does one thing well.
</aside>

### Checkpoint ✓

Your agent should now:
- Automatically chain 4 tool calls to produce a study plan
- Adapt the plan based on urgency (CRITICAL vs HIGH vs NORMAL)
- Save the plan to state for future reference

---

## Step 6 (Bonus): Connect to Google MCP Servers
Duration: 05:00

<aside class="warning">
<strong>This step is optional.</strong> It introduces concepts that require additional Google Cloud setup. The presenter will demo this live — you can follow along or explore it after the event.
</aside>

### What is MCP?

**Model Context Protocol (MCP)** is an open standard that lets AI agents connect to external services through a unified interface. Instead of writing custom API integrations, you connect to an MCP server and get a set of tools automatically.

Google provides **fully managed MCP servers** for its services:

| MCP Server | What it provides |
|------------|-----------------|
| Google Workspace MCP | Gmail, Calendar, Docs, Sheets, Drive |
| BigQuery MCP | Query and analyze BigQuery datasets |
| Firebase MCP | Interact with Firebase projects |
| Cloud Monitoring MCP | Metrics, alerts, dashboards |

### Connecting to Google Workspace MCP

```python
from google.adk.tools.mcp_tool import MCPToolset, SseServerParams

workspace_toolset = MCPToolset(
    connection_params=SseServerParams(
        url="https://workspacemcp.googleapis.com/",
    )
)

root_agent = Agent(
    name="study_agent",
    model="gemini-2.0-flash",
    description="A student study planning assistant with calendar access.",
    instruction=INSTRUCTION,
    tools=[
        # ... your existing tools ...
        workspace_toolset,  # adds Calendar, Docs, Drive tools
    ],
)
```

With this connected, your agent could:
- Create a Google Calendar event for each study session
- Read your syllabus from Google Docs
- Save your study plan to Google Drive

### What you'd need

1. Enable the Google Calendar API in your Google Cloud project
2. Set up OAuth 2.0 credentials (or use Application Default Credentials)
3. Grant the MCP server access to your Google account

<aside class="positive">
<strong>Learn more:</strong> See the <a href="https://cloud.google.com/blog/products/ai-machine-learning/google-managed-mcp-servers-are-available-for-everyone">Google Managed MCP Servers announcement</a> for full setup instructions.
</aside>

---

## Step 7: Summary & What's Next
Duration: 03:00

### What you built

You started with a plain chatbot and transformed it into a real AI Agent:

| Step | What you added | Concept |
|------|---------------|---------|
| Step 2 | Basic agent with Gemini | LLM reasoning |
| Step 3 | `get_current_time`, `get_subject_deadline`, `calculate_days_remaining` | Tools |
| Step 4 | `save_priority_subject`, `get_priority_subject` | Session State |
| Step 5 | `create_study_plan` + orchestration instruction | Workflow |
| Step 6 | Google Workspace MCP | External integrations |

### The core pattern

```
AI Agent = LLM + Tools + State + Workflow
```

- **LLM** provides reasoning and language understanding
- **Tools** give the agent access to real data and actions
- **State** gives the agent memory within a session
- **Workflow** lets the agent handle multi-step tasks autonomously

### Ideas to extend this project

- **Wikipedia search tool** — let the agent look up study material
- **Multi-agent system** — one agent analyzes priorities, another creates the schedule
- **Persistent state** — use `DatabaseSessionService` to remember across sessions
- **Google Calendar integration** — automatically block study time on your calendar
- **Deploy to Cloud Run** — make your agent accessible from anywhere

### Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Google AI Studio (get API keys)](https://aistudio.google.com/)
- [Google Managed MCP Servers](https://cloud.google.com/blog/products/ai-machine-learning/google-managed-mcp-servers-are-available-for-everyone)
- [Codelab source code](https://github.com/eiyuumiru/student-study-agent-codelab)
- [GDGoC-UIT](https://gdg.community.dev/gdg-on-campus-university-of-information-technology-ho-chi-minh-city-vietnam/)

### Keep building!

The agent you built today is a foundation. Real-world agents follow the same pattern — they just have more tools, richer state, and more sophisticated workflows. You now have the mental model to build them.
