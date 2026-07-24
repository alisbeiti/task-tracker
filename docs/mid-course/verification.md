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

Input:
Blank comment

Expected:
HTTP 422

Actual:
HTTP 422

Result:
PASS

---

### Break Test 2

Input:
Invalid priority value

Expected:
HTTP 422

Actual:
HTTP 422

Result:
PASS