# Documentation Standards

<!-- SCOPE: Reference rules for generated project documentation ONLY. Defines structure, writing, and verification requirements. -->
<!-- DOC_KIND: reference -->
<!-- DOC_ROLE: canonical -->
<!-- READ_WHEN: Read when creating, updating, auditing, or validating project documentation. -->
<!-- SKIP_WHEN: Skip when you only need the project map or a specific project-domain fact. -->
<!-- PRIMARY_SOURCES: docs/documentation_standards.md, docs/principles.md -->

## Quick Navigation

| Need | Read |
|------|------|
| Project map | [README.md](README.md) |
| Principles behind the rules | [principles.md](principles.md) |
| Canonical entry point | [../AGENTS.md](../AGENTS.md) |

## Agent Entry

- Purpose: Canonical reference for documentation requirements and validation rules.
- Read when: You are creating, editing, or auditing documentation.
- Skip when: You only need a domain-specific project fact.
- Canonical: Yes.
- Read next: `principles.md` for rationale or the target doc you are editing.
- Primary sources: `docs/documentation_standards.md`, `docs/principles.md`.

## Critical Requirements

| Requirement | Why It Exists |
|-------------|---------------|
| `AGENTS.md` is the canonical machine-facing root doc | Keeps the always-loaded entry point small and stable |
| `CLAUDE.md` is a `@AGENTS.md` import stub with a `## Claude Code` delta (≤50 lines) | Claude Code expands `@AGENTS.md` at launch; the stub carries only harness-specific deltas |
| Every generated doc has the standard header contract | Enables deterministic routing and auditing |
| Every generated doc has `Quick Navigation`, `Agent Entry`, and `Maintenance` | Enables section-first reading |
| No raw placeholders outside allowlisted task setup docs | Published docs must be immediately usable |
| Prefer links and source references over embedded implementation code | Keeps docs concise and reduces drift |
| Stack references must match project stack (Python/GitLab) | No Node/GitHub examples in a Python project |

## Structural Rules

| Rule | Requirement |
|------|-------------|
| Header contract | `SCOPE`, `DOC_KIND`, `DOC_ROLE`, `READ_WHEN`, `SKIP_WHEN`, `PRIMARY_SOURCES` in first 12 lines |
| Top sections | `## Quick Navigation`, `## Agent Entry`, `## Maintenance` |
| Doc kinds | `index`, `reference`, `how-to`, `explanation`, `record` |
| Doc roles | `canonical`, `navigation`, `working`, `derived` |
| Root model | `AGENTS.md` canonical; `CLAUDE.md` is an `@AGENTS.md` import stub |
| Line budget | AGENTS.md ≤ 200 lines (target ≤ 150); CLAUDE.md ≤ 50 lines (target ≤ 20) |

## Writing Rules

| Rule | Guidance |
|------|----------|
| Map-first | Put routing and purpose before details |
| Section-first | Make top sections enough for initial triage |
| Single source of truth | One canonical document per topic; link outward |
| Token efficiency | Prefer tables, short bullets, and direct links over long prose |
| No code blocks | Root docs define navigation, not implementations — link to source instead |
| Official sources | Python docs (<https://docs.python.org>), GitLab docs, PyPI for package links |

## Placeholder Policy

| Forbidden | Allowed |
|-----------|---------|
| `{{...}}` template markers | Actual values |
| `[TBD: ...]` | Omit the claim or use a neutral fallback |
| `TODO`, `Coming soon`, `Lorem ipsum` | Concrete facts or silence |
| Leaked template metadata | Publishable content only |

## Code Fence Rules

Allowed fence languages (operational/data formats only):

| Language | Use |
|----------|-----|
| `shell` | CLI commands and invocations |
| `toml` / `yaml` / `json` | Configuration snippets |
| `text` / `plaintext` | Plain output, not code |
| `mermaid` | Architecture/flow diagrams |

Forbidden: `python`, `javascript`, `typescript`, `csharp` — link to source files instead.

## Verification Checklist

- [ ] Header contract complete (all 6 tags in first 12 lines)
- [ ] Top sections present (`Quick Navigation`, `Agent Entry`, `Maintenance`)
- [ ] Internal links resolve to existing paths
- [ ] No leaked template metadata
- [ ] No forbidden placeholders
- [ ] `Maintenance` section has update triggers and verification steps
- [ ] External links use official domains (docs.python.org, not third-party tutorials)

## Maintenance

**Update Triggers:**
- When the shared docs-quality contract changes
- When document kinds or roles change
- When the root entrypoint model changes
- When new recurring violations appear

**Verification:**
- [ ] Structural and writing rules remain accurate
- [ ] Verification checklist is actionable
- [ ] Root entrypoint rules match current AGENTS.md / CLAUDE.md

**Last Updated:** 2026-05-11
