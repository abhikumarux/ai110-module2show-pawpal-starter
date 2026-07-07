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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
