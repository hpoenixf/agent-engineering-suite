---
name: aes-grilling
description: Stress-test a plan, decision, or idea through a focused design-tree interview. Resolve obvious choices automatically and ask the user only about consequential tradeoffs, preferences, and ambiguous decisions.
---

Stress-test the user's thinking until you reach a shared model at the requested discussion depth, with a concrete current delivery commitment. Map the problem as a **design tree**: decisions branch into the decisions that depend on them.

The goal is not to maximize questions. The goal is to expose the smallest set of decisions that can materially change the outcome.

## Delivery stages

Assess whether the proposed spec is too broad for one delivery: look for several independently valuable outcomes, peripheral work delaying the first usable result, or unresolved dependencies and uncertainty that make a single commitment hard to verify. Explain the relevant reason and recommend a phased cut when useful; document length or task count alone is not a reason to split. Keep small cohesive work together.

Separate discussion depth from implementation scope. The user may want to discuss the whole design now and implement it in batches. Honor that breadth while defining the first useful result the user can actually obtain.

- Map the whole direction when useful, then strictly separate execution into independently usable stages. State each stage's scope and exclusions, intended output, necessary dependencies and implementation order; make acceptance concrete before that stage starts. A single spec may contain these stages; separate changes when ownership or acceptance lifecycles warrant it.
- Build the execution queue around the core end-to-end result and its necessary dependencies. Keep current-stage tasks and acceptance separate from later-stage queues. Until the core result is delivered, advance only work needed for that result; peripheral systems wait for their stage, including when parallel agents are available. Explain any claimed prerequisite by the current outcome it enables. Stage labels on a flat mixed queue do not satisfy this rule.
- Put the core path first. UI polish, automation, historical comparison, integrations, and quality optimization enter a stage only when its stated result needs them. Keep security, permissions, privacy, and essential correctness with the effect they protect.
- Make the current stage concrete enough to execute and accept. Discuss later stages to the user's requested depth: they may remain a rough direction, open questions, or a lightweight design sketch. Settle future constraints that would force costly rework now; keep other uncertainty explicit and revisit it when that stage starts.
- When useful, reserve future extension points in the design: purpose, expected inputs/outputs, ownership or compatibility constraints, and unresolved choices. Record these in the existing plan/spec as provisional design notes; implementation scaffolding belongs in the current stage only when it has a demonstrated current need. Later detail does not become a prerequisite for current delivery.
- Preserve an explicit user sequence. For example, offline generation and obtaining the file come before model integration when requested; a model stub or a passing test that leaves no obtainable file does not fulfill that delivery.
- If autonomous execution is the requested capability, define a complete command or ordinary request that succeeds without human parameter repair, manual artifacts, or mid-run takeover. Program-owned data transfer belongs in the implementation, not in extra user requirements.
- When the user narrows scope, revise the current commitment and move deferred work out of its completion conditions. Keep prior decisions and useful unfinished work traceable.

Use the existing summary or plan to record the scope assessment and reason for splitting or keeping it together, current output and acceptance, stage order, and later-stage sketches/open questions. Do not add a second checklist, a mandatory phase count, or another approval round.

## Decision filter

Before asking anything on the frontier, classify each node:

### Auto-resolve

Do **not** ask the user when there is a clearly dominant answer. Choose it and continue when one option is strongly preferred because it:

- directly follows from goals or constraints the user already stated;
- is supported by substantially stronger evidence or established practice;
- is low-risk, low-cost, and easy to reverse;
- removes complexity without sacrificing a stated requirement; or
- is an implementation detail whose alternatives would not materially change the user's outcome.

Treat the recommended option as settled. Mention it only when it helps the user understand a later tradeoff or the final summary. Do not turn an obvious recommendation into a confirmation question.

### Ask

Ask the user only when the decision is **load-bearing** and the answer cannot be responsibly inferred. Typical reasons:

- two or more viable options have meaningful tradeoffs;
- the choice materially changes scope, cost, risk, timeline, quality, or future flexibility;
- the choice depends on the user's values, priorities, appetite, or taste;
- the decision is expensive or difficult to reverse; or
- available evidence is genuinely insufficient to prefer one option strongly.

If a choice is important but you still have a strong recommendation, ask the question and put the recommendation first-class in the prompt.

## Detail filter

Shield the user from details that are unlikely to affect their decision.

Keep internal or omit entirely:

- low-level implementation mechanics;
- naming, file layout, boilerplate, and routine configuration;
- minor edge cases with no material effect on the recommended direction;
- intermediate reasoning that only supports an already-settled choice;
- facts you can inspect or derive yourself.

Surface a detail only if changing it could alter the recommendation, introduce a meaningful risk, constrain a later branch, or require an explicit user preference.

Prefer outcome-level language. Collapse several low-level decisions into one higher-level question whenever they represent the same tradeoff.

## Rounds and frontier

Work the tree in **rounds**. The **frontier** is the set of unresolved, decision-worthy nodes whose prerequisites are already settled.

Before every round:

1. Recompute the frontier at the user's requested discussion breadth. Keep current implementation decisions distinct from later-stage exploration; default to current-stage blockers when no broader discussion was requested.
2. Auto-resolve obvious nodes using the decision filter.
3. Remove low-impact details using the detail filter.
4. Ask only the remaining load-bearing questions.

Do not ask a question whose answer depends on another unresolved question in the same round; leave it for a later round.

Keep rounds compact. Prefer fewer, higher-leverage questions over exhaustive coverage.

Format each asked question like this:

```
❓ **Q1 — <decision title>**: <the tradeoff in concise, outcome-level language>

➡️ **Recommendation:** <recommended option and the main reason>
```

When useful, include 2-4 materially distinct options. Do not enumerate cosmetic variants.

## Facts vs decisions

Finding **facts** is your job, never the user's. Inspect the environment, files, tools, or other available evidence instead of asking the user to retrieve information you can obtain yourself.

The user's attention is reserved for decisions that require their judgment. Do not ask them to validate your research process, implementation details, or obvious defaults.

## Completion

The interview is complete when the current deliverable, observable acceptance and execution order are clear, no unresolved load-bearing decision blocks that stage, and the user's requested broader discussion has been covered at the agreed depth. Later-stage questions may remain explicitly open; a clear first stage is not a reason to cut short a requested whole-design discussion. Interview completion is a settled plan, not evidence that implementation or delivery has succeeded.

End with a concise summary of:

- the decisions that materially shape the outcome;
- any assumptions that remain genuinely important; and
- the first deliverable and its acceptance, the stage order, and the next action; and
- the scope assessment, deferred capabilities, provisional extension points and open questions, distinguishing discussed direction from implementation commitments.

Do not add a ceremonial confirmation step when the direction is already clear. If the user originally asked you to produce or execute something after the grilling, proceed from the settled decisions unless the next step is irreversible, externally consequential, or explicitly requires confirmation.

