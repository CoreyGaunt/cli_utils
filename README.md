# cli_utils

## Branch-new command (JIRA integration)

Brainstorming: take in a user's creds for JIRA for a resource. Take
user input for a ticket identifier (e.g. DATA-123), search JIRA for
that ticket using the resource, and pull a branch name from the
ticket.

Alternatively: pull a list of tickets assigned to them, then add
search and filter to generate the branch name.

---

# Action items

## Codebase restructure

### Refactor to standard Python naming and directory structure

Look at [this code here](https://github.com/Ledgebrook-insurtech/shared-python-packages/tree/main/packages/ledgebrook-data-utils) as an example.

CG Note:

    I _think_ this is mostly there. I will want to revisit it later this week (WO 2026-03-02).

### Restructure to use classes and finer-grained functions

Use a GUM class for gum-related logic and an optional Click/CLI
helper.

### Use explicit command registration in cli.py

Import from `cliutils.src.commands` instead of filesystem discovery.

### Fix theme-select themes_dir

Set `themes_dir` to `cliutils/themes/` (not `cliutils/src/themes`).

### Port find_all_files_in_directory

Port from `archive/tools/utils/tools_utils.py` into CLIUtils (or
equivalent) so theme-select works.

### Unify layout

Either put commands under `cliutils/commands/` (no `src`) or use a
single `src/cliutils/` tree; align `setup.py` and SOURCES with the
chosen layout.

### Resolve excluded-commands config

Names should match command module stems (e.g. `cmd_s3_sync`); fix or
remove if unused.

---

## Makefile and tooling (replaces ad-hoc init)

### Replace current init/setup flow with Makefile commands

e.g. `make install`, `make install-shell`.

### Update requirements and install to use uv

Use **uv** as the package manager.

---

## Shell setup automation

### Automate setup of gum_env_variables, zsh_scripts, zsh_theme_files

Via Makefile and optionally `cliutils setup-shell`.

### ~/.zprofile

Idempotently append GUM env vars and PR template snippet from
`gum_vars_zprofile.txt` (e.g. sentinel comment to avoid duplicates).

### ~/.zshrc

Idempotently append snippet from `gum_vars_zshrc.txt` with `<ROOT>`
replaced by install root (e.g. `~/.cliutils`).

### theme_picker.sh

Fix hardcoded cache path to a portable path (e.g.
`~/.cliutils/cache`); install or symlink script to a known location
under the chosen root.

### headline.zsh-theme

Install (or symlink) into `$ZSH_CUSTOM/themes/` when OMZ is present;
ensure `zsh_pallettes_dir` points at the directory containing theme
YAMLs.

### Use ~/.cliutils as single root for shell assets

Paths are predictable and `<ROOT>` is no longer manual.

---

## Pallettes / themes: single source of truth

### Roll ~/.pallettes (bash_pallettes) into cli_utils

Either move `bash_pallettes/` into repo (e.g.
`palettes/bash_pallettes/`) or add .pallettes as a git submodule (e.g.
`cli_utils/palettes`).

### Treat ANSI-format YAMLs in bash_pallettes as single source of truth

Use them for theme colors.

### Add Makefile target to convert ANSI → bold rgb + hex_

Write derived YAMLs to `cliutils/themes/` (replace/supersede
`copy_to_clis.sh`).

### Fix or retire copy_to_clis.sh

Update paths to `cliutils/themes` and
`zsh_scripts/theme_picker.sh`, or remove once Makefile does the same.

---

## Features and UX

### Update branch-new to pull from JIRA/Linear API

Pull branch name or ticket list from JIRA/Linear API.

### Make gum variables, theme installation, shell integration flexible

More user-friendly; see shell setup automation and pallettes above.

### (Stretch) Use LLM to parse file changes and generate PR body

---
