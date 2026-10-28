---
name: aes-spec-flow
description: Plan, implement, and verify an evidence-linked specification using a self-contained structural evidence toolkit. Use for spec lifecycle and provenance checks, not as proof of semantic acceptance.
---

# Evidence-linked spec flow

Fix the requested scope, owner, revision and acceptance boundary before changing implementation. Read the active spec and its prior evidence; do not create a competing spec for an already owned task. Separate proposal, implementation, selected tests, real integration, product acceptance and archive.

The bundled [toolkit guide](toolkit/README.md) documents the actual CLI, schema and supported files. Resolve `toolkit/bin/spec-evidence.mjs` from this skill directory. Use its `--help` before choosing arguments. It supports structural lint stages, verification and status; it does not run paid evaluation, prove business quality, authorize deployment or automatically close a spec.

1. Plan the smallest coherent end-to-end outcome with explicit exclusions, dependencies and observable acceptance.
2. Implement within current permissions; attach evidence to the original owner and immutable revision.
3. Run relevant checks, preserving failures and unknown outcomes. Structural pass is not runtime acceptance.
4. Verify code, evidence, generated documentation and actual deliverable agree. Archive only when the agreed acceptance is actually supported and archival is authorized.

The toolkit README is authoritative for structural guarantees. Never weaken scope or check a task merely to make lint pass. A blocked real evaluation does not prevent unrelated authorized implementation, but remains an explicit gap.
