# Task Tracking System

<!-- DOC_KIND: index -->
<!-- DOC_ROLE: canonical -->
<!-- READ_WHEN: Read when you need the task system workflow, state transitions, and provider rules. -->
<!-- SKIP_WHEN: Skip when you only need the live board or a specific task artifact. -->
<!-- PRIMARY_SOURCES: .hex-skills/environment_state.json, docs/tasks/kanban_board.md -->
<!-- SCOPE: Task tracking system workflow and rules ONLY. Contains task lifecycle, naming conventions, and integration rules. -->
<!-- DO NOT add here: actual task details → task files, kanban status → kanban_board.md, implementation guides → guides/ -->

## Quick Navigation

- [Kanban Board](kanban_board.md)
- [Architecture](../project/architecture.md)
- [Requirements](../project/requirements.md)

## Agent Entry

| Signal | Value |
|--------|-------|
| Purpose | Defines task workflow, provider rules, status meanings, and task-document conventions. |
| Read When | You need workflow rules, provider behavior, or task lifecycle guidance. |
| Skip When | You only need the current active items. |
| Canonical | Yes |
| Next Docs | [Kanban Board](kanban_board.md), [Architecture](../project/architecture.md) |
| Primary Sources | `.hex-skills/environment_state.json`, `docs/tasks/kanban_board.md` |

---

## Overview

This folder contains the project's task management system, organizing all development work into trackable units with clear status progression. Task provider: **Linear** (workspace: `geosense-ufr`, team: `XRFF`).

### Folder Structure

```text
docs/tasks/
├── README.md           # This file — task tracking workflow and rules
└── kanban_board.md     # Live navigation to active tasks
```

All task tracking (Epics, User Stories, Tasks) uses the Linear MCP provider (`mcp__linear__*`). Linear is the single source of truth.

---

## Core Concepts

### Task Lifecycle

**Workflow:**

```text
Backlog/Postponed → Todo → In Progress → To Review → Done
                                              ↓
                                         To Rework → (back to In Progress)
```

**Statuses:**

| Status | Meaning |
|--------|---------|
| Backlog | New tasks requiring estimation and approval |
| Postponed | Deferred tasks for future iterations |
| Todo | Approved tasks ready for development |
| In Progress | Currently being developed |
| To Review | Awaiting code review and validation |
| To Rework | Needs fixes after review |
| Done | Completed, reviewed, tested, approved |

**Manual Statuses** (not in workflow): Canceled, Duplicate

### Epic Structure

| Level | Linear Entity | Description |
|-------|--------------|-------------|
| Epic | Project | Scope grouping (e.g., H-D model improvements, yield table expansion) |
| User Story | Issue `label: user-story` | "As a… I want… So that…" + Given-When-Then AC |
| Task | Child issue of Story | Implementation unit, 3–5 h, with clear acceptance criteria |

### Foundation-First Execution Order

**Critical Rule**: Foundation tasks execute BEFORE consumer tasks.

| Layer | Definition | Example |
|-------|-----------|---------|
| Foundation | Core algorithms, data structures, model functions | `models/hd.py` — fit function |
| Consumer | CLI, registry integration, IO adapters | `yield_tables/cli.py` — uses fit result |

---

## Critical Rules

### Rule 1: Task Provider Integration

**CRITICAL**: Use `mcp__linear__*` methods for all task operations (team: `XRFF`, workspace: `geosense-ufr`).

**Prohibited**: Direct Linear API, GitHub CLI, file-based task tracking.

### Rule 2: Integration Rules

**Tests**: Created ONLY in the final Story task (Story Finalizer test task).

| Rule | Detail |
|------|--------|
| No separate test tasks | Implementation tasks focus on feature code only |
| No inline test creation | Test planner creates the Story Finalizer test task after quality gate |
| Documentation in-task | Docs updates included in the same implementation task, never separate |

### Rule 3: Story-Level Test Strategy

**Value-Based Testing**: Test only scenarios with Priority ≥15 (Impact × Likelihood).

Each test must pass all 6 Usefulness Criteria: Risk Priority ≥15, Confidence ROI, Behavioral, Predictive, Specific, Non-Duplicative.

### Rule 4: Context Budget Rule

`kanban_board.md` contains ONLY links and titles — no descriptions, no implementation notes.

---

## Task Workflow

### Planning Guidelines

| Dimension | Value |
|-----------|-------|
| Optimal task size | 3–5 hours |
| Too small | < 2 h → merge |
| Too large | > 8 h → split |
| Max tasks per Story | 7 (1–6 impl + 1 test task) |

### Workflow Skills

| Category | Skill | Purpose |
|----------|-------|---------|
| Planning | ln-210-epic-coordinator | Decompose scope → 3–7 Epics |
| Planning | ln-220-story-coordinator | Decompose Epic → 5–10 Stories |
| Planning | ln-300-task-coordinator | Decompose Story → 1–6 implementation tasks |
| Validation | ln-310-multi-agent-validator | Validates Stories/Tasks → Backlog → Todo |
| Execution | ln-400-story-executor | Orchestrate Story execution |
| Execution | ln-401-task-executor | Execute implementation tasks |
| Execution | ln-404-test-executor | Execute Story Finalizer test tasks |
| Execution | ln-402-task-reviewer | Review tasks (To Review → Done/Rework) |
| Quality | Story quality gate | Quality checks, regression, test planning, verdict |

---

## Project Configuration

### Quality Commands

```bash
pip install -e ".[dev]"
pytest
pytest -v --tb=short
pytest --cov=pylometree
```

### Documentation Structure

| Doc | Path | Purpose |
|-----|------|---------|
| Requirements | [../project/requirements.md](../project/requirements.md) | FR-XXX-NNN with MoSCoW |
| Architecture | [../project/architecture.md](../project/architecture.md) | C4 Model, arc42 |
| Tech Stack | [../project/tech_stack.md](../project/tech_stack.md) | Versions, rationale |
| ADRs | [../reference/adrs/](../reference/adrs/) | Architecture decisions |
| Research | [../reference/research/](../reference/research/) | Investigation notes |

### Label Taxonomy

| Kind | Labels |
|------|--------|
| Functional | `feature`, `bug`, `refactoring`, `documentation`, `testing` |
| Type | `user-story`, `implementation-task`, `test-task` |

---

## Linear Integration

### Team Coordinates

| Variable | Value |
|----------|-------|
| Workspace | `geosense-ufr` |
| Team | `XRFF` |
| Issue tracker | https://linear.app/geosense-ufr/team/XRFF/all |

### Operations Reference

**Epic (Project) Operations:**

| Operation | Method |
|-----------|--------|
| List | `mcp__linear__list_projects(team="XRFF")` |
| Get | `mcp__linear__get_project(query="Epic N")` |
| Create | `mcp__linear__save_project({name, description, team: "XRFF", state: "planned"})` |
| Update | `mcp__linear__save_project({id, state, description})` |

**Story / Task Operations:**

| Operation | Method |
|-----------|--------|
| List stories | `mcp__linear__list_issues(project=epicId, label="user-story")` |
| Create story | `mcp__linear__save_issue({title: "US{NNN}: Title", project: epicId, team: "XRFF", labels: ["user-story"], state: "Backlog"})` |
| Create task | `mcp__linear__save_issue({title: "T{NNN}: Title", parentId: storyId, team: "XRFF", labels: ["implementation-task"], state: "Backlog"})` |
| Update status | `mcp__linear__save_issue({id, state: "In Progress"})` |
| Add comment | `mcp__linear__save_comment({issueId, body})` |

---

## Maintenance

**Update Triggers:**
- When adding new workflow skills
- When changing task lifecycle statuses
- When updating Critical Rules
- When Linear team coordinates change

**Verification:**
- [ ] Linear team coordinates correct (workspace: geosense-ufr, team: XRFF)
- [ ] Workflow skills table matches available skills
- [ ] Critical Rules align with current development principles
- [ ] Quality commands match current pyproject.toml

**Last Updated:** 2026-05-11

