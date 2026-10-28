# Agent Engineering Suite

[简体中文](README.zh-CN.md)

A practical, evidence-driven engineering toolkit: clarify decisions, execute specifications, preserve history, deepen architecture, review changes, maintain docs, assess maturity and track a roadmap.

**One source, two forms. Install one module or the complete suite as standalone Skills or Codex plugins.** Modules do not require the workflow router or private services.

## Modules

| Module | Actual delivery |
|---|---|
| spec-flow | Original structural evidence CLI, schema/tests and lifecycle skill |
| history | Original decision-history CLI, protected manual notes and reusable views |
| architecture | Owner/deletion, contract, lifecycle and hotspot audits; report guidance |
| grilling | Consequential design-tree decisions and delivery staging |
| code-review | Independent standards and originating-spec review axes |
| docs-maintenance | Canonical-source sync and authorization-aware cleanup planning |
| maturity | Generic rubric plus optional generic 24/28/16 calculators; no private scores |
| roadmap | Independent evidence-linked ownership, dependency and status tracking |
| workflow | Optional routing plus acceptance/release/handoff templates |

## Build and inspect

Use Node 26.11.1; no dependency installation is required.

```sh
node scripts/build.mjs
node scripts/validate.mjs
node --test tests/*.test.mjs
```

Generated output is under `dist/`. Do not edit it; source skills live under `skills/`. See [installation](docs/installation.md), [compatibility and validation limits](docs/compatibility.md), and [provenance](docs/provenance.md).

No automatic publishing, paid evaluation, destructive cleanup, account access or permission expansion. Structural evidence and score arithmetic do not prove product quality. Full private-plugin parity is not claimed; omitted private integrations and baselines are documented.
