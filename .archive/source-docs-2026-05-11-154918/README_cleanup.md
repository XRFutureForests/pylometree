# Source Docs Archive — Rollback Instructions

**Created:** 2026-05-11-154918
**Pipeline:** ln-100-documents-pipeline

## What was archived

| File | Reason |
|------|--------|
| README.md | Non-canonical root doc — content migrated to docs/project/ |
| CONTRIBUTING.md | Non-canonical — principles migrated to docs/principles.md |
| docs/architecture.md | Non-canonical — migrated to docs/project/architecture.md |
| docs/README.md | Non-canonical nav index — replaced by canonical docs/README.md |
| WORK_PLAN.md | Internal roadmap — not migrated (internal only) |
| docs/internal-phases-roadmap.md | Internal roadmap — not migrated (internal only) |

## Rollback

To restore originals:

```powershell
Copy-Item ".archive\source-docs-2026-05-11-154918\original\README.md" "README.md" -Force
Copy-Item ".archive\source-docs-2026-05-11-154918\original\CONTRIBUTING.md" "CONTRIBUTING.md" -Force
Copy-Item ".archive\source-docs-2026-05-11-154918\original\architecture.md" "docs\architecture.md" -Force
Copy-Item ".archive\source-docs-2026-05-11-154918\original\docs_README.md" "docs\README.md" -Force
```

Note: WORK_PLAN.md and docs/internal-phases-roadmap.md were NOT deleted (internal documents preserved).
