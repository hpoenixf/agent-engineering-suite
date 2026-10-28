# Contract, lifecycle, test-governance, and recent-change audits

Run these audits within the requested scope before qualifying strong candidates. They extend, rather than replace, the three-level owner/deletion review. Use repository evidence and existing tools; no additional plugin, MCP permission, or dependency is required.

## 1. Freeze the recent-change window

By default inspect the last seven days ending at the review's recorded observation time; honor an explicitly requested window instead. Record the timezone (UTC unless specified), exact start/end timestamps, target branch, and immutable base/head commit. Distinguish uncommitted changes from committed history.

With local Git, resolve the selected revision to a SHA, inspect repository/shallow-history coverage, and enumerate its reachable commits in the window. For example, adapt these read-only commands using the recorded values:

```sh
git rev-parse --verify HEAD
git rev-parse --is-shallow-repository
git log <head-sha> --since=<start-iso> --until=<end-iso> --format='%H %cI %s' --name-status --find-renames
git log <head-sha> --since=<start-iso> --until=<end-iso> --numstat --format='%H' --find-renames
git show --format=fuller --find-renames <selected-commit> -- <selected-path>
```

Use committer timestamps for this default window and say so; author dates and branch integration dates may differ. Git history simplification, shallow clones, unavailable parents, and clock skew can limit coverage. Follow connector pagination when using remote history; resolve branch to a fixed SHA and retrieve the relevant per-commit patches. Report API limits, missing patches, truncation, and inaccessible history. Do not invent a complete ranking from partial history, and do not fetch new access or install dependencies merely to fill gaps.

Normalize renames to a logical file lineage using recorded rename pairs; do not silently count old/new paths as separate hotspots. Similarity-based detection is evidence, not certainty. State ambiguous rename/split/copy lineage.

For each plausible hotspot collect:
- distinct non-merge commits touching the logical file;
- effective added/deleted lines after identifying generated files, lockfiles, formatting-only changes, vendored output, and bulk migrations;
- repeatedly edited functions or responsibility blocks from actual patches;
- files co-changed in the same meaningful commits and which owner boundaries those changes cross;
- the change motivation from issue/spec, commit, review, or incident evidence.

Keep raw and adjusted counts distinguishable. Explain exclusion rules and retain mixed semantic changes for inspection rather than excluding a whole commit casually. Inspect merge-only resolutions separately; do not double count merge diffs and their reachable constituent commits. Squashed commits hide iteration frequency: report that limitation rather than reconstructing invented commits. Broad migration co-change and large-file churn are noise until causal links are established. Counts are prioritization aids, not architecture verdicts.

Select the strongest few hotspots for call-chain and responsibility analysis. Ask whether repeated edits reflect one coherent evolving responsibility, unrelated reasons to change, overlapping authority, an unclear lifecycle boundary, or a shared invariant that correctly belongs together. Consider splitting at a real owner boundary, merging a shallow seam into its rightful owner, or retaining the current design. Never split mechanically by lines or commit count; an intentionally cohesive module can be both large and busy.

Report window/head/timezone, history coverage, counting/noise rules, supporting commits and code anchors, owner/caller evidence, recommendation, and a specific reason not to split (or the condition under which splitting becomes worthwhile). Missing history is an explicit limitation, not a reason to substitute full test runs for architecture analysis.

## 2. Contract and promise ledger

For each serious candidate compare:

| Evidence | Record |
| --- | --- |
| Accepted spec and user intent | Required capability, acceptance stage, authorized scope, current decision owner |
| Real producer and consumer | Who creates, reads, or relies on each fact; external/dynamic consumers and remaining uncertainty |
| Code | Current implementation and actual reachable owner, not automatic normative truth |
| Tests | Invariant asserted, seam, fixture authority, and whether this is future authoring or accepted regression |
| Runtime evidence | Revision, environment, process boundary, actual observation, and claim it can support |

Use current accepted decisions to distinguish a defect from a deliberately staged future capability. Do not automatically privilege code, historical docs, archived specs, checked boxes, or locally green tests. An archived/checked item or partial test pass is not fresh whole-system acceptance. When evidence conflicts, state the competing claims, what remains unresolved, and which user/spec/domain/security owner has authority to reconcile them; do not silently weaken the contract.

Classify each promise as retained, narrowed/removed with authorization, staged, or unverified. An absent consumer after a bounded search is not proof of global absence. Unknown evidence means unverified, not worthless. Retire historical promises and compatibility only with producer/consumer and deletion-test evidence; names, age, modification time, and a tidy diff are insufficient.

Explicitly preserve permissions, scope and run isolation, original receipt identity, charging/accounting semantics, idempotency, recovery, and unknown-effect handling where applicable. A new owner must inherit their original invariants; never turn unknown effects into assumed success/failure or re-dispatch merely for cleaner architecture. A historical compatibility promise is not equivalent to one of these protected boundaries.

## 3. Lifecycle and responsibility audit

Trace construction, configuration, prepare, dispatch, settlement, retry/replay, and teardown for affected paths. Look for undocumented required order such as calling `configure!` before use, mutable half-initialized objects, repeated setup, and callers coordinating state that should belong to one owner. Determine who validates readiness and owns failure/recovery at each transition.

Inspect long methods spanning prepare/dispatch/settlement for distinct authority, effects, and result boundaries. Improve owner placement and locality first. Do not merely create more files, pass a giant context object, or introduce an all-purpose ContextManager that moves the same confusion. Keep transactions and shared invariants cohesive; state what a proposed split hides and what coordination it adds.

## 4. Test governance and truthful claims

- Separate future authoring RED tests from regressions against currently accepted behavior. Record the intended stage and source; neither quietly promote RED into a current release blocker nor dismiss an accepted regression as future work.
- Check fixtures for stale selectors and hooks attached to the wrong owner. Trace the actual production entry and observation seam before changing assertions.
- For idempotent replay, ensure repeated capture does not append a second effect and create a false snapshot. Assert identity, effect count, and relevant settlement semantics at the real owner.
- Distinguish a synthetic wake/callback from a real accepted continuation claim. Test what the producer actually emits and the consumer actually accepts.
- Label same-process/in-memory proof separately from restart or cross-process recovery. Never describe one as the other.
- Do not delete, skip, weaken assertions, narrow scenarios, or redefine acceptance just to get green. When retiring an obsolete seam, first map and migrate its original required invariants to the real production seam and demonstrate coverage there.

Choose verification that resolves the specific uncertainty at the current stage. Reuse applicable evidence with its revision and limits; avoid repeated offline checks that cannot establish the missing runtime claim. A pass supports only the exercised contract and environment.

## 5. Candidate disposition and stopping rule

For every recommendation state retained capability, removed/narrowed promise (or none), real producer/consumer, current/proposed owner, evidence and limits, acceptance stage, and safest next step. Include split/merge/retain rationale and protected invariants.

Check existing owners, active specs, issues, and refactors before opening another plan. Continue or amend the existing work within authorization instead of creating duplicate specs. If creating or implementing a follow-on is not authorized, propose it rather than taking that action. End the review when qualified evidence-backed candidates and the next decision are clear; do not manufacture work or rerun unchanged validation to appear active.

