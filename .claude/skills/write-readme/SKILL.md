---
name: write-readme
description: Create or update README documentation so new developers can set up, run, change, and deploy the Tufts SEDS site. Use when asked to write docs, a README, onboarding instructions, or when setup/deploy steps, apps, or env vars change and the docs are now out of date.
---

# Writing READMEs for new developers

The reader is a Tufts student who may be new to Django, git, or both. They should be able to go from cloning the repo to seeing the site running, and making their first change, without asking anyone.

## 1. Collect facts from the repo. Don't rely on memory or the old README.
Check these before writing:
- Python version and dependencies: `requirements.txt` (what Vercel installs) and `sedsite.yml` (conda). If they disagree, say which one wins, or fix the drift.
- Env vars: read `tuftsseds/tuftsseds_core/settings.py` for every `os.environ` / `os.environ.get`. Document each key's name and purpose, never its value.
- Apps: `INSTALLED_APPS` and `tuftsseds/siteapps/*`. Write one line on what each app owns.
- URLs: `tuftsseds/tuftsseds_core/urls.py` and each app's `urls.py`.
- Deployment: `vercel.json`, `api/index.py`. Note any steps that aren't automated, such as production migrations.
- Existing docs: `README.md`, `merging-strat.md`, and `.claude/skills/*`. Link to them rather than repeating them.

Run every command you document, or clearly mark it as untested.

## 2. Structure of the root README.md
1. **What this is**: one paragraph and the live URL (sedstufts.org).
2. **Quick start**: numbered steps from nothing to `runserver`: prerequisites, clone, environment, `.env` (list the keys and who to ask for values), migrate, run. Put the commands in copy-pasteable code blocks, with both macOS/Linux and Windows versions where they differ (e.g. venv activation).
3. **Project layout**: a short tree of the main folders, each with a one-line purpose.
4. **Common tasks**: short recipes that link to the matching skills: add a page, change a model, upload spreadsheet data, edit CSS/JS, open a PR.
5. **Databases & safety**: SQLite vs the shared Postgres databases, what `DEBUG`/`REGULAR_DB` do, and "never run migrate against production casually".
6. **Deployment**: how merging to `main` goes live, and the steps you must do by hand.
7. **Troubleshooting**: real errors people hit, each with a fix (e.g. the SQLite `ArrayField` migration).
8. **Who to ask**: officer roles, not personal emails.

## 3. Per-app READMEs (optional)
For a complicated app, add `tuftsseds/siteapps/<app>/README.md` covering its models, where its data comes from (which Master List spreadsheet and CSV columns), its URLs/templates, and anything unusual.

## 4. Style
- Write steps in the imperative, one action per step, and describe what success looks like ("You should see ... at http://127.0.0.1:8000").
- Don't include secrets, passwords, database hosts, or personal contact details. Say who to ask instead.
- Keep it current. Remove sections about features that no longer exist, like the blog.
- When done, re-read it as a newcomer. Every command should work as written, and every path should exist (`ls` them).
