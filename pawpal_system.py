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

    def __post_init__(self):
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK.keys())}, got '{self.priority}'")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is high."""
        return self.priority == "high"

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
        """Append a task to the scheduler's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name from the task list."""
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def sort_tasks_by_priority(self) -> None:
        """Sort tasks in-place from highest to lowest priority."""
        self.tasks.sort(key=lambda t: PRIORITY_RANK[t.priority])

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
