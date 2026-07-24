# User Stories

## Feature 1 – Task Comments

### US-01: Add comments
### US-02: Delete comments
### US-03: View comments

### Acceptance Criteria
- User can add / delete comments.
- Comment text cannot be blank.
- Comment appears immediately.

**AI Assumption Corrected**
AI suggested rich-text comments with timestamps editable by users. Only plain text comments were implemented because the assignment did not require formatting.


## Feature 2 – Search & Combined Filters

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