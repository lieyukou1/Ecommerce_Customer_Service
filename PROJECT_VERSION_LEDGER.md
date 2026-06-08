# Project Version Ledger

## Purpose

This file is the human-readable index for major project milestones, experiment checkpoints, and rollback anchors.

Use it together with git branches and git tags:

- `branch`: carries ongoing work
- `tag`: immutable rollback anchor
- `this file`: explains what each anchor actually means

Do not rollback by guessing commit hashes from memory.

## Versioning Rules

### 1. Project Milestones

Use milestone tags for meaningful repo-wide checkpoints:

- format: `milestone/v<major>.<minor>.<patch>-<short-name>`
- example: `milestone/v0.1.0-baseline-pre-semantic-refactor`

Suggested meaning:

- `major`: architecture phase change
- `minor`: meaningful functional milestone inside that phase
- `patch`: small but stable correction on the same milestone line

### 2. Work Branches

Use dedicated branches for risky or long-running work:

- `feature/<topic>`
- `refactor/<topic>`
- `experiment/<topic>`
- `hotfix/<topic>`

Examples:

- `feature/semantic-decision-refactor`
- `experiment/turnplan-semantic-supervision`

### 3. Training / Evaluation Versions

Keep model experiments on their existing round naming, but map important checkpoints back into git milestones when they change code, data contracts, or evaluation logic.

Examples:

- `round_01` ... `round_06`: experiment chronology
- `milestone/v0.2.0-semantic-schema-cutover`: repository checkpoint

### 4. Rollback Rule

Rollback priority:

1. rollback to a named `tag`
2. if needed, switch to a known `branch`
3. only use raw commit hashes when the tag/branch map is missing

Before any high-risk refactor:

1. commit current work
2. add a tag if the checkpoint is important
3. append one line to this ledger

## Current Milestones

| Version | Git Ref | Commit | Date | Type | Meaning | Rollback Use |
|---|---|---|---|---|---|---|
| V0.1.0 | `milestone/v0.1.0-baseline-pre-semantic-refactor` | `e775101` | 2026-06-08 | baseline | First protected repo snapshot after git setup, SSH push, and cache cleanup. This is the anchor before any semantic-decision refactor starts. | Return here if later backend / dataset / evaluation refactors become confusing or unstable. |

## Operating Notes

### What counts as a new milestone

Add a new milestone when one of these happens:

- backend routing or protocol logic changes materially
- training data schema changes materially
- evaluation contract changes materially
- a new direction replaces the previous main line
- a version is stable enough that we would realistically want to come back to it

### What does not need a milestone

These usually only need ordinary commits:

- typo fixes
- tiny docs edits
- local script cleanup
- one-off experiment notes without code or contract impact

## Quick Commands

### See all milestone tags

```powershell
git tag --list "milestone/*"
```

### See what a milestone points to

```powershell
git show --stat milestone/v0.1.0-baseline-pre-semantic-refactor
```

### Create a new working branch

```powershell
git switch -c feature/semantic-decision-refactor
```

### Rollback by inspecting a milestone

```powershell
git switch main
git log --oneline --decorate --graph --all
git show milestone/v0.1.0-baseline-pre-semantic-refactor
```

If we truly need a hard restore later, decide it explicitly at that time. Do not guess and do not rush destructive commands.
