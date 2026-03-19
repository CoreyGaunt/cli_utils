# CLI Utils — Refactor Design Decisions & Task List

---

## Part 1 — Design Decisions

### 1. SubprocessUtilities — two new methods

**Decision:** Add `run_command()` and `run_and_return()` to `SubprocessUtilities`. Remove direct `subprocess.run()` calls from all command files and route them through these methods instead.

**Reasoning:** The command files currently repeat the same boilerplate (`shell=True`, `check=True`, `cwd=Path.cwd()`) on every subprocess call. Centralising this means consistent defaults, consistent error handling, and one place to change behaviour if needed.

**Method responsibilities:**

- `run_command(cmd)` — fire-and-forget. Lets output stream to the terminal. Used for `git add`, `git commit`, `git push`, `gh pr create` etc.
- `run_and_return(cmd)` — captures and returns stdout as a stripped string. Used for `git branch --show-current`, `git rev-parse`, `git diff` etc.

**Error handling — Philosophy 2 (re-raise after logging):** Both methods catch `CalledProcessError`, print a rich-formatted error message, then re-raise. The caller decides whether to recover or let it propagate. This preserves `pr_create`'s existing draft fallback behaviour and keeps the plumbing/policy separation clean.

**Instantiation:** Add `subprocess_utils = SubprocessUtilities()` at the module level in each command file, alongside the existing `prompts = GumPrompts()` and `config_manager = ConfigManager()`.

---

### 2. HttpClient — thin HTTP wrapper

**Decision:** Create `tools/http_client.py` with a single `HttpClient` class that wraps `requests.Session`.

**Reasoning:** HTTP is a first-class Python concern. Using `subprocess` + `curl` for API calls loses structured error handling, type safety, and session management. `HttpClient` gives consistent auth, timeouts, and error formatting across all outbound HTTP — without any command file knowing `requests` exists.

**What it owns:**
- `requests.Session` setup and lifecycle
- Default headers (`Content-Type: application/json`, `Accept: application/json`)
- Caller-supplied headers and Basic Auth merged in at init
- `get(url, params)` and `post(url, payload)` methods
- Timeout enforcement (default 10 seconds)
- Catching and re-raising `HTTPError`, `ConnectionError`, and `Timeout` with rich-formatted messages

**What it does NOT own:**
- Base URLs (each API client owns its own)
- Auth credentials (passed in from `ClientConnections`)
- Response body parsing (callers call `.json()` on the returned response)

**Context manager:** `HttpClient` exposes a `close()` method. `ClientConnections` is the only class that implements `__enter__` / `__exit__` — it calls `close()` on whichever clients were actually instantiated. `HttpClient` itself does not need to be a context manager.

---

### 3. LLMClient — Anthropic API client

**Decision:** Create `tools/llm.py` with an `LLMClient` class. It receives a pre-validated `api_key` string from `ClientConnections` and builds its own `HttpClient` instance.

**What it owns:**
- Anthropic base URL and model name as class-level constants
- Building the prompt payload for each operation
- Parsing the response JSON into usable Python types
- `suggest_commit(diff, commit_types) -> tuple[str, str]` — returns `(type, message)`
- `suggest_pr_body(branch_name, diff_stat, diff_patch, template) -> str`

**Prompting decisions:**
- `suggest_commit` asks for JSON output (`{"type": "feat", "message": "..."}`) so the response is reliably parseable. Wrap `json.loads()` in a try/except and return empty strings if parsing fails — the command file handles the graceful fallback.
- `suggest_pr_body` passes the PR template and asks the model to return filled markdown only, no preamble.
- Truncate diffs to ~6000 characters before sending — full diffs can be enormous and most of the signal is in the first portion.

**Does not read env vars** — credentials come in as constructor arguments from `ClientConnections`.

---

### 4. JiraClient — Jira REST API client

**Decision:** Create `tools/jira_client.py` with a `JiraClient` class. Receives `base_url`, `email`, and `api_token` from `ClientConnections` and builds its own `HttpClient` with Basic Auth.

**What it owns:**
- Jira base URL construction
- JQL query building (`assignee = currentUser() AND statusCategory != Done`)
- `get_my_tickets(project_key, max_results) -> list[dict]` — each dict has `key`, `summary`, `status`
- `format_for_gum(tickets) -> str` — formats ticket list as space-separated quoted strings for `gum filter`
- `parse_key_from_selection(selection) -> tuple[str, str]` — extracts `(ticket_key, slug)` from a gum selection string

**Slug generation:** lowercase the ticket summary, strip non-alphanumeric characters, replace spaces with hyphens, truncate at 50 characters.

**Single quotes in ticket summaries** must be escaped (`'` → `'\''`) before passing to gum — unescaped quotes will break the shell command.

**Does not read env vars** — credentials come in as constructor arguments.

---

### 5. ClientConnections — service aggregator

**Decision:** Create `tools/client_connections.py` with a `ClientConnections` class that aggregates all external clients, handles credential reading, and exposes clients via lazy `@property` accessors.

**What it owns:**
- Reading all env vars (`ANTHROPIC_API_KEY`, `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`)
- Validating credentials are present — if not, print a helpful error and `sys.exit(1)`
- Lazy instantiation of `LLMClient` and `JiraClient` via `@property`
- Context manager (`__enter__` / `__exit__`) that closes only the clients that were actually instantiated

**Lazy `@property` pattern:**
```python
def __init__(self):
    self._llm = None
    self._jira = None

@property
def llm(self):
    if self._llm is None:
        # validate env var, then build
        self._llm = LLMClient(api_key=...)
    return self._llm
```

The property only runs when something accesses `clients.llm`. If a command never accesses `clients.jira`, Jira credentials are never checked and `JiraClient` is never built.

**Why `sys.exit(1)` here instead of re-raise:** Missing credentials are not recoverable — there's nothing the calling command can meaningfully do. The policy decision is "exit", and it belongs here rather than bubbling up through multiple layers.

**Context manager — why only here:** `__enter__` / `__exit__` live only on `ClientConnections` because that's the level where command files write their `with` block. `LLMClient`, `JiraClient`, and `HttpClient` only need plain `close()` methods. `ClientConnections.__exit__` checks `if self._llm` and `if self._jira` before calling close — lazy properties mean either could still be `None`.

---

### 6. Instantiation in command files

**Decision:** `ClientConnections` is instantiated **inside the command function**, not at module level — and only inside the branch that actually needs it.

**Reasoning:** Module-level instantiation runs at import time, before the user has run anything. Instantiating inside the function, inside a guard, means credentials are only checked when the code path that needs them is actually exercised.

```python
# commit.py
@click.command("commit")
@click.option("--no-ai", is_flag=True)
def commit(no_ai):
    ...
    if not no_ai:
        with ClientConnections() as clients:
            suggested_type, suggested_message = clients.llm.suggest_commit(diff)
```

If `--no-ai` is passed, `ClientConnections` is never created, `ANTHROPIC_API_KEY` is never checked, nothing.

**Passing clients to helpers:** Since `ClientConnections` is instantiated inside the function, helpers that need a client should receive it as a parameter rather than building their own. Example: `_generate_type_and_message(llm_client=clients.llm)`.

---

### 7. branch_new.py — gum refactor + Jira

**Decision:** Complete the half-finished gum refactor (remove remaining `beaupy` usage) at the same time as adding Jira integration.

**Final branch name format:**
- With ticket: `feature/DATA-123-my-ticket-slug`
- Without ticket: `feature/my-branch-name`

**Graceful fallback:** If Jira is not configured or returns no tickets, the command falls back to a manual `gum_input` prompt. `--no-jira` flag skips Jira entirely.

---

### 8. config.yml additions

Add two new sections:

```yaml
jira:
  max_results: 30

ai:
  disabled: false
  max_diff_chars: 6000
```

---

### 9. requirements.txt

Add `requests` — the only new dependency introduced by this refactor.

---

## Part 2 — Task List

Work through these in order. Each phase is self-contained and testable before moving on.

---

### Phase 1 — SubprocessUtilities

- [ ] Add `run_command(cmd: str)` to `SubprocessUtilities`
  - Runs with `shell=True`, `check=True`, `cwd=Path.cwd()`
  - Streams output to terminal (no `stdout=PIPE`)
  - Catches `CalledProcessError`, prints rich error, re-raises
- [ ] Add `run_and_return(cmd: str) -> str` to `SubprocessUtilities`
  - Same defaults but captures stdout
  - Returns `result.stdout.strip()`
  - Catches `CalledProcessError`, prints rich error, re-raises
- [ ] Update `commit.py` — replace all `subprocess.run()` calls with `subprocess_utils.run_command()` or `subprocess_utils.run_and_return()`
  - Add `subprocess_utils = SubprocessUtilities()` at module level
  - Remove `import subprocess` if no longer needed directly
- [ ] Update `pr_create.py` — same as above
  - Preserve the draft fallback `try/except` — this is a case where the command handles the re-raised exception itself
- [ ] Update `branch_new.py` — same as above
- [ ] Smoke test each command manually to confirm behaviour is unchanged

---

### Phase 2 — HttpClient

- [ ] Add `requests` to `requirements.txt`
- [ ] Create `tools/http_client.py`
  - `__init__(self, headers: dict = None, auth: tuple = None, timeout: int = 10)`
    - Build `requests.Session()`
    - Merge caller headers into defaults
    - Set `self.session.auth` if auth tuple provided
  - `get(self, url: str, params: dict = None) -> requests.Response`
    - Calls `session.get()` with timeout
    - Calls `response.raise_for_status()`
    - Catches `HTTPError`, `ConnectionError`, `Timeout` — rich print, re-raise
  - `post(self, url: str, payload: dict = None) -> requests.Response`
    - Calls `session.post(url, json=payload)` — use `json=` not `data=`
    - Same error handling as `get()`
  - `close(self)` — calls `self.session.close()`
- [ ] Export `HttpClient` from `tools/__init__.py`
- [ ] Test instantiation manually: `http = HttpClient(); print(http.session.headers)`

---

### Phase 3 — LLMClient

- [ ] Create `tools/llm.py`
  - Define `BASE_URL` and `MODEL` as class constants
  - `__init__(self, api_key: str)` — builds `HttpClient` with Anthropic headers
  - `suggest_commit(self, diff: str, commit_types: list) -> tuple[str, str]`
    - Builds JSON payload with prompt
    - Calls `self.http.post()`
    - Parses `response.json()["content"][0]["text"]`
    - Wraps `json.loads()` in try/except — returns `("", "")` on parse failure
  - `suggest_pr_body(self, branch_name, diff_stat, diff_patch, template) -> str`
    - Same pattern, returns filled markdown string
  - `_build_commit_prompt(self, diff, commit_types) -> str` — private helper
  - `_build_pr_prompt(self, ...) -> str` — private helper
  - `close(self)` — calls `self.http.close()`
- [ ] Export `LLMClient` from `tools/__init__.py`

---

### Phase 4 — JiraClient

- [ ] Create `tools/jira_client.py`
  - `__init__(self, base_url: str, email: str, api_token: str)`
    - Stores `self.base_url = base_url.rstrip("/")`
    - Builds `HttpClient(auth=(email, api_token))`
  - `get_my_tickets(self, project_key: str = "", max_results: int = 30) -> list[dict]`
    - Builds JQL string
    - Calls `self.http.get(url, params={"jql": ..., "maxResults": ..., "fields": ...})`
    - Note: pass `params=` dict to `http.get()` — requests handles URL encoding automatically
    - Returns list of dicts with `key`, `summary`, `status`
  - `format_for_gum(self, tickets: list[dict]) -> str`
    - Formats as `'KEY: Summary [Status]' 'KEY: Summary [Status]'`
    - Escapes single quotes in summaries (`'` → `'\''`)
  - `parse_key_from_selection(selection: str) -> tuple[str, str]` — static or class method
    - Extracts ticket key with regex
    - Generates slug from summary
  - `close(self)` — calls `self.http.close()`
- [ ] Export `JiraClient` from `tools/__init__.py`

---

### Phase 5 — ClientConnections

- [ ] Create `tools/client_connections.py`
  - `__init__(self)` — sets `self._llm = None`, `self._jira = None`
  - `@property llm` — reads `ANTHROPIC_API_KEY`, validates, builds and caches `LLMClient`
  - `@property jira` — reads `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, validates all three (collect all missing vars before exiting), builds and caches `JiraClient`
  - `__enter__(self)` — returns `self`
  - `__exit__(self, exc_type, exc_val, exc_tb)` — calls `close()` on `self._llm` and `self._jira` if not None, returns `False`
- [ ] Export `ClientConnections` from `tools/__init__.py`

---

### Phase 6 — Update commit.py

- [ ] Add `--no-ai` flag to `@click.command`
- [ ] In the "commit all" branch: call `subprocess_utils.run_and_return("git diff --cached")` to get the diff before staging
- [ ] In the "subset of files" branch: move `git add` call to happen **before** `_generate_type_and_message()` so staged diff is available
- [ ] Update `_generate_type_and_message()` to accept an optional `llm_client` parameter
  - If `llm_client` provided: call `llm_client.suggest_commit(diff, commit_types)`
  - Print suggestion to console before gum prompts
  - Float suggested type to top of gum filter list
  - Pre-fill gum input with suggested message
  - If no suggestion (parse failed or empty diff): fall back to normal prompts silently
- [ ] Wrap `ClientConnections` usage in `with` block inside the `if not no_ai` guard

---

### Phase 7 — Update pr_create.py

- [ ] Add `--no-ai` flag to `@click.command`
- [ ] After parsing branch name and loading template: add `if not no_ai` block
  - Get diff: `subprocess_utils.run_and_return("git diff main...HEAD --stat")` and full patch
  - Open `with ClientConnections() as clients:`
  - Call `clients.llm.suggest_pr_body(branch_name, diff_stat, diff_patch, template)`
  - Use the result as the `templated_text` passed to `gum_write` instead of raw template
- [ ] Keep `with ClientConnections()` block closed **before** `gum_write` opens — the LLM call should complete and the connection close before the user enters the editor

---

### Phase 8 — Rewrite branch_new.py

- [ ] Remove all `beaupy` imports and usage
- [ ] Add `subprocess_utils = SubprocessUtilities()` at module level
- [ ] Add `--no-jira` flag to `@click.command`
- [ ] Rewrite using `GumPrompts` and `ConfigManager` throughout:
  - `gum_filter` for branch prefix selection (from `config["branches"]["branch-prefixes"]`)
  - `gum_confirm` for "Link a Jira ticket?"
  - `gum_filter` for ticket selection
  - `gum_input` for branch name (pre-filled with slug if ticket was selected)
- [ ] Add Jira flow inside `if not no_jira` guard:
  - Instantiate `ClientConnections` inside the guard
  - Call `clients.jira.get_my_tickets(project_key=config["general"]["team-tag"])`
  - If no tickets returned: print message, fall through to manual name entry
  - Parse selection to get `(ticket_ref, slug)`
- [ ] Assemble branch name: `f"{branch_type}/{ticket_ref}-{slug}"` or `f"{branch_type}/{slug}"`
- [ ] Use `subprocess_utils.run_and_return()` for `git rev-parse --abbrev-ref origin/HEAD`
- [ ] Use `subprocess_utils.run_command()` for checkout, pull, create, push

---

### Phase 9 — Config and cleanup

- [ ] Add `jira` and `ai` sections to `assets/config.yml`
- [ ] Remove `beaupy` from `requirements.txt` if no longer used anywhere
- [ ] Add `requests` to `requirements.txt`
- [ ] Verify `tools/__init__.py` exports all new classes
- [ ] Run `pip install -e .` to pick up dependency changes
- [ ] End-to-end test all three commands:
  - `cliutils commit --no-ai` — confirm existing behaviour unchanged
  - `cliutils commit` — confirm AI suggestion appears and is pre-filled
  - `cliutils pr-create --no-ai` — confirm existing behaviour unchanged
  - `cliutils pr-create` — confirm AI fills PR body before editor opens
  - `cliutils branch-new --no-jira` — confirm gum refactor works, branch created correctly
  - `cliutils branch-new` — confirm Jira tickets appear, branch name assembled correctly

---

## Reference — Final file structure

```
src/cliutils/
├── __init__.py
├── __main__.py
├── cliutils_config.py
├── assets/
│   ├── config.yml                  # updated — jira + ai sections added
│   ├── data/
│   ├── shell/
│   ├── templates/
│   └── themes/
├── commands/
│   ├── __init__.py
│   ├── branch_new.py               # rewritten — beaupy removed, gum + jira added
│   ├── commit.py                   # updated — --no-ai, LLM suggestions
│   ├── pr_create.py                # updated — --no-ai, LLM PR body
│   └── theme_select.py             # unchanged
└── tools/
    ├── __init__.py                 # updated — new exports
    ├── client_connections.py       # new
    ├── config_manager.py           # unchanged
    ├── gum_prompts.py              # unchanged
    ├── http_client.py              # new
    ├── jira_client.py              # new
    ├── llm.py                      # new
    ├── subprocess_utilities.py     # updated — run_command + run_and_return
    └── terminal_installer.py       # unchanged
```
