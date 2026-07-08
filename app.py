import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state initialization ---
# Guards ensure objects are created once and persist across reruns.
if "owner" not in st.session_state:
    st.session_state.owner = None

if "pet" not in st.session_state:
    st.session_state.pet = None

if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# --- Section 1: Owner + Pet Setup ---
st.subheader("1. Tell us about you and your pet")

with st.form("setup_form"):
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input("Your name", value="Alex")
        available_minutes = st.number_input("Available time today (minutes)", min_value=10, max_value=480, value=120)
        start_time = st.text_input("Start time (HH:MM)", value="08:00")
    with col2:
        pet_name = st.text_input("Pet name", value="Biscuit")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        breed = st.text_input("Breed", value="Golden Retriever")
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

    submitted = st.form_submit_button("Save Owner & Pet")
    if submitted:
        # Create Owner and Pet instances from form data, then wire into Scheduler.
        owner = Owner(
            name=owner_name,
            available_minutes=int(available_minutes),
            preferred_start_time=start_time,
        )
        pet = Pet(name=pet_name, species=species, breed=breed, age=int(age))
        st.session_state.owner = owner
        st.session_state.pet = pet
        st.session_state.scheduler = Scheduler(owner=owner, pet=pet)
        st.success(f"Saved! {pet.get_summary()}")

st.divider()

# --- Section 2: Add Tasks ---
st.subheader("2. Add care tasks")

if st.session_state.scheduler is None:
    st.info("Complete step 1 first to unlock task entry.")
else:
    with st.form("task_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            task_name = st.text_input("Task name", value="Morning Walk")
            category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment"])
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        with col3:
            is_recurring = st.checkbox("Recurring?", value=True)
            frequency = st.selectbox("Frequency", ["daily", "weekly"])
            notes = st.text_input("Notes (optional)", value="")

        task_submitted = st.form_submit_button("Add Task")
        if task_submitted:
            new_task = Task(
                name=task_name,
                category=category,
                duration_minutes=int(duration),
                priority=priority,
                is_recurring=is_recurring,
                frequency=frequency,
                notes=notes,
            )
            # add_task() appends the Task object to the Scheduler's task list.
            st.session_state.scheduler.add_task(new_task)
            st.success(f"Added: {new_task.get_summary()}")

    # Show current task list
    tasks = st.session_state.scheduler.tasks
    if tasks:
        st.markdown("**Current tasks:**")
        st.table([t.to_dict() for t in tasks])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Section 3: Generate Schedule ---
st.subheader("3. Generate today's schedule")

if st.session_state.scheduler is None:
    st.info("Complete steps 1 and 2 first.")
elif not st.session_state.scheduler.tasks:
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate Schedule"):
        # generate_plan() sorts by priority and fits tasks into the time budget.
        st.session_state.scheduler.generate_plan()

    if st.session_state.scheduler.scheduled_plan:
        st.success("Here's your plan for today:")
        for entry in st.session_state.scheduler.scheduled_plan:
            task = entry["task"]
            st.markdown(
                f"**{entry['start']} – {entry['end']}** &nbsp; {task.name} "
                f"({task.duration_minutes} min) — *{task.priority} priority*"
            )

        skipped = st.session_state.scheduler.get_skipped_tasks()
        if skipped:
            st.warning("Skipped (not enough time):")
            for t in skipped:
                st.markdown(f"- {t.name} ({t.duration_minutes} min)")
