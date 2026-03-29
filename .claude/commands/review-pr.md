# Review PR — imdbapi-client

**Repo:** `aharbii/imdbapi-client`

Post findings as a comment only. Do not submit a GitHub review status.
The human decides whether to merge.

---

## Step 1 — Read PR, issue, and diff

```bash
gh pr view $ARGUMENTS --repo aharbii/imdbapi-client
gh issue view [LINKED_ISSUE] --repo aharbii/imdbapi-client
gh pr diff $ARGUMENTS --repo aharbii/imdbapi-client
```

---

## Blocking findings

**IMDb client-specific patterns:**
- Adapter pattern broken (callers receive raw HTTP responses)
- Sync HTTP calls in async context
- Retry base delay makes SSE streaming unacceptably slow (current open issue #8 is 30s)
- `os.getenv()` instead of Pydantic BaseSettings

**Python standards:**
- Missing type annotations, bare `except:`, `print()`, `type: ignore` without comment
- Line > 100 chars, no tests for new logic

**PR hygiene:** AI disclosure missing, issue not linked, Conventional Commits not followed.

---

## Post as a comment

```bash
gh pr comment $ARGUMENTS --repo aharbii/imdbapi-client \
  --body "[review comment body]"
```

```
## Review — [date]
Reviewed by: [tool and model]

### Verdict
PASS — no blocking findings. Human call to merge.
— or —
BLOCKING FINDINGS — must fix before merge.

### Blocking findings
[file:line] — [issue and fix]

### Non-blocking observations
[file:line] — [observation]

### Cross-cutting gaps
[any item not handled and not noted in PR body]
```
