from dataclasses import dataclass, field
from dataclasses import asdict

PRIORITY_RANK = {"high": 1, "medium": 2, "low": 3}


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    special_needs: list[str] = field(default_factory=list)

    def get_summary(self) -> str:
        """Return a readable one-line description of the pet."""
        base = f"{self.name} ({self.breed}, {self.species}, age {self.age})"
        if self.special_needs:
            return base + f" — special needs: {', '.join(self.special_needs)}"
        return base

    def add_special_need(self, need: str) -> None:
        """Add a special need if it isn't already listed."""
        if need not in self.special_needs:
            self.special_needs.append(need)

    def remove_special_need(self, need: str) -> None:
        """Remove a special need if it exists."""
        if need in self.special_needs:
            self.special_needs.remove(need)


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferred_start_time: str = "08:00"
    preferences: dict = field(default_factory=dict)

    def get_time_budget(self) -> int:
        """Return the total daily minutes the owner has available."""
        return self.available_minutes

    def update_preferences(self, key: str, value) -> None:
        """Set or overwrite a single owner preference."""
        self.preferences[key] = value

    def start_time_in_minutes(self) -> int:
        """Convert preferred_start_time 'HH:MM' to minutes from midnight."""
        hours, mins = self.preferred_start_time.split(":")
        return int(hours) * 60 + int(mins)


@dataclass
class Task:
    name: str
    category: str
    duration_minutes: int
    priority: str          # "high", "medium", or "low"
    is_recurring: bool = False
    frequency: str = "daily"
    notes: str = ""
    completed: bool = False
    start_time: str = ""   # optional fixed time as "HH:MM"
    pet_name: str = ""     # stamped by Scheduler.add_task

    def __post_init__(self):
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK.keys())}, got '{self.priority}'")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is high."""
        return self.priority == "high"

    def create_next_occurrence(self) -> "Task":
        """Return a fresh, incomplete copy of this task for its next occurrence."""
        return Task(
            name=self.name,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            is_recurring=self.is_recurring,
            frequency=self.frequency,
            notes=self.notes,
            completed=False,
            start_time=self.start_time,
            pet_name=self.pet_name,
        )

    def get_summary(self) -> str:
        """Return a readable one-line description of the task."""
        recurrence = f" ({self.frequency})" if self.is_recurring else ""
        return f"{self.name} [{self.category}] — {self.duration_minutes} min, priority: {self.priority}{recurrence}"

    def to_dict(self) -> dict:
        """Return all task fields as a plain dictionary."""
        return asdict(self)


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []
        self.scheduled_plan: list[dict] = []  # each entry: {start, end, task}

    def add_task(self, task: Task) -> None:
        """Append a task to the scheduler's task list, stamping it with this pet's name."""
        if not task.pet_name:
            task.pet_name = self.pet.name
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name from the task list."""
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def complete_task(self, task_name: str) -> Task | None:
        """Mark the named task complete. If it's daily/weekly recurring, auto-schedule its next occurrence.

        Returns the newly created occurrence, or None if no occurrence was spawned.
        """
        for task in self.tasks:
            if task.name == task_name and not task.completed:
                task.mark_complete()
                if task.is_recurring and task.frequency in ("daily", "weekly"):
                    next_task = task.create_next_occurrence()
                    self.add_task(next_task)
                    return next_task
                return None
        return None

    def sort_tasks_by_priority(self) -> None:
        """Sort tasks in-place from highest to lowest priority."""
        self.tasks.sort(key=lambda t: PRIORITY_RANK[t.priority])

    def sort_tasks_by_time(self) -> None:
        """Sort tasks in-place by their start_time. Tasks with no start_time sort last."""
        self.tasks.sort(key=lambda t: _hhmm_to_minutes(t.start_time) if t.start_time else float("inf"))

    def filter_tasks(self, completed: bool = None, pet_name: str = None) -> list[Task]:
        """Return tasks matching the given completion status and/or pet name (either filter is optional)."""
        results = self.tasks
        if completed is not None:
            results = [t for t in results if t.completed == completed]
        if pet_name is not None:
            results = [t for t in results if t.pet_name == pet_name]
        return results

    def get_recurring_tasks(self) -> list[Task]:
        """Return only the recurring tasks."""
        return [t for t in self.tasks if t.is_recurring]

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of tasks whose fixed start_time windows overlap."""
        return _find_conflicts(self.tasks)

    def get_conflict_warnings(self) -> list[str]:
        """Return human-readable warning strings for each conflicting pair, instead of raising."""
        return [_format_conflict_warning(a, b) for a, b in self.detect_conflicts()]

    def generate_plan(self) -> None:
        """Build a time-slotted daily plan that fits within the owner's time budget."""
        self.sort_tasks_by_priority()
        self.scheduled_plan = []

        time_remaining = self.owner.get_time_budget()
        current_minute = self.owner.start_time_in_minutes()

        for task in self.tasks:
            if task.duration_minutes <= time_remaining:
                start = _minutes_to_hhmm(current_minute)
                end = _minutes_to_hhmm(current_minute + task.duration_minutes)
                self.scheduled_plan.append({"start": start, "end": end, "task": task})
                current_minute += task.duration_minutes
                time_remaining -= task.duration_minutes

    def get_plan_summary(self) -> str:
        """Return the scheduled plan as a formatted, human-readable string."""
        if not self.scheduled_plan:
            return "No plan generated yet. Call generate_plan() first."

        lines = [f"Daily plan for {self.pet.name} ({self.pet.breed}):"]
        for entry in self.scheduled_plan:
            task = entry["task"]
            lines.append(
                f"  {entry['start']} – {entry['end']}  {task.name} ({task.duration_minutes} min) [priority: {task.priority}]"
            )

        skipped = self.get_skipped_tasks()
        if skipped:
            lines.append("\nSkipped (not enough time):")
            for task in skipped:
                lines.append(f"  - {task.name} ({task.duration_minutes} min)")

        return "\n".join(lines)

    def get_skipped_tasks(self) -> list[Task]:
        """Return tasks that were not scheduled due to insufficient time."""
        scheduled_names = {entry["task"].name for entry in self.scheduled_plan}
        return [t for t in self.tasks if t.name not in scheduled_names]


# --- helpers ---

def _minutes_to_hhmm(total_minutes: int) -> str:
    """Convert an integer minute offset from midnight to an 'HH:MM' string."""
    hours = (total_minutes // 60) % 24
    mins = total_minutes % 60
    return f"{hours:02d}:{mins:02d}"


def _hhmm_to_minutes(hhmm: str) -> int:
    """Convert an 'HH:MM' string to minutes from midnight."""
    hours, mins = hhmm.split(":")
    return int(hours) * 60 + int(mins)


def _find_conflicts(tasks: list[Task]) -> list[tuple[Task, Task]]:
    """Lightweight O(n log n) sweep: sort timed tasks by start, then only compare
    each task against the ones immediately after it, stopping as soon as a later
    task starts after the current one ends. Never raises — tasks with no
    start_time are simply ignored since they can't conflict."""
    timed_tasks = [t for t in tasks if t.start_time]
    timed_tasks.sort(key=lambda t: _hhmm_to_minutes(t.start_time))

    conflicts = []
    for i in range(len(timed_tasks)):
        a = timed_tasks[i]
        a_end = _hhmm_to_minutes(a.start_time) + a.duration_minutes
        for j in range(i + 1, len(timed_tasks)):
            b = timed_tasks[j]
            if _hhmm_to_minutes(b.start_time) >= a_end:
                break
            conflicts.append((a, b))
    return conflicts


def _format_conflict_warning(a: Task, b: Task) -> str:
    """Build a human-readable warning message for a conflicting pair of tasks."""
    if a.pet_name and b.pet_name and a.pet_name != b.pet_name:
        return (
            f"⚠️  Conflict: {a.name} ({a.pet_name}) at {a.start_time} overlaps with "
            f"{b.name} ({b.pet_name}) at {b.start_time} — the owner can't do both at once."
        )
    return f"⚠️  Conflict: {a.name} at {a.start_time} overlaps with {b.name} at {b.start_time}."


def find_conflicts_across_schedulers(schedulers: list["Scheduler"]) -> list[str]:
    """Check for time conflicts across multiple pets' schedulers (e.g. one owner, several pets).

    A shared owner can only be in one place at a time, so this pools every scheduler's
    tasks together and re-runs the same lightweight sweep. Returns warning strings
    instead of raising, so a scheduling clash never crashes the program.
    """
    all_tasks = [task for scheduler in schedulers for task in scheduler.tasks]
    return [_format_conflict_warning(a, b) for a, b in _find_conflicts(all_tasks)]
