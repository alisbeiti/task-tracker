# Manual Security Check

## What I checked
I went through every field validator in `app/models.py` and the comment validator in `app/main.py` to see if any of them actually filter out SQL-ish characters (quotes, semicolons, `--`, SQL keywords, etc.).

## What I found
Nothing does. `title` and comment `text` just get `.strip()`'d and checked for blank/length — that's it. `description` and `assignee` have no validation at all. None of them touch or block special characters. So a payload like `'; DROP TABLE tasks; --` would pass right through as a normal string.

## Why it's not a problem right now
The app never builds a SQL query out of user input — everything's stored in a plain Python dict in `storage.py`, not a database. So there's nothing for an injection payload to actually inject into.

## Why it still matters
The validators aren't doing this by design, it's just a side effect of the storage choice. If this app ever gets a real SQL database wired in later, none of the current validation would stop SQL injection — that protection would have to be added separately (parameterized queries), not assumed to already be there.
