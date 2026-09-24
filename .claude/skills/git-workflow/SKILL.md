---
name: git-workflow
description: Branching, committing, and syncing conventions for the Tufts-SEDS/Website repo. Use when starting new work, making commits, pulling in changes from main, or when someone is about to commit directly to main.
---

# Git workflow

The `main` branch of `Tufts-SEDS/Website` is what Vercel deploys to sedstufts.org. Anything on `main` goes live.

## Start new work on a branch
```bash
git switch main
git pull
git switch -c <type>/<short-description>
```
Use these branch prefixes: `updates/` for content or page changes, `feature/` for new functionality, `fix/` for bugs. Use lowercase words joined by hyphens, e.g. `updates/remove-blog-and-add-leadership`.

Never commit directly to `main`. If you already did, see `git-fix-mistakes`.

## Commits
- Keep each commit to one logical change. Separate "Remove blog app" from "Add leadership page".
- Write the subject in the imperative, under about 60 characters, and say what changed: "Move Author model into events app", not "fix" or "updates". Add a body when the reason isn't obvious, and always for migrations.
- Before committing, review what you're including:
  ```bash
  git status
  git diff --staged
  ```
- Never commit `.env`, `db.sqlite3`, `.venv/`, `.DS_Store`, credentials, or large raw photos. `.gitignore` covers most of these, but check `git status` anyway.
- Commit migrations together with the model changes that need them.

## Keep your branch up to date
```bash
git fetch origin
git merge origin/main      # Or: git rebase origin/main (only if nobody else uses your branch)
```
Fix any conflicts (see `git-fix-mistakes`), run the checks in `django-local-dev`, then push.

## Push and open a PR
```bash
git push -u origin <branch>
```
Then follow the `github-pull-request` skill.

## Line endings
The repo is used on Windows and macOS. Keep `core.autocrlf` set to `true` on Windows and `input` on macOS/Linux. A diff that changes every line of a file you barely touched is a line-ending problem; don't commit it.
