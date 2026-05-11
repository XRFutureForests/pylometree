# Task Navigation

<!-- SCOPE: Quick navigation to active tasks in Linear -->
<!-- DOC_KIND: how-to -->
<!-- DOC_ROLE: working -->
<!-- READ_WHEN: Read when you need the current board, provider setup, or epic/story/task navigation. -->
<!-- SKIP_WHEN: Skip when you only need workflow policy or template rules. -->
<!-- PRIMARY_SOURCES: .hex-skills/environment_state.json, docs/tasks/README.md, Linear XRFF team -->
<!-- DO NOT add here: task descriptions, implementation notes, workflow rules → tasks/README.md -->

> **Last Updated**: 2026-05-11 (Hierarchical format: Status → Epic → Story → Tasks)

## Quick Navigation

- [Task Rules](./README.md)
- [Architecture](../project/architecture.md)
- [Requirements](../project/requirements.md)

## Agent Entry

| Signal | Value |
|--------|-------|
| Purpose | Gives live navigation and provider-specific board setup for active work. |
| Read When | You need current epics, stories, tasks, or provider coordinates. |
| Skip When | You only need lifecycle policy or documentation standards. |
| Canonical | No, this is a working document |
| Next Docs | [Task Rules](./README.md) |
| Primary Sources | Linear XRFF team, `docs/tasks/README.md` |

---

## Provider Configuration

**Task provider:** Linear

### Linear Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| **Team** | XRFF | Linear team name |
| **Workspace** | geosense-ufr | Linear workspace slug |
| **Workspace URL** | https://linear.app/geosense-ufr | Linear workspace |

**Quick Access:**
- [Backlog](https://linear.app/geosense-ufr/team/XRFF/backlog)
- [Active](https://linear.app/geosense-ufr/team/XRFF/active)
- [All Issues](https://linear.app/geosense-ufr/team/XRFF/all)

### Common Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| **Next Epic Number** | 1 | Next available Epic number |

---

## Epic Story Counters

| Epic | Last Story | Next Story | Last Task | Next Task |
|------|------------|------------|-----------|-----------|
| Epic 0 | - | US001 | - | T001 |

> Story numbering: US001+ per Epic. Task numbering: T001+ per Story.

---

## Work in Progress

**Format:** Status → Epic → Story → Tasks hierarchy.

### Backlog

**Epic 0: Common Tasks**

  - _(No active stories. Run ln-210-epic-coordinator to decompose scope.)_

### Todo

_(empty)_

### In Progress

_(empty)_

### To Review

_(empty)_

### To Rework

_(empty)_

### Done

_(empty)_

---

## Workflow Reference

| Status | Purpose |
|--------|---------|
| **Backlog** | New items requiring estimation and approval |
| **Postponed** | Deferred for future iterations |
| **Todo** | Approved, ready for development |
| **In Progress** | Active development |
| **To Review** | Awaiting review |
| **To Rework** | Needs fixes |
| **Done** | Completed and approved |

---

## Maintenance

**Update Triggers:**
- Epic, story, or task navigation changes
- Linear team coordinates change
- Board numbering changes

**Verification:**
- [ ] Linear workspace URL resolves (https://linear.app/geosense-ufr)
- [ ] XRFF team links work
- [ ] Next counters reflect current board state

**Last Updated:** 2026-05-11

