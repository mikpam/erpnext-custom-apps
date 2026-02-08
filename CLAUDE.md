# CLAUDE.md - AIterated ERPNext Custom Apps

## Frappe Compatibility Rules (CRITICAL)
- ONLY use public Frappe API: frappe.get_doc(), frappe.get_list(),
  frappe.get_value(), @frappe.whitelist(), frappe.throw()
- NEVER monkey-patch or override internal Frappe classes
- NEVER import from frappe.core internals — use hooks.py for all overrides
- Use hooks.py scheduler_events for background jobs, not custom cron
- DocType definitions must use standard field types only
- All API endpoints must use @frappe.whitelist() decorator
- Use frappe.enqueue() for async tasks, not threading

## Testing Requirements
- Every new DocType must have test_*.py with CRUD tests
- Every API endpoint must have integration tests
- Tests must pass against current Frappe stable release
- Run: bench --site test_site run-tests --app your_app

## Frontend Rules
- Use Frappe's built-in JS API (cur_frm, frappe.call, list_settings)
- No external frontend frameworks (React/Vue) inside Frappe pages
- Custom pages use frappe.pages pattern
- Form customizations go in {doctype}.js client scripts

## Environment
- Dev: Railway (Docker) — erpnext-production-e56b.up.railway.app
- Production: Frappe Cloud
- API keys: os.environ with fallback to site_config.json
- External service calls must have try/except with frappe.log_error()
- Railway project: erpnext-demo (ID: 4cb0a514-c7ed-4bf6-ae9f-143c198f4774)
- ERPNext v15 on Python 3.11.6 (v16 requires Python 3.12+)
- Volume mount: /home/frappe/bench/sites (persists across deploys)
- Apps dir: /home/frappe/bench/apps (NOT persisted — redeploy wipes it)

## Railway Deploy Gotchas
- Setting env vars triggers a redeploy which rebuilds the container
- Only /home/frappe/bench/sites is on a persistent volume
- Custom apps, pip packages, and code changes via SSH are LOST on redeploy
- After any redeploy: must re-scaffold app, re-install pip packages, re-write files, re-migrate
- Use `kill <gunicorn PID>` to restart workers (supervisor auto-restarts)
- supervisord has no control socket configured — cannot use supervisorctl
- Windows PATH leaks into `railway ssh` commands — use shell scripts in /tmp to avoid quoting issues

## Git Conventions
- Branch from main for features
- PR required, no direct push to main
- Commit messages: conventional commits format

## Repo Structure
```
erpnext-custom-apps/
  CLAUDE.md
  .gitignore
  ai_task_log/              # Frappe app root (pip-installable)
    __init__.py
    hooks.py
    modules.txt
    pyproject.toml
    ai_task_log/            # Module directory
      __init__.py
      api.py                # @frappe.whitelist() endpoints
      doctype/
        __init__.py
        ai_task_log/        # DocType directory
          __init__.py
          ai_task_log.json  # DocType definition
          ai_task_log.py    # Controller
          ai_task_log.js    # Form client script
          ai_task_log_list.js  # List view customization
          test_ai_task_log.py  # Tests
```

## Adding a New Custom App
1. Create app dir under repo root following the same nested structure
2. Add hooks.py, modules.txt, pyproject.toml, __init__.py at app root
3. Add module dir with doctype/ subdirectories
4. Deploy: SSH into Railway, scaffold with `bench new-app`, copy files over, `bench install-app`, `bench migrate`
