---
name: github-pull-request
description: Open, describe, review, and merge pull requests for Tufts-SEDS/Website with the gh CLI. Use when work on a branch is ready to go live, when asked to write a PR description, or when reviewing someone else's PR.
---

# Pull requests

Every change reaches `main`, and so production, through a PR.

## Before opening
1. Make sure the branch is up to date with `origin/main` (see `git-workflow`).
2. Run `python manage.py check` and `python manage.py makemigrations --check --dry-run`, then load the pages you changed.
3. Review the full diff that the PR will contain:
   ```bash
   git log --oneline origin/main..HEAD
   git diff origin/main...HEAD --stat
   ```

## Open it
```bash
git push -u origin <branch>
gh pr create --base main --title "<imperative summary>" --body-file pr.md
```
Use this structure for the description:
```markdown
## What
- Bullet list of user-visible changes (pages added/removed, data changed).

## Why
One or two sentences.

## Database
- None, or: which migrations are included, what data they change or delete,
  and "Run `python manage.py migrate` against production after deploy."

## How I tested
- Commands run and pages checked. Say plainly what was not tested.
```
Call out anything destructive, such as deleted tables or data, in the Database section so the reviewer sees it before merging.

## Reviewing a PR
```bash
gh pr checkout <number>
gh pr diff <number>
```
Check for:
- Migrations that delete or rename data. Is that intended, and is it stated in the description?
- Dead links: removed URL names still used somewhere (`git grep "{% url 'app:name'"`).
- Nav changes made in only some of the `base*.html` files.
- Secrets, `.env`, or huge images in the diff.

Leave feedback with `gh pr review <number> --comment -b "..."` (or `--approve` / `--request-changes`).

## Merging
- Merge from GitHub or run `gh pr merge <number> --squash --delete-branch`. Squashing keeps `main` history readable.
- Watch the Vercel deployment, then load sedstufts.org to confirm it.
- If the PR had migrations, run them against production right away (see `django-models-migrations`).
