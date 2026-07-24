# Mini Architecture Decision Record

## Context

The two features selected for implementation are:

1. Task comments.
2. Search with combined filters.

The implementation should remain simple and consistent with the existing FastAPI architecture and JSON-based data storage.

---

## Decision

### Feature 1

Search + Combined Filters

Supported filters:
- search
- status
- priority
- assignee

Filtering occurs inside the existing service layer (GET /tasks) without introducing additional endpoints.

### Feature 2

Task comments

New endpoints **List**, **Add**, **Delete** are introduced for comment management. 

- Add comment
- List Taks including comment
- Delete comment

---

## Alternatives Suggested by AI

AI suggested:

- Full-text SQLite search
- Pagination
- Separate comment service
- Nested comment replies

---

## Rejected Decisions

These alternatives were rejected because they increased complexity and were outside the assignment scope.