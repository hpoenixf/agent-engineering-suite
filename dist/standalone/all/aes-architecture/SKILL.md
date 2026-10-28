---
name: aes-architecture
description: Standalone codebase architecture review. Find deepening opportunities plus misplaced ownership, duplicate interfaces, unnecessary pass-through layers, test-only production seams, compatibility shadows, misleading test seams, recent-change hotspots, and unsupported contract promises; present a visual HTML report, then guide the selected refactor through a decision-tree interview and alternative interface design. Use for architecture review, simplification, locality, testability, AI-navigability, seam placement, or "why is this layer here?" investigations.
---

# Improve Codebase Architecture — Standalone

Find architectural friction and propose **deepening opportunities**: changes that increase capability behind smaller, better-placed interfaces. Do not optimize for the number of modules removed. Optimize for **correct ownership, depth, locality, leverage, and truthful test seams**.

This skill is fully self-contained. Do not call or depend on external architecture, grilling, or domain-modeling skills.

## Architecture vocabulary

Use these terms precisely in architecture discussion.

- **Module**: anything with an interface and an implementation; function, class, package, or tier-spanning slice.
- **Interface**: everything a caller must know to use the module correctly, including invariants, ordering, error modes, configuration, and performance characteristics.
- **Implementation**: what sits inside the module.
- **Depth**: leverage at the interface. A module is **deep** when much behaviour sits behind a small interface, **shallow** when callers must understand nearly as much as the implementation.
- **Seam**: a place where behaviour can vary without editing at that location; the location where a module's interface lives.
- **Adapter**: a concrete thing that satisfies an interface at a seam.
- **Leverage**: capability callers get per unit of interface they must learn.
- **Locality**: how strongly change, bugs, knowledge, and verification concentrate in one place.
- **Owner**: the module that is authoritative for one concept's identity, schema, state, policy, lifecycle, or semantics.
- **Shadow owner**: another module that duplicates or reinterprets an owner's facts and can drift independently.
- **Compatibility shadow**: a deprecated alias, translator, registry, wrapper, re-export, or copy retained after the real production seam moved elsewhere.

Do not substitute vague terms such as "cleaner", "more maintainable", or "more abstract" for the concrete properties above.

## Core principles

1. **Depth is a property of the interface, not implementation size.**
2. **Correct ownership precedes single ownership.** Going from three owners to one is not enough if the remaining owner is still the wrong place.
3. **Deletion test is mandatory.** Imagine deleting the module:
   - if required complexity spreads into real callers, the module is earning its seam;
   - if the mapping, schema copy, compatibility logic, or test structure simply disappears, it is likely shallow or misplaced.
4. **The interface is the test surface.** Tests should cross the same seam production crosses. A production-source module used only by tests is suspicious unless explicitly staged for a future owner.
5. **Upstream contracts should not be recopied downstream.** If an upstream owner already defines identity/schema/state, downstream modules should normally consume it rather than rebuild a parallel catalog.
6. **One adapter = hypothetical seam; two materially different adapters = evidence of a real seam.**
7. **Replace, don't layer.** When a better seam exists, migrate invariants and delete the old layer; do not keep a compatibility wrapper indefinitely.
8. **Accept dependencies; don't create them internally** when internal creation blocks testing.
9. **Return results where practical instead of hiding outcomes in side effects.**

## Three-level architecture review

Every serious candidate must pass all three levels. Do not stop after fixing Level 1.

### Level 1 — Duplicate owner check

Ask: **Is the same concept statically encoded in more than one place?**

Trace concepts such as:
- tool names, descriptions, schemas, permissions, capabilities;
- route/action mappings;
- error/status enums;
- configuration defaults and resource limits;
- persistence/recovery identities;
- domain classifications and presentation taxonomies;
- provider metadata and adapter registries.

Flag:
- repeated schema declarations;
- mapping tables that mirror an upstream registry;
- derived fields persisted beside their authoritative input and revalidated later;
- two catalogs that must remain synchronized;
- model-facing and provider-facing identities that differ only because of a translation layer.

A successful Level-1 refactor may reduce N owners to one. **Continue to Level 2.**

### Level 2 — Owner placement check

Ask: **Should the remaining owner exist here at all?**

Trace the concept from its natural authority to its consumers.

Examples:
- a protocol/server already owns a tool's identity and schema, while Runtime owns a second "canonical" tool contract;
- a source adapter already owns provenance/freshness, while a downstream projection recreates the same facts;
- a domain object already owns classification, while presentation code reclassifies it;
- a gateway owns source handles, while Runtime reconstructs a parallel state machine.

Prefer the owner closest to the concept's natural authority. A runtime/orchestrator should not own business-tool vocabulary merely because it happens to execute calls.

### Level 3 — Deletion test

Ask: **What exactly happens if this module disappears?**

Classify the result:

- **Complexity relocates**: callers now each need real coordination/policy/state logic → the module is earning its seam.
- **Complexity internalizes**: one deeper owner absorbs the behaviour behind a smaller interface → good deepening candidate.
- **Complexity vanishes**: only pass-through mappings, duplicate schemas, compatibility aliases, or self-tests disappear → strong deletion candidate.
- **Invariant disappears**: a real safety/semantic invariant would be lost → migrate that invariant to the correct owner before deletion.

Record this verdict explicitly for every surfaced candidate.

## High-signal scans

### A. Ownership-chain scan

For each hot concept, draw:

```text
natural authority
  -> registry/schema
  -> adapter
  -> runtime/orchestrator
  -> model/UI
```

At every hop ask:
- Is identity renamed?
- Is schema redefined?
- Is policy duplicated?
- Is state copied?
- Is a derived projection later treated as authority?
- Is a second validation only checking that two copies still agree?

A long chain is not automatically bad. A chain where adjacent modules carry nearly identical interfaces is.

### B. Production reachability scan

For modules under production source roots (`src`, `server`, equivalent):
- find non-test importers/callers;
- distinguish production reachability from tests, fixtures, labs, generated artifacts, and historical docs;
- flag modules whose only active consumers are tests.

A test-only production module is not automatically dead. It needs one of:
- an explicit near-term future owner/change;
- dynamic/plugin loading that static search cannot see;
- generated/runtime discovery evidence;
- a documented compatibility requirement with a real external consumer.

Otherwise treat it as a retirement candidate, not proven dead code. Record the search scope and unresolved dynamic/external consumers before recommending deletion.

### C. Compatibility-shadow scan

Search for:
- deprecated aliases;
- re-export-only files;
- `compat`, `legacy`, `fallback`, `adapter`, `wrapper`, `translator`, `projection`, `registry`, `facade`, `mapper`;
- old/new protocol translators;
- dual read/write paths;
- "keep historical import surface stable" comments;
- tests that exercise only the compatibility layer.

Do not delete based on names or modification time. Apply the ownership, contract, and deletion tests, preserving protected invariants.

### D. Schema/identity duplication scan

Compare declarations across:
- MCP/RPC/server registration vs model-tool catalogs;
- provider schema vs application schema;
- persisted receipt identity vs synthetic action identity;
- Skill/tool allowlists vs runtime ceilings;
- domain enums repeated in config, server, model, and UI.

Strong signal: a new capability requires synchronized edits to several static lists.

### E. Test-oracle scan

Ask:
- Does the test use the same seam production uses?
- Is the test proving the behaviour, or only proving a translator/helper/registry behaves according to itself?
- Does a helper create facts production never creates?
- Did a historical implementation become the oracle after production moved?
- Are tests green because they assert the mapping layer, not the end-to-end invariant?

If a production seam moved, migrate the invariant to the new seam before deleting old tests. Apply the test-governance checks in `CONTRACT-AND-HOTSPOT-AUDITS.md`: stage-aware RED vs accepted regression, fixture/owner correctness, replay capture, synthetic vs accepted events, and process-boundary evidence.

### F. Runtime/orchestrator ownership scan

Runtime modules attract accidental ownership. Inspect whether they own:
- business-tool catalogs;
- domain taxonomies;
- provider-specific schemas;
- source-state machines;
- semantic normalization beyond mechanical validation;
- duplicated authorization facts.

Runtime may legitimately own lifecycle, budgets, cancellation, recovery, receipts, continuation, and orchestration. Treat domain/business vocabulary inside Runtime as a prompt to verify placement.

### G. Contracts, lifecycle, and recent-change hotspots

Read and apply `CONTRACT-AND-HOTSPOT-AUDITS.md`. Freeze the default seven-day history window and target SHA; prioritize meaningful churn, repeated function edits, and cross-owner co-change without equating frequency with poor architecture. Compare accepted intent, producers/consumers, code, tests, and runtime evidence. Audit initialization ordering and prepare/dispatch/settlement responsibility. Preserve protected boundaries and mark missing evidence as unverified.

## Dependency categories for deepening

Classify dependencies before proposing a refactor:

1. **in-process** — pure computation/in-memory; usually deepenable directly.
2. **local-substitutable** — local test stand-in exists, e.g. in-memory FS or local DB; keep seam internal.
3. **ports & adapters** — remote but owned dependency; define a port at the seam, with production and in-memory/test adapters.
4. **mock** — true external third party; inject a port and use a mock adapter in tests.

## Process

### 1. Scope before scanning

Apply YAGNI. Deepening pays off where change is likely.

- If the user names a module, subsystem, or pain point, use that scope.
- Inspect the last seven days of change history within the requested scope by default, or the explicit user window. Use the fixed-window, rename/noise, and coverage procedure in `CONTRACT-AND-HOTSPOT-AUDITS.md`. Prefer areas repeatedly changed, reviewed, or associated with incidents/spec churn; frequency alone does not justify splitting.
- Read `CONTEXT.md`, `CONTEXT-MAP.md`, architecture docs, active specs, and relevant ADRs before judging ownership.
- Inspect recent architecture/refactor history when available. Ask not only "what was fixed?" but **"what assumption did the earlier review stop at?"** This often reveals a locally improved but globally misplaced owner.

### 2. Explore organically, then run the mandatory audits

Walk the codebase for normal friction:
- understanding one concept requires bouncing through many tiny modules;
- interface nearly matches implementation;
- orchestration knowledge leaks across seams;
- call sites repeat coordination;
- important behaviour is hard to test through the public interface;
- modules exist to translate between nearly identical shapes.

Then run these mandatory audits on the strongest hot spots:
1. ownership-chain scan;
2. production-reachability scan;
3. schema/identity duplication scan;
4. compatibility-shadow scan;
5. test-oracle scan;
6. contract/promise and protected-invariant audit;
7. lifecycle/initialization and prepare/dispatch/settlement responsibility audit;
8. recent-change hotspot audit, with explicit missing-history limitations;
9. Level 1 → Level 2 → Level 3 review.

Do not claim the scan is complete after merely centralizing duplicate maps.

### 3. Candidate qualification

For each candidate, capture:

- **Current owner chain**: natural authority → current owners/consumers.
- **Problem**: what callers/maintainers must know today.
- **Deletion-test verdict**: relocates, internalizes, vanishes, or loses invariant.
- **Test-surface verdict**: production seam, shadow seam, or test-only seam.
- **Proposed owner**: where the behaviour should live after the refactor.
- **Modules to delete/internalize**.
- **Dependency category**.
- **Contract disposition**: retained capability, removed/narrowed promise or none, real producer/consumer, protected invariants, and current acceptance stage.
- **Evidence and limits**: source anchors, history window/coverage, runtime boundary, unresolved claims and reconciliation owner.
- **Safe next step**: split/merge/retain rationale, reason not to split, existing owner/spec, and the smallest authorized action that resolves uncertainty.
- **Recommendation strength**:
  - `Strong`: clear wrong-owner/shadow/pass-through issue with a credible target owner.
  - `Worth exploring`: material friction but trade-offs or hidden consumers remain.
  - `Speculative`: pattern is suggestive but evidence is incomplete.

Do not surface cosmetic file moves as architecture candidates.

### 4. Produce the HTML architecture report

Write one self-contained HTML report to an authorized artifact directory, outside the repo unless requested otherwise. Respect user filesystem rules and prohibitions on temporary-directory development; do not assume the OS temp directory is allowed. Follow `HTML-REPORT.md`.

Each candidate card must include:
- Files/modules involved
- Current owner chain
- Problem
- Proposed owner/solution
- Deletion-test verdict
- Test-surface verdict
- Benefits in locality, leverage, and tests
- Before / After visualization
- Recommendation strength
- Dependency category
- ADR conflict callout when relevant
- Contract disposition, evidence limits, acceptance stage, and safe next step
- Hotspot evidence and split/merge/retain rationale, including why not to split

Add a compact **Review blind spot** note when the candidate plausibly survived prior refactors because review stopped at a local optimization (for example "three owners → one owner") instead of questioning the remaining seam. Keep this factual and source-backed.

End with a **Top recommendation** section naming the strongest candidate and why.

Do **not** design the final interface during initial scanning. Ask which candidate to explore only if the user has not already selected one or authorized autonomous selection. Honor existing scope and implementation authorization; resolve source-answerable facts without asking again.

### 5. Decision-tree grilling loop

Once a candidate is selected by the user or under their authorization, model the unresolved design as a tree.

Before each round:
1. recompute the frontier;
2. auto-resolve facts and dominated implementation details;
3. ask only load-bearing decisions.

Use:

```md
❓ **Q1 — <title>**: <trade-off>

➡️ **Recommendation:** <answer and reason>
```

The tree should normally cover:
- intended responsibility and correct owner;
- exact seam placement;
- what becomes internal vs crosses the interface;
- state/lifecycle ownership;
- authorization/policy ownership when relevant;
- what old modules disappear;
- which compatibility shadows are deleted;
- what tests migrate to the real seam;
- recovery/operational constraints;
- migration sequencing.

Do not implement while load-bearing decisions remain unresolved. Existing explicit implementation authorization is sufficient for source-resolvable choices; ask only about genuine scope, security, or consequential trade-offs not already settled. Review authorization alone does not authorize repository edits.

### 6. Maintain domain language inline

During the grilling loop:
- add genuinely canonical domain terms to the relevant `CONTEXT.md`;
- do not record implementation details as glossary terms;
- when "owner", "projection", "runtime", or "adapter" is overloaded, resolve the domain-specific meaning before using it in a decision.

### 7. Offer ADRs sparingly

Offer an ADR only when all are true:
1. hard to reverse;
2. surprising without context;
3. a real trade-off.

A deliberate decision to keep a seemingly redundant seam can merit an ADR if future reviewers would otherwise repeatedly try to delete it.

### 8. Design the interface at least three ways

When concrete design starts, first state constraints and the intended owner. Then generate at least three materially different designs:

- **Minimal interface**: smallest surface, maximum depth.
- **Flexible interface**: extension points where real variation exists.
- **Common-path interface**: dominant caller is trivial.
- **Ports & adapters variant** when multiple real adapters justify the seam.

For each:
1. interface and invariants;
2. usage example;
3. implementation hidden behind it;
4. dependency/adapter strategy;
5. migration/deletion impact;
6. trade-offs in depth, locality, leverage, and test surface.

Compare them explicitly and recommend one.

### 9. Finalize the refactor plan

Cover:
- target owner/module/interface;
- modules to collapse/delete/internalize;
- compatibility shadows to remove;
- tests to migrate/delete;
- domain/ADR updates;
- incremental order;
- rollback/compatibility constraints;
- architecture guard when the failure mode is likely to recur.

Prefer a guard on the real structural failure (duplicate catalog, test-only production seam, shadow registry) over a comment reminding maintainers not to repeat it.


