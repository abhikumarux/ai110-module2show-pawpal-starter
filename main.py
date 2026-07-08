from pawpal_system import Owner, Pet, Task, Scheduler, find_conflicts_across_schedulers

owner = Owner(name="Alex", available_minutes=120, preferred_start_time="08:00")

biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
luna = Pet(name="Luna", species="cat", breed="Siamese", age=5, special_needs=["anxiety"])

# Tasks are added out of time order on purpose, to exercise sort_tasks_by_time().
biscuit_tasks = [
    Task("Grooming",          "grooming",   duration_minutes=45, priority="medium", start_time="17:00"),
    Task("Morning Walk",      "walk",       duration_minutes=30, priority="high",   is_recurring=True, start_time="08:00", completed=True),
    Task("Enrichment Puzzle", "enrichment", duration_minutes=20, priority="low",    start_time="12:30"),
    Task("Feeding",           "feeding",    duration_minutes=10, priority="high",   is_recurring=True, start_time="08:15"),
]

luna_tasks = [
    Task("Playtime",          "enrichment", duration_minutes=15, priority="medium", start_time="18:00"),
    Task("Medication",        "meds",       duration_minutes=5,  priority="high",   is_recurring=True, start_time="08:00"),
    Task("Feeding",           "feeding",    duration_minutes=10, priority="high",   is_recurring=True, start_time="08:00", completed=True),
]

biscuit_scheduler = Scheduler(owner=owner, pet=biscuit)
for task in biscuit_tasks:
    biscuit_scheduler.add_task(task)
biscuit_scheduler.generate_plan()

luna_scheduler = Scheduler(owner=owner, pet=luna)
for task in luna_tasks:
    luna_scheduler.add_task(task)
luna_scheduler.generate_plan()

print("=" * 50)
print("        TODAY'S SCHEDULE")
print(f"        Owner: {owner.name}")
print("=" * 50)
print()
print(biscuit_scheduler.get_plan_summary())
print()
print(luna_scheduler.get_plan_summary())
print()
print("=" * 50)


def print_tasks(label: str, tasks: list[Task]) -> None:
    print(label)
    if not tasks:
        print("  (none)")
        return
    for t in tasks:
        time_str = t.start_time or "??:??"
        print(f"  {time_str}  {t.name} [{t.pet_name}] — completed: {t.completed}")


print()
print("=" * 50)
print("        SORTING & FILTERING DEMO")
print("=" * 50)

for scheduler in (biscuit_scheduler, luna_scheduler):
    print()
    print(f"--- {scheduler.pet.name} ---")

    scheduler.sort_tasks_by_time()
    print_tasks("Tasks sorted by time:", scheduler.tasks)

    incomplete = scheduler.filter_tasks(completed=False)
    print_tasks("Incomplete tasks:", incomplete)

    completed = scheduler.filter_tasks(completed=True)
    print_tasks("Completed tasks:", completed)

    by_pet = scheduler.filter_tasks(pet_name=scheduler.pet.name)
    print_tasks(f"Tasks for {scheduler.pet.name}:", by_pet)

    warnings = scheduler.get_conflict_warnings()
    print("Conflicts:")
    if not warnings:
        print("  (none)")
    else:
        for warning in warnings:
            print(f"  {warning}")

print()
print("=" * 50)
print("        CROSS-PET CONFLICT CHECK")
print("=" * 50)
print("(One owner can't do two things at once, even for different pets.)")
print()

household_warnings = find_conflicts_across_schedulers([biscuit_scheduler, luna_scheduler])
if not household_warnings:
    print("  (none)")
else:
    for warning in household_warnings:
        print(f"  {warning}")

print()
print("=" * 50)
