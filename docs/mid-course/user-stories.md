# User Stories

## Feature 1 – Search & Combined Filters

### US-01: Search tasks

**As a** team member

**I want** to search tasks by title or description

**So that** I can quickly find the task I need.

### Acceptance Criteria
- Given tasks exist,
- When I enter a search keyword,
- Then only tasks whose title or description contains the keyword are displayed.
- Search is case-insensitive.
- Empty search returns all tasks.

**AI Assumption Corrected**
AI initially suggested searching task IDs as well. This was removed because the requirements specify searching only the title and description.

---

### US-02: Filter by status and priority

...

---

### US-03: Combine search and filters

...

---

## Feature 2 – Task Comments

### US-04: Add comments

...

### Acceptance Criteria
- User can add comments.
- Comment text cannot be blank.
- Comment appears immediately.

**AI Assumption Corrected**
AI suggested rich-text comments with timestamps editable by users. Only plain text comments were implemented because the assignment did not require formatting.

---

### US-05: View comments

...

---

### US-06: Delete comments