from pawpal_system import Owner, Pet, Task, Scheduler


def make_task(name="Walk", priority="high", duration=30):
    return Task(name=name, category="walk", duration_minutes=duration, priority=priority)


def test_mark_complete_changes_status():
    task = make_task("Morning Walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_scheduler_count():
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    scheduler = Scheduler(owner=owner, pet=pet)

    assert len(scheduler.tasks) == 0
    scheduler.add_task(make_task("Walk"))
    scheduler.add_task(make_task("Feeding", priority="medium", duration=10))
    assert len(scheduler.tasks) == 2
