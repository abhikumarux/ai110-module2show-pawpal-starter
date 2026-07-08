from pawpal_system import Owner, Pet, Task, Scheduler


# --- Helpers ---

def make_owner(minutes=120, start="08:00"):
    return Owner(name="Alex", available_minutes=minutes, preferred_start_time=start)

def make_pet():
    return Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)

def make_scheduler():
    return Scheduler(owner=make_owner(), pet=make_pet())

def make_task(name="Walk", priority="high", duration=30, start_time="", recurring=False):
    return Task(
        name=name,
        category="walk",
        duration_minutes=duration,
        priority=priority,
        is_recurring=recurring,
        frequency="daily",
        start_time=start_time,
    )


# --- Original tests ---

def test_mark_complete_changes_status():
    task = make_task("Morning Walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_scheduler_count():
    scheduler = make_scheduler()
    assert len(scheduler.tasks) == 0
    scheduler.add_task(make_task("Walk"))
    scheduler.add_task(make_task("Feeding", priority="medium", duration=10))
    assert len(scheduler.tasks) == 2


# --- Sorting correctness ---

def test_sort_by_priority_orders_high_to_low():
    scheduler = make_scheduler()
    scheduler.add_task(make_task("Enrichment", priority="low"))
    scheduler.add_task(make_task("Grooming",   priority="medium"))
    scheduler.add_task(make_task("Walk",        priority="high"))

    scheduler.sort_tasks_by_priority()
    priorities = [t.priority for t in scheduler.tasks]
    assert priorities == ["high", "medium", "low"]


def test_sort_by_time_orders_chronologically():
    scheduler = make_scheduler()
    scheduler.add_task(make_task("Grooming",   start_time="17:00"))
    scheduler.add_task(make_task("Walk",       start_time="08:00"))
    scheduler.add_task(make_task("Enrichment", start_time="12:30"))

    scheduler.sort_tasks_by_time()
    times = [t.start_time for t in scheduler.tasks]
    assert times == ["08:00", "12:30", "17:00"]


def test_sort_by_time_pushes_untimed_tasks_last():
    scheduler = make_scheduler()
    scheduler.add_task(make_task("No Time Task", start_time=""))
    scheduler.add_task(make_task("Walk",         start_time="08:00"))

    scheduler.sort_tasks_by_time()
    assert scheduler.tasks[0].start_time == "08:00"
    assert scheduler.tasks[1].start_time == ""


# --- Recurrence logic ---

def test_completing_recurring_task_spawns_new_occurrence():
    scheduler = make_scheduler()
    scheduler.add_task(make_task("Walk", recurring=True))

    scheduler.complete_task("Walk")

    # original marked complete + one new occurrence added
    assert len(scheduler.tasks) == 2
    completed = [t for t in scheduler.tasks if t.completed]
    pending   = [t for t in scheduler.tasks if not t.completed]
    assert len(completed) == 1
    assert len(pending) == 1
    assert pending[0].name == "Walk"


def test_completing_non_recurring_task_does_not_spawn():
    scheduler = make_scheduler()
    scheduler.add_task(make_task("Grooming", recurring=False))

    scheduler.complete_task("Grooming")

    assert len(scheduler.tasks) == 1
    assert scheduler.tasks[0].completed is True


# --- Conflict detection ---

def test_two_overlapping_tasks_flagged_as_conflict():
    scheduler = make_scheduler()
    # Both start at 08:00 — direct overlap
    scheduler.add_task(make_task("Walk",    start_time="08:00", duration=30))
    scheduler.add_task(make_task("Feeding", start_time="08:00", duration=10))

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) > 0


def test_non_overlapping_tasks_have_no_conflicts():
    scheduler = make_scheduler()
    scheduler.add_task(make_task("Walk",    start_time="08:00", duration=30))
    scheduler.add_task(make_task("Feeding", start_time="09:00", duration=10))

    conflicts = scheduler.detect_conflicts()
    assert conflicts == []


def test_no_tasks_returns_no_conflicts():
    scheduler = make_scheduler()
    assert scheduler.detect_conflicts() == []


# --- Edge cases ---

def test_generate_plan_with_no_tasks_returns_empty():
    scheduler = make_scheduler()
    scheduler.generate_plan()
    assert scheduler.scheduled_plan == []
    assert scheduler.get_skipped_tasks() == []


def test_task_exceeding_budget_is_skipped():
    scheduler = Scheduler(owner=make_owner(minutes=10), pet=make_pet())
    scheduler.add_task(make_task("Long Walk", duration=60))

    scheduler.generate_plan()
    assert scheduler.scheduled_plan == []
    assert len(scheduler.get_skipped_tasks()) == 1


def test_task_exactly_filling_budget_is_scheduled():
    scheduler = Scheduler(owner=make_owner(minutes=30), pet=make_pet())
    scheduler.add_task(make_task("Walk", duration=30))

    scheduler.generate_plan()
    assert len(scheduler.scheduled_plan) == 1
    assert scheduler.get_skipped_tasks() == []
