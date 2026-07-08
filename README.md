# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
==================================================
        TODAY'S SCHEDULE
        Owner: Alex
==================================================

Daily plan for Biscuit (Golden Retriever):
  08:00 – 08:30  Morning Walk (30 min) [priority: high]
  08:30 – 08:40  Feeding (10 min) [priority: high]
  08:40 – 09:25  Grooming (45 min) [priority: medium]
  09:25 – 09:45  Enrichment Puzzle (20 min) [priority: low]

Daily plan for Luna (Siamese):
  08:00 – 08:10  Feeding (10 min) [priority: high]
  08:10 – 08:15  Medication (5 min) [priority: high]
  08:15 – 08:30  Playtime (15 min) [priority: medium]

==================================================
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks_by_priority()`, `Scheduler.sort_tasks_by_time()` | Sorts tasks in-place either by priority rank (high → low) or by `start_time` ("HH:MM"), with untimed tasks pushed to the end. |
| Filtering | `Scheduler.filter_tasks(completed=..., pet_name=...)`, `Scheduler.get_recurring_tasks()` | Returns tasks matching completion status and/or pet name (either filter is optional), or just the recurring ones. |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.get_conflict_warnings()`, `find_conflicts_across_schedulers()` | A lightweight O(n log n) sweep — sort timed tasks by start time, then compare each task only against the ones immediately after it, stopping as soon as a later task starts after the current one ends. Flags true time-window overlaps (not just exact start-time matches), returns human-readable warning strings instead of raising, and can check across multiple pets' schedulers since one owner can only be in one place at a time. |
| Recurring tasks | `Task.create_next_occurrence()`, `Scheduler.complete_task()` | Marking a `daily` or `weekly` task complete via `complete_task()` automatically spawns a fresh, incomplete copy of it for the next occurrence and adds it back to the schedule. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
