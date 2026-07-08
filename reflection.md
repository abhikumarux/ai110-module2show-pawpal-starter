# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I started with four classes: `Pet`, `Owner`, `Task`, and `Scheduler`. `Pet` and `Owner` hold the core data — who the pet is and how much time the owner has. `Task` represents a single care activity with a name, category, duration, and priority. `Scheduler` is the brain: it takes the owner and pet as context, holds a list of tasks, and is responsible for sorting them and generating a daily plan that fits within the owner's time budget.

**b. Design changes**

The skeleton is still early, but reviewing it revealed a few things I'll need to address during implementation:

- `Task` has no fixed-time constraint field. For tasks like medication that must happen at a specific time, I'll likely add a `time_constraint` attribute to `Task` rather than hardcoding that logic in the scheduler.
- `generate_plan()` is at risk of doing too much — sorting, time tracking, slot assignment, and skipped task handling all in one place. I'm planning to break out a private helper to keep it manageable.
- `Task.priority` is a plain string with no validation. I'll use a ranking dict or Enum so that sorting is consistent and bad values can't sneak in.
- `scheduled_plan` needs a defined dict shape (keys for start time, task name, duration) before `get_plan_summary()` can safely read from it.
- `Owner.preferred_start_time` is stored as a string like `"08:00"` but needs to be numeric for time arithmetic in the scheduler. I'll convert it to minutes from midnight early rather than parsing it repeatedly.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The two constraints that drive everything are time and priority. The owner's `available_minutes` is the hard ceiling — the scheduler won't go over it no matter what. Priority decides which tasks get first access to that budget: high-priority tasks like medication and feeding are scheduled before medium or low ones, so if time runs short, it's always the enrichment puzzle that gets dropped, not the morning meds.

I also built in optional fixed start times on tasks, which acts as a softer constraint — it doesn't force the scheduler to slot a task at a specific moment, but it does let conflict detection catch cases where two tasks the owner pinned to the same time are going to collide.

I decided to prioritize time budget and task priority above everything else because those are the two things a pet owner actually loses sleep over. Missing a walk because there wasn't time is forgivable. Missing medication because the scheduler buried it under low-priority tasks is not.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff I made is in how `detect_conflicts()` decides two tasks actually clash. Right now it treats the owner as if they only have one pair of hands, ever — if two tasks' time windows overlap at all, even by a minute, it flags them as a conflict, whether they belong to the same pet or two different pets. That's not really how a morning goes in real life. Filling two food bowls at 8:00 for two different pets isn't a real conflict; it's the kind of thing an owner can do in the same couple of minutes without thinking twice. But my scheduler has no way to know that — it only sees a start time and a duration, not how much attention a task actually demands.

I did think about fixing this properly, maybe adding something like an `attention_level` field to `Task` so quick, low-effort tasks wouldn't trip the conflict check against each other. I decided not to go down that road for this version. It would mean a new field on every task, a second thing to reason about inside the conflict-checking logic, and a UI to let the owner set it — a lot of added surface area for a problem that's more of an annoyance than a real bug. Instead I leaned on the idea that it's better to warn too often than not enough: an owner can glance at a warning and shrug it off if it's a false alarm, but if the scheduler stayed quiet about a genuine double-booking — like two pets needing medication at the exact same moment — that's a much worse failure. It's the same instinct that shaped `generate_plan()`: I picked the simpler, greedy, easy-to-follow approach over a fully optimal one, knowing it would sometimes skip a task it technically could have fit, because I'd rather have logic I can trust and explain than logic that's clever but opaque.

---

## 3. AI Collaboration

**a. How you used AI**

The most effective thing the AI did for this project was help me think out loud at the design stage before writing a single line of code. Prompts like "what attributes does a Task class need for a pet care scheduler?" and "what are the most important edge cases to test for a scheduler with recurring tasks?" forced a structured design conversation that I probably would have skipped if I was coding on my own. The brainstorming phase felt genuinely collaborative — I'd push back, the AI would adjust, and we'd land somewhere better than either of us started.

Once implementation started, the most useful thing was asking the AI to flag potential bottlenecks in the skeleton ("look at this code and tell me what's going to be a problem"). It caught the `generate_plan()` complexity risk and the `priority` validation gap before I hit them in practice.

**b. Judgment and verification**

At one point the AI suggested adding an `attention_level` field to `Task` — a 1–3 scale of how much focus a task demands — so the conflict checker could distinguish between two trivial overlapping tasks (fine) and two intensive ones (a real problem). It was a genuinely good idea. I thought about it, wrote out what the change would look like, and decided against it.

The issue wasn't that it was wrong — it was that it added a new field to every task, a more complicated condition inside the conflict logic, and a new UI control for the owner to fill in. That's a lot of surface area for a feature that mainly makes conflict warnings slightly less noisy. The simpler rule — warn on any overlap, let the owner decide if it matters — is easier to understand, easier to test, and harder to get wrong. I verified the decision by tracing through what would happen in the "medication + feeding at the same time" case: the dumb rule still catches the dangerous scenario, which is the one that actually matters.

---

## 4. Testing and Verification

**a. What you tested**

The 13 tests cover five areas: task completion status, task addition, priority and time sorting, recurring task auto-spawn, and conflict detection. I also tested three edge cases specifically: a scheduler with no tasks, a task whose duration exceeds the entire time budget, and a task that fills the budget exactly (the off-by-one case).

Priority sorting and conflict detection were the most important to test because they're the two behaviors the rest of the system relies on. If `sort_tasks_by_priority()` is wrong, `generate_plan()` schedules the wrong things. If `detect_conflicts()` is wrong, the UI gives false reassurance. Getting those wrong silently would be worse than a crash.

**b. Confidence**

4 out of 5. The logic layer — scheduling, sorting, filtering, conflict detection, recurrence — is well-covered and I'm confident it behaves correctly. The missing confidence comes from the Streamlit UI, which I haven't tested with automated tools. It's possible a session state edge case or a form rerun causes unexpected behavior that my unit tests wouldn't catch.

If I had more time, I'd test: tasks with duplicate names (which one gets removed?), an invalid `HH:MM` format in `start_time`, and what happens when `complete_task()` is called on a task name that doesn't exist in the list.

---

## 5. Reflection

**a. What went well**

The part I'm most satisfied with is the conflict detection system, specifically the cross-pet version. It started as a basic overlap check and grew into something that actually models a real constraint: one owner, multiple pets, finite attention. The fact that `find_conflicts_across_schedulers()` can take a list of schedulers and flag double-bookings across all of them feels like the most "real-world" piece of the whole project — it's solving a problem a pet owner would genuinely run into on a busy morning.

**b. What you would improve**

I'd redesign how `generate_plan()` handles fixed-time tasks. Right now it sorts by priority and assigns slots greedily starting from the owner's preferred start time — it completely ignores `start_time` on individual tasks. A task pinned to 17:00 gets scheduled at 08:40 if it's medium priority. That's wrong. In the next iteration I'd add a second pass: anchor fixed-time tasks first, then fill gaps with the remaining priority-sorted tasks.

**c. Key takeaway**

The biggest thing I learned is that using AI well is mostly about knowing when to push back. The AI is fast, fluent, and almost always produces something that works — but "works" and "fits your design" aren't the same thing. Every time I accepted a suggestion without tracing through how it connected to the rest of the system, I ended up with something I had to rethink later. The most productive sessions were the ones where I treated the AI like a junior engineer: smart, capable, helpful, but needing someone to keep the bigger picture in mind. That's the lead architect role — not writing every line, but knowing why every line is there.
