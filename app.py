import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Your daily pet care planner — built around your time, your pet's needs, and your priorities.")

# --- Session state initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ──────────────────────────────────────────
# SECTION 1: Owner + Pet Setup
# ──────────────────────────────────────────
st.subheader("1. Tell us about you and your pet")

with st.form("setup_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name       = st.text_input("Your name", value="Alex")
        available_minutes = st.number_input("Available time today (minutes)", min_value=10, max_value=480, value=120)
        start_time       = st.text_input("Start time (HH:MM)", value="08:00")
    with col2:
        pet_name = st.text_input("Pet name", value="Biscuit")
        species  = st.selectbox("Species", ["dog", "cat", "other"])
        breed    = st.text_input("Breed", value="Golden Retriever")
        age      = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

    if st.form_submit_button("Save Owner & Pet"):
        owner = Owner(name=owner_name, available_minutes=int(available_minutes), preferred_start_time=start_time)
        pet   = Pet(name=pet_name, species=species, breed=breed, age=int(age))
        st.session_state.owner     = owner
        st.session_state.pet       = pet
        st.session_state.scheduler = Scheduler(owner=owner, pet=pet)
        st.success(f"Saved! {pet.get_summary()}")

st.divider()

# ──────────────────────────────────────────
# SECTION 2: Add Tasks
# ──────────────────────────────────────────
st.subheader("2. Add care tasks")

if st.session_state.scheduler is None:
    st.info("Complete step 1 first to unlock task entry.")
else:
    with st.form("task_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_name  = st.text_input("Task name", value="Morning Walk")
            category   = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment"])
            start_time_task = st.text_input("Fixed start time (HH:MM, optional)", value="")
        with col2:
            duration   = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
            priority   = st.selectbox("Priority", ["high", "medium", "low"])
        with col3:
            is_recurring = st.checkbox("Recurring?", value=True)
            frequency    = st.selectbox("Frequency", ["daily", "weekly"])
            notes        = st.text_input("Notes (optional)", value="")

        if st.form_submit_button("Add Task"):
            new_task = Task(
                name=task_name,
                category=category,
                duration_minutes=int(duration),
                priority=priority,
                is_recurring=is_recurring,
                frequency=frequency,
                notes=notes,
                start_time=start_time_task.strip(),
            )
            st.session_state.scheduler.add_task(new_task)
            st.success(f"Added: {new_task.get_summary()}")

    # --- Task table sorted by priority ---
    tasks = st.session_state.scheduler.tasks
    if tasks:
        st.session_state.scheduler.sort_tasks_by_priority()
        sorted_tasks = st.session_state.scheduler.tasks

        st.markdown("**Current tasks (sorted by priority):**")
        display_rows = [
            {
                "Task":     t.name,
                "Category": t.category,
                "Duration": f"{t.duration_minutes} min",
                "Priority": t.priority,
                "Start":    t.start_time or "—",
                "Recurring": "Yes" if t.is_recurring else "No",
                "Done":     "✓" if t.completed else "",
            }
            for t in sorted_tasks
        ]
        st.table(display_rows)

        # --- Conflict warnings surfaced immediately after task list ---
        warnings = st.session_state.scheduler.get_conflict_warnings()
        if warnings:
            st.warning("**Scheduling conflicts detected** — two or more tasks overlap in time. Review the start times below and adjust before generating your plan.")
            for w in warnings:
                st.markdown(f"- {w}")
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ──────────────────────────────────────────
# SECTION 3: Generate Schedule
# ──────────────────────────────────────────
st.subheader("3. Generate today's schedule")

if st.session_state.scheduler is None:
    st.info("Complete steps 1 and 2 first.")
elif not st.session_state.scheduler.tasks:
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate Schedule"):
        st.session_state.scheduler.generate_plan()

    if st.session_state.scheduler.scheduled_plan:
        pet  = st.session_state.pet
        owner = st.session_state.owner
        st.success(f"Today's plan for **{pet.name}** ({pet.breed}) — {owner.available_minutes} min available")

        # Render plan as a clean table
        plan_rows = [
            {
                "Time Slot":  f"{e['start']} – {e['end']}",
                "Task":       e["task"].name,
                "Category":   e["task"].category,
                "Duration":   f"{e['task'].duration_minutes} min",
                "Priority":   e["task"].priority,
                "Recurring":  "Yes" if e["task"].is_recurring else "No",
            }
            for e in st.session_state.scheduler.scheduled_plan
        ]
        st.table(plan_rows)

        # Skipped tasks
        skipped = st.session_state.scheduler.get_skipped_tasks()
        if skipped:
            st.warning(f"**{len(skipped)} task(s) skipped** — not enough time in today's budget:")
            for t in skipped:
                st.markdown(f"- **{t.name}** ({t.duration_minutes} min, {t.priority} priority)")
        else:
            st.info("All tasks fit within today's time budget.")
