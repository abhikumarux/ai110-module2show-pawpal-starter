from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner(name="Alex", available_minutes=120, preferred_start_time="08:00")

biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
luna = Pet(name="Luna", species="cat", breed="Siamese", age=5, special_needs=["anxiety"])

biscuit_tasks = [
    Task("Morning Walk",      "walk",       duration_minutes=30, priority="high",   is_recurring=True),
    Task("Feeding",           "feeding",    duration_minutes=10, priority="high",   is_recurring=True),
    Task("Enrichment Puzzle", "enrichment", duration_minutes=20, priority="low"),
    Task("Grooming",          "grooming",   duration_minutes=45, priority="medium"),
]

luna_tasks = [
    Task("Feeding",           "feeding",    duration_minutes=10, priority="high",   is_recurring=True),
    Task("Medication",        "meds",       duration_minutes=5,  priority="high",   is_recurring=True),
    Task("Playtime",          "enrichment", duration_minutes=15, priority="medium"),
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
