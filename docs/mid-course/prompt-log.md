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

## AI Response

The frontend now supports task comments directly in the existing task modal without changing the board layout. In index.html, I added:

a compact comments panel inside the task form for viewing existing comments
an input and action for adding a new comment
a delete button for each comment
a comment count shown on each task card footer
inline status and validation messages for comment actions
This keeps the existing board and card styling intact while making the comments workflow feel native to the app.

## Prompt 4 Update: Make the Modal Scrollable Since the Previous Update Hides the model's Footer

Update the modal (clsas=modal-card) so that it is scrollable when its content exceeds the available screen height. Keep the header and footer (including the Save Task and Cancel buttons) fixed and always visible, and make only the modal body scrollable. Ensure no content or buttons are cut off on any screen size, while preserving the existing design, layout, and functionality.

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
- tests/test_tasks.py

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


## AI Response

I updated test_tasks.py with focused regression tests for the comment endpoints only. The new cases reuse the existing client and created_task fixtures, and they cover:

successful comment listing
successful comment creation
successful comment deletion
blank/whitespace-only comment rejection with HTTP 422
HTTP 404 for a missing task
HTTP 404 for a missing comment

## running the test:
pytest -q tests/test_tasks.py -k "comment"

6 passed


------------------------------------------------------------------------------------------------

## Feature 2 - Search + combined filters

## Prompt 1 - Backend API Changes

I want to implement the "Search + Combined Filters" feature incrementally.

Update only the backend API.

Requirements:
- Extend the existing GET /tasks endpoint.
- Support optional query parameters for:
  - search (search task title and description)
  - status (ToDo, InProgress, Done)
  - priority (Low, Medium, High)
  - assignee
- Allow multiple filters to be combined in a single request.
- If no filters are provided, preserve the existing behavior and return all tasks.
- Return an empty list (HTTP 200) when no tasks match the search or filters.
- Return HTTP 422 for invalid filter values if the backend validates them.
- Keep the implementation compatible with the existing JSON-based data storage.
- Reuse the existing task retrieval logic where possible.

Files to update:
- main.py
- storage.py (only if filtering logic belongs there)

Constraints:
- Do not modify the frontend.
- Do not write tests yet.
- Do not introduce new endpoints.
- Do not introduce new dependencies or frameworks.
- Keep changes small and consistent with the existing FastAPI architecture.

Output:
1. Explain the implementation approach.
2. Show only the modified code.

## AI Response

The existing GET /tasks endpoint now accepts optional query parameters for search, status, priority, and assignee.
Filtering is applied in the shared storage retrieval path so the behavior stays consistent with the current JSON-backed task model.
The implementation preserves the existing “return all tasks” behavior when no filters are provided.
Because status and priority use the existing Pydantic enums, invalid values are handled by FastAPI with HTTP 422 automatically.
Search is case-insensitive and checks both task title and description.

## Prompt 2 – Frontend Changes

The backend now supports search and combined filters.

Update only the frontend.

Requirements:
- Add a compact search and filter bar above the task board.
- Include:
  - Search text box
  - Status filter
  - Priority filter
  - Assignee filter
- Call the existing GET /tasks endpoint with the selected query parameters.
- Allow search and filters to work together.
- Keep the existing board layout unchanged.
- Keep all task columns visible, even when no tasks match.
- Display empty states correctly when a column has no tasks.
- Display a friendly message when no tasks match the search criteria.
- Preserve the existing task board behavior.

File to update:
- index.html

Constraints:
- Do not modify backend code.
- Reuse the existing JavaScript functions where possible.
- Keep the UI simple and consistent with the existing design.
- Do not redesign the application.

Output:
1. Explain the UI changes.
2. Show only the modified HTML/CSS/JavaScript.

## AI Response

The frontend now has a compact toolbar above the task board with:

a search box
status, priority, and assignee filters
a clear button
These controls call the existing GET /tasks endpoint with combined query parameters, so search and filters work together. The existing board layout and task-card behavior remain intact, all three columns stay visible, and empty states now show friendly messages for both empty columns and no-match results.

## Prompt 3 – Regression Tests

The Search + Combined Filters feature has been implemented.

Update only the test suite.

Requirements:
Add focused regression tests for:

- Searching by task title.
- Searching by task description.
- Filtering by status.
- Filtering by priority.
- Filtering by assignee.
- Combining multiple filters (for example, status + priority).
- Combining search text with filters.
- Returning HTTP 200 with an empty list when no tasks match.
- Returning HTTP 422 for invalid filter values if backend validation is implemented.
- Verifying that GET /tasks without query parameters still returns all tasks.

File to update:
- test_tasks.py

Constraints:
- Reuse existing fixtures where possible.
- Follow the current test style.
- Keep the tests focused only on search and filtering.
- Do not modify application code.
- Do not add unrelated tests.

Output:
1. Explain the testing strategy.
2. Show only the new or modified tests.
3. Explain how to run only these tests before executing the full test suite.

## AI Response

The new regression cases in test_tasks.py are focused only on the search-and-filter behavior for GET /tasks. They cover:

title and description search
individual filtering by status, priority, and assignee
combined filters
combined search + filters
empty results returning HTTP 200 with an empty list
invalid filter values returning HTTP 422
default behavior when no query parameters are provided
I verified this subset locally with pytest, and it passed: 11 passed, 22 deselected.

## Use this command before the full suite:
pytest -q tests/test_tasks.py -k "search or filter or combines or matches or invalid_filter_value or without_query_parameters"
