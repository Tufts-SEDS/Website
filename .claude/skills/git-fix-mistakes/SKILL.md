---
name: git-fix-mistakes
description: Recover from common git mistakes in the Tufts SEDS repo, such as committing to main, merge conflicts, a bad commit, a committed secret, or lost work. Use when someone says git is "broken", something went wrong, or they want to undo something.
---

# Fixing git mistakes

First, find out where things stand. Don't run anything destructive yet:
```bash
git status
git log --oneline -10
git reflog -10           # Every recent position of HEAD. Lost commits are usually here.
```
Before running `reset --hard`, `push --force`, or `clean`, say exactly what will be lost and get the user's confirmation. Prefer the options below that keep history.

## Committed to main but haven't pushed
```bash
git switch -c <new-branch>          # The branch keeps your commits
git switch main
git reset --hard origin/main        # Put local main back to match GitHub
```

## Pushed a bad commit to main
Don't force-push `main`. Undo it with a new commit, and do that on a branch through a PR:
```bash
git revert <sha>
```

## Undo the last local commit but keep the changes
`git reset --soft HEAD~1`

## Throw away uncommitted changes to one file
`git restore <file>`. This can't be undone, so confirm first.

## Merge conflicts
1. Run `git status` to list the conflicted files.
2. In each file, choose between the `<<<<<<<`, `=======`, `>>>>>>>` sections, or combine them. Remove all markers.
3. For migration conflicts (two new migrations with the same number), keep both files and run `python manage.py makemigrations --merge`.
4. Run `git add <files>`, then `git commit` (for a merge) or `git rebase --continue` (for a rebase).
5. Run the checks in `django-local-dev` before pushing.

To give up: `git merge --abort` / `git rebase --abort`.

## Committed a secret (.env, database password, API key)
1. Treat the secret as leaked, even if you removed it in a later commit. Rotate it right away (change the Postgres password in Railway, generate a new `SECRET_KEY`).
2. Remove the file from tracking: `git rm --cached .env`, and make sure it's in `.gitignore`.
3. Rewriting history is a last resort and needs everyone to re-clone. Ask a repo admin.

## "Your branch has diverged"
Run `git pull --rebase` for your own branch. If others share the branch, use `git pull` (merge) instead.

## Lost work
Find the commit in `git reflog`, then run `git switch -c rescue <sha>`.
