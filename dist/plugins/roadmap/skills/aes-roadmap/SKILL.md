---
name: aes-roadmap
description: Track evidence-backed roadmap items, dependencies, ownership and next acceptance steps without converting maturity scores or unchecked tasks into completion.
---

# Roadmap tracking

Read the existing roadmap before creating new items. Use stable item IDs, explicit owner and scope; merge only real duplicates while preserving their references. Record the current revision and observation time. The [item contract](references/item.json) is an example data shape, not an automatic acceptance engine.

Separate current delivery commitment from later options. Current milestones need concrete deliverables and observable acceptance; distant work may remain directional. State necessary dependencies and the independently allowed next action for blocked items. Do not manufacture work to keep a queue busy.

Use the preserved [backlog state machine](references/backlog-workflow.md): candidate → evaluated → ready_for_proposal → spec_draft → implementing → verified → accepted, with deferred/rejected/duplicate branches. Each transition needs an owner, reason and evidence reference. Accepted requires implementation, verification, accepted specification and history handoff; a commit, test count or maturity score cannot close it. Reopening preserves prior completion evidence and explains the changed scope or regression.

Use local versioned files, not a mandatory service or cross-module runtime. Read maturity results optionally and link their exact scope/version; do not make roadmap installation depend on maturity or let score changes mutate statuses. Respect current writers and existing release ownership. No implicit external issue creation, publication, paid calls or security changes.

Completion: a coherent current plan with traceable status changes, real blockers, accountable next steps and clear deferred work. Report unchanged items as unchanged, not progress.
