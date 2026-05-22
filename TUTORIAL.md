# Student Study Planning Agent

Welcome to the **GDGoC-UIT Build with AI** codelab!

## Setup — do this first

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Get your Gemini API key** → [Google AI Studio](https://aistudio.google.com/apikey)  
Click **Create API key**, then copy it.

**3. Set the key**

```bash
export GOOGLE_API_KEY="paste_your_key_here"
```

**4. Start the agent UI**

```bash
adk web --allow_origins 'regex:https://.*.cloudshell.dev'
```

Click **Web Preview → Preview on port 8000** in the Cloud Shell toolbar above.

---

## Files you'll edit

```
study_agent/
├── agent.py    ← register tools, update the instruction
└── tools.py    ← implement the TODO functions here
```

---

## Step 3 — Add Tools

`get_all_subjects()` is already implemented for you — it returns the canonical list of subjects so the agent never has to guess names.

Open `study_agent/tools.py` and implement the 3 `TODO` functions:

- `get_current_time()` → return `{"current_time": "YYYY-MM-DD HH:MM:SS", "date": "YYYY-MM-DD"}`
- `get_subject_deadline(subject)` → case-insensitive lookup against `SUBJECT_DEADLINES`, return found/not found
- `calculate_days_remaining(deadline_date)` → compute days, return status: `overdue / due_today / critical / urgent / normal`

Restart `adk web` and test:

```
What time is it right now?
When is the NLP deadline?
How many days until Machine Learning?
```

---

## Step 4 — Session State

In **`tools.py`**:
1. Uncomment `from google.adk.tools import ToolContext` at the top
2. Uncomment + implement `save_priority_subject` and `get_priority_subject`

In **`agent.py`**:
3. Uncomment `get_priority_subject` and `save_priority_subject` in the imports block
4. Add both to the `tools=[...]` list

Restart and test across two turns:

```
Turn 1: I'm most worried about my NLP assignment.
Turn 2: How many days do I have left for that?
```

---

## Step 5 — Study Plan

In **`tools.py`**:
1. Uncomment + implement `create_study_plan`
   Return a plan dict based on urgency: `OVERDUE / DUE TODAY / CRITICAL / HIGH / NORMAL`
   Also save it: `tool_context.state["last_study_plan"] = plan`

In **`agent.py`**:
2. Uncomment `create_study_plan` in imports + add to `tools=[...]`
3. Expand `INSTRUCTION` to describe the 5-step workflow (check priority → get deadline → calc days → create plan)

Restart and test the full flow:

```
Turn 1: I'm most worried about NLP.
Turn 2: Create a study plan for tonight.
```

Watch the ADK UI — you should see 4 tool calls fire automatically.

---

## Troubleshooting

```bash
# ModuleNotFoundError? Make sure you're at the repo root:
cd ~/student-study-agent-codelab

# Restart adk web after every file save:
# Ctrl+C  →  adk web --allow_origins 'regex:https://.*.cloudshell.dev'
```
