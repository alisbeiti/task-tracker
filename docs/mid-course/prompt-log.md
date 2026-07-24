# Prompt Log

## Feature 1 - Task comments

## Ask for a plan before code


### Prompt 1 (Weak)

"Help me implement task comments."

### Why it was weak

It did not specify the technology or expected behavior.

---

### Improved Prompt

I want to implement the following feature incrementally. Before writing any code, provide an implementation plan only.

Feature:
Task Comments

Requirements:
- Extend the existing task data model to support a list of comments for each task.  Each task has a unique Task ID, and comments are associated with the corresponding task using that Task ID.
- Support adding, listing, and deleting comments.
- Reject blank comments.
- Return appropriate not-found responses for missing tasks or comments.
- Create new API to list, add, and delete comments for a task
- Do not create new endpoints unless  necessary.

Current project files:
- main.py
- models.py

Output format:

| Step | File or Selection | What Changes | How I Verify It |
|------|-------------------|--------------|-----------------|

Constraints:
- Do not write any code yet.
- Keep the implementation small and incremental.
- Each step should modify only a small number of files.
- After each step, include a simple verification method (run the app, execute a test, or manually verify the behavior).
- Keep the plan aligned with an incremental workflow: make a small change, inspect the diff, verify it, then continue.
- Do not introduce new frameworks, databases, backend services, authentication, or unrelated files.
- Keep the solution consistent with the existing FastAPI application and JSON file-based data storage.

### AI Response

Step	File or Selection	What Changes	How I Verify It
1	models.py	Add a small comment schema and extend the task model so each task can carry a comments list. Keep the change narrow and backward-friendly for existing task data.	Inspect the diff and run a quick Python import/check to confirm the new models load correctly.
2	storage.py	Add minimal in-memory comment operations scoped by task ID so comments are stored and retrieved with the correct task. Keep the logic close to the existing task storage pattern.	Inspect the diff and run a focused test or small script that creates a task, adds a comment, lists it, and deletes it.
3	main.py	Add task-scoped comment endpoints under the existing task routes, such as list/add/delete comments for a given task. Use nested task routes rather than introducing a new top-level comments API.	Start the app and verify the flow through Swagger UI or curl, including blank-comment rejection and 404 responses.
4	test_tasks.py	Add small regression tests for successful comment operations, blank-comment rejection, and missing task/comment handling. Keep the test scope focused on comments only.	Run the relevant pytest tests and confirm they pass after each small change.


---

## Prompt 2 – Update the data model and storage

I want to implement Task Comments incrementally.

Update only the data model and storage layer.

Requirements:
- Extend the existing task data model to support comments.
- Each task has a unique Task ID.
- Comments are associated with a task using the Task ID.
- Design the model so a task can contain zero or more comments.
- Preserve compatibility with existing JSON task data where possible.
- Update the JSON storage logic so comments are loaded and saved correctly.
- Do not modify API endpoints.
- Do not modify the UI.
- Do not write any tests yet.

Files to update:
- models.py
- storage.py

Constraints:
- Keep the implementation simple.
- Follow the existing coding style.
- Do not introduce new frameworks or dependencies.
- Keep changes as small as possible.

Output:
1. Explain the proposed changes.
2. Show only the modified code.
3. Explain how to verify the changes before moving to the next step.

## AI Response

Proposed changes
The data model and storage layer now support task comments without changing the API or UI.

Added a small comment model and attached a comments list to each task response so a task can hold zero or more comments.
Kept the change backward-friendly by allowing older task payloads to load even if they do not include comments.
Added storage helpers for:
adding a comment to a task,
reading comments for a task,
deleting a comment by its ID.

## Prompt 3 Update the API (main.py)

I have already updated the data model and storage layer to support task comments.

Now update only the API layer.

Requirements:
- Create REST APIs for task comments.
- Support:
  - List comments for a task.
  - Add a comment to a task.
  - Delete a comment from a task.
- Return 404 if the task does not exist.
- Return 404 if the requested comment does not exist.
- Reject blank or whitespace-only comments with HTTP 422.
- Reuse the existing storage layer.
- Keep the API consistent with the existing FastAPI coding style.

File to update:
- main.py

Constraints:
- Do not modify models.py.
- Do not modify storage.py.
- Do not modify the frontend.
- Keep changes localized.
- Do not introduce authentication, pagination, or unrelated features.

Output:
1. Explain the API design.
2. Show only the modified code.
3. Explain how to verify the endpoints using Swagger UI or curl.

---

## AI Response

API design
The comment API is implemented as task-scoped routes under the existing task resource, which keeps it consistent with the current FastAPI style:

GET /tasks/{task_id}/comments

Lists all comments for an existing task.
Returns 404 if the task does not exist.
POST /tasks/{task_id}/comments

Adds a comment to an existing task.
Rejects blank or whitespace-only comments with 422 via the request model validation.
Returns 404 if the task does not exist.
DELETE /tasks/{task_id}/comments/{comment_id}

Deletes a specific comment from an existing task.
Returns 404 if the task does not exist or if the comment does not exist.
This reuses the existing storage layer and keeps the change localized to the API module.

---
### Prompt 4 Update the UI (index.html)

The backend APIs for task comments are complete.

Now update only the frontend.

Requirements:
- Update index.html to support task comments.
- Display comments when viewing or editing a task.
- Allow users to:
  - View existing comments.
  - Add a new comment.
  - Delete a comment.
- Display a comment count on each task card if practical.
- Refresh the comments section after adding or deleting a comment.
- Show validation errors returned by the backend.
- Keep the existing board layout unchanged.
- Do not redesign the application.

File to update:
- index.html

Constraints:
- Do not modify backend code.
- Reuse the existing JavaScript style.
- Keep UI changes minimal.
- Keep the implementation consistent with the existing application.

Output:
1. Explain the UI changes.
2. Show only the modified HTML/JavaScript.
3. Explain how to manually verify the feature in the browser.

## Prompt 5 Add regression tests

The Task Comments feature has been implemented.

Now update only the test suite.

Requirements:
Add focused regression tests for:

- Successfully listing comments for a task.
- Successfully adding a comment.
- Successfully deleting a comment.
- Rejecting blank or whitespace-only comments (HTTP 422).
- Returning HTTP 404 when the task does not exist.
- Returning HTTP 404 when the requested comment does not exist.

File to update:
- test_tasks.py

Constraints:
- Keep the tests focused on task comments only.
- Reuse existing fixtures and helper functions where possible.
- Follow the existing test style.
- Do not modify application code.
- Do not add unrelated tests.

Output:
1. Explain the test strategy.
2. Show only the new or modified tests.
3. Explain how to run only these tests before executing the full test suite.
