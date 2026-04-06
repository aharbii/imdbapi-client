# Session Start — imdbapi-client

Run these checks in parallel, then give a prioritised summary. Do not read any source files.

```bash
gh issue list --repo aharbii/imdbapi-client --state open --limit 20 \
  --json number,title,labels,assignees
```

```bash
gh pr list --repo aharbii/imdbapi-client --state open \
  --json number,title,state,labels,headRefName
```

```bash
gh issue list --repo aharbii/movie-finder-chain --state open --limit 5 \
  --json number,title,labels
```

```bash
git status && git log --oneline -5
```

Then summarise:

- **Open issues in this repo** — number, title, severity label
- **Open PRs** — which are ready to review, which are blocked
- **Chain issues that touch imdbapi** — any cross-cutting dependencies
- **Current branch and uncommitted changes**
- **Recommended next action** — one specific thing

Keep the summary under 20 lines. Do not propose solutions yet.
