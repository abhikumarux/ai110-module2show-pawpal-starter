from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    special_needs: list[str] = field(default_factory=list)

    def get_summary(self) -> str:
        pass

    def add_special_need(self, need: str) -> None:
        pass

    def remove_special_need(self, need: str) -> None:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferred_start_time: str = "08:00"
    preferences: dict = field(default_factory=dict)

    def get_time_budget(self) -> int:
        pass

    def update_preferences(self, key: str, value) -> None:
        pass


@dataclass
class Task:
    name: str
    category: str
    duration_minutes: int
    priority: str          # "high", "medium", or "low"
    is_recurring: bool = False
    frequency: str = "daily"
    notes: str = ""

    def is_high_priority(self) -> bool:
        pass

    def get_summary(self) -> str:
        pass

    def to_dict(self) -> dict:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []
        self.scheduled_plan: list[dict] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_name: str) -> None:
        pass

    def sort_tasks_by_priority(self) -> None:
        pass

    def generate_plan(self) -> None:
        pass

    def get_plan_summary(self) -> str:
        pass

    def get_skipped_tasks(self) -> list[Task]:
        pass
