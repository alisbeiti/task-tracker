# Verification

## Baseline

Before implementing the features:

- Existing pytest suite passed.
- Existing board loaded correctly.

---

## Backend Tests

Feature 1

✓ Add comment

✓ Reject blank comment

✓ Delete comment

✓ Missing task returns 404

✓ Missing comment returns 404

Feature 2

✓ Search by title

✓ Search by description

✓ Combined status + priority

✓ No matching results returns []

✓ Invalid status returns HTTP 422



---

## Manual Browser Checks

### Search

- Search updates results.
- Empty search displays all tasks.

### Filters

- Multiple filters work together.
- Empty columns remain visible.

### Comments

- Comment added successfully.
- Comment count updates.
- Deleted comments disappear.

---

## Behavior Contract

### Before Refactor

All existing task CRUD functionality worked correctly.

### After Refactor

All previous functionality remained unchanged.

New functionality passed all verification tests.

---

## Break Tests

### Break Test 1

### Break Test – Filter by Status

Purpose:

Verify that the regression test detects when status filtering is broken.

Temporary change:
Modified the `list_tasks()` endpoint to ignore the `status` query parameter by passing `status=None`.

@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: None,
    priority: TaskPriority | None = None,
    search: str | None = None,
    assignee: str | None = None,
) -> list[TaskResponse]:
    return storage.get_all_tasks(status=status, priority=priority, search=search, assignee=assignee)


result:

FAILED tests/test_tasks.py::test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list - assert 422 == 200
FAILED tests/test_tasks.py::test_list_tasks_filter_by_priority_returns_only_matches - assert 422 == 200
FAILED tests/test_tasks.py::test_list_tasks_search_by_title_returns_only_matching_tasks - assert 422 == 200
FAILED tests/test_tasks.py::test_list_tasks_search_by_description_returns_only_matching_tasks - assert 422 == 200
FAILED tests/test_tasks.py::test_list_tasks_filter_by_status_returns_only_matching_tasks - assert 422 == 200
FAILED tests/test_tasks.py::test_list_tasks_filter_by_assignee_returns_only_matching_tasks - assert 422 == 200
FAILED tests/test_tasks.py::test_list_tasks_combines_multiple_filters - assert 422 == 200
FAILED tests/test_tasks.py::test_list_tasks_combines_search_with_filters - assert 422 == 200
FAILED tests/test_tasks.py::test_list_tasks_no_matches_returns_200_and_empty_list - assert 422 == 200
FAILED tests/test_tasks.py::test_list_tasks_without_query_parameters_returns_all_tasks - assert 422 == 200
10 failed

##
The original code was restored and the test passed successfully afterward.