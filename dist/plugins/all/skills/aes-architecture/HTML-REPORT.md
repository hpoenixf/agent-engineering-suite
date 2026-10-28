# HTML Report Format

Render the architecture review as one self-contained HTML file in an authorized artifact directory, respecting user filesystem restrictions. Tailwind and Mermaid may come from CDNs. The report should make ownership and deletion decisions visually obvious, not look like a generic dashboard.

## Required structure

### Header

Show:
- repo name and revision/date;
- legend: module, seam, leakage, authoritative owner, shadow owner, test-only seam;
- one sentence defining the review focus;
- hotspot window, timezone, fixed head SHA, history coverage/truncation, and counting/noise rules.

### Candidate cards

Each candidate card must include:

- **Title**: name the architectural move, e.g. “Delete the synthetic Tool contract”.
- **Badges**:
  - recommendation strength: `Strong`, `Worth exploring`, `Speculative`;
  - dependency category;
  - test surface: `production`, `shadow`, or `test-only`.
- **Files/modules**: compact monospaced list.
- **Owner chain**: `natural authority → current owner(s) → consumer`.
- **Before / After diagram**: centrepiece.
- **Problem**: one sentence.
- **Proposed owner**: one sentence.
- **Deletion-test verdict**: one of:
  - complexity relocates;
  - complexity internalizes;
  - complexity vanishes;
  - invariant must migrate first.
- **Wins**: short bullets using locality/leverage/depth/test-surface language.
- **Review blind spot**: optional one-line note when prior refactors plausibly stopped at local consolidation rather than owner placement.
- **ADR callout** when applicable.
- **Contract disposition**: capability retained, promise removed/narrowed or none, real producer/consumer, protected invariants, and acceptance stage.
- **Evidence and limits**: compact source/commit anchors and unsupported claims; do not equate local green with whole-system acceptance.
- **Hotspot rationale**: meaningful change/repeated-function/co-change evidence; split, merge, or retain recommendation and reason not to split.
- **Safe next step**: existing owner/spec and the smallest authorized action; unresolved decision owner when needed.

## Diagram patterns

Use the visual form that best explains the candidate.

### 1. Owner-chain diagram

Best for duplicate or misplaced authority.

Before:

```text
MCP schema → static model catalog → Runtime contract → model
              ^ shadow owner        ^ shadow owner
```

After:

```text
MCP schema ───────────────→ Tool surface → model
   authoritative owner
```

Use dark fill for the authoritative owner, red/amber for shadow owners, and a dashed outline for compatibility seams.

### 2. Deletion-test diagram

Two panels:
- “delete it”;
- “what remains”.

If callers inherit real policy/state complexity, show the spread.
If only arrows/translation boxes disappear, show the simplified path and label “complexity vanishes”.

### 3. Production-vs-test reachability

Use two lanes:

```text
production:  A → B → C
tests:       T → LegacyHelper
```

Highlight a production-source module with no production edge as `test-only seam`.

### 4. Cross-section

Use stacked bands for several thin pass-through layers. The after view should show one deeper owner with former internals faded inside.

### 5. Mass diagram

Show interface surface vs implementation mass. Good for shallow modules where callers learn almost everything.

## Style guidance

- Editorial, sparse, diagram-led.
- Use one accent plus red for leakage/shadow ownership and amber for uncertainty.
- Avoid decorative metrics.
- Keep candidate prose short; if a paragraph is needed to explain the diagram, redraw it.
- Use architecture vocabulary precisely: module, interface, implementation, depth, shallow, deep, seam, adapter, leverage, locality, owner, shadow owner.
- Do not call every intermediary a “wrapper”; name its actual architectural role.

## Top recommendation

One larger card with:
- candidate name;
- why it is strongest;
- owner move (`from → to`);
- deletion-test verdict;
- expected deletion/internalization count if known.

No ceremonial conclusion.


