---
name: aes-code-review
description: Standalone two-axis code review. Review changes since a fixed point along Standards and Spec axes, discover the originating issue/spec without external setup files, apply repository standards plus a built-in code-smell baseline, and report both axes separately. Use for branch, PR, WIP, or "review since X" requests.
---

# Code Review — Standalone

Review the diff between `HEAD` and a fixed point along two independent axes:

- **Standards**: does the change conform to this repository's documented coding standards and baseline code-quality heuristics?
- **Spec**: does the change faithfully implement the originating issue, requirement, or spec?

Keep these axes separate throughout. A change may pass one and fail the other. Do not merge, rerank, or collapse the findings into one score.

This skill is fully self-contained. Do not depend on `docs/agents/issue-tracker.md`, `/setup-matt-pocock-skills`, or any external skill.

## 1. Pin the fixed point

Use the fixed point supplied by the user: commit SHA, branch, tag, `main`, `HEAD~5`, etc.

If the user gives a PR, infer the base branch from the PR metadata when tooling allows. If they give a branch but no base and the repository has an obvious default branch, use the default branch. Only ask when the fixed point genuinely cannot be inferred.

Resolve the fixed point before reviewing:

- `git rev-parse <fixed-point>`
- `git diff <fixed-point>...HEAD`
- `git log <fixed-point>..HEAD --oneline`

Use the three-dot diff so the comparison is against the merge-base.

Stop early and report clearly when:

- the ref cannot be resolved;
- the diff is empty;
- repository access is unavailable.

Do not let these failures surface later inside the review passes.

## 2. Discover the spec source

Find the originating requirement in this order:

1. **Issue/PR references in commit messages or branch metadata**: `#123`, `Closes #45`, GitLab `!67`, issue URLs, PR URLs, ticket keys, etc.
   - If a connected repository tool can resolve the issue/PR, fetch it directly.
   - Prefer the issue body/specification text over discussion comments unless the comments explicitly amend the requirement.
   - If the remote tracker cannot be accessed, note that limitation and continue discovery below.
2. **User-provided path or URL**: use it as the primary spec source.
3. **Repository files**: search `docs/`, `specs/`, `.scratch/`, `.github/`, or similar requirement directories for filenames matching the branch name, feature name, ticket number, or commit wording.
4. **PR description**: when reviewing a PR, use the PR body as a spec source if it contains explicit requirements or acceptance criteria.
5. **No spec**: if no requirement source can be found, do not block the whole review. Run the Standards axis and report `No spec available` under Spec. Ask the user for a spec only when they specifically need the Spec axis completed.

When multiple sources disagree, do not silently reconcile them. State the conflict and identify which source is newer or more authoritative when that is explicit.

## 3. Discover repository standards

Search for documents that define how code should be written, including but not limited to:

- `AGENTS.md`
- `CLAUDE.md`
- `CONTRIBUTING.md`
- `CODING_STANDARDS.md`
- `STYLEGUIDE.md`
- repo-specific README sections
- package- or directory-local instruction files

Respect scope: a standards file nearest the changed code may override broader repository guidance.

Skip rules already deterministically enforced by tooling when the tool output is available (formatter, linter, type checker, generated-file checks, etc.). The review should focus on judgement that automation does not already settle.

### Built-in smell baseline

Always carry the following heuristics unless a documented repository standard explicitly endorses the pattern. Repository standards override this baseline. Smells are judgement calls, not hard violations.

- **Mysterious Name**: name does not reveal what a function, variable, or type means. → rename; if no honest name exists, inspect the design.
- **Duplicated Code**: same logic shape appears in multiple changed hunks/files. → extract the shared shape when that improves locality rather than creating speculative abstraction.
- **Feature Envy**: a method reaches into another object's data more than its own. → move behavior toward the data it uses.
- **Data Clumps**: the same fields/params repeatedly travel together. → consider one domain type.
- **Primitive Obsession**: a primitive/string represents a meaningful domain concept. → consider a focused type.
- **Repeated Switches**: the same switch/if cascade on the same discriminator repeats. → centralize the branching or use polymorphism when justified.
- **Shotgun Surgery**: one logical change requires scattered edits across many files. → gather what changes together into one module.
- **Divergent Change**: one file/module changes for unrelated reasons. → split responsibilities if the split improves locality.
- **Speculative Generality**: abstractions, hooks, flags, or parameters exist for requirements the spec does not have. → remove or inline until a real need exists.
- **Message Chains**: callers depend on long navigation such as `a.b().c().d()`. → hide the navigation behind a better interface.
- **Middle Man**: class/function mostly delegates onward. → remove the unnecessary indirection when it adds no policy or abstraction value.
- **Refused Bequest**: subclass/implementer ignores or overrides much of what it inherits. → prefer composition or a narrower interface.

For each baseline finding, label it `possible <Smell Name>` or equivalent. Do not phrase a smell as a categorical violation.

## 4. Run two independent review passes

Prefer two independent parallel review contexts when the environment supports them. If parallel sub-agents are unavailable, run the passes sequentially but keep their evidence, criteria, and conclusions isolated. Do not let one axis influence the other.

### Standards pass

Inputs:

- fixed point;
- exact diff or changed-file patches;
- commit list;
- standards-source files and their relevant rules;
- the built-in smell baseline above.

Review for:

1. **Documented-standard violations**
   - cite the standards source and exact rule;
   - cite the changed file/hunk;
   - distinguish hard requirements from recommendations.
2. **Baseline smells**
   - name the smell;
   - cite the changed hunk;
   - explain why it may matter in this repository;
   - suppress the smell if repository guidance explicitly prefers that design.

Do not complain about unchanged legacy code unless the new diff materially worsens or relies on it.

Keep this section concise: target under 400 words unless the user asks for a deep review.

### Spec pass

Inputs:

- fixed point;
- exact diff or changed-file patches;
- commit list;
- spec/issue/PR requirement source.

Review for:

1. **Missing or partial requirements**: the source asked for something the diff does not fully implement.
2. **Scope creep**: behavior or complexity added without support from the source requirement.
3. **Incorrect implementation**: a requirement appears implemented, but the behavior does not actually satisfy it.
4. **Acceptance-risk gaps**: missing error states, edge cases, migrations, tests, compatibility, or observable behavior explicitly required by the spec.

Cite the requirement text or line for every finding. If the source has no line numbering, quote the smallest useful phrase and identify the section/heading.

Do not invent implied requirements unless you label them clearly as inference rather than spec failure.

Keep this section concise: target under 400 words unless the user asks for a deep review.

If no spec exists, skip this pass and report exactly that rather than converting Standards concerns into Spec findings.

## 5. Evidence discipline

Every actionable finding should answer:

- **Where?** file and hunk/line.
- **What evidence?** exact repo standard, spec requirement, or named smell heuristic.
- **Why does it matter?** concrete consequence in behavior, maintainability, locality, testability, or correctness.
- **What is the smallest reasonable fix?** concise remediation, not a redesign unless the finding truly requires one.

Prioritize correctness and requirement mismatches over stylistic preferences.

Avoid:

- generic praise;
- hypothetical bugs unsupported by the diff;
- restating formatter/linter output as review insight;
- demanding broad refactors unrelated to the changed code;
- turning a smell heuristic into a hard rule.

## 6. Aggregate without collapsing the axes

Use this output structure:

```md
## Standards

<findings from the Standards pass>

## Spec

<findings from the Spec pass, or "No spec available">

Summary: Standards — N findings; worst within this axis: <issue or none>. Spec — M findings; worst within this axis: <issue, none, or no spec available>.
```

Do not:

- pick one overall winner across axes;
- compute a combined score;
- hide a Spec failure because Standards are clean;
- hide a Standards failure because the feature works.

## 7. Severity inside an axis

When useful, classify findings inside each axis as:

- **Blocking**: likely correctness, security, data-loss, contract, or explicit-spec failure that should be fixed before merge.
- **Important**: significant maintainability, testability, standards, or partial-requirement issue.
- **Minor**: localized quality issue with limited impact.
- **Judgement call**: code smell or design concern where reasonable engineers may disagree.

Severity is local to each axis. Never use it to rank Standards against Spec.

## 8. Follow-up behavior

If the user asks to fix findings:

- preserve the Standards/Spec distinction in the implementation plan;
- fix blocking correctness/spec issues before judgement-call smells;
- avoid unrelated cleanup;
- rerun the same fixed-point review after changes when possible.

If the user asks for a shorter review, reduce prose, not evidence quality.

