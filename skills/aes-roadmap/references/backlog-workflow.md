# Evidence-linked research backlog workflow

Portable adaptation of the author's research-backlog-tracker. Configure the repository's research root, single status ledger, active-spec root, accepted-spec root and history root from existing project conventions. Do not create a parallel authority. Research is candidate input, not approved requirements. Current accepted specifications, implementation and tests determine actual behavior; the ledger records route and evidence only.

## Stable identities and state gates

Keep a stable `BL-xxx` ID when a title or file moves. Never reuse a retired ID. One canonical item may have multiple source anchors. Exclude the ledger itself when discovering research sources.

| State | Minimum evidence |
|---|---|
| candidate | Source and source anchor |
| evaluated | Repository-context value, authority, freshness, failure semantics, risks and non-goals reviewed |
| ready_for_proposal | Agreed scope, owner, priority and minimal acceptance |
| spec_draft | Actual active proposal/design/tasks or spec delta, evidence baseline where applicable |
| implementing | Linked implementation/test entry, outstanding tasks and blockers |
| verified | Actual verification/run results plus remaining acceptance/history handoff |
| accepted | Accepted specification, implementation, verification and history handoff agree |
| deferred | Reason, revisit trigger and review date |
| rejected | Decision owner/date, reason and alternative where relevant |
| duplicate | Canonical BL ID and deduplication reason |

Normal route: candidate → evaluated → ready_for_proposal → spec_draft → implementing → verified → accepted. Do not skip evaluation before a proposal or jump directly from implementation to acceptance.

Candidate/evaluated may move to deferred/rejected/duplicate with reasons. Deferred may return to ready_for_proposal when its recorded trigger is satisfied. Pre-implementation duplicate branches retain the canonical identity. Changed or withdrawn implementations require an explicit superseding/reopened record; never erase old transition history. Blocker is a separate field, not a replacement for evidence stage.

## Maintenance

1. Enumerate actual research documents and read their source anchors. Inspect existing active and accepted specs semantically; do not infer coverage from a title or directory.
2. Allocate an unused stable ID, or link another source to an existing canonical item. Keep long-term capability themes as candidate themes until evaluation warrants decomposition.
3. Update status, priority, owner, source anchor, spec/implementation/test references, next action, blocker and last-reviewed date. Mechanical synchronization alone cannot advance status.
4. Append a transition record including initial registration, date, previous/new state, reason and evidence. Correct errors with another record, not history rewrites.
5. Meaningful architecture, permission, failure or reusable verification findings need a history handoff. Mechanical link/date edits may record “history not needed” with a reason. History skill installation is optional; follow the project's existing history process when absent.

Before promotion determine the problem, source evidence, scope/non-goals, conflicts with active changes, deterministic authority retained, minimal acceptance, fail-closed/recovery behavior, owner, dependencies and review date. Only record spec_draft after the proposal actually exists. Read project spec instructions; never backfill invented baseline evidence.

## Audit and verification

Each research source should be linked from the ledger; each item should link the correct research/spec/implementation/test/history layer. Accepted must point to an accepted specification, not merely an active proposal. Check unexplained state jumps, deferred triggers/dates, duplicate canonical IDs, stale conclusions after source changes and incomplete handoff.

Minimum fields: id, title, source, source_anchor, priority, status, spec, implementation_and_tests, owner, next_action, blocker, last_reviewed, evidence. Use explicit unknown values, repository-relative links and dates. Link long evidence rather than duplicating it into every row.

Run the repository's existing relevant validators when available and authorized. No fixed machine-specific skill validator, package installation or account connector is required. Verify links and state records locally; disclose missing validators. Link validity does not prove implementation or acceptance.
